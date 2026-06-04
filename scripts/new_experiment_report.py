"""Generate a lightweight experiment report with optional baseline comparison."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

THESIS = Path("docs/thesis")
REGISTRY = THESIS / "experiment-registry.md"
AUTORESEARCH = THESIS / "autoresearch-results.tsv"
REPORTS = THESIS / "experiment-reports"


def markdown_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append(cells)
    return rows


def registry() -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    if not REGISTRY.exists():
        return records
    for cells in markdown_rows(REGISTRY.read_text(encoding="utf-8")):
        if cells and re.fullmatch(r"EXP-(?:AUTO-)?[A-Za-z0-9.-]+", cells[0]):
            records[cells[0]] = {
                "claim": cells[1] if len(cells) > 1 else "",
                "config": cells[2] if len(cells) > 2 else "",
                "dataset": cells[3] if len(cells) > 3 else "",
                "command": cells[4] if len(cells) > 4 else "",
                "output": cells[5] if len(cells) > 5 else "",
                "metrics": cells[6] if len(cells) > 6 else "",
                "status": cells[7] if len(cells) > 7 else "",
                "notes": cells[9] if len(cells) > 9 else "",
                "storage_backend": cells[10] if len(cells) > 10 else "",
                "remote_artifact_uri": cells[11] if len(cells) > 11 else "",
                "remote_status": cells[12] if len(cells) > 12 else "",
                "artifact_hash": cells[13] if len(cells) > 13 else "",
            }
    return records


def load_metrics(exp_id: str, output: str) -> dict[str, float | str]:
    candidates = []
    if output and "TBD" not in output:
        first_output = output.split(";")[0].strip("` ")
        candidates.append(Path(first_output) / "metrics.json")
    candidates.append(Path("outputs") / exp_id / "metrics.json")
    for path in candidates:
        if path.exists():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {"error": f"invalid json: {path}"}
            return {str(k): v for k, v in raw.items() if isinstance(v, (int, float, str))}
    return {}


def primary_numeric(metrics: dict[str, float | str]) -> tuple[str, float] | None:
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            return key, float(value)
    return None


def autoresearch_row(exp_id: str) -> str:
    if not AUTORESEARCH.exists():
        return "not_found"
    for line in AUTORESEARCH.read_text(encoding="utf-8").splitlines():
        if exp_id in line:
            return line
    return "not_found"


def write_report(exp_id: str, baseline_id: str | None) -> Path:
    records = registry()
    exp = records.get(exp_id, {})
    baseline = records.get(baseline_id or "", {}) if baseline_id else {}
    exp_metrics = load_metrics(exp_id, exp.get("output", ""))
    base_metrics = load_metrics(baseline_id or "", baseline.get("output", "")) if baseline_id else {}
    exp_primary = primary_numeric(exp_metrics)
    base_primary = primary_numeric(base_metrics)
    delta = "TBD"
    if exp_primary and base_primary and exp_primary[0] == base_primary[0]:
        delta = f"{exp_primary[1] - base_primary[1]:.6g}"
    output_dir = exp.get("output", "").split(";")[0].strip("` ")
    env_snapshot = Path(output_dir) / "environment.txt" if output_dir else Path("outputs") / exp_id / "environment.txt"
    REPORTS.mkdir(parents=True, exist_ok=True)
    report = REPORTS / f"{exp_id}.md"
    report.write_text(
        f"""# Experiment Report: {exp_id}

| Field | Value |
|---|---|
| Experiment ID | {exp_id} |
| Baseline | {baseline_id or 'none'} |
| Claim / Question | {exp.get('claim', 'TBD')} |
| Config | {exp.get('config', 'TBD')} |
| Dataset / Split | {exp.get('dataset', 'TBD')} |
| Command | {exp.get('command', 'TBD')} |
| Output | {exp.get('output', 'TBD')} |
| Storage Backend | {exp.get('storage_backend') or 'TBD'} |
| Remote Artifact URI | {exp.get('remote_artifact_uri') or 'TBD'} |
| Remote Status | {exp.get('remote_status') or 'TBD'} |
| Artifact Hash / Manifest | {exp.get('artifact_hash') or 'TBD'} |
| Registry Status | {exp.get('status', 'TBD')} |
| Environment Snapshot | {'present' if env_snapshot.exists() else 'missing'} |

## Metric Comparison

| Metric | Baseline | New | Delta |
|---|---:|---:|---:|
| {exp_primary[0] if exp_primary else 'primary_metric/TBD'} | {base_primary[1] if base_primary else 'TBD'} | {exp_primary[1] if exp_primary else 'TBD'} | {delta} |

## Verify / Guard

| Gate | Evidence | Status |
|---|---|---|
| verify | {autoresearch_row(exp_id)} | pending |
| guard | config, split, leakage, stability, environment snapshot | pending |
| storage | local index plus remote artifact URI/hash when full outputs live off-Mac | {'pending' if not exp.get('remote_artifact_uri') and 'remote_desktop_4060' in (exp.get('storage_backend', '') + exp.get('notes', '')) else 'recorded_or_not_applicable'} |

## Claim Promotion Decision

| Decision | Notes |
|---|---|
| pending | Promote only after verify and guard are reviewed. |
""",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a lightweight EXP-* report.")
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--baseline")
    args = parser.parse_args()
    path = write_report(args.experiment_id, args.baseline)
    print(f"wrote experiment report: {path}")


if __name__ == "__main__":
    main()
