"""Audit Zotero-backed literature coverage for thesis sections."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

THESIS_DIR = Path("docs/thesis")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


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


def weak(value: str) -> bool:
    return value.strip().lower() in {"", "tbd", "missing", "pending", "none", "not_added", "unchecked", "not_checked"}


def audit(thesis_dir: Path) -> tuple[list[str], list[str], dict[str, object]]:
    p0: list[str] = []
    p1: list[str] = []
    sections: dict[str, dict[str, object]] = {}

    for cells in markdown_rows(read_text(thesis_dir / "section-citation-map.md")):
        if len(cells) >= 6 and re.fullmatch(r"SEC-[A-Za-z0-9.-]+", cells[0]):
            sections.setdefault(
                cells[0],
                {
                    "segments": 0,
                    "zoteroVerified": 0,
                    "strongVerified": 0,
                    "candidates": 0,
                    "coverageStatus": cells[4],
                    "collectionCoverage": "missing",
                },
            )
        elif len(cells) >= 11 and re.fullmatch(r"SEG-[A-Za-z0-9.-]+", cells[0]):
            section_id = cells[1]
            item = sections.setdefault(
                section_id,
                {
                    "segments": 0,
                    "zoteroVerified": 0,
                    "strongVerified": 0,
                    "candidates": 0,
                    "coverageStatus": "missing",
                    "collectionCoverage": "missing",
                },
            )
            item["segments"] = int(item["segments"]) + 1
            if not weak(cells[3]):
                item["candidates"] = int(item["candidates"]) + 1
            if cells[7].strip().lower() in {"in_zotero", "final"}:
                item["zoteroVerified"] = int(item["zoteroVerified"]) + 1
            if cells[5].strip().lower() == "strong" and cells[7].strip().lower() in {"in_zotero", "final"}:
                item["strongVerified"] = int(item["strongVerified"]) + 1

    for cells in markdown_rows(read_text(thesis_dir / "citation-provenance.md")):
        if len(cells) >= 15 and re.fullmatch(r"CIT-[A-Za-z0-9.-]+", cells[0]):
            section_id = cells[1]
            item = sections.setdefault(
                section_id,
                {
                    "segments": 0,
                    "zoteroVerified": 0,
                    "strongVerified": 0,
                    "candidates": 0,
                    "coverageStatus": "missing",
                    "collectionCoverage": "missing",
                },
            )
            if cells[9].strip().lower() in {"in_zotero", "final"}:
                item["zoteroVerified"] = int(item["zoteroVerified"]) + 1
            if cells[8].strip().lower() == "supports" and cells[9].strip().lower() in {"in_zotero", "final"}:
                item["strongVerified"] = int(item["strongVerified"]) + 1

    for cells in markdown_rows(read_text(thesis_dir / "zotero-collection-coverage.md")):
        if len(cells) >= 8 and re.fullmatch(r"SEC-[A-Za-z0-9.-]+", cells[0]):
            item = sections.setdefault(
                cells[0],
                {
                    "segments": 0,
                    "zoteroVerified": 0,
                    "strongVerified": 0,
                    "candidates": 0,
                    "coverageStatus": "missing",
                    "collectionCoverage": "missing",
                },
            )
            item["collectionCoverage"] = cells[7]

    if not (thesis_dir / "zotero-literature-hub.md").exists():
        p1.append("missing Zotero literature hub snapshot")
    if not sections:
        p1.append("no SEC-* rows found for Zotero coverage audit")

    for section_id, item in sections.items():
        if int(item["zoteroVerified"]) == 0:
            p1.append(f"{section_id} has no Zotero-backed citation")
        if int(item["strongVerified"]) == 0:
            p1.append(f"{section_id} has no strong Zotero-backed citation")
        if weak(str(item["collectionCoverage"])):
            p1.append(f"{section_id} has missing Zotero collection coverage")

    return p0, p1, {"sections": sections, "sectionCount": len(sections)}


def render(p0: list[str], p1: list[str], details: dict[str, object]) -> str:
    lines = [
        "# Zotero Coverage Audit",
        "",
        f"- sections: {details.get('sectionCount', 0)}",
        f"- P0: {len(p0)}",
        f"- P1: {len(p1)}",
        "",
        "## P0",
    ]
    lines.extend(f"- {item}" for item in p0) if p0 else lines.append("- none")
    lines.append("")
    lines.append("## P1")
    lines.extend(f"- {item}" for item in p1) if p1 else lines.append("- none")
    lines.append("")
    lines.append("## Section Summary")
    lines.append("| Section ID | Segments | Zotero-backed | Strong Zotero-backed | Collection Coverage |")
    lines.append("|---|---:|---:|---:|---|")
    sections = details.get("sections", {})
    if isinstance(sections, dict):
        for section_id, item in sorted(sections.items()):
            if isinstance(item, dict):
                lines.append(
                    f"| {section_id} | {item.get('segments', 0)} | {item.get('zoteroVerified', 0)} | {item.get('strongVerified', 0)} | {item.get('collectionCoverage', 'missing')} |"
                )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit Zotero-backed section citation coverage.")
    parser.add_argument("--project", default=".", help="Project root.")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    parser.add_argument("--write-report", help="Optional Markdown report path.")
    parser.add_argument("--warn-only", action="store_true", help="Return success even when issues exist.")
    args = parser.parse_args()

    thesis_dir = Path(args.project) / THESIS_DIR
    p0, p1, details = audit(thesis_dir)
    if args.write_report:
        path = Path(args.write_report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(p0, p1, details), encoding="utf-8")
    if args.json:
        print(json.dumps({"p0": p0, "p1": p1, "details": details}, ensure_ascii=False, indent=2))
    else:
        print(render(p0, p1, details))
    if p0 or p1:
        raise SystemExit(0 if args.warn_only else 1)


if __name__ == "__main__":
    main()
