# Academic Search Policy

## Purpose

Use this file to plan and audit multi-source literature search before a paper is promoted into `section-citation-map.md` or `citation-provenance.md`.

This policy adapts useful ideas from `nature-academic-search` into the local thesis workflow. It is a search and verification guide, not an automatic paper downloader.

## Source Routing

| Source | Best Use | Required Record | Do Not Use For |
|---|---|---|---|
| Semantic Scholar | broad discovery, citation graph, related papers | `literature-matrix.md`, `deep-research-tasks.md` | final metadata truth by itself |
| Zotero | local library, collections, tags, BibTeX/RIS export | `zotero-literature-hub.md`, `zotero-collection-coverage.md` | replacing `CIT-*` evidence |
| Scite | support / contrast / mention checks | `citation-provenance.md` | replacing direct reading for core claims |
| PubMed | biomedical and clinical literature | PMID, query, MeSH terms | non-biomedical-only default search |
| CrossRef | DOI, title, author, year metadata check | DOI, metadata status | claim-support verification |
| arXiv | preprints, technical methods, recent ML work | arXiv ID and version when available | final peer-reviewed status |
| Publisher / DOI page | final metadata, venue, corrections, PDF access | metadata verification note | broad discovery |

## Search Query Register

| Search ID | Section ID | Segment ID | Query | Source | Keywords / MeSH | Filters | Candidate Count | Useful Count | Next Action |
|---|---|---|---|---|---|---|---:|---:|---|
| SEARCH-001 | SEC-INTRO-001 | SEG-001/TBD | TBD | Semantic Scholar / PubMed / CrossRef / arXiv / Web / TBD | TBD | year/language/type/TBD | 0 | 0 | create candidates |

## Verification Ladder

| Level | Meaning | Promotion Use |
|---|---|---|
| candidate | found by search, metadata unverified | do not cite yet |
| metadata_verified | DOI / PMID / arXiv / title / author / year checked | can enter citation queue |
| in_zotero | item exists in local Zotero with collection/tag | can support section coverage |
| reader_checked | direct reading or source map confirms relevance | can support important segment |
| scite_checked | support / contrast / mention checked | useful for claim-support audit |
| supports_claim | source-grounded evidence supports exact sentence | can become final `CIT-*` evidence |

## Rules

- Record search terms and source before adding many papers to Zotero.
- Prefer DOI, PMID, arXiv ID, or Semantic Scholar ID over title-only candidates.
- MeSH terms are useful when the topic is biomedical; do not force MeSH on non-biomedical sections.
- A Zotero item is not final evidence until it is mapped to `SEC-*` / `SEG-*` and promoted through `citation-provenance.md`.
- A Scite check is helpful but does not replace reading the source for core claims.
