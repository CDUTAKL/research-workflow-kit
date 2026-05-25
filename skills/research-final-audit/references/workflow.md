# Final Audit Workflow

## Audit Tier Selection

Use `docs/thesis/evidence-promotion-policy.md` to choose the tier before auditing.

| Tier | Use When | Minimum Output |
|---|---|---|
| `quick` | daily, after a new run, figure, citation, or claim change | short issue list and next action |
| `advisor` | before supervisor review or milestone meetings | advisor-ready risk list across claims, citations, data, figures, and code |
| `final` | before DOCX/PDF release, defense, or submission | full go/no-go decision with formatting and defense readiness |

For all tiers, use manuscript-facing IDs: `SEC-*`, `CLM-*`, `EXP-*`, `DATA-*`, and `FIG-*`. `SEG-*` is a section-level citation unit, not a replacement for a claim ID.

## Claim Audit

| Manuscript claim | Location | Evidence source | Status | Required fix |
|---|---|---|---|---|
| Claim text | section/page | result/citation/figure | supported/weak/unsupported | action |

Status rules:

- `Supported`: direct result or citation supports the exact claim.
- `Weak`: evidence is related but claim wording is too broad.
- `Unsupported`: no provided evidence supports it.

Common risky words:

- robust
- significant
- state of the art
- generalizes
- proves
- always
- substantially
- first
- novel

Use these only when evidence and citations justify them.

## Paper-to-Evidence Audit

Use this when a manuscript, thesis, table, caption, or draft reports concrete numbers or comparisons. Verify the paper against raw result files, not against summaries.

| Paper claim | Location | Raw evidence | Raw value | Paper value | Status | Required fix |
|---|---|---|---:|---:|---|---|
| claim text | section/table/caption | file/key/path | value | value | exact/rounding_ok/mismatch | action |

Status rules:

- `exact`: paper value exactly matches raw evidence.
- `rounding_ok`: paper value is standard rounding to displayed precision.
- `mismatch`: paper value, comparison, or scope wording does not match raw evidence.
- `untraceable`: no raw file/key supports the claim.

Specific failure modes:

| Failure mode | What to check | Fix |
|---|---|---|
| Number inflation | paper value vs raw value | replace with raw value or valid rounding |
| Best-seed cherry-pick | per-seed results vs reported summary | label as best seed or report mean/variance |
| Config mismatch | compared methods use same split/data/preprocessing/budget | remove comparison or align protocol |
| Aggregation mismatch | claimed seed/run count vs actual files | correct count and summary statistic |
| Delta error | absolute and relative improvement arithmetic | recompute and correct wording |
| Caption-table mismatch | caption claim vs figure/table content | rewrite caption or fix visual |
| Scope overclaim | wording vs number of datasets/seeds/settings | narrow wording or add evidence |

Quantitative extraction checklist:

- percentages, decimals, absolute values, and ranks.
- "improves by", "reduces by", "relative improvement", and "average over".
- best/mean/median wording.
- number of seeds, datasets, samples, classes, folds, or experiments.
- figure captions and table notes.
- qualitative scope phrases such as consistently, robustly, substantially, and across all.

## Citation Audit

| Citation | Location | Metadata status | Supports sentence? | Issue |
|---|---|---|---|---|
| key/title | section | verified/unverified | yes/no/partial | fix |

Check:

- title, authors, year, venue, DOI/arXiv/URL.
- cited paper is primary source where needed.
- citation supports the exact sentence.
- reference style is consistent.
- every in-text citation appears in references and every reference is cited if required.

## Figure and Table Evidence Audit

| Visual | Location | Source data/script | Caption claim | Evidence status | Fix |
|---|---|---|---|---|---|
| Figure/Table | section | path | caption claim | supported/weak/mismatch | action |

Check:

- the visual is cited in the text.
- caption describes only what the visual actually shows.
- table bolding or ranking matches numeric values.
- axes, legends, units, and class labels are correct.
- exported figure matches the latest data, not an obsolete render.
- uncertainty shown in the visual matches the text.

## Visual Reference And Redraw Audit

Use this for model architecture diagrams, method overview figures, workflow diagrams, and other schematic figures that used Image Gen Skill or another reference image.

| Visual | Reference image | Reference accuracy | Source of truth | Formal redraw tool | Metadata check | Decision |
|---|---|---|---|---|---|---|
| Figure | `figures/references/...` | pass/revise/failed | `.network.json`/model.py/data/source note | draw.io/Python/PPTX/SVG/TikZ/Figma/BioRender | pass/pending/revise | accept/revise/block |

Check:

