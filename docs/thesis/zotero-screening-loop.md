# Zotero Screening Loop

## Purpose

Use this file for a human-supervised literature screening loop inspired by `zotero-med-pipeline`, adapted from a medical-only RSS/PubMed workflow into a general thesis literature workflow.

The loop is optional and lightweight. It should improve literature intake, Zotero organization, and feedback learning without replacing source-grounded reading or `section-citation-map.md`.

## Loop

```text
candidate sources
-> merge and dedupe
-> A/B/C/D screening
-> Zotero queue/writeback
-> title/abstract translation notes when useful
-> spreadsheet review
-> feedback learning
-> section citation map / deep research packets
```

## Screening Labels

| Label | Meaning | Action |
|---|---|---|
| A-core | directly supports the thesis topic, method, dataset, metric, or main claim | read, add to Zotero, map to `SEC-*` / `SEG-*` / `CLM-*` |
| B-section | useful for one chapter or subsection, but not a central paper | add to section packet or related work group |
| C-background | broad field context, survey, or backup citation | keep as candidate/background |
| D-exclude | not relevant or not trustworthy for this thesis | keep exclusion reason; do not cite |

## Candidate Intake

| Item ID | Source | Search Query / Feed | Title | Identifier | Date | Initial Label | Dedupe Key | Status | Notes |
|---|---|---|---|---|---|---|---|---|---|
| LIT-CAND-001 | Semantic Scholar / Zotero / Scite / Web / PubMed / RSS / TBD | TBD | TBD | DOI/arXiv/S2/PMID/TBD | TBD | A-core/B-section/C-background/D-exclude/TBD | DOI/title/TBD | candidate |  |

## Zotero Writeback Queue

| Item ID | Title | Identifier | Target Collection / Tag | Label | Zotero Status | BibTeX Status | PDF Status | Next Action |
|---|---|---|---|---|---|---|---|---|
| LIT-CAND-001 | TBD | DOI/arXiv/S2/PMID/TBD | thesis/YYYY-MM-DD/TBD | A-core/TBD | not_added / in_zotero / duplicate / blocked | missing / candidate / final | missing / attached / manual | add_to_zotero |

## Feedback Learning

| Feedback ID | Source File | Item ID | Previous Label | User Feedback | Evidence Type | Preference Update | Status |
|---|---|---|---|---|---|---|---|
| FB-001 | spreadsheet / advisor note / Zotero note / TBD | LIT-CAND-001 | B-section/TBD | keep / drop / upgrade / downgrade / note | positive / negative / ambiguous / TBD | tentative / stable / needs_more_feedback / ambiguous | pending |

## Section Handoff

| Item ID | Label | Section ID | Segment ID | Candidate Use | Support Status | Next Action |
|---|---|---|---|---|---|---|
| LIT-CAND-001 | A-core/TBD | SEC-INTRO-001/TBD | SEG-001/TBD | background / method / dataset / metric / limitation / contrast | metadata_only / support_checked / directly_read / TBD | update `section-citation-map.md` |

## Guardrails

- Do not automatically cite items just because they are A/B labels.
- Do not treat semantic neighbors as feedback-labeled papers.
- Do not broadly exclude a topic from one negative feedback row.
- Keep feedback evidence, preference clusters, and stable screening rules separate.
- PDF acquisition remains manual unless the user explicitly provides a legal source.
- Zotero and spreadsheet exports are convenience layers; thesis evidence remains in `docs/thesis/`.
