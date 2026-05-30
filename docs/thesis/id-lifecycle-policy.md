# ID Lifecycle Policy

## Purpose

Use this file to keep the research workflow ID system understandable as the project grows. IDs are not just labels; they are the links between chapters, paragraphs, claims, experiments, data, citations, figures, materials, benchmarks, Zotero screening, and final artifacts.

## ID Types

| Prefix | Meaning | Primary File |
|---|---|---|
| `SEC-*` | Thesis chapter or section | `section-citation-map.md`, `writing-outline.md` |
| `SEG-*` | Paragraph-level argument or citation unit | `section-citation-map.md` |
| `CLM-*` | Thesis claim or conclusion statement | `claim-evidence-map.md` |
| `EXP-*` | Experiment run or reviewed experiment record | `experiment-registry.md` |
| `DATA-*` | Dataset, processed data, or result data | `data-availability.md` |
| `FIG-*` | Figure, table, model architecture diagram, or workflow diagram | `figure-plan.md`, `diagram-replica-tasks.md` |
| `MAT-*` | Material passport record | `material-passport.md` |
| `CIT-*` | Citation provenance record | `citation-provenance.md` |
| `BMK-*` | Baseline or benchmark comparison record | `benchmark-report-schema.md` |
| `ZCOL-*` | Zotero collection coverage record | `zotero-collection-coverage.md` |
| `DRT-*` | Deep research task packet | `deep-research-tasks.md` |
| `ZREV-*` | Zotero screening review item | `zotero-screening-loop.md` |

## Lifecycle Status

| Status | Meaning | Promotion Rule |
|---|---|---|
| `draft` | Newly created and not verified | May guide work, but must not support final claims |
| `candidate` | Has initial content but incomplete evidence | May appear in planning tables |
| `verified` | Source, path, data, citation, or experiment record has been checked | May support advisor review |
| `promoted` | Safe to use in thesis text, final figures, or defense materials | Must pass evidence promotion and audit checks |
| `deprecated` | Preserved for history but no longer used | Must not be newly cited or promoted |
| `superseded` | Replaced by another ID | Must record the replacement ID |

## Naming Relationship Rules

| Rule | Required Relationship |
|---|---|
| Section structure | `SEC-*` can contain multiple `SEG-*` items |
| Paragraph-to-claim | `SEG-*` can support one or more `CLM-*` items |
| Claim evidence | `CLM-*` must link to at least one `EXP-*`, `DATA-*`, `CIT-*`, or `FIG-*` before promotion |
| Experiment trace | `EXP-*` must link to `DATA-*` or an output path before review |
| Figure trace | `FIG-*` must link to a `CLM-*` and source data, source experiment, or source-of-truth diagram plan |
| Material passport | `MAT-*` can reference `EXP-*`, `DATA-*`, `FIG-*`, `CIT-*`, `SEC-*`, or `CLM-*` |
| Benchmark comparison | `BMK-*` must link baseline and new experiment records |
| Zotero screening | `ZCOL-*` and `ZREV-*` are screening process records; they do not replace verified `CIT-*` evidence |

## Current ID Registry

Use this table for important IDs whose lifecycle state needs explicit tracking. Routine references can remain in their primary files, but promoted or deprecated items should be recorded here.

| ID | Type | Status | Primary File | Related IDs | Replacement ID | Owner | Updated On | Notes |
|---|---|---|---|---|---|---|---|---|
| CLM-001 | claim | draft | `claim-evidence-map.md` | EXP-001/TBD; DATA-001/TBD; FIG-001/TBD; CIT-001/TBD |  | user/Codex | TBD | template claim |

## Audit Rules

- Unknown ID prefixes should be fixed or explicitly documented before advisor review.
- Auxiliary planning/export labels such as `TASK-*`, `XLS-*`, `GIT-*`, `FB-*`, `IDEA-*`, `LIT-*`, and `BATCH-*` are not evidence lifecycle IDs unless promoted into one of the controlled prefixes above.
- Deprecated IDs must not be used in final thesis text, figures, or defense slides.
- Superseded IDs must name the replacement ID.
- Promoted `CLM-*` items must be traceable through evidence records and final artifacts.
- Final audit should run `scripts/audit_id_lifecycle.py --warn-only` before export.
