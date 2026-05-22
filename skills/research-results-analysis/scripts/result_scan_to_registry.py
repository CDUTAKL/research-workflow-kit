#!/usr/bin/env python3
"""Convert result-scan-table.csv into candidate experiment-registry entries.

The output is intentionally conservative. It groups metrics by result directory,
selects candidate best values per metric, and writes an auto-generated block to
`experiment-registry.md`. Users must review protocol, split, seed, and
comparability before using any row as evidence.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean


AUTO_START = "<!-- AUTO-GENERATED: result_scan_to_registry START -->"
AUTO_END = "<!-- AUTO-GENERATED: result_scan_to_registry END -->"
LOWER_IS_BETTER = {"loss", "rmse", "mae"}
GENERIC_RESULT_DIRS = {"log", "logs", "archive", "artifact", "artifacts", "result", "results", "output", "outputs"}


@dataclass
class MetricValue:
    metric: str
    value: float
    file: str
    location: str
    status: str
    note: str


@dataclass
class ExperimentGroup:
    run_dir: str
    files: set[str] = field(default_factory=set)
    values: list[MetricValue] = field(default_factory=list)


def slug_parts(path_text: str) -> list[str]:
    normalized = path_text.replace("\\", "/")
    return [part for part in normalized.split("/") if part]


def infer_run_dir(file_path: str, depth: int) -> str:
    parts = slug_parts(file_path)
    if len(parts) <= 1:
        return "."
    parent_parts = parts[:-1]
    file_stem = Path(parts[-1]).stem
    if parent_parts and parent_parts[-1].lower() in GENERIC_RESULT_DIRS:
        parent_with_file = parent_parts + [file_stem]
        if len(parent_with_file) <= depth + 1:
            return "/".join(parent_with_file)
        return "/".join(parent_with_file[-(depth + 1) :])
    if len(parent_parts) <= depth:
        return "/".join(parent_parts)
    return "/".join(parent_parts[-depth:])


def parse_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def read_scan_table(path: Path, group_depth: int) -> dict[str, ExperimentGroup]:
    groups: dict[str, ExperimentGroup] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"file", "metric", "value", "location", "status", "note"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"scan table missing columns: {', '.join(sorted(missing))}")

        for row in reader:
            value = parse_float(row.get("value", ""))
            if value is None:
                continue
            file_path = row["file"]
            run_dir = infer_run_dir(file_path, group_depth)
            group = groups.setdefault(run_dir, ExperimentGroup(run_dir=run_dir))
            group.files.add(file_path)
            group.values.append(
                MetricValue(
                    metric=row["metric"],
                    value=value,
                    file=file_path,
                    location=row.get("location", ""),
                    status=row.get("status", ""),
                    note=row.get("note", ""),
                )
            )
    return groups


def best_value(values: list[MetricValue]) -> MetricValue:
    metric = values[0].metric
    if metric in LOWER_IS_BETTER:
        return min(values, key=lambda item: item.value)
    return max(values, key=lambda item: item.value)


def metric_summary(group: ExperimentGroup, max_metrics: int) -> str:
    by_metric: dict[str, list[MetricValue]] = defaultdict(list)
    for value in group.values:
        by_metric[value.metric].append(value)

    parts = []
    for metric in sorted(by_metric)[:max_metrics]:
        values = by_metric[metric]
        best = best_value(values)
        avg = mean(item.value for item in values)
        direction = "min" if metric in LOWER_IS_BETTER else "max"
        parts.append(f"{metric} {direction}={best.value:.6g}, mean={avg:.6g}, n={len(values)}")
    if len(by_metric) > max_metrics:
        parts.append(f"+{len(by_metric) - max_metrics} more metrics")
    return "; ".join(parts)


def infer_status(group: ExperimentGroup) -> str:
    if any(value.status == "anomaly" for value in group.values):
        return "candidate_review"
    if any(value.status == "warn" for value in group.values):
        return "candidate_review"
    return "candidate"


def safe_cell(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    return text.replace("|", "\\|")


def make_registry_block(groups: dict[str, ExperimentGroup], source: Path, max_rows: int, max_metrics: int) -> str:
    now = dt.datetime.now().isoformat(timespec="seconds")
    ranked = sorted(groups.values(), key=lambda group: (-len(group.values), group.run_dir))
    limited = ranked[:max_rows]

    lines = [
        AUTO_START,
        "",
        "## Auto-Generated Candidate Registry",
        "",
        f"- Generated at: {now}",
        f"- Source scan table: `{source}`",
        f"- Grouping rule: parent result directory",
        f"- Candidate groups found: {len(groups)}",
        f"- Rows shown: {len(limited)}",
        "",
        "Review rules:",
        "",
        "- These rows are candidates only; they are not thesis evidence until reviewed.",
        "- Confirm dataset split, seed, config, metric code, and comparable baseline before citing.",
        "- Promote reviewed rows into the manual `Experiment Table` above or keep this block as traceability.",
        "- Use `claim-evidence-map.md` only after claim support is audited.",
        "",
        "| Experiment ID | Research Question / Claim | Method / Config | Dataset / Split | Command / Notebook | Output Path | Key Metrics | Status | Date | Notes |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]

    for index, group in enumerate(limited, start=1):
        experiment_id = f"EXP-AUTO-{index:03d}"
        status = infer_status(group)
        notes = f"{len(group.files)} files, {len(group.values)} metric rows; review before use"
        lines.append(
            "| "
            + " | ".join(
                [
                    experiment_id,
                    "TBD",
                    "TBD",
                    "TBD",
                    "TBD",
                    f"`{safe_cell(group.run_dir)}`",
                    safe_cell(metric_summary(group, max_metrics)),
                    status,
                    "TBD",
                    safe_cell(notes),
                ]
            )
            + " |"
        )

    lines.extend(["", AUTO_END, ""])
    return "\n".join(lines)


def replace_auto_block(original: str, block: str) -> str:
    if AUTO_START in original and AUTO_END in original:
        pattern = re.compile(re.escape(AUTO_START) + r".*?" + re.escape(AUTO_END), re.DOTALL)
        return pattern.sub(block.strip(), original).rstrip() + "\n"
    return original.rstrip() + "\n\n" + block


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create candidate experiment registry rows from result scan output.")
    parser.add_argument("--scan-table", default="docs/thesis/result-scan-table.csv", help="Path to result-scan-table.csv.")
    parser.add_argument("--registry", default="docs/thesis/experiment-registry.md", help="Experiment registry Markdown file to update.")
    parser.add_argument("--group-depth", type=int, default=2, help="Number of parent path parts to use as a run group.")
    parser.add_argument("--max-rows", type=int, default=80, help="Maximum candidate registry rows to write.")
    parser.add_argument("--max-metrics", type=int, default=8, help="Maximum metric summaries per row.")
    parser.add_argument("--dry-run", action="store_true", help="Print generated block without modifying the registry.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scan_table = Path(args.scan_table).resolve()
    registry = Path(args.registry).resolve()

    if not scan_table.exists():
        raise FileNotFoundError(f"scan table not found: {scan_table}")
    if not registry.exists():
        raise FileNotFoundError(f"registry file not found: {registry}")

    groups = read_scan_table(scan_table, group_depth=args.group_depth)
    block = make_registry_block(groups, scan_table, max_rows=args.max_rows, max_metrics=args.max_metrics)

    if args.dry_run:
        print(block)
        return 0

    original = registry.read_text(encoding="utf-8")
    updated = replace_auto_block(original, block)
    registry.write_text(updated, encoding="utf-8")

    print(f"Updated: {registry}")
    print(f"Candidate groups: {len(groups)}")
    print(f"Rows written: {min(len(groups), args.max_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
