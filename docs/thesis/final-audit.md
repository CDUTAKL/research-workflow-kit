# Final Audit

## Update Rules

- Use this file before submission, defense, export, or major supervisor review.
- Record issues by priority and close them only after checking the manuscript or source file.
- Link each serious issue to the affected claim, section, figure, table, citation, or experiment.
- Stages 11-12 are intended to be finished on the user's laptop; record the laptop artifact path or version when final production moves off the Mac research console.

## Priority Legend

| Priority | Meaning |
|---|---|
| P0 | Blocks submission or invalidates a main claim |
| P1 | Must fix before supervisor/submission review |
| P2 | Important quality issue |
| P3 | Polish or optional improvement |

## Audit Run Log

| Date | Manuscript Version | Auditor | Scope | Result |
|---|---|---|---|---|
| TBD | TBD | TBD | full/partial | pending |

## Issue Table

| Issue ID | Priority | Area | Problem | Evidence | Fix | Status |
|---|---|---|---|---|---|---|
| AUD-001 | P1 | claim/citation/figure/format | TBD | TBD | TBD | open |

## Claim Audit

| Claim ID | Manuscript Location | Evidence Source | Status | Required Fix |
|---|---|---|---|---|
| CLM-001 | TBD | experiment/literature/figure/TBD | missing | add evidence or weaken wording |

## Citation Audit

| Citation | Manuscript Location | Metadata Verified | Supports Current Sentence | Action |
|---|---|---|---|---|
| TBD | TBD | no | pending | verify_metadata |

## Data Availability Audit

| Dataset / Claim | Source Data Traceable | Access / Restriction Recorded | Hash / Manifest | Data Dictionary | Action |
|---|---|---|---|---|---|
| DATA-001 / CLM-001 | pending | pending | pending | pending | update `data-availability.md` |

## Code And Autoresearch Trace Audit

| Item | Contract / State | Evidence | Status | Action |
|---|---|---|---|---|
| EXP-001 | experiment contract | config, smoke config, output manifest, registry row | pending | run `check_experiment_contract.py` |
| Iteration 1 | verify/guard gates | `autoresearch-results.tsv`, `autoresearch-state.json` | pending | review before claim promotion |

## Figure / Table / Formula Audit

| Item | Numbering Correct | Referenced In Text | Source Traceable | Caption Safe | Action |
|---|---|---|---|---|---|
| Fig-001 | pending | pending | pending | pending | TBD |

## Export And Defense Checklist

| Check | Status | Notes |
|---|---|---|
| DOCX exports cleanly through Documents / Pages / optional Word | pending |  |
| LaTeX doctor passes before optional LaTeX compile | pending |  |
| References render correctly | pending |  |
| Section citation map covers each citation-worthy section | pending |  |
| Data availability statement and dataset restrictions are recorded | pending |  |
| Autoresearch iterations have verify/guard decisions | pending |  |
| Experiment code contracts pass for cited runs | pending |  |
| Figure and table numbering is consistent | pending |  |
| Network architecture figures have spec, vector output, and QA report | pending |  |
| Appendix and acknowledgements are complete | pending |  |
| Defense slides align with supported claims | pending |  |
| Backup evidence files are traceable | pending |  |
| Final laptop artifact paths or versions are recorded | pending |  |

## Nature-Derived Enhancement Audit

| Enhancement | Target Artifact | Evidence Stable Before Polish? | Traceability Preserved? | Status | Notes |
|---|---|---|---|---|---|
| nature-figure rules | final figures | pending | pending | planned | check core conclusion, panel hierarchy, export format |
| nature-polishing rules | final manuscript sections | pending | pending | planned | check hedging, sentence clarity, overclaim risk |
| nature-paper2ppt rules | defense or seminar PPTX | pending | pending | planned | check slide argument spine and selected evidence figures |
| nature-data rules | final data availability record | pending | pending | planned | check dataset provenance, access restrictions, hashes, data dictionary |
| codex-autoresearch / ARIS loop rules | experiment iteration log | pending | pending | planned | check resume state, verify gate, guard gate, and human decision |
