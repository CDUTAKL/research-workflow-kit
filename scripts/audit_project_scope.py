"""Audit title-first thesis scope control gates."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PENDING_RE = re.compile(r"\|\s*(pending|draft|TBD|missing)\s*\|", re.IGNORECASE)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def audit(thesis_dir: Path) -> tuple[list[str], list[str], list[str], dict[str, str]]:
    p0: list[str] = []
    p1: list[str] = []
    info: list[str] = []
    path = thesis_dir / "project-scope-control.md"
    text = read_text(path)
    details = {"path": path.as_posix(), "status": "missing"}

    if not text:
        p1.append("missing project scope control file")
        return p0, p1, info, details

    required_sections = {
        "Title Review Gates": "title review gates are missing",
        "Causal Availability Contract": "causal availability contract is missing",
        "Graph / Structure Definition Gate": "graph or structure definition gate is missing",
        "Downgrade / Rename Policy": "downgrade or rename policy is missing",
        "Promotion Rule": "title phrase promotion rule is missing",
    }
    for section, message in required_sections.items():
        if section not in text:
            p1.append(message)

    if PENDING_RE.search(text):
        p1.append("project scope control still has pending title, causal, node, or downgrade decisions")
        details["status"] = "pending"
    else:
        details["status"] = "ready"

    if "Final thesis title" in text and re.search(
        r"\| Final thesis title \|.*\|\s*locked\s*\|", text, re.IGNORECASE
    ) and not re.search(r"\b(?:CLM|EXP|DATA|FIG|CIT)-[A-Za-z0-9.-]+\b", text):
        p0.append("final thesis title is locked but no structured evidence IDs are linked in project scope control")

    info.append(f"project scope control: {details['status']}")
    return p0, p1, info, details


def render(p0: list[str], p1: list[str], info: list[str]) -> str:
    lines = ["# Project Scope Audit", ""]
    lines.extend(["## P0", ""])
    lines.extend([f"- {item}" for item in p0] or ["- none"])
    lines.extend(["", "## P1", ""])
    lines.extend([f"- {item}" for item in p1] or ["- none"])
    lines.extend(["", "## Info", ""])
    lines.extend([f"- {item}" for item in info] or ["- none"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".", help="Project root containing docs/thesis.")
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args()
    thesis_dir = Path(args.project) / "docs" / "thesis"
    p0, p1, info, _details = audit(thesis_dir)
    print(render(p0, p1, info))
    if p0:
        return 0 if args.warn_only else 2
    if p1:
        return 0 if args.warn_only else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
