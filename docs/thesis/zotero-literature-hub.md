# Zotero Literature Hub

## Purpose

Use this file as the operating policy for making Zotero the thesis literature hub.

Zotero stores the paper library, metadata, attachments, notes, collections, tags, and citation keys. The thesis workflow stores the evidence decisions in `docs/thesis/`: which section needs the paper, which claim it supports, how strong the support is, whether metadata was verified, and whether the citation is ready for writing.

## Source Of Truth

| Layer | Source | Role |
|---|---|---|
| Literature library | Zotero Desktop | paper metadata, PDF attachments, notes, collections, tags |
| Library inventory snapshot | `zotero-literature-hub.md` / `zotero-collection-coverage.md` | local index of collection/tag coverage |
| Screening loop | `zotero-screening-loop.md` | A/B/C/D intake, keep/drop decisions, Zotero writeback queue |
| Section matching | `section-citation-map.md` | `SEC-*` / `SEG-*` citation candidates and support grade |
| Citation provenance | `citation-provenance.md` | formal `CIT-*` records, metadata/support verification, export status |
| Final bibliography | `references.bib` or chosen export path | writing/export artifact generated from verified Zotero-backed citations |

## Recommended Zotero Collections

| Collection / Tag | Use |
|---|---|
| `thesis/01_seed_papers` | seed papers that define the field or method |
| `thesis/02_background` | background and related-work context |
| `thesis/03_methods` | method papers and architectural references |
| `thesis/04_baselines` | baselines, benchmark methods, competitor models |
| `thesis/05_datasets` | dataset papers and data source references |
| `thesis/06_experiments` | papers used to explain results or failure modes |
| `thesis/07_writing_citations` | papers ready to cite in thesis text |
| `thesis/08_defense` | high-signal references useful for defense questions |
| `thesis/99_excluded` | excluded or duplicate papers kept for auditability |

## Recommended Tags

| Tag | Meaning |
|---|---|
| `status:unread` | added but not read |
| `status:skimmed` | skimmed enough for rough triage |
| `status:read` | read and summarized |
| `status:verified` | metadata and support were verified |
| `support:strong` | can support a core claim or paragraph |
| `support:partial` | supports part of a claim, needs caveat |
| `support:background` | context only, not strong evidence |
| `support:contradictory` | useful as limitation or contrast |
| `use:introduction` | likely for introduction / background |
| `use:method` | likely for methods |
| `use:experiment` | likely for experiment analysis |
| `use:discussion` | likely for discussion / limitations |
| `use:defense` | useful for defense questions |

## Section Mapping Rule

| Thesis ID | Zotero Linkage Rule |
|---|---|
| `SEC-*` | every citation-heavy section should point to one or more Zotero collections/tags |
| `SEG-*` | every citation-worthy paragraph should have candidate papers and support grades |
| `CLM-*` | a literature-backed claim must link to `CIT-*` or a verified `SEG-*` citation row |
| `CIT-*` | each formal citation should include Zotero status, identifier, support status, and export status |
| `ZCOL-*` | Zotero collection coverage records only describe coverage; they do not replace `CIT-*` |
| `ZREV-*` | screening/review events only describe selection process; they do not replace formal citations |

## Operating Loop

1. Discover papers with Semantic Scholar, Web, Scite, Zotero search, PubMed/arXiv, or advisor recommendations.
2. Add useful candidates to Zotero and assign collection/tag.
3. Record intake decision in `zotero-screening-loop.md`.
4. Snapshot or update library coverage with `sync_zotero_inventory.py` and `audit_zotero_coverage.py`.
5. Promote section candidates into `section-citation-map.md`.
6. Promote formal citations into `citation-provenance.md`.
7. Export `references.bib` only from verified or writing-ready citations.
8. Run final audit before DOCX/PDF/PPTX production.

## Dashboard Expectations

The Dashboard literature tab should answer:

- Is Zotero reachable?
- How many citation rows are still `not_added`?
- Which sections lack Zotero-backed verified citations?
- Which Zotero collections are under-covered?
- Is the bibliography export stale or incomplete?

## Promotion Rules

| Rule | Meaning |
|---|---|
| Zotero item exists | useful but not enough for citation |
| Zotero item + identifier | metadata is easier to verify |
| Zotero item + `section-citation-map.md` row | paper is assigned to a thesis section or paragraph |
| Zotero item + `citation-provenance.md` row | paper can become formal citation evidence |
| Zotero item + verified support + export status | paper is ready for writing or final bibliography |
