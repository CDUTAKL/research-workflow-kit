"""Suggest local citation candidates for a SEC-* section without network access.

Scoring is intentionally deterministic and conservative. It rewards evidence
that makes a citation easier to verify locally: stable identifiers, Zotero
presence, reader/Scite checks, strong support labels, and direct SEC/SEG links.
It penalizes candidates already excluded, metadata-only candidates without a
reader check, and blocked/invalid metadata. The result is a triage order for
manual confirmation, not an automatic citation decision.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

THESIS_DIR = Path("docs/thesis")
SUGGESTIONS = THESIS_DIR / "section-citation-suggestions.md"
IDENTIFIER_RE = re.compile(r"(10\.\d{4,9}/\S+|arXiv:\S+|S2:\S+|PMID:\S+|PubMed:\S+)", re.IGNORECASE)
SCORE_LEDGER = {
    "identifier": 2,
    "zotero": 2,
    "reader_or_scite": 2,
    "strong_support": 3,
    "partial_or_background_support": 1,
    "section_match": 3,
    "segment_link": 1,
    "excluded": -5,
    "metadata_only_without_reader": -2,
    "blocked_or_invalid": -4,
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


def norm(value: Any) -> str:
    return str(value if value is not None else "").strip()


def usable(value: str) -> bool:
    return norm(value).lower().strip("` ") not in {"", "tbd", "missing", "none", "n/a", "-"}


def title_key(title: str, identifier: str) -> str:
    if usable(identifier):
        return identifier.lower()
    return re.sub(r"\W+", " ", title.lower()).strip()


def add_candidate(candidates: dict[str, dict[str, Any]], item: dict[str, Any]) -> None:
    title = norm(item.get("title"))
    identifier = norm(item.get("identifier"))
    if not usable(title) and not usable(identifier):
        return
    key = title_key(title or identifier, identifier)
    existing = candidates.get(key)
    if existing is None:
        candidates[key] = item
        return
    for field in ("section_id", "segment_id", "source", "support", "metadata_status", "zotero_status", "reader_status", "notes"):
        old = norm(existing.get(field))
        new = norm(item.get(field))
        if new and new not in old:
            existing[field] = "; ".join(part for part in (old, new) if part)


def collect_candidates(thesis_dir: Path, section_id: str) -> list[dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}

    for cells in markdown_rows(read_text(thesis_dir / "section-citation-map.md")):
        if cells and re.fullmatch(r"SEG-[A-Za-z0-9.-]+", cells[0]) and len(cells) >= 9:
            if section_id and cells[1] != section_id:
                continue
            add_candidate(
                candidates,
                {
                    "title": cells[3],
                    "identifier": cells[4],
                    "section_id": cells[1],
                    "segment_id": cells[0],
                    "source": "section-citation-map",
                    "support": cells[5],
                    "metadata_status": cells[6],
                    "zotero_status": cells[7],
                    "reader_status": cells[8],
                    "notes": cells[10] if len(cells) > 10 else "",
                },
            )

    for cells in markdown_rows(read_text(thesis_dir / "citation-provenance.md")):
        if cells and re.fullmatch(r"CIT-[A-Za-z0-9.-]+", cells[0]) and len(cells) >= 11:
            if section_id and cells[1] != section_id:
                continue
            add_candidate(
                candidates,
                {
                    "title": cells[4],
                    "identifier": cells[5],
                    "section_id": cells[1],
                    "segment_id": cells[2],
                    "source": "citation-provenance",
                    "support": cells[8],
                    "metadata_status": cells[7],
                    "zotero_status": cells[9],
                    "reader_status": cells[10],
                    "notes": cells[14] if len(cells) > 14 else "",
                },
            )

    for cells in markdown_rows(read_text(thesis_dir / "literature-matrix.md")):
        if cells and len(cells) >= 14 and cells[0] != "Paper":
            manuscript_use = cells[8] if len(cells) > 8 else ""
            if section_id and section_id.lower() not in " ".join(cells).lower() and not usable(manuscript_use):
                continue
            add_candidate(
                candidates,
                {
                    "title": cells[0],
                    "identifier": cells[3],
                    "section_id": section_id or "TBD",
                    "segment_id": "TBD",
                    "source": "literature-matrix",
                    "support": cells[12] if len(cells) > 12 else "",
                    "metadata_status": cells[9] if len(cells) > 9 else "",
                    "zotero_status": cells[11] if len(cells) > 11 else "",
                    "reader_status": cells[13] if len(cells) > 13 else "",
                    "notes": manuscript_use,
                },
            )

    for cells in markdown_rows(read_text(thesis_dir / "zotero-screening-loop.md")):
        if cells and len(cells) >= 8 and re.fullmatch(r"LIT-CAND-[A-Za-z0-9.-]+", cells[0]):
            label = cells[6] if len(cells) > 6 else ""
            add_candidate(
                candidates,
                {
                    "title": cells[3],
                    "identifier": cells[4],
                    "section_id": section_id or "TBD",
                    "segment_id": "TBD",
                    "source": "zotero-screening-loop",
                    "support": label,
                    "metadata_status": cells[8] if len(cells) > 8 else "",
                    "zotero_status": "",
                    "reader_status": "",
                    "notes": cells[9] if len(cells) > 9 else "",
                },
            )
        if cells and len(cells) >= 7 and re.fullmatch(r"LIT-CAND-[A-Za-z0-9.-]+", cells[0]) and "SEC-" in " ".join(cells):
            if section_id and section_id not in cells:
                continue
            add_candidate(
                candidates,
                {
                    "title": cells[0],
                    "identifier": "",
                    "section_id": cells[2] if len(cells) > 2 else section_id,
                    "segment_id": cells[3] if len(cells) > 3 else "TBD",
                    "source": "zotero-section-handoff",
                    "support": cells[5] if len(cells) > 5 else "",
                    "metadata_status": "",
                    "zotero_status": "",
                    "reader_status": "",
                    "notes": cells[6] if len(cells) > 6 else "",
                },
            )

    for cells in markdown_rows(read_text(thesis_dir / "zotero-collection-coverage.md")):
        row_text = " ".join(cells)
        if section_id and section_id not in row_text:
            continue
        if len(cells) >= 8 and cells[0].startswith("SEC-"):
            papers = "; ".join(part for part in cells[3:6] if usable(part))
            add_candidate(
                candidates,
                {
                    "title": papers or cells[0],
                    "identifier": "",
                    "section_id": cells[0],
                    "segment_id": "TBD",
                    "source": "zotero-collection-coverage",
                    "support": cells[7] if len(cells) > 7 else "",
                    "metadata_status": "",
                    "zotero_status": "in_zotero" if "CIT-" in row_text else "",
                    "reader_status": "",
                    "notes": cells[6] if len(cells) > 6 else "",
                },
            )

    for packet in sorted((thesis_dir / "section-research-packets").glob("*.md")):
        if section_id and packet.stem != section_id:
            continue
        for cells in markdown_rows(read_text(packet)):
            if len(cells) >= 8 and cells[0].startswith("P-"):
                add_candidate(
                    candidates,
                    {
                        "title": cells[1],
                        "identifier": cells[2],
                        "section_id": section_id or packet.stem,
                        "segment_id": "TBD",
                        "source": packet.as_posix(),
                        "support": cells[3],
                        "metadata_status": cells[4],
                        "zotero_status": cells[5],
                        "reader_status": cells[6],
                        "notes": cells[7],
                    },
                )

    return list(candidates.values())


def score_candidate(item: dict[str, Any], section_id: str) -> tuple[int, list[str], str]:
    score = 0
    reasons: list[str] = []
    identifier = norm(item.get("identifier"))
    support = norm(item.get("support")).lower()
    metadata = norm(item.get("metadata_status")).lower()
    zotero = norm(item.get("zotero_status")).lower()
    reader = norm(item.get("reader_status")).lower()
    section = norm(item.get("section_id"))
    segment = norm(item.get("segment_id"))

    if usable(identifier) and (IDENTIFIER_RE.search(identifier) or identifier.lower() not in {"doi/arxiv/s2/pmid/tbd"}):
        score += SCORE_LEDGER["identifier"]
        reasons.append("identifier")
    if "in_zotero" in zotero:
        score += SCORE_LEDGER["zotero"]
        reasons.append("zotero")
    if any(term in reader for term in ("support", "reader", "source", "checked", "directly_read")) or "claim_support_checked" in metadata:
        score += SCORE_LEDGER["reader_or_scite"]
        reasons.append("reader/scite")
    if "strong" in support or "supports" in support or "a-core" in support.lower():
        score += SCORE_LEDGER["strong_support"]
        reasons.append("strong")
    elif any(term in support for term in ("partial", "background", "b-section", "c-background")):
        score += SCORE_LEDGER["partial_or_background_support"]
        reasons.append("support")
    if section_id and section == section_id:
        score += SCORE_LEDGER["section_match"]
        reasons.append("section")
    if usable(segment) and segment != "TBD":
        score += SCORE_LEDGER["segment_link"]
        reasons.append("segment")
    if "d-exclude" in support.lower():
        score += SCORE_LEDGER["excluded"]
        reasons.append("excluded")
    if "metadata_only" in support.lower() and not reader:
        score += SCORE_LEDGER["metadata_only_without_reader"]
        reasons.append("metadata-only")
    if "invalid" in metadata or "blocked" in zotero:
        score += SCORE_LEDGER["blocked_or_invalid"]
        reasons.append("blocked")

    use_note = "候选引用"
    if "contradict" in support or "limiting" in support:
        use_note = "适合限制/对比讨论"
    elif score >= 8:
        use_note = "优先核查"
    elif score >= 4:
        use_note = "可作为章节候选"
    return score, reasons, use_note


def build_suggestions(thesis_dir: Path, section_id: str) -> list[dict[str, Any]]:
    suggestions: list[dict[str, Any]] = []
    for item in collect_candidates(thesis_dir, section_id):
        score, reasons, use_note = score_candidate(item, section_id)
        item = {**item, "score": score, "reasons": ", ".join(reasons) or "candidate", "use_note": use_note}
        suggestions.append(item)
    suggestions.sort(key=lambda item: (-int(item["score"]), norm(item.get("title")).lower()))
    return suggestions


def write_markdown(path: Path, section_id: str, suggestions: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Section Citation Suggestions",
        "",
        "## Purpose",
        "",
        "Generated local-only suggestions from existing thesis console records. These are candidates, not final citations.",
        "",
        f"## Suggestions For {section_id or 'ALL'}",
        "",
        "| Rank | Score | Section ID | Segment ID | Candidate Reference | Identifier | Source | Zotero / Scite / Reader | Suggested Use | Reasons |",
        "|---:|---:|---|---|---|---|---|---|---|---|",
    ]
    if suggestions:
        for index, item in enumerate(suggestions, start=1):
            reader = " / ".join(
                part for part in (norm(item.get("zotero_status")), norm(item.get("reader_status")), norm(item.get("metadata_status"))) if usable(part)
            ) or "TBD"
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(index),
                        str(item["score"]),
                        norm(item.get("section_id")) or section_id or "TBD",
                        norm(item.get("segment_id")) or "TBD",
                        norm(item.get("title")) or "TBD",
                        norm(item.get("identifier")) or "TBD",
                        norm(item.get("source")) or "TBD",
                        reader,
                        norm(item.get("use_note")) or "TBD",
                        norm(item.get("reasons")) or "TBD",
                    ]
                )
                + " |"
            )
    else:
        lines.append("| 1 | 0 | TBD | TBD | No local candidates found | TBD | local records | TBD | create deep research task | no-candidates |")
    lines.extend(
        [
            "",
            "## Next Actions",
            "",
            "- Confirm useful candidates manually before adding them to `section-citation-map.md` or `citation-provenance.md`.",
            "- Use Semantic Scholar, Zotero, Scite, or source-grounded reading separately when new papers are needed.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Suggest local section citation candidates without network access.")
    parser.add_argument("--thesis-dir", default="docs/thesis")
    parser.add_argument("--section-id", default="")
    parser.add_argument("--out", default=str(SUGGESTIONS))
    parser.add_argument("--json-out")
    args = parser.parse_args()

    thesis_dir = Path(args.thesis_dir)
    suggestions = build_suggestions(thesis_dir, args.section_id)
    write_markdown(Path(args.out), args.section_id, suggestions)
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"sectionId": args.section_id, "suggestions": suggestions}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote citation suggestions: {args.out}")
    print(f"suggestions: {len(suggestions)}")


if __name__ == "__main__":
    main()
