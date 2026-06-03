"""Append a lightweight weekly research review and update its summary."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

from edit_workflow_record import append_row_to_table, log_edit, update_status

THESIS_DIR = Path("docs/thesis")
WEEKLY_REVIEW = THESIS_DIR / "weekly-review.md"


def current_week() -> str:
    year, week, _ = dt.date.today().isocalendar()
    return f"{year}-W{week:02d}"


def cell(value: Any, fallback: str = "TBD") -> str:
    text = str(value if value is not None else "").strip()
    return text if text else fallback


def ensure_weekly_file(root: Path) -> Path:
    path = root / WEEKLY_REVIEW
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Weekly Review\n\n"
        "Use this file once per week to keep the research workflow from spreading across too many files.\n\n"
        "## Weekly Reviews\n\n"
        "| Week | Focus | Completed | Evidence Stronger | Evidence Weaker / Risk | Best Experiment | Next 1-3 Actions | Files To Ignore Next Week | Notes |\n"
        "|---|---|---|---|---|---|---|---|---|\n\n"
        "## Current Weekly Summary\n\n"
        "| Field | Value |\n"
        "|---|---|\n"
        "| Current week | TBD |\n"
        "| Main focus | TBD |\n"
        "| Current best experiment | TBD |\n"
        "| Strongest evidence | TBD |\n"
        "| Biggest risk | TBD |\n"
        "| Next action 1 | TBD |\n"
        "| Next action 2 | TBD |\n"
        "| Next action 3 | TBD |\n",
        encoding="utf-8",
    )
    return path


def replace_summary(text: str, fields: dict[str, Any]) -> str:
    summary = {
        "Current week": cell(fields.get("week"), current_week()),
        "Main focus": cell(fields.get("focus")),
        "Current best experiment": cell(fields.get("best_experiment")),
        "Strongest evidence": cell(fields.get("evidence_stronger")),
        "Biggest risk": cell(fields.get("evidence_risk")),
        "Next action 1": cell(fields.get("next_action_1")),
        "Next action 2": cell(fields.get("next_action_2")),
        "Next action 3": cell(fields.get("next_action_3")),
    }
    block = "## Current Weekly Summary\n\n| Field | Value |\n|---|---|\n"
    block += "".join(f"| {key} | {value} |\n" for key, value in summary.items())
    marker = "## Current Weekly Summary"
    if marker not in text:
        return text.rstrip() + "\n\n" + block
    before, _ = text.split(marker, 1)
    return before.rstrip() + "\n\n" + block


def update_weekly(root: Path, fields: dict[str, Any]) -> dict[str, Any]:
    path = ensure_weekly_file(root)
    row = [
        fields.get("week", current_week()),
        fields.get("focus"),
        fields.get("completed"),
        fields.get("evidence_stronger"),
        fields.get("evidence_risk"),
        fields.get("best_experiment"),
        fields.get("next_actions"),
        fields.get("files_to_ignore"),
        fields.get("notes"),
    ]
    append_row_to_table(root, path, "Week", row)
    text = replace_summary(path.read_text(encoding="utf-8"), fields)
    path.write_text(text, encoding="utf-8")
    log_edit(root, "update weekly review", path, cell(fields.get("week"), current_week()), cell(fields.get("next_actions"), "weekly review update"))
    if fields.get("next_actions"):
        update_status(root, {"next_action": fields.get("next_actions")})
    return {"ok": True, "target": path.as_posix(), "week": cell(fields.get("week"), current_week())}


def main() -> None:
    parser = argparse.ArgumentParser(description="Append a weekly research review.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--week")
    parser.add_argument("--focus")
    parser.add_argument("--completed")
    parser.add_argument("--evidence-stronger")
    parser.add_argument("--evidence-risk")
    parser.add_argument("--best-experiment")
    parser.add_argument("--next-actions")
    parser.add_argument("--next-action-1")
    parser.add_argument("--next-action-2")
    parser.add_argument("--next-action-3")
    parser.add_argument("--files-to-ignore")
    parser.add_argument("--notes")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    fields = {
        "week": args.week,
        "focus": args.focus,
        "completed": args.completed,
        "evidence_stronger": args.evidence_stronger,
        "evidence_risk": args.evidence_risk,
        "best_experiment": args.best_experiment,
        "next_actions": args.next_actions,
        "next_action_1": args.next_action_1,
        "next_action_2": args.next_action_2,
        "next_action_3": args.next_action_3,
        "files_to_ignore": args.files_to_ignore,
        "notes": args.notes,
    }
    fields = {key: value for key, value in fields.items() if value is not None}
    result = update_weekly(Path(args.root).resolve(), fields)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"updated weekly review: {result['target']}")


if __name__ == "__main__":
    main()
