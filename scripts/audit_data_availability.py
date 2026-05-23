"""Audit thesis data availability records."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


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


def is_missing(value: str) -> bool:
    return value.strip().lower() in {"", "tbd", "missing", "n/a", "pending"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit docs/thesis/data-availability.md.")
    parser.add_argument("--path", default="docs/thesis/data-availability.md")
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args()

    path = Path(args.path)
    errors: list[str] = []
    warnings: list[str] = []
    datasets = 0
    traces = 0

    if not path.exists():
        print(f"ERROR: {path} not found")
        sys.exit(0 if args.warn_only else 1)

    for cells in markdown_rows(path.read_text(encoding="utf-8")):
        if not cells:
            continue
        if re.fullmatch(r"DATA-\d+", cells[0]) and len(cells) >= 12:
            datasets += 1
            data_id = cells[0]
            hash_value = cells[6] if len(cells) > 6 else ""
            access = cells[7] if len(cells) > 7 else ""
            license_value = cells[8] if len(cells) > 8 else ""
            data_dictionary = cells[9] if len(cells) > 9 else ""
            command = cells[10] if len(cells) > 10 else ""
            status = cells[11].lower() if len(cells) > 11 else ""
            if is_missing(hash_value):
                warnings.append(f"{data_id} is missing hash or manifest")
            if is_missing(access):
                errors.append(f"{data_id} is missing access level")
            if is_missing(license_value):
                warnings.append(f"{data_id} is missing license or permission")
            if is_missing(data_dictionary):
                warnings.append(f"{data_id} is missing data dictionary")
            if is_missing(command):
                warnings.append(f"{data_id} is missing generation command")
            if status in {"missing", "invalid"}:
                errors.append(f"{data_id} status is {status}")
        if re.fullmatch(r"CLM-\d+", cells[0]):
            traces += 1
            claim_id = cells[0]
            source_data = cells[2] if len(cells) > 2 else ""
            script = cells[4] if len(cells) > 4 else ""
            artifact = cells[5] if len(cells) > 5 else ""
            trace_status = cells[6].lower() if len(cells) > 6 else ""
            if is_missing(source_data):
                errors.append(f"{claim_id} has no source data")
            if is_missing(script):
                warnings.append(f"{claim_id} has no script or notebook")
            if is_missing(artifact):
                errors.append(f"{claim_id} has no output artifact")
            if trace_status in {"missing", "invalid"}:
                errors.append(f"{claim_id} trace status is {trace_status}")

    print(f"Datasets: {datasets}  |  Claim traces: {traces}")
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
