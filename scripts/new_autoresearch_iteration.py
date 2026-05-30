"""Append or update a human-supervised autoresearch iteration record."""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

FIELDS = [
    "iteration",
    "date",
    "experiment_id",
    "branch",
    "commit",
    "target",
    "change_summary",
    "primary_metric",
    "baseline_value",
    "new_value",
    "delta",
    "verify_status",
    "guard_status",
    "decision",
    "notes",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return [dict(row) for row in reader if row]


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in FIELDS})


def next_iteration(rows: list[dict[str, str]]) -> str:
    numbers: list[int] = []
    for row in rows:
        try:
            numbers.append(int(row.get("iteration", "0")))
        except ValueError:
            continue
    return str(max(numbers, default=0) + 1)


def compute_delta(baseline: str, new_value: str) -> str:
    try:
        return f"{float(new_value) - float(baseline):.6g}"
    except ValueError:
        return ""


def update_state(path: Path, args: argparse.Namespace, iteration: str) -> None:
    default_state = {
        "current_target_claim": args.target_claim or "TBD",
        "current_best_run": args.experiment_id,
        "recent_attempts": [],
        "next_candidate_experiments": [],
        "failure_reasons": [],
        "needs_human_confirmation": args.needs_human_confirmation,
        "last_updated": str(date.today()),
    }
    if path.exists():
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            state = default_state
    else:
        state = default_state
    state["current_target_claim"] = args.target_claim or state.get("current_target_claim", "TBD")
    if args.decision in {"accept", "promote", "keep"}:
        state["current_best_run"] = args.experiment_id
    state["last_updated"] = str(date.today())
    state["needs_human_confirmation"] = args.needs_human_confirmation
    attempts = state.setdefault("recent_attempts", [])
    attempts.append(
        {
            "iteration": iteration,
            "experiment_id": args.experiment_id,
            "decision": args.decision,
            "verify_status": args.verify_status,
            "guard_status": args.guard_status,
        }
    )
    state["recent_attempts"] = attempts[-10:]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Record an autoresearch iteration.")
    parser.add_argument("--results", default="docs/thesis/autoresearch-results.tsv")
    parser.add_argument("--state", default="docs/thesis/autoresearch-state.json")
    parser.add_argument("--iteration")
    parser.add_argument("--target-claim")
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--branch", default="TBD")
    parser.add_argument("--commit", default="TBD")
    parser.add_argument("--target", default="local_mac/remote_desktop_4060")
    parser.add_argument("--change-summary", required=True)
    parser.add_argument("--primary-metric", default="TBD")
    parser.add_argument("--baseline-value", default="")
    parser.add_argument("--new-value", default="")
    parser.add_argument("--verify-status", default="pending")
    parser.add_argument("--guard-status", default="pending")
    parser.add_argument("--decision", default="pending")
    parser.add_argument("--notes", default="")
    parser.add_argument("--needs-human-confirmation", action="store_true", default=True)
    args = parser.parse_args()

    results_path = Path(args.results)
    state_path = Path(args.state)
    rows = read_rows(results_path)
    iteration = args.iteration or next_iteration(rows)
    delta = compute_delta(args.baseline_value, args.new_value)
    new_row = {
        "iteration": iteration,
        "date": str(date.today()),
        "experiment_id": args.experiment_id,
        "branch": args.branch,
        "commit": args.commit,
        "target": args.target,
        "change_summary": args.change_summary,
        "primary_metric": args.primary_metric,
        "baseline_value": args.baseline_value,
        "new_value": args.new_value,
        "delta": delta,
        "verify_status": args.verify_status,
        "guard_status": args.guard_status,
        "decision": args.decision,
        "notes": args.notes,
    }

    replaced = False
    for idx, row in enumerate(rows):
        if row.get("iteration") == iteration:
            rows[idx] = new_row
            replaced = True
            break
    if not replaced:
        rows.append(new_row)
    write_rows(results_path, rows)
    update_state(state_path, args, iteration)
    action = "updated" if replaced else "appended"
    print(f"{action} iteration {iteration} in {results_path}")
    print(f"updated state: {state_path}")


if __name__ == "__main__":
    main()

