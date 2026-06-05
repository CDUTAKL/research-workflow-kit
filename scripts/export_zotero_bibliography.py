"""Export or stage a bibliography from verified Zotero-backed citation rows."""
from __future__ import annotations

import argparse
import re
import subprocess
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


def verified_citations(thesis_dir: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    for cells in markdown_rows(read_text(thesis_dir / "citation-provenance.md")):
        if len(cells) >= 15 and re.fullmatch(r"CIT-[A-Za-z0-9.-]+", cells[0]):
            metadata_ok = cells[7].strip().lower() in {"metadata_verified", "verified", "final"}
            support_ok = cells[8].strip().lower() in {"supports", "partial", "background"}
            zotero_ok = cells[9].strip().lower() in {"in_zotero", "final"}
            export_ok = cells[13].strip().lower() in {"bibtex", "final", "ready"}
            if metadata_ok and support_ok and zotero_ok and export_ok:
                rows.append(cells)
    return rows


def run_helper(helper: Path, out: Path) -> str:
    result = subprocess.run(
        ["python3", str(helper), "export-bibtex", "--out", str(out)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or result.stdout.strip() or "Zotero export failed")
    return result.stdout.strip()


def write_stub_bib(rows: list[list[str]], out: Path) -> None:
    entries: list[str] = []
    for cells in rows:
        cit_id = cells[0].replace("-", "_")
        title = cells[4] or cells[0]
        identifier = cells[5]
        entries.append(
            "\n".join(
                [
                    f"@misc{{{cit_id},",
                    f"  title = {{{title}}},",
                    f"  note = {{{identifier}; verify/export from Zotero before final submission}},",
                    "}",
                    "",
                ]
            )
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(entries), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export bibliography for verified Zotero-backed citations.")
    parser.add_argument("--project", default=".", help="Project root.")
    parser.add_argument("--out", default="references.bib", help="BibTeX output path.")
    parser.add_argument("--helper", help="Optional Zotero helper zotero.py; if omitted, writes a review stub BibTeX.")
    parser.add_argument("--allow-stub", action="store_true", help="Allow stub BibTeX when Zotero helper is not provided.")
    args = parser.parse_args()

    root = Path(args.project)
    thesis_dir = root / THESIS_DIR
    out = root / args.out
    rows = verified_citations(thesis_dir)
    if args.helper:
        output = run_helper(Path(args.helper), out)
        print(output or f"exported bibliography: {out}")
    elif args.allow_stub:
        write_stub_bib(rows, out)
        print(f"wrote bibliography stub: {out} ({len(rows)} verified citation rows)")
    else:
        raise SystemExit("Provide --helper to export from Zotero, or --allow-stub for a review-only BibTeX stub.")


if __name__ == "__main__":
    main()