- Image Gen or other reference images are not inserted directly as final thesis/manuscript figures unless explicitly approved.
- The reference image was checked for wrong labels, hallucinated modules, incorrect arrows, inconsistent tensor shapes, and unsupported numeric values.
- The final formal figure was redrawn from source-of-truth records, not copied from the generated bitmap.
- Structured model, method, workflow, and architecture diagrams used draw.io as the default formal redraw path unless a reason for another tool is recorded.
- The final export path is recorded in `figure-plan.md` or `network-architecture-figures.md`.
- PNG/PDF/SVG/PPTX outputs were checked for unwanted Image Gen C2PA/OpenAI provenance metadata when the image was derived from a generated reference.
- The caption describes the real model, method, or data source, not the Image Gen prompt.

## Formatting Audit

| Item | Check |
|---|---|
| Abstract | word limit, problem-method-result-contribution |
| Keywords | required count and style |
| Headings | match school/venue template |
| Figures | numbered, captioned, cited in text |
| Tables | numbered, captioned, cited in text |
| Equations | numbered if referenced, variables defined |
| References | style, ordering, completeness |
| Appendix | referenced and not hiding essential evidence |
| Acknowledgments | funding, advisor, conflict statements if needed |

## Tool-Layer Audit

Use this when `docs/thesis/` contains tool integration records.

| Record | Check | Risk | Route |
|---|---|---|---|
| `task-board-sync.md` | important thesis tasks are not lost in Notion-only state | missed deadlines or unsynced advisor feedback | Notion or `$research-workflow-orchestrator` |
| `git-version-log.md` | formal experiment results have branch/commit or dirty-state record | result cannot be tied to code version | GitHub or `$research-experiment-engineering` |
| `spreadsheet-exports.md` | spreadsheets are reviewed and not stale against source files | manuscript table uses stale values | Spreadsheets or `$research-results-analysis` |
| `defense-prep.md` | slide claims trace to audited claims and figures | defense overclaims or lacks backup evidence | Presentations or `$research-paper-figures` |
| Nature-derived figure/polish/PPT records | high-standard figure, prose, or slide checks were applied only after evidence was stable | style hides unsupported science | `$research-paper-figures`, `$research-paper-writing`, Presentations |
| `data-availability.md` | data-backed claims have dataset provenance, access status, hash/manifest, and data dictionary | final thesis cannot defend where data came from | `$research-data-availability` |
| `section-citation-map.md` | citation-heavy sections have verified candidate citations and support grades | related work or background has weak/unsupported citations | `$research-literature-review`, `$semanticscholar-skill`, Zotero, Scite |
| `workflow-dashboard.md` | current stage, blockers, missing evidence, and audit tier are visible | project state is hard to understand or stale | `$research-workflow-orchestrator` |
| `evidence-graph.json` / `evidence-graph.mmd` | core claim relationships can be inspected as a graph | hidden missing links across claim/data/figure/experiment records | `$research-workflow-orchestrator` |
| `autoresearch-results.tsv` / `autoresearch-state.json` | iterative experiments have verify/guard decisions and resumable state | method iteration cannot be audited | `$research-autoresearch-loop` |
| experiment contract records | cited runs have config, smoke config, registry row, output manifest, and environment snapshot for formal GPU runs | result cannot be reproduced or tied to code | `$research-code-quality`, `$research-experiment-engineering` |

Tool-layer rules:

- Notion is task management, not evidence storage.
- GitHub records do not replace local reproducibility records.
- Spreadsheets are review/export artifacts; source data must remain traceable.
- Presentation slides must not introduce claims that are absent from `claim-evidence-map.md`.
- Nature-style polish must not convert weak evidence into stronger wording.

## Nature-Derived Final Checks

Use these checks when a paper, thesis section, figure package, or PPT deck has been polished with nature-skills-derived rules.

| Artifact | Check | Route |
|---|---|---|
| Figure package | core conclusion, panel evidence, non-redundancy, source-data traceability, editable vector/raster rationale | `$research-paper-figures` |
| Final figure package | `figure-audit-standard.md` status, figure claim, panel roles, source data, script/notebook, export status, and revision items | `$research-paper-figures` |
| Network architecture diagram | draw.io redraw record, `.network.json` spec, layout/connections/panels/audit fields, SVG/PDF/PNG outputs, PPTX mode, QA report, topology-only caption | `$research-paper-figures` |
| Source-grounded paper reader | `paper.md`, `source_map.json`, key blocks, figure/table notes, and direct-reading evidence for important claims | `$research-literature-review` and `$pdf` |
| Citation batch | segment IDs, candidate references, support grades, dedupe keys, Zotero/Scite/metadata status | `$research-literature-review`, `$semanticscholar-skill`, Zotero, Scite |
| Data availability | dataset IDs, source/processed data, access restrictions, hashes, data dictionary, and final statement | `$research-data-availability` |
| Autoresearch loop | iteration TSV, state JSON, verify gate, guard gate, and human decision | `$research-autoresearch-loop` |
| Code contract | config, smoke config, registry row, output manifest, metrics, logs, remote 4060 handoff | `$research-code-quality` |
| Environment snapshot | `outputs/EXP-*/environment.txt`, CUDA/PyTorch/Python/GPU/git state, fixed desktop profile when known | `$research-code-quality`, `$research-experiment-engineering` |
| Manuscript prose | section job, hourglass flow, hedging, sentence clarity, citation placement, overclaim risk | `$research-paper-writing` |
| PPTX deck | one argument spine, selected figures as evidence, Chinese slide titles as claims, speaker notes, backup evidence paths | Presentations and `$research-final-audit` |

