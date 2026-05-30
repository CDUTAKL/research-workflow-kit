"""Audit workflow ID naming and lifecycle consistency."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

KNOWN_PREFIXES = {"SEC", "SEG", "CLM", "EXP", "DATA", "FIG", "MAT", "CIT", "BMK", "ZCOL", "DRT", "ZREV"}
IGNORED_AUXILIARY_PREFIXES = {"BATCH", "FB", "GIT", "IDEA", "LIT", "TASK", "XLS"}
LIFECYCLE_STATUSES = {"draft", "candidate", "verified", "promoted", "deprecated", "superseded"}
ID_RE = re.compile(r"\b(?:SEC|SEG|CLM|EXP|DATA|FIG|MAT|CIT|BMK|ZCOL|DRT|ZREV)-(?:AUTO-)?[A-Za-z0-9][A-Za-z0-9.-]*\b")
ID_LIKE_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,5}-(?:AUTO-)?[A-Z0-9.-]*\d{3,}[A-Z0-9.-]*\b")
MISSING = {"", "tbd", "missing", "pending", "n/a", "none", "-"}


DEFINITION_FILES = {
    "SEC": "section-citation-map.md",
    "SEG": "section-citation-map.md",
    "CLM": "claim-evidence-map.md",
    "EXP": "experiment-registry.md",
    "DATA": "data-availability.md",
    "FIG": "figure-plan.md",
    "MAT": "material-passport.md",
    "CIT": "citation-provenance.md",
    "BMK": "benchmark-report-schema.md",
    "ZCOL": "zotero-collection-coverage.md",
    "DRT": "deep-research-tasks.md",
    "ZREV": "zotero-screening-loop.md",
}


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


def missing(value: str) -> bool:
    return value.strip().lower().strip("` ") in MISSING


def prefix_of(item_id: str) -> str:
    return item_id.split("-", 1)[0]


def scan_console_ids(thesis_dir: Path) -> tuple[Counter[str], dict[str, set[str]], set[str]]:
    counts: Counter[str] = Counter()
    locations: dict[str, set[str]] = defaultdict(set)
    unknown: set[str] = set()
    if not thesis_dir.exists():
        return counts, locations, unknown
    for path in thesis_dir.rglob("*"):
        if path.suffix.lower() not in {".md", ".tsv", ".json"}:
            continue
        text = read_text(path)
        for item in ID_RE.findall(text):
            counts[item] += 1
            locations[item].add(path.relative_to(thesis_dir).as_posix())
        for item in ID_LIKE_RE.findall(text):
            if item.startswith("CITE-EXPORT") or item.startswith("AUD-"):
                continue
            prefix = prefix_of(item)
            if prefix in IGNORED_AUXILIARY_PREFIXES:
                continue
            if prefix not in KNOWN_PREFIXES:
                unknown.add(item)
    return counts, locations, unknown


def parse_lifecycle_registry(thesis_dir: Path) -> dict[str, dict[str, str]]:
    registry: dict[str, dict[str, str]] = {}
    path = thesis_dir / "id-lifecycle-policy.md"
    for cells in markdown_rows(read_text(path)):
        if len(cells) < 9 or cells[0] == "ID":
            continue
        if ID_RE.fullmatch(cells[0]):
            registry[cells[0]] = {
                "type": cells[1],
                "status": cells[2].lower(),
                "primary_file": cells[3],
                "related_ids": cells[4],
                "replacement_id": cells[5],
                "owner": cells[6],
                "updated_on": cells[7],
                "notes": cells[8],
            }
    return registry


def parse_definition_rows(thesis_dir: Path) -> dict[str, set[str]]:
    definitions: dict[str, set[str]] = defaultdict(set)
    for prefix, filename in DEFINITION_FILES.items():
        path = thesis_dir / filename
        for cells in markdown_rows(read_text(path)):
            if not cells:
                continue
            item_id = cells[0]
            if ID_RE.fullmatch(item_id) and prefix_of(item_id) == prefix:
                definitions[item_id].add(filename)
    return definitions


def audit_claim_links(thesis_dir: Path) -> list[str]:
    warnings: list[str] = []
    for cells in markdown_rows(read_text(thesis_dir / "claim-evidence-map.md")):
        if len(cells) < 8 or not cells[0].startswith("CLM-"):
            continue
        evidence = " | ".join(cells[3:6])
        if not re.search(r"\b(?:EXP|DATA|CIT|FIG)-", evidence):
            warnings.append(f"{cells[0]} has no EXP/DATA/CIT/FIG evidence link")
    return warnings


def audit_figure_links(thesis_dir: Path) -> list[str]:
    warnings: list[str] = []
    for cells in markdown_rows(read_text(thesis_dir / "figure-plan.md")):
        if len(cells) < 2 or not cells[0].startswith("FIG-"):
            continue
        row = " | ".join(cells)
        status = cells[-1].lower()
        if status in {"final", "done", "reviewed"} and not re.search(r"\b(?:CLM|EXP|DATA)-", row):
            warnings.append(f"{cells[0]} is {status} but has no CLM/EXP/DATA source link")
    return warnings


def audit(thesis_dir: Path) -> tuple[list[str], list[str], list[str], dict[str, object]]:
    p0: list[str] = []
    p1: list[str] = []
    info: list[str] = []
    if not (thesis_dir / "id-lifecycle-policy.md").exists():
        p1.append("missing console file: id-lifecycle-policy.md")

    counts, locations, unknown = scan_console_ids(thesis_dir)
    registry = parse_lifecycle_registry(thesis_dir)
    definitions = parse_definition_rows(thesis_dir)

    for item in sorted(unknown):
        p1.append(f"unknown ID prefix or unmanaged ID: {item}")

    for item_id, files in sorted(definitions.items()):
        if len(files) > 1:
            p1.append(f"{item_id} appears as a primary row in multiple files: {', '.join(files)}")

    for item_id, record in sorted(registry.items()):
        status = record["status"]
        if status not in LIFECYCLE_STATUSES:
            p1.append(f"{item_id} has invalid lifecycle status: {status}")
        if status == "superseded" and missing(record["replacement_id"]):
            p1.append(f"{item_id} is superseded but has no replacement ID")
        if status == "deprecated" and counts.get(item_id, 0) > 1:
            p1.append(f"{item_id} is deprecated but still referenced in {len(locations.get(item_id, []))} files")

    p1.extend(audit_claim_links(thesis_dir))
    p1.extend(audit_figure_links(thesis_dir))

    info.append(f"ids={sum(counts.values())} unique_ids={len(counts)} lifecycle_records={len(registry)}")
    details = {
        "ids": dict(counts),
        "locations": {key: sorted(value) for key, value in locations.items()},
        "lifecycle": registry,
        "definitions": {key: sorted(value) for key, value in definitions.items()},
    }
    return p0, p1, info, details


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit workflow ID lifecycle and naming consistency.")
    parser.add_argument("--thesis-dir", default="docs/thesis")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    p0, p1, info, details = audit(Path(args.thesis_dir))
    if args.json:
        print(json.dumps({"p0": p0, "p1": p1, "info": info, "details": details}, ensure_ascii=False, indent=2))
    else:
        print(info[0] if info else "ids=0 unique_ids=0 lifecycle_records=0")
        print(f"Errors: {len(p0)}")
        for item in p0:
            print(f"- P0: {item}")
        print(f"Warnings: {len(p1)}")
        for item in p1:
            print(f"- P1: {item}")
    if p0 and not args.warn_only:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
