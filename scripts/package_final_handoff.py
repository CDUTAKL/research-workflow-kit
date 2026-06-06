"""Package final artifacts listed in final-artifact-manifest.md for Windows review."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any

from audit_final_artifacts import missing, parse_artifacts

ROOT = Path.cwd()
THESIS_DIR = Path("docs/thesis")
DEFAULT_OUT_DIR = Path("handoff-packages")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    return name.strip("-") or "artifact"


def resolve_source(path_text: str, root: Path) -> Path:
    path = Path(path_text.strip("` "))
    if not path.is_absolute():
        path = root / path
    return path.expanduser().resolve()


def update_manifest_checksums(manifest_path: Path, checksums: dict[str, str]) -> None:
    lines = manifest_path.read_text(encoding="utf-8").splitlines()
    updated: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            updated.append(line)
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 11 or cells[0] not in checksums:
            updated.append(line)
            continue
        cells[6] = f"sha256:{checksums[cells[0]]}"
        updated.append("| " + " | ".join(cells) + " |")
    manifest_path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def package_handoff(
    root: Path,
    thesis_dir: Path,
    out_dir: Path,
    update_checksums: bool = False,
) -> dict[str, Any]:
    manifest_path = thesis_dir / "final-artifact-manifest.md"
    if not manifest_path.exists():
        raise FileNotFoundError(f"missing manifest: {manifest_path}")

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    package_name = f"final-handoff-{timestamp}"
    package_dir = out_dir / package_name
    artifacts_dir = package_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    packaged: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    checksum_by_key: dict[str, str] = {}

    for item in parse_artifacts(thesis_dir):
        key = item["artifact_key"]
        status = item["transfer_status"]
        source_text = item["mac_source_path"]
        if status == "blocked":
            skipped.append({"artifact_key": key, "reason": "blocked"})
            continue
        if missing(source_text):
            skipped.append({"artifact_key": key, "reason": "missing Mac Source Path"})
            continue
        source = resolve_source(source_text, root)
        if not source.exists() or not source.is_file():
            skipped.append({"artifact_key": key, "reason": f"source not found: {source}"})
            continue

        target_rel = Path("artifacts") / safe_name(key) / source.name
        target = package_dir / target_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        checksum = sha256(target)
        checksum_by_key[key] = checksum
        packaged.append(
            {
                "artifact_key": key,
                "format": item["format"],
                "source_ids": item["source_ids"],
                "original_path": str(source),
                "package_path": target_rel.as_posix(),
                "checksum": f"sha256:{checksum}",
                "transfer_status": status,
            }
        )

    snapshot = package_dir / "final-artifact-manifest.snapshot.md"
    shutil.copy2(manifest_path, snapshot)

    manifest = {
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        "root": str(root),
        "source_manifest": str(manifest_path),
        "artifacts": packaged,
        "skipped": skipped,
    }
    (package_dir / "handoff-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    checksum_lines = [f"{item['checksum'].split(':', 1)[1]}  {item['package_path']}" for item in packaged]
    (package_dir / "checksums.sha256").write_text("\n".join(checksum_lines) + ("\n" if checksum_lines else ""), encoding="utf-8")

    summary_lines = [
        "# Final Handoff Summary",
        "",
        f"- Created: {manifest['created_at']}",
        f"- Packaged artifacts: {len(packaged)}",
        f"- Skipped artifacts: {len(skipped)}",
        f"- Package directory: `{package_dir}`",
        "",
        "## Packaged",
        "",
    ]
    summary_lines.extend([f"- `{item['artifact_key']}` -> `{item['package_path']}` ({item['checksum']})" for item in packaged] or ["- none"])
    summary_lines.extend(["", "## Skipped", ""])
    summary_lines.extend([f"- `{item['artifact_key']}`: {item['reason']}" for item in skipped] or ["- none"])
    (package_dir / "handoff-summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    zip_path = package_dir / f"{package_name}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in package_dir.rglob("*"):
            if path == zip_path or path.is_dir():
                continue
            archive.write(path, path.relative_to(package_dir))

    if update_checksums and checksum_by_key:
        update_manifest_checksums(manifest_path, checksum_by_key)

    return {
        "ok": True,
        "package_dir": str(package_dir),
        "zip_path": str(zip_path),
        "packaged": packaged,
        "skipped": skipped,
        "updated_manifest_checksums": bool(update_checksums and checksum_by_key),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Package final artifacts from the manifest for Windows compatibility review.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--thesis-dir", default=str(THESIS_DIR))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--update-manifest-checksums", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    thesis_dir = Path(args.thesis_dir)
    if not thesis_dir.is_absolute():
        thesis_dir = root / thesis_dir
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = root / out_dir

    result = package_handoff(root, thesis_dir, out_dir, args.update_manifest_checksums)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"wrote handoff package: {result['zip_path']}")
        print(f"packaged: {len(result['packaged'])}  skipped: {len(result['skipped'])}")
        for item in result["skipped"]:
            print(f"- skipped {item['artifact_key']}: {item['reason']}")


if __name__ == "__main__":
    main()
