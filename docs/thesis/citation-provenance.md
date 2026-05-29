# Citation Provenance

## Purpose

Use this file to record how citation candidates were verified before they are promoted into thesis text, BibTeX, RIS, ENW, Zotero RDF, or final references.

This complements `section-citation-map.md` and `zotero-screening-loop.md`. It focuses on provenance: who or what verified the metadata, when it was verified, and whether the cited paper truly supports the target segment.

## Update Rules

- Candidate citations are not final until metadata and support are verified.
- Record `verified_by` and `verified_on` for every core citation used in an important `SEG-*` or `CLM-*`.
- Distinguish metadata verification from support verification. A correct DOI does not prove that the paper supports the claim.
- Keep Zotero status visible, but treat `docs/thesis/` records as the thesis evidence source of truth.

## Citation Verification Registry

| Citation ID | Section ID | Segment ID | Claim ID | Title | Identifier | Candidate Source | Metadata Status | Support Status | Zotero Status | Scite / Reader Evidence | Verified By | Verified On | Export Status | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CIT-001 | SEC-INTRO-001 | SEG-001 | CLM-001/TBD | TBD | DOI/arXiv/S2/PMID/TBD | Semantic Scholar / Zotero / Scite / Web / paper-search / PubMed / TBD | candidate / metadata_verified / invalid / TBD | unchecked / supports / partial / background / contradicts / TBD | not_added / in_zotero / duplicate / blocked | Scite / reader path / source map / TBD | Codex/user/Zotero/Scite/TBD | YYYY-MM-DD/TBD | bibtex/ris/enw/zotero-rdf/final/TBD |  |

## Bibliography Export Trace

| Export ID | Scope | Format | Source Citations | Destination | Generated On | Verified Count | Unverified Count | Status |
|---|---|---|---|---|---|---|---|---|
| CITE-EXPORT-001 | SEC-INTRO-001/TBD | bibtex/ris/enw/zotero-rdf | CIT-001/TBD | TBD | YYYY-MM-DD/TBD | 0 | 1 | draft |

## Promotion Rules

| Rule | Meaning |
|---|---|
| `metadata_verified` is necessary but not sufficient | DOI/title/author/year are checked, but claim support may still be absent |
| `supports` requires source-grounded evidence | Use Scite, direct PDF reading, Zotero notes, or `paper-readings/<paper>/source_map.json` |
| `background` papers should not support strong claims | Use them for context only |
| `contradicts` should be preserved | Contradictory literature is useful for limitations and discussion |
