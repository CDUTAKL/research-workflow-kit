"""Create a section-level deep research task packet."""
from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path

TASKS = Path("docs/thesis/deep-research-tasks.md")
PACKETS = Path("docs/thesis/section-research-packets")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def next_task_id(text: str) -> str:
    ids = [int(match) for match in re.findall(r"\bDRT-(\d+)\b", text)]
    return f"DRT-{(max(ids) + 1) if ids else 1:03d}"


def append_task(section_id: str, topic: str) -> tuple[str, Path]:
    TASKS.parent.mkdir(parents=True, exist_ok=True)
    if not TASKS.exists():
        TASKS.write_text(
            "# Deep Research Tasks\n\n| Task ID | Section ID | Topic | Search Queries | Candidate Papers | Must-Read Papers | Citation Gap | Scite/Zotero Status | Packet Path | Status | Next Action |\n|---|---|---|---|---|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )
    text = read_text(TASKS)
    task_id = next_task_id(text)
    packet = PACKETS / f"{section_id}.md"
    row = f"| {task_id} | {section_id} | {topic} | TBD | TBD | TBD | missing | not_checked | `{packet}` | planned | define search queries |\n"
    TASKS.write_text(text.rstrip() + "\n" + row, encoding="utf-8")
    return task_id, packet


def write_packet(packet: Path, section_id: str, topic: str, overwrite: bool) -> None:
    packet.parent.mkdir(parents=True, exist_ok=True)
    if packet.exists() and not overwrite:
        return
    today = dt.date.today().isoformat()
    packet.write_text(
        f"""# Deep Research Packet: {section_id}

| Field | Value |
|---|---|
| Section ID | {section_id} |
| Topic | {topic} |
| Created | {today} |
| Status | planned |

## Section Question

TBD

## Keyword Set

| Type | Terms |
|---|---|
| core concepts | TBD |
| methods | TBD |
| datasets / metrics | TBD |
| Chinese terms | TBD |
| English terms | TBD |

## Search Queries

| Query ID | Query | Source | Status |
|---|---|---|---|
| Q-001 | TBD | Semantic Scholar / Web / Zotero / Scite | planned |

## Candidate Papers

| Paper ID | Title | DOI / arXiv / S2 | Role | Metadata Status | Zotero Status | Scite / Reader Status | Decision |
|---|---|---|---|---|---|---|---|
| P-001 | TBD | TBD | foundational/recent/competitor/dataset/metric/TBD | candidate | not_added | not_checked | screen |

## Citation Gaps

| Segment ID | Gap | Needed Evidence | Candidate Paper | Status |
|---|---|---|---|---|
| SEG-001/TBD | TBD | support/background/contrast/TBD | TBD | open |

## Final Citation Decisions

| Citation | Supports | Use In Section? | Notes |
|---|---|---|---|
| TBD | TBD | pending |  |
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a SEC-* deep research task packet.")
    parser.add_argument("--section-id", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"SEC-[A-Za-z0-9.-]+", args.section_id):
        raise SystemExit("section id must look like SEC-INTRO-001")
    task_id, packet = append_task(args.section_id, args.topic)
    write_packet(packet, args.section_id, args.topic, args.overwrite)
    print(f"appended deep research task {task_id}: {packet}")


if __name__ == "__main__":
    main()
