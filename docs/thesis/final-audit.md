# Final Audit

## Update Rules

- Use this file before submission, defense, export, or major supervisor review.
- Record issues by priority and close them only after checking the manuscript or source file.
- Link each serious issue to the affected claim, section, figure, table, citation, or experiment.
- Stage 11 starts on the Mac: complete draft DOCX/PDF/PPTX artifacts, check evidence/citations, and prepare the handoff manifest/package.
- Stage 12 finishes on the user's laptop: verify the handoff package, finalize document layout/export, finish defense materials, and record the laptop artifact path/version.
- Apply `evidence-promotion-policy.md` before promoting any `SEC-*`, `CLM-*`, `EXP-*`, `DATA-*`, or `FIG-*` item to final evidence.
- Apply `id-lifecycle-policy.md` before final writing so deprecated or superseded IDs do not leak into the thesis.
- Use `final-artifact-manifest.md` as the Mac-to-laptop handoff contract.
- Run `scripts/research_workflow_doctor.py --write-dashboard` before advisor or final audit when the project console exists.
- Check `plugin-gate-policy.md` and `plugin-review-log.md` when Codex Security, Build Web Apps, Data Analytics, Product Design, or CodeRabbit gates were recommended.
- If the Dashboard, evidence graph, or result charts will be shown to an advisor, apply Build Web Data Visualization checks for truthful chart choice, readable labels, accessible contrast, uncertainty/missingness visibility, and desktop/mobile legibility.

## Priority Legend

| Priority | Meaning |
|---|---|
| P0 | Blocks submission or invalidates a main claim |
| P1 | Must fix before supervisor/submission review |
| P2 | Important quality issue |
| P3 | Polish or optional improvement |

## Audit Run Log

| Date | Manuscript Version | Audit Tier | Auditor | Scope | Result |
|---|---|---|---|---|---|
| TBD | TBD | quick/advisor/final | TBD | full/partial | pending |

## Audit Tiers

| Tier | When To Run | Must Check | Output |
|---|---|---|---|
| quick | daily, after new experiment output, before continuing a branch | changed `CLM-*`, new `EXP-*`, new `DATA-*`, new `FIG-*`, broken citations, obvious overclaiming | short issue list and next action |
| advisor | before supervisor meeting, milestone review, or chapter handoff | claim map, section citation coverage, figures/tables, data traceability, code contracts, 4060 snapshots, final artifact copied/verified status, limitations | advisor-ready risk list |
| final | before DOCX/PDF release, defense, or submission | all quick/advisor checks plus formatting, bibliography, final data availability, defense slides, laptop artifact paths, artifact checksums, ID lifecycle conflicts | final go/no-go decision |

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
| FIG-001 | pending | pending | pending | pending | TBD |

## Quick Audit Checklist

| Check | Status | Notes |
|---|---|---|
| Changed `CLM-*` items still match evidence scope | pending |  |
| New `EXP-*` outputs have registry rows and status | pending |  |
| New `DATA-*` references have path/access/hash or known gap | pending |  |
| New `FIG-*` items have source data or source-of-truth notes | pending |  |
| New structured diagrams use Mac draw.io or Windows Visio route and record source-of-truth notes | pending |  |
| New citations are at least metadata candidates, not invented references | pending |  |
| New Zotero screening candidates are not cited before metadata/relevance checks | pending |  |
| New core citations have `citation-provenance.md` entries before final prose use | pending |  |
| New evidence-critical materials have `material-passport.md` entries | pending |  |
| Dashboard flow-editor writes are reviewed in `workflow-edit-log.md` | pending |  |
| Dashboard/evidence graph visual issues do not hide P0/P1 blockers | pending |  |
| Required plugin gates are recorded or explicitly not applicable | pending |  |

## Advisor Audit Checklist

| Check | Status | Notes |
|---|---|---|
| Each important `SEC-*` has section citation coverage | pending |  |
| Main `CLM-*` items are supported or deliberately weakened | pending |  |
| Reviewed `EXP-*` runs pass contract checks | pending |  |
| `remote_desktop_4060` formal runs include environment snapshot and remote artifact URI/hash/status | pending |  |
| Figures/tables use `FIG-*` IDs and have safe captions | pending |  |
| `diagram-replica-tasks.md` records draw.io / Visio outputs for structured diagrams | pending |  |
| A/B/C/D literature screening labels have section handoff or exclusion reasons | pending |  |
| Zotero collections cover target sections in `zotero-collection-coverage.md` | pending |  |
| Formal baseline comparisons are recorded in `benchmark-report-schema.md` | pending |  |
| Data restrictions and availability language are advisor-reviewable | pending |  |
| Advisor-facing charts and evidence graph are readable and do not hide uncertainty | pending |  |
| Data Analytics / Product Design review notes exist when formal results or visuals are advisor-facing | pending |  |
| DOCX/PDF/PPTX handoff rows in `final-artifact-manifest.md` are copied or verified | pending |  |
| Important IDs have valid lifecycle status in `id-lifecycle-policy.md` | pending |  |

## Final Audit Checklist

| Check | Status | Notes |
|---|---|---|
| No main claim remains weak without caveat | pending |  |
| Every final figure/table has `FIG-*`, source trace, and export path | pending |  |
| Every data-backed claim has a `DATA-*` trace and availability status | pending |  |
| Every cited formal GPU result has an environment snapshot | pending |  |
| Bibliography, citation rendering, and section citation map agree | pending |  |
| Citation provenance records include metadata/support verification for core citations | pending |  |
| Zotero screening feedback does not create unsupported stable screening rules | pending |  |
| Material passport and benchmark report schema agree with promoted claims | pending |  |
| `workflow-dashboard.md` and evidence graph are refreshed | pending |  |
| Dashboard and evidence graph pass visual readability and accessibility checks | pending |  |
| `plugin_gate_advisor.py --audit-only` passes and required plugin gates are closed | pending |  |
| Defense slides only use promoted evidence | pending |  |
| All final artifacts are verified on the laptop with checksums | pending |  |
| Deprecated or superseded IDs are absent from final prose, figures, and slides | pending |  |

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
| Remote 4060 formal runs have environment snapshots plus verified remote artifact URI/hash/status | pending |  |
| Figure and table numbering is consistent | pending |  |
| Network architecture figures have draw.io or Visio redraw record, spec, vector output, and QA report | pending |  |
| Appendix and acknowledgements are complete | pending |  |
| Defense slides align with supported claims | pending |  |
| Backup evidence files are traceable | pending |  |
| Final laptop artifact paths or versions are recorded | pending |  |
| `final-artifact-manifest.md` passes `scripts/audit_final_artifacts.py --tier final` | pending |  |
| `id-lifecycle-policy.md` passes `scripts/audit_id_lifecycle.py --warn-only` without final blockers | pending |  |

## Nature-Derived Enhancement Audit

| Enhancement | Target Artifact | Evidence Stable Before Polish? | Traceability Preserved? | Status | Notes |
|---|---|---|---|---|---|
| nature-figure rules | final figures | pending | pending | planned | check core conclusion, panel hierarchy, export format |
| nature-polishing rules | final manuscript sections | pending | pending | planned | check hedging, sentence clarity, overclaim risk |
| nature-paper2ppt rules | defense or seminar PPTX | pending | pending | planned | check slide argument spine and selected evidence figures |
| nature-data rules | final data availability record | pending | pending | planned | check dataset provenance, access restrictions, hashes, data dictionary |
| codex-autoresearch / ARIS loop rules | experiment iteration log | pending | pending | planned | check resume state, verify gate, guard gate, and human decision |
