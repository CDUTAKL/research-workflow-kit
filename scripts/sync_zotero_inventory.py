"""Create a local Zotero inventory snapshot for the thesis workflow.

The script is intentionally conservative: it can read JSON exported by the
Zotero plugin helper, or it can call the helper when a path is provided. It does
not write to Zotero. The output is a Markdown snapshot that helps map Zotero
items, collections, tags, and citation keys back into `docs/thesis/`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

THESIS_DIR = Path("docs/thesis")
OUTPUT = THESIS_DIR / "zotero-literature-hub.md"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run_helper(helper: Path) -> Any:
    result = subprocess.run(
        ["python3", str(helper), "inventory", "--json"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or result.stdout.strip() or "Zotero helper failed")
    return json.loads(result.stdout)


def as_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("items", "results", "library", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def field(item: dict[str, Any], *names: str) -> str:
    for name in names:
        value = item.get(name)
        if value is None:
            continue
        if isinstance(value, list):
            return "; ".join(str(part) for part in value if str(part).strip())
        if isinstance(value, dict):
            return "; ".join(f"{key}:{val}" for key, val in value.items())
        text = str(value).strip()
        if text:
            return text
    return "TBD"


def render_inventory(items: list[dict[str, Any]], source: str) -> str:
    now = dt.datetime.now().isoformat(timespec="seconds")
    lines = [
        "# Zotero Literature Hub",
        "",
        "## Purpose",
        "",
        "Use this file as the local inventory snapshot for Zotero-backed thesis literature. It complements `zotero-screening-loop.md`, `zotero-collection-coverage.md`, `section-citation-map.md`, and `citation-provenance.md`.",
        "",
        "## Snapshot Metadata",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Generated On | {now} |",
        f"| Source | {source} |",
        f"| Item Count | {len(items)} |",
        "",
        "## Zotero Item Inventory",
        "",
        "| Zotero Item Key | BibTeX Key | Title | Year | Creators | Identifier | Collections / Tags | Status Hint | Section / Claim Hint | Next Action |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    if not items:
        lines.append("| TBD | TBD | TBD | TBD | TBD | DOI/arXiv/S2/PMID/TBD | thesis/TBD | not_synced | SEC-INTRO-001/TBD | run Zotero inventory |")
    for item in items:
        zotero_key = field(item, "itemKey", "key", "zoteroItemKey", "zotero_key")
        bibtex_key = field(item, "bibtexKey", "citationKey", "citekey", "bibtex_key")
        title = field(item, "title", "name")
        year = field(item, "year", "date")
        creators = field(item, "creators", "authors", "creatorSummary")
        identifier = field(item, "doi", "DOI", "identifier", "arxiv", "pmid", "url")
        collections = field(item, "collections", "collection", "tags", "tagNames")
        status = "in_zotero" if zotero_key != "TBD" else "candidate"
        section_hint = "SEC-INTRO-001/TBD"
        next_action = "map_to_section"
        lines.append(
            f"| {zotero_key} | {bibtex_key} | {title} | {year} | {creators} | {identifier} | {collections} | {status} | {section_hint} | {next_action} |"
        )
    lines.extend(
        [
            "",
            "## Usage Notes",
            "",
            "- Do not cite from this inventory alone.",
            "- Promote useful papers into `section-citation-map.md` first.",
            "- Promote formal citations into `citation-provenance.md` with metadata and support verification.",
            "- Use `export_zotero_bibliography.py` only after citation rows are verified or writing-ready.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Write a local Zotero inventory snapshot.")
    parser.add_argument("--input-json", help="JSON inventory exported by the Zotero helper.")
    parser.add_argument("--helper", help="Path to the Zotero plugin helper zotero.py. Calls inventory --json.")
    parser.add_argument("--out", default=str(OUTPUT), help="Markdown output path.")
    args = parser.parse_args()

    if args.input_json:
        source = args.input_json
        payload = read_json(Path(args.input_json))
    elif args.helper:
        source = args.helper
        payload = run_helper(Path(args.helper))
    else:
        source = "manual/template"
        payload = []

    items = as_list(payload)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_inventory(items, source), encoding="utf-8")
    print(f"wrote Zotero inventory: {out} ({len(items)} items)")


if __name__ == "__main__":
    main()
