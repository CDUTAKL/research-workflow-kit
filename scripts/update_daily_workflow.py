"""Update the lightweight daily workflow entry and dashboard status."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

from edit_workflow_record import append_row_to_table, log_edit, update_status

THESIS_DIR = Path("docs/thesis")
DAILY_ENTRY = THESIS_DIR / "daily-workflow-entry.md"


def today() -> str:
    return dt.date.today().isoformat()


def cell(value: Any, fallback: str = "TBD") -> str:
    text = str(value if value is not None else "").strip()
    return text if text else fallback


def ensure_daily_file(root: Path) -> Path:
    path = root / DAILY_ENTRY
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Daily Workflow Entry\n\n"
        "## Purpose\n\n"
        "Use this file as the lightweight daily entry point for the research workflow.\n\n"
        "## Daily Entries\n\n"
        "| Date | Stage | Focus | Goal | Blocker | Next Action | Done Note | Tomorrow |\n"
        "|---|---|---|---|---|---|---|---|\n",
        encoding="utf-8",
    )
    return path


def update_daily(root: Path, fields: dict[str, Any]) -> dict[str, Any]:
    path = ensure_daily_file(root)
    row = [
        fields.get("date", today()),
        fields.get("stage"),
        fields.get("focus"),
        fields.get("goal"),
        fields.get("blocker"),
        fields.get("next_action"),
        fields.get("done_note"),
        fields.get("tomorrow"),
    ]
    append_row_to_table(root, path, "Date", row)
    log_edit(root, "update daily workflow", path, "daily", cell(fields.get("next_action"), "daily workflow update"))

    status_fields = {
        "current_stage": fields.get("stage"),
        "active_focus": fields.get("focus"),
        "main_blocker": fields.get("blocker"),
        "next_action": fields.get("next_action"),
        "audit_tier": fields.get("audit_tier"),
    }
    status_fields = {key: value for key, value in status_fields.items() if value is not None}
    if status_fields:
        update_status(root, status_fields)
    return {"ok": True, "target": path.as_posix(), "date": cell(fields.get("date"), today())}


def main() -> None:
    parser = argparse.ArgumentParser(description="Update daily workflow entry and dashboard status.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--date")
    parser.add_argument("--stage")
    parser.add_argument("--focus")
    parser.add_argument("--goal")
    parser.add_argument("--blocker")
    parser.add_argument("--next-action")
    parser.add_argument("--done-note")
    parser.add_argument("--tomorrow")
    parser.add_argument("--audit-tier")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    fields = {
        "date": args.date,
        "stage": args.stage,
        "focus": args.focus,
        "goal": args.goal,
        "blocker": args.blocker,
        "next_action": args.next_action,
        "done_note": args.done_note,
        "tomorrow": args.tomorrow,
        "audit_tier": args.audit_tier,
    }
    fields = {key: value for key, value in fields.items() if value is not None}
    result = update_daily(Path(args.root).resolve(), fields)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"updated daily workflow entry: {result['target']}")


if __name__ == "__main__":
    main()
