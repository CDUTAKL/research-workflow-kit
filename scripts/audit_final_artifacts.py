"""Audit final artifact handoff readiness for stages 11-12."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


FINAL_FORMATS = {"docx", "pdf", "pptx"}
MISSING = {"", "tbd", "missing", "pending", "n/a", "none", "-"}


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


def parse_artifacts(thesis_dir: Path) -> list[dict[str, str]]:
    path = thesis_dir / "final-artifact-manifest.md"
    artifacts: list[dict[str, str]] = []
    for cells in markdown_rows(read_text(path)):
        if len(cells) < 11 or cells[0] == "Artifact Key":
            continue
        artifacts.append(
            {
                "artifact_key": cells[0],
                "stage": cells[1],
                "source_ids": cells[2],
                "mac_source_path": cells[3],
                "laptop_target_path": cells[4],
                "format": cells[5].lower(),
                "checksum": cells[6],
                "produced_by": cells[7],
                "transfer_status": cells[8].lower(),
                "laptop_verification": cells[9].lower(),
                "notes": cells[10],
            }
        )
    return artifacts


def audit(thesis_dir: Path, tier: str = "quick") -> tuple[list[str], list[str], list[str], list[dict[str, str]]]:
    path = thesis_dir / "final-artifact-manifest.md"
    p0: list[str] = []
    p1: list[str] = []
    info: list[str] = []
    if not path.exists():
        message = "missing console file: final-artifact-manifest.md"
        if tier == "final":
            p0.append(message)
        else:
            p1.append(message)
        return p0, p1, [message], []

    artifacts = parse_artifacts(thesis_dir)
    if not artifacts:
        p1.append("final-artifact-manifest.md has no artifact rows")

    for item in artifacts:
        key = item["artifact_key"]
        status = item["transfer_status"]
        fmt = item["format"]
        if status == "blocked":
            p0.append(f"{key} transfer is blocked")
        if status == "pending":
            if tier == "quick":
                p1.append(f"{key} is still pending laptop handoff")
            else:
                p0.append(f"{key} is still pending laptop handoff for {tier} audit")
        if tier in {"advisor", "final"} and fmt in FINAL_FORMATS and status not in {"copied", "verified"}:
            p0.append(f"{key} ({fmt}) is not copied or verified for {tier} audit")
        if tier == "final" and status != "verified":
            p0.append(f"{key} is not verified on the laptop for final audit")
        if missing(item["checksum"]):
            if tier == "final":
                p0.append(f"{key} is missing checksum for final audit")
            else:
                p1.append(f"{key} is missing checksum")
        mac_path = item["mac_source_path"].strip("` ")
        if not missing(mac_path) and not Path(mac_path).expanduser().exists():
            message = f"{key} Mac source path does not exist: {mac_path}"
            if tier == "final":
                p0.append(message)
            else:
                p1.append(message)
        if status == "verified" and missing(item["laptop_verification"]):
            p1.append(f"{key} is verified but laptop verification note is missing")
        if tier == "final" and missing(item["laptop_target_path"]):
            p0.append(f"{key} is missing laptop target path for final audit")

    info.append(f"final_artifacts={len(artifacts)} tier={tier}")
    return p0, p1, info, artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit final artifact handoff readiness.")
    parser.add_argument("--thesis-dir", default="docs/thesis")
    parser.add_argument("--tier", choices=["quick", "advisor", "final"], default="quick")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    p0, p1, info, artifacts = audit(Path(args.thesis_dir), args.tier)
    if args.json:
        print(json.dumps({"p0": p0, "p1": p1, "info": info, "artifacts": artifacts}, ensure_ascii=False, indent=2))
    else:
        print(f"Final Artifacts: {len(artifacts)}  |  Tier: {args.tier}")
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
