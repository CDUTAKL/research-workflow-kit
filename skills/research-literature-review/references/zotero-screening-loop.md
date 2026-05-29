# Zotero Screening Loop

This reference adapts useful ideas from `Chip-G0202/zotero-med-pipeline` into the local thesis literature workflow.

## Purpose

Use a light, human-supervised screening loop when a project needs recurring literature intake, Zotero organization, and feedback learning.

Do not turn the thesis workflow into a black-box paper harvester. The output must still be mapped to sections, claims, and source-grounded reading evidence.

## Generalized Loop

```text
candidate sources
-> merge and dedupe
-> A/B/C/D screening
-> Zotero writeback queue
-> spreadsheet review
-> feedback learning
-> section citation map / deep research packets
```

## Candidate Sources

Use any source that is appropriate for the field:

- Semantic Scholar
- Zotero local library
- Scite
- arXiv / PubMed / publisher pages
- Web search
- RSS feeds when stable and useful

Do not inherit the medical-only PubMed/PMC restriction unless the current project is medical.

## Labels

| Label | Meaning | Thesis Action |
|---|---|---|
| A-core | directly useful for the thesis topic, method, dataset, metric, or main claim | read and map to `SEC-*`, `SEG-*`, or `CLM-*` |
| B-section | useful for a specific chapter/subsection | place in section packet |
| C-background | broad context or backup citation | keep as background candidate |
| D-exclude | not relevant or not reliable | keep exclusion reason, do not cite |

## Feedback Learning

Feedback can come from:

- spreadsheet review rows
- advisor notes
- Zotero notes/tags
- manual keep/drop/upgrade/downgrade decisions

Keep three layers separate:

1. feedback evidence: what the user said about one item
2. preference cluster: repeated signals about a topic/method/paper type
3. screening rule: stable rule used for future filtering

A single feedback row is not enough to create a stable rule. Conflicting evidence should become `ambiguous`.

## Zotero Writeback

Zotero is a library and review convenience layer. It does not replace:

- `literature-matrix.md`
- `section-citation-map.md`
- source-grounded readers
- `claim-evidence-map.md`

Suggested tags:

- `thesis:A-core`
- `thesis:B-section`
- `thesis:C-background`
- `thesis:D-exclude`
- `SEC-INTRO-001`
- `CLM-001`

## Records

Use:

- `docs/thesis/zotero-screening-loop.md`
- `docs/thesis/literature-matrix.md`
- `docs/thesis/deep-research-tasks.md`
- `docs/thesis/section-research-packets/`
- `docs/thesis/section-citation-map.md`

## Guardrails

- Never fabricate metadata or citations.
- Do not cite papers before metadata and relevance checks pass.
- Do not use semantic neighbors as pseudo-labeled feedback.
- Do not broadly exclude a whole topic from one negative row.
- Keep PDF acquisition manual or legally sourced.
- Export spreadsheets are review aids; Markdown records remain source of truth.
