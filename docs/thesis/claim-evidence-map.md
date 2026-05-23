# Claim Evidence Map

## Update Rules

- Every thesis claim must map to at least one experiment, figure/table, literature source, or explicit limitation.
- Do not promote a claim to the manuscript until its status is `supported` or the wording is weakened.
- Use this file as the bridge between experiment results, literature review, figures, and writing.
- Use `CLM-*` for thesis claims and `EXP-*` / `EXP-AUTO-*` for experiment evidence references.
- Use `SEC-*`, `DATA-*`, and `FIG-*` links from `evidence-promotion-policy.md` before marking a claim as `supported`.
- Claim audits read `Experiment Evidence` from this file and check it against `experiment-registry.md`.
- Literature-backed claims should connect to `section-citation-map.md`.
- Data-backed claims should connect to `data-availability.md`.

## Claim Status Legend

| Status | Meaning |
|---|---|
| `supported` | Direct evidence supports the claim under stated scope |
| `weak` | Directional evidence exists but needs caution or more experiments |
| `unsupported` | Current evidence does not support the claim |
| `missing` | Claim is important but evidence has not been produced |

## Claim Table

| Claim ID | Claim Draft | Status | Experiment Evidence | Figure/Table | Literature Evidence | Caveat | Next Action |
|---|---|---|---|---|---|---|---|
| CLM-001 | TBD | missing | EXP-001/TBD | FIG-001/TBD | Paper/TBD | TBD | add evidence or weaken claim |

## Result-To-Claim Review

| Result Source | Metric / Finding | Candidate Claim | Supported Scope | Do Not Claim | Review Status |
|---|---|---|---|---|---|
| `result-scan-table.csv` | TBD | TBD | TBD | TBD | pending |

## Citation Support Checks

| Claim ID | Citation | What The Citation Must Support | Scite / Direct Reading Status | Decision |
|---|---|---|---|---|
| CLM-001 | TBD | TBD | pending | do_not_cite_yet |

## Data Support Checks

| Claim ID | Dataset / Artifact | Data Availability Status | Trace Decision |
|---|---|---|---|
| CLM-001 | DATA-001/TBD | pending | do_not_use_yet |

## Section Citation Links

| Claim ID | Section ID | Segment IDs | Citation Coverage | Next Action |
|---|---|---|---|---|
| CLM-001 | SEC-INTRO-001/TBD | SEG-001/TBD | missing | update `section-citation-map.md` |
