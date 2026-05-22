#!/usr/bin/env python3
"""Scan common experiment result files and produce thesis-console reports.

This is a lightweight first-pass scanner. It extracts common metric names from
CSV/TSV/JSON/TXT/LOG files and records where each value came from. It does not
replace manual experiment auditing or claim review.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any, Iterable


SUPPORTED_SUFFIXES = {".json", ".csv", ".tsv", ".txt", ".log"}
DEFAULT_IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "external-skill-candidates",
}
DEFAULT_IGNORED_FILENAMES = {
    "result-scan-table.csv",
}

METRIC_ALIASES = {
    "accuracy": "accuracy",
    "acc": "accuracy",
    "f1": "f1",
    "f1_score": "f1",
    "f1score": "f1",
    "macro_f1": "macro_f1",
    "macro_avg": "macro_avg",
    "macro_average": "macro_avg",
    "precision": "precision",
    "recall": "recall",
    "loss": "loss",
    "auc": "auc",
    "roc_auc": "auc",
    "rmse": "rmse",
    "mae": "mae",
    "r2": "r2",
    "r_squared": "r2",
}

BOUNDED_METRICS = {"accuracy", "f1", "macro_f1", "precision", "recall", "auc"}
NONNEGATIVE_METRICS = {"loss", "rmse", "mae"}


@dataclass
class MetricRecord:
    file: str
    file_type: str
    metric: str
    value: float
    unit_or_scale: str
    location: str
    context: str
    status: str
    note: str


@dataclass
class ParseIssue:
    file: str
    file_type: str
    issue: str


def normalize_key(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("%", " percent")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def metric_name_from_path(path_parts: Iterable[str]) -> str | None:
    normalized = [normalize_key(str(part)) for part in path_parts if str(part).strip()]
    if not normalized:
        return None

    joined = "_".join(normalized)
    last = normalized[-1]

    if "macro_avg" in joined or "macro_average" in joined:
        if last in {"f1_score", "f1", "f1score"}:
            return "macro_f1"
        if last in {"precision", "recall"}:
            return f"macro_{last}"
        if last in {"support", "count", "n"}:
            return None
        return "macro_avg"

    if joined in METRIC_ALIASES:
        return METRIC_ALIASES[joined]
    if last in METRIC_ALIASES:
        return METRIC_ALIASES[last]
    return None


def to_float(value: Any) -> tuple[float | None, str]:
    if isinstance(value, bool):
        return None, ""
    if isinstance(value, (int, float)):
        number = float(value)
        return number, "ratio_or_raw"
    if not isinstance(value, str):
        return None, ""

    text = value.strip()
    if not text:
        return None, ""

    percent = text.endswith("%")
    text = text.rstrip("%").strip()
    text = text.replace(",", "")

    try:
        number = float(text)
    except ValueError:
        return None, ""

    return number, "percent" if percent else "ratio_or_raw"


def assess_metric(metric: str, value: float, unit_or_scale: str) -> tuple[str, str]:
    if not math.isfinite(value):
        return "anomaly", "value is not finite"

    if metric in BOUNDED_METRICS:
        if value < 0:
            return "anomaly", "bounded metric is negative"
        if unit_or_scale == "percent":
            if value > 100:
                return "anomaly", "percentage metric is greater than 100"
            return "ok", "percentage scale"
        if value <= 1:
            return "ok", "ratio scale"
        if value <= 100:
            return "warn", "bounded metric may be stored as 0-100 percent"
        return "anomaly", "bounded metric is greater than 100"

    if metric in NONNEGATIVE_METRICS and value < 0:
        return "anomaly", "nonnegative metric is negative"

    return "ok", ""


def short_context(value: Any, max_len: int = 180) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def add_record(
    records: list[MetricRecord],
    file_path: Path,
    root: Path,
    file_type: str,
    metric: str,
    value: float,
    unit_or_scale: str,
    location: str,
    context: str,
) -> None:
    status, note = assess_metric(metric, value, unit_or_scale)
    records.append(
        MetricRecord(
            file=relative_display(file_path, root),
            file_type=file_type,
            metric=metric,
            value=value,
            unit_or_scale=unit_or_scale,
            location=location,
            context=short_context(context),
            status=status,
            note=note,
        )
    )


def relative_display(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def iter_result_files(root: Path, include_hidden: bool) -> list[Path]:
    files: list[Path] = []
    for current_root, dirnames, filenames in os.walk(root):
        current_path = Path(current_root)
        kept_dirs = []
        for dirname in dirnames:
            if dirname in DEFAULT_IGNORED_DIRS:
                continue
            if not include_hidden and dirname.startswith("."):
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs

        for filename in filenames:
            if filename in DEFAULT_IGNORED_FILENAMES:
                continue
            if not include_hidden and filename.startswith("."):
                continue
            path = current_path / filename
            if path.suffix.lower() in SUPPORTED_SUFFIXES:
                files.append(path)
    return sorted(files)


def parse_json_file(path: Path, root: Path, records: list[MetricRecord]) -> None:
    data = json.loads(path.read_text(encoding="utf-8-sig"))

    def walk(value: Any, key_path: tuple[str, ...]) -> None:
        metric = metric_name_from_path(key_path)
        number, unit = to_float(value)
        if metric and number is not None:
            add_record(
                records,
                path,
                root,
                "json",
                metric,
                number,
                unit,
                ".".join(key_path),
                value,
            )

        if isinstance(value, dict):
            for child_key, child_value in value.items():
                walk(child_value, key_path + (str(child_key),))
        elif isinstance(value, list):
            for index, child_value in enumerate(value):
                walk(child_value, key_path + (f"[{index}]",))

    walk(data, ())


def detect_delimiter(path: Path) -> str:
    if path.suffix.lower() == ".tsv":
        return "\t"
    sample = path.read_text(encoding="utf-8-sig", errors="replace")[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
        return dialect.delimiter
    except csv.Error:
        return ","


def parse_table_file(path: Path, root: Path, records: list[MetricRecord]) -> None:
    delimiter = detect_delimiter(path)
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        if not reader.fieldnames:
            return

        fields = [field or "" for field in reader.fieldnames]
        normalized_fields = {field: normalize_key(field) for field in fields}
        metric_field = next(
            (field for field, normalized in normalized_fields.items() if normalized in {"metric", "metrics", "name"}),
            None,
        )
        value_field = next(
            (field for field, normalized in normalized_fields.items() if normalized in {"value", "score", "mean"}),
            None,
        )

        for row_index, row in enumerate(reader, start=2):
            if metric_field and value_field:
                metric = metric_name_from_path((row.get(metric_field, ""),))
                number, unit = to_float(row.get(value_field, ""))
                if metric and number is not None:
                    add_record(
                        records,
                        path,
                        root,
                        path.suffix.lower().lstrip("."),
                        metric,
                        number,
                        unit,
                        f"row {row_index}: {metric_field}/{value_field}",
                        row,
                    )

            for field in fields:
                metric = metric_name_from_path((field,))
                if not metric:
                    continue
                number, unit = to_float(row.get(field, ""))
                if number is None:
                    continue
                add_record(
                    records,
                    path,
                    root,
                    path.suffix.lower().lstrip("."),
                    metric,
                    number,
                    unit,
                    f"row {row_index}: {field}",
                    row,
                )


def build_text_regex() -> re.Pattern[str]:
    aliases = sorted(METRIC_ALIASES.keys(), key=len, reverse=True)
    alias_pattern = "|".join(re.escape(alias).replace("_", r"[\s_-]*") for alias in aliases)
    return re.compile(
        rf"\b(?P<metric>{alias_pattern}|macro\s+avg)\b"
        rf"\s*(?:[:=]|is|was|of)?\s*"
        rf"(?P<value>[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?%?)",
        re.IGNORECASE,
    )


TEXT_METRIC_RE = build_text_regex()


def parse_text_file(path: Path, root: Path, records: list[MetricRecord], max_bytes: int) -> None:
    raw = path.read_bytes()
    if len(raw) > max_bytes:
        raw = raw[:max_bytes]
    text = raw.decode("utf-8-sig", errors="replace")
    file_type = path.suffix.lower().lstrip(".")

    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in TEXT_METRIC_RE.finditer(line):
            metric = metric_name_from_path((match.group("metric"),))
            number, unit = to_float(match.group("value"))
            if metric and number is not None:
                add_record(
                    records,
                    path,
                    root,
                    file_type,
                    metric,
                    number,
                    unit,
                    f"line {line_number}",
                    line,
                )


def parse_file(path: Path, root: Path, records: list[MetricRecord], max_text_bytes: int) -> ParseIssue | None:
    before = len(records)
    suffix = path.suffix.lower()
    try:
        if suffix == ".json":
            parse_json_file(path, root, records)
        elif suffix in {".csv", ".tsv"}:
            parse_table_file(path, root, records)
        elif suffix in {".txt", ".log"}:
            parse_text_file(path, root, records, max_text_bytes)
    except Exception as exc:  # Keep scanner resilient across mixed output files.
        return ParseIssue(relative_display(path, root), suffix.lstrip("."), f"{type(exc).__name__}: {exc}")

    if len(records) == before:
        return ParseIssue(relative_display(path, root), suffix.lstrip("."), "no supported metric pattern found")
    return None


def write_csv(records: list[MetricRecord], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "file",
                "file_type",
                "metric",
                "value",
                "unit_or_scale",
                "location",
                "context",
                "status",
                "note",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(record.__dict__)


def metric_summary(records: list[MetricRecord]) -> list[tuple[str, int, float, float, float]]:
    values_by_metric: dict[str, list[float]] = defaultdict(list)
    for record in records:
        values_by_metric[record.metric].append(record.value)
    rows = []
    for metric, values in sorted(values_by_metric.items()):
        rows.append((metric, len(values), min(values), max(values), mean(values)))
    return rows


def markdown_table(headers: list[str], rows: Iterable[Iterable[Any]], limit: int | None = None) -> str:
    row_list = list(rows)
    if limit is not None:
        row_list = row_list[:limit]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in row_list:
        escaped = [str(cell).replace("\n", " ").replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(escaped) + " |")
    if not row_list:
        lines.append("| none |" + " |".join([""] * (len(headers) - 1)) + " |")
    return "\n".join(lines)


def write_summary(
    records: list[MetricRecord],
    issues: list[ParseIssue],
    scanned_files: list[Path],
    root: Path,
    out_dir: Path,
    out_path: Path,
) -> None:
    anomalies = [record for record in records if record.status in {"warn", "anomaly"}]
    files_with_metrics = sorted({record.file for record in records})
    parsed_count = len(files_with_metrics)

    lines = [
        "# Result Scan Summary",
        "",
        f"- Scan time: {dt.datetime.now().isoformat(timespec='seconds')}",
        f"- Scan root: `{root}`",
        f"- Output directory: `{out_dir}`",
        f"- Result files discovered: {len(scanned_files)}",
        f"- Files with extracted metrics: {parsed_count}",
        f"- Extracted metric rows: {len(records)}",
        f"- Files without parsed metrics or with parse issues: {len(issues)}",
        "",
        "## Metric Summary",
        "",
        markdown_table(
            ["Metric", "Count", "Min", "Max", "Mean"],
            ((m, c, f"{lo:.6g}", f"{hi:.6g}", f"{avg:.6g}") for m, c, lo, hi, avg in metric_summary(records)),
        ),
        "",
        "## Extracted Metrics",
        "",
        markdown_table(
            ["File", "Metric", "Value", "Location", "Status", "Note"],
            (
                (r.file, r.metric, f"{r.value:.8g}", r.location, r.status, r.note)
                for r in records
            ),
            limit=120,
        ),
        "",
        "## Suspected Anomalies",
        "",
        markdown_table(
            ["File", "Metric", "Value", "Location", "Status", "Note"],
            (
                (r.file, r.metric, f"{r.value:.8g}", r.location, r.status, r.note)
                for r in anomalies
            ),
            limit=120,
        ),
        "",
        "## Unparsed Or Metric-Free Files",
        "",
        markdown_table(
            ["File", "Type", "Issue"],
            ((issue.file, issue.file_type, issue.issue) for issue in issues),
            limit=120,
        ),
        "",
        "## Next Steps",
        "",
        "- Review `result-scan-table.csv` before copying values into the thesis.",
        "- Add reviewed metrics to `experiment-registry.md` with experiment IDs and protocol notes.",
        "- Promote only reviewed results into `claim-evidence-map.md`.",
        "- Use `$research-results-analysis` to classify supported, weak, unsupported, and missing claims.",
        "- Treat warnings and anomalies as audit items until the scale, split, and metric computation are confirmed.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan experiment result files for common metrics.")
    parser.add_argument("--root", default=".", help="Root directory to scan recursively.")
    parser.add_argument("--out-dir", default="docs/thesis", help="Output directory for summary and CSV files.")
    parser.add_argument(
        "--max-text-bytes",
        type=int,
        default=2_000_000,
        help="Maximum bytes to inspect per TXT/LOG file.",
    )
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden files and directories.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    scanned_files = iter_result_files(root, include_hidden=args.include_hidden)
    records: list[MetricRecord] = []
    issues: list[ParseIssue] = []

    for path in scanned_files:
        issue = parse_file(path, root, records, max_text_bytes=args.max_text_bytes)
        if issue:
            issues.append(issue)

    csv_path = out_dir / "result-scan-table.csv"
    summary_path = out_dir / "result-scan-summary.md"
    write_csv(records, csv_path)
    write_summary(records, issues, scanned_files, root, out_dir, summary_path)

    print(f"Scanned files: {len(scanned_files)}")
    print(f"Extracted metric rows: {len(records)}")
    print(f"Wrote: {summary_path}")
    print(f"Wrote: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
