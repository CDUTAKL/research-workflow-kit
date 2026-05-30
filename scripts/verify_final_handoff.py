"""Verify a final handoff zip or directory with checksums.sha256."""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def latest_package(root: Path) -> Path:
    packages = sorted((root / "handoff-packages").glob("final-handoff-*/*.zip"))
    if not packages:
        raise FileNotFoundError("no handoff package zip found under handoff-packages/")
    return packages[-1]


def read_checksum_lines(path: Path) -> list[tuple[str, str]]:
    checksums: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split(maxsplit=1)
        if len(parts) != 2:
            checksums.append(("", stripped))
            continue
        checksums.append((parts[0], parts[1].strip()))
    return checksums


def verify_directory(package_dir: Path) -> dict[str, Any]:
    checksum_file = package_dir / "checksums.sha256"
    results: list[dict[str, str]] = []
    if not checksum_file.exists():
        return {"ok": False, "package_dir": str(package_dir), "results": [], "errors": ["missing checksums.sha256"]}

    for expected, rel_path in read_checksum_lines(checksum_file):
        target = package_dir / rel_path
        if not expected:
            results.append({"path": rel_path, "status": "fail", "expected": "", "actual": "", "reason": "invalid checksum line"})
            continue
        if not target.exists() or not target.is_file():
            results.append({"path": rel_path, "status": "missing", "expected": expected, "actual": "", "reason": "missing file"})
            continue
        actual = sha256(target)
        results.append(
            {
                "path": rel_path,
                "status": "pass" if actual == expected else "fail",
                "expected": expected,
                "actual": actual,
                "reason": "" if actual == expected else "checksum mismatch",
            }
        )

    ok = all(item["status"] == "pass" for item in results)
    return {"ok": ok, "package_dir": str(package_dir), "results": results, "errors": []}


def verify_package(path: Path) -> dict[str, Any]:
    if path.is_dir():
        return verify_directory(path)
    if not path.exists():
        raise FileNotFoundError(f"package not found: {path}")
    if path.suffix.lower() != ".zip":
        raise ValueError("handoff package must be a zip file or extracted directory")
    with tempfile.TemporaryDirectory() as tmp:
        extract_dir = Path(tmp) / "handoff"
        with zipfile.ZipFile(path) as archive:
            archive.extractall(extract_dir)
        result = verify_directory(extract_dir)
        result["package_zip"] = str(path)
        return result


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# Final Handoff Verify Report",
        "",
        f"- Package: `{result.get('package_zip') or result.get('package_dir')}`",
        f"- Status: `{'pass' if result.get('ok') else 'fail'}`",
        "",
        "| Artifact Path | Status | Reason |",
        "|---|---|---|",
    ]
    for item in result.get("results", []):
        lines.append(f"| {item['path']} | {item['status']} | {item.get('reason', '') or 'ok'} |")
    for error in result.get("errors", []):
        lines.append(f"| package | fail | {error} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a final handoff package.")
    parser.add_argument("package", nargs="?", help="handoff zip or extracted directory")
    parser.add_argument("--latest", action="store_true", help="verify latest handoff package under handoff-packages/")
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if args.latest:
        package_path = latest_package(root)
    elif args.package:
        package_path = Path(args.package)
        if not package_path.is_absolute():
            package_path = root / package_path
    else:
        raise SystemExit("provide a package path or --latest")

    result = verify_package(package_path)
    if args.write_report:
        report = Path(args.write_report)
        if not report.is_absolute():
            report = root / report
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(render_report(result), encoding="utf-8")
        result["report_path"] = str(report)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Final handoff verify: {'PASS' if result['ok'] else 'FAIL'}")
        for item in result.get("results", []):
            print(f"- {item['status']}: {item['path']} {item.get('reason', '')}")
        for error in result.get("errors", []):
            print(f"- fail: {error}")
    if not result["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