Do not treat polished figures or slides as evidence sources. They must trace back to raw results, literature, and `docs/thesis/`.
Do not treat candidate citation batches as final references. Important citations need verified metadata plus Zotero, Scite, or source-map-backed direct reading status.

## Compile/Export Advice

- For LaTeX: run the LaTeX doctor first, then use the LaTeX compile skill or local project compile command only when a TeX runtime is available; inspect warnings about missing refs/citations.
- For DOCX: use the Documents plugin (`documents:documents` in Codex plugin contexts) for DOCX inspection/editing and inspect generated PDF after export, not only the DOCX. Pages or Microsoft Word are optional local review tools.
- For PDF: use `$pdf` when rendering, extraction, or layout review matters.
- For figures: verify final PDF/Word rendering, not only source images.
- For bibliography: check both source `.bib` and rendered references.

## Production Handoff

Use this sequence for final documents:

```text
$research-final-audit for scientific and submission risk
  -> Documents plugin for DOCX template, layout, and visual rendering checks
  -> $pdf for final PDF rendering and extraction checks
-> LaTeX doctor, then LaTeX compile only when a TeX runtime is available
```

## Audit-to-Revision Loop

Audit output must route each issue to the next corrective skill.

| Issue type | Route |
|---|---|
| raw result mismatch | `$research-results-analysis` |
| unsupported or exaggerated claim | `$research-paper-writing` and `$research-results-analysis` |
| unclear or misleading figure | `$research-paper-figures` |
| citation missing or unsupported | `$research-literature-review`, `$semanticscholar-skill`, Scite, or Zotero |
| section citation coverage gap | `$research-literature-review` |
| missing data availability | `$research-data-availability` |
| missing code contract | `$research-code-quality` |
| missing autoresearch verify/guard decision | `$research-autoresearch-loop` |
| missing task/progress sync | Notion or `$research-workflow-orchestrator` |
| missing code version trace | GitHub or `$research-experiment-engineering` |
| stale spreadsheet export | Spreadsheets or `$research-results-analysis` |
| DOCX layout problem | Documents plugin |
| PDF rendering problem | `$pdf` |
| LaTeX compile/citation warning | LaTeX doctor, then LaTeX compile |
| defense slide gap | Presentations or `$research-paper-figures` |
| paper-to-PPT structure gap | Presentations, `nature-paper2ppt` reference rules, or `$research-final-audit` |

Revision loop rules:

- P0 issues block submission.
- P1 issues should be fixed before advisor review, blind review, or defense.
- P2 issues can be batched into polishing.
- P3 issues are optional unless required by a template.
- If a result changes, rerun claim audit and figure/table checks before final submission.

## Iterative Paper Loop

Final audit is not only a last-pass checklist. It can send the work backward:

```text
audit failure -> analysis or literature or figure repair -> writing revision -> final audit again
```

Use this loop when:

- a main claim is unsupported.
- a reviewer-style objection exposes a missing baseline.
- a citation does not support the sentence.
- a figure caption overstates the result.
- formatting changes alter figure/table numbering or references.

## Defense Checklist

| Slide topic | Purpose |
|---|---|
| Background | Why the problem matters |
| Challenge | What is technically hard |
| Method | What was built |
| Innovation | What is new or improved |
| Experiment design | How claims were tested |
| Results | What evidence supports the thesis |
| Limitations | What remains unsolved |
| Q&A prep | Likely committee questions |

## Final Priority Scale

- P0: submission blocker, incorrect claim, fake/unverified citation, missing required section.
- P1: high-risk reviewer/committee issue, weak evidence, unclear method, broken figure/table reference.
- P2: clarity, tone, formatting, caption, minor consistency.
- P3: optional polish.

## Final Output Checklist

- Every quantitative claim is exact, validly rounded, or explicitly flagged.
- Every strong scope word is justified by experiment scope.
- Every figure/table caption matches the visual and source data.
- Every citation is real and supports the sentence.
- Every P0/P1 item has an assigned route and fix.
- Rendering/compilation checks are performed or explicitly marked unavailable.
