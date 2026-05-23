"""Audit docs/thesis/section-citation-map.md for citation coverage gaps."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


VALID_SUPPORT = {"strong", "partial", "background", "limiting", "contradictory", "metadata_only"}
FINAL_STATUSES = {"metadata_verified", "in_zotero", "claim_support_checked"}


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit section-level citation map.")
    parser.add_argument("--map", default="docs/thesis/section-citation-map.md")
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args()

    path = Path(args.map)
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        print(f"ERROR: {path} not found")
        sys.exit(0 if args.warn_only else 1)

    rows = markdown_rows(path.read_text(encoding="utf-8"))
    sections: set[str] = set()
    segments: list[dict[str, str]] = []
    for cells in rows:
        if not cells:
            continue
        if re.fullmatch(r"SEC-[A-Za-z0-9.-]+", cells[0]):
            sections.add(cells[0])
        if re.fullmatch(r"SEG-\d+", cells[0]):
            segments.append(
                {
                    "segment": cells[0],
                    "section": cells[1] if len(cells) > 1 else "",
                    "candidate": cells[3] if len(cells) > 3 else "",
                    "identifier": cells[4] if len(cells) > 4 else "",
                    "support": cells[5].lower() if len(cells) > 5 else "",
                    "source_status": cells[6].lower() if len(cells) > 6 else "",
                    "reader_status": cells[8].lower() if len(cells) > 8 else "",
                }
            )

    for seg in segments:
        if seg["section"] not in sections:
            errors.append(f"{seg['segment']} references missing section {seg['section']}")
        if not seg["candidate"] or seg["candidate"] == "TBD":
            errors.append(f"{seg['segment']} has no candidate reference")
        if seg["support"] not in VALID_SUPPORT:
            warnings.append(f"{seg['segment']} has unrecognized support grade `{seg['support']}`")
        if not seg["identifier"] or seg["identifier"] == "TBD":
            warnings.append(f"{seg['segment']} has no DOI/arXiv/S2 identifier")
        if seg["support"] == "strong" and seg["source_status"] not in FINAL_STATUSES:
            warnings.append(f"{seg['segment']} strong support is not metadata/source verified")
        if seg["support"] == "strong" and "not_checked" in seg["reader_status"]:
            warnings.append(f"{seg['segment']} strong support lacks Scite or reader check")

    print(f"Sections: {len(sections)}  |  Segments: {len(segments)}")
    print(f"Errors: {len(errors)}  |  Warnings: {len(warnings)}")
    if warnings:
        print("WARNINGS:")
        for item in warnings:
            print(f"  [!] {item}")
    if errors:
        print("BLOCKING ERRORS:")
        for item in errors:
            print(f"  [x] {item}")
    if errors and not args.warn_only:
        sys.exit(1)


if __name__ == "__main__":
    main()
