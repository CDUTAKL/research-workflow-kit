---
name: research-workflow-orchestrator
description: Use when coordinating a full research project, graduation thesis, dissertation, paper pipeline, literature-to-experiment-to-writing workflow, or when deciding which research, notebook, PDF, DOCX, citation, visualization, or audit skill to use next.
---

# Research Workflow Orchestrator

Use this skill as the entry point for a multi-stage research or thesis workflow. It coordinates specialized skills instead of replacing them.

## Core Rule

Always turn a broad research request into a staged workflow with artifacts, skill sequence, risks, and next concrete actions. Prefer real project files and evidence over generic advice.

## Skill Routing

- Planning and advisor topic intake: use `$research-paper-plan`.
- Idea discovery and early research direction: use `$research-paper-plan` with `docs/thesis/idea-discovery.md` for paper pools, idea matrices, novelty risks, and shortlists.
- Literature discovery, Zotero literature hub management, source-grounded paper reading, related work, section-level citation matching, deep research task packets, Zotero screening loops, and citation batches: use `$research-literature-review`; use `$semanticscholar-skill` for real Semantic Scholar searches when exact papers, citations, or BibTeX candidates matter; use `$pdf` when full-paper PDF reading, original/translation alignment, figure/table extraction, or source anchors matter.
- Experiment architecture, code design, `local_mac` CPU-only smoke tests, `remote_desktop_4060` primary GPU runs, `cloud_autodl` fallback training with evidence auto-save and auto-shutdown, training/evaluation scripts, config/log/output conventions, reproducibility, and mapping code runs to thesis experiments: use `$research-experiment-engineering`; use `$research-code-quality` for skeletons, contract checks, smoke configs, output manifests, 4060 handoff templates, and AutoDL fallback templates.
- Human-supervised iterative experiment improvement: use `$research-autoresearch-loop` for `autoresearch-results.tsv`, `autoresearch-state.json`, verify gates, guard gates, baseline comparison reports, and recovery decisions.
- Experiment recording and exploration: use `$jupyter-notebook`.
- Result interpretation: use `$research-results-analysis`; use Build Web Data Visualization as a chart-choice, uncertainty-display, dashboard-chart, evidence-graph, accessibility, and visual-QA guide when results need to become advisor-facing visuals.
- Figures, tables, diagrams, captions, Nature-style figure audit, and model-architecture rendering: use `$research-paper-figures`; for structured model/method/workflow diagrams, use draw.io as the default Mac formal redraw tool after Image Gen visual reference and content-accuracy checks. On Windows with Microsoft Visio, optionally use the Visio JSON-plan route inspired by `codex-visio-replica-workflow`. Use Build Web Data Visualization for complex chart selection and dashboard/evidence graph design QA.
- Drafting and revision: use `$research-paper-writing`.
- Data provenance and data availability: use `$research-data-availability` before final writing, final audit, DOCX/PDF production, and defense preparation.
- DOCX thesis/manuscript production: use the Documents plugin (`documents:documents` in Codex plugin contexts). Pages or Microsoft Word may be used locally for human review, but Word is optional.
- PDF review or final rendering checks: use `$pdf`.
- Final submission or defense checks: use `$research-final-audit`.
- Task planning and progress dashboards: use Notion when the user wants project tasks, weekly plans, or supervisor feedback synced outside the repo.
- Code versioning and GitHub work: use GitHub for repository state, issues, PRs, CI, and version traceability around major code changes or formal experiments.
- CodeRabbit: optional pre-merge AI code review for important scripts, dashboard, CI, and skill changes. Run only when authenticated, and do not treat it as a default CI dependency.
- Plugin gates: use `plugin-gate-policy.md`, `plugin-review-log.md`, and `scripts/plugin_gate_advisor.py` to recommend Codex Security, Build Web Apps, Data Analytics, Product Design, or CodeRabbit checks by stage. These gates are review aids, not evidence sources.
- Codex Security: use when stages 5-6 touch local Dashboard APIs, file-writing scripts, remote 4060 scripts, CI, open-path boundaries, or other security-sensitive code.
- Build Web Apps: use for Dashboard React/Vite implementation, interaction bugs, responsive layout, Browser/Safari checks, and frontend QA.
- Data Analytics: use in stages 7-8 for result data quality, metric diagnostics, baseline-delta, uncertainty, failed-run, and anomaly checks.
- Product Design: use in stages 9 and 12 for advisor-facing Dashboard, figure, diagram, and defense-slide readability or visual hierarchy review.
- Device workflow: treat `local_mac` as the stages 1-11 research console and main DOCX/PDF/PPTX production machine, `remote_desktop_4060` as the primary GPU execution target, `cloud_autodl` as a stronger fallback, and the Windows laptop as the stage 12 compatibility review and final submission-check machine.
- Evidence workflow: use `evidence-promotion-policy.md` and `id-lifecycle-policy.md` to keep `SEC-*`, `SEG-*`, `CLM-*`, `EXP-*`, `DATA-*`, `FIG-*`, `MAT-*`, `CIT-*`, `BMK-*`, `ZCOL-*`, `DRT-*`, and `ZREV-*` relationships consistent before final writing or defense.
- Project overview: use `workflow-dashboard.md`, `console-file-index.md`, `weekly-review.md`, the legacy-compatible `daily-workflow-entry.md`, `scripts/research_workflow_doctor.py`, `scripts/update_daily_workflow.py`, `scripts/update_weekly_review.py`, `scripts/export_evidence_graph.py`, `scripts/dashboard_control_server.py`, `scripts/edit_workflow_record.py`, and `dashboard-web/` when the user needs a one-page status view, file-layer guidance, weekly convergence, current research workspace, health check, focused evidence chain, experiment comparison, or local web dashboard with refresh/open/export/edit actions.
- Read-only dashboard publishing: Vercel may be considered later for an advisor/demo preview, but the local write API, private research data, and unpublished thesis evidence must not be deployed.
- Skill maintenance: use `scripts/audit_skills.py` when changing or installing skills, or before merging workflow changes, to catch missing references, missing scripts, and old tool assumptions.
- Engineering discipline: use Superpowers for TDD, systematic debugging, verification, and code review during implementation work.
- Spreadsheet exports: use Spreadsheets for reviewable literature, result, claim, and audit tables without replacing source records.
- Defense slides: use Presentations for PPTX creation/editing; use draw.io exports for structured diagrams; use Figma or BioRender only as optional visual refinement tools when available. Canva is optional only if explicitly available and useful.
- Image Gen Skill is used in stage 9 as the mandatory visual-reference generator for model architecture, method overview, workflow, and schematic figures when visual quality matters. Its output is checked for content accuracy and then redrawn formally; it is not treated as final manuscript evidence.
- draw.io / draw.io MCP is the default stage 9 formal redraw route for model architecture, method overview, workflow, evidence graph, and system diagrams. Export SVG/PDF/PNG for thesis use and package into PPTX for defense slides when needed.
- Windows Visio is an optional direct-use route for figure replication: reference image -> JSON plan -> `.vsdx` -> EMF/PDF/PNG -> thesis/PPTX handoff. Record it in `diagram-replica-tasks.md`; do not let Visio become the source of truth.
- Zotero literature hub is the stage 2-10 citation backbone: Zotero stores the local library, `zotero-literature-hub.md` stores the inventory/policy snapshot, `zotero-screening-loop.md` records intake decisions, `zotero-collection-coverage.md` checks collection coverage, and `citation-provenance.md` promotes formal `CIT-*` rows. Do not cite unverified candidates directly from Zotero.
- Figma can be used in stage 9 or 12 for optional diagram refinement, reusable design components, and visual system work after the draw.io/source-of-truth record and visual reference are established.
- Scite and Zotero are the default citation-verification helpers: Scite checks support/contrast/mention status, while Zotero manages local library records and citation exports. Neither replaces direct source-grounded reading for critical claims.
- Supabase database migration, Overleaf synchronization, reviewer-response workflow, and arXiv auto-submit are out of scope for the current graduation-thesis workflow.
- Nature-derived high-standard enhancements: use downloaded `nature-academic-search`, `nature-figure`, `nature-reader`, `nature-citation`, `nature-data`, `nature-writing`, `nature-polishing`, and `nature-paper2ppt` source material as reference layers. `nature-academic-search` strengthens multi-source search routing, `nature-figure` strengthens figure audit, `nature-reader` strengthens source-grounded paper reading, `nature-citation` strengthens long-text citation batching, `nature-data` strengthens data availability, `nature-writing/polishing` strengthens final prose and advisor precheck, and `nature-paper2ppt` strengthens defense slides. They do not replace the local `research-*` evidence workflow. Do not add `nature-response` for graduation-thesis-only workflows unless the user later asks for journal review response support.

## Project Console

## Project Template Initialization

Use the global template source when a project needs to be initialized or repaired:

```text
<research-workflow-kit>/
  README.md
  init_research_workflow.py
  docs/thesis/
  scripts/
  .claude/settings.local.template.json
```

Initialize the current project with:

```bash
python <research-workflow-kit>/init_research_workflow.py --project .
```

Add `--with-claude-hook` when the user wants a Claude Code Stop hook template copied into the project. Use `--overwrite` only when the user explicitly wants existing project files refreshed from the template.

Ownership rules:

- Global Codex skills in the user's Codex skills directory, usually `~/.codex/skills`, define reusable research behavior.
- The cloned `research-workflow-kit` repository defines reusable project scaffolding.
- Each active project owns its own `docs/thesis/` evidence console and `scripts/` automation.
- When multiple copies exist, prefer the current project's `docs/thesis/` for evidence and the installed skill's `scripts/` for reusable skill behavior.

When a project needs persistent organization, suggest this structure:

```text
docs/thesis/
  topic-intake.md
  thesis-brief.md
  tool-integration-map.md
  task-board-sync.md
  console-file-index.md
  weekly-review.md
  git-version-log.md
  literature-matrix.md
  zotero-literature-hub.md
  zotero-screening-loop.md
  zotero-collection-coverage.md
  paper-readings/
  section-citation-map.md
  section-citation-suggestions.md
  citation-provenance.md
  deep-research-tasks.md
  section-research-packets/
  idea-discovery.md
  experiment-architecture.md
  experiment-runbook.md
  reproducibility-checklist.md
  evidence-promotion-policy.md
  id-lifecycle-policy.md
  benchmark-report-schema.md
  experiment-registry.md
  experiment-integrity-checklist.md
  autoresearch-loop.md
  autoresearch-results.tsv
  autoresearch-state.json
  experiment-reports/
  experiment-notebook-index.md
  claim-evidence-map.md
  material-passport.md
  data-availability.md
  figure-plan.md
  diagram-replica-tasks.md
  diagram-plans/
  network-architecture-figures.md
  spreadsheet-exports.md
  research-materials-index.md
  final-artifact-manifest.md
  final-handoff-verify-report.md
  writing-outline.md
  final-audit.md
  defense-prep.md
  skill-audit-report.md
  workflow-edit-log.md
```

When the user asks to update thesis status, view thesis progress, resume thesis work, review thesis materials, or decide what to do next, inspect `docs/thesis/` first. If the files exist, summarize the current state from the console before recommending next steps. If they do not exist, suggest creating the console, or create it directly when the user asks for implementation.

The core console files are:

| File | Primary use |
|---|---|
| `topic-intake.md` | advisor title intake, topic decomposition, first research blueprint |
| `thesis-brief.md` | Topic, research question, contributions, constraints, timeline |
| `tool-integration-map.md` | plugin/skill roles by workflow stage |
| `workflow-dashboard.md` | one-page current stage, blockers, recent experiments, evidence gaps, audit tier |
| `console-file-index.md` | layered source-file map to reduce daily cognitive load |
| `weekly-review.md` | short weekly convergence record: stronger/weaker evidence, best experiment, next 1-3 actions |
| `daily-workflow-entry.md` | legacy-compatible current research workspace record: focus, blocker, next action, done note |
| `dashboard-web/` | React/Vite local web dashboard rendering generated workflow data |
| `workflow-edit-log.md` | audit trail for flow-editor writes to Markdown source records |
| `task-board-sync.md` | Notion task board and progress sync |
| `git-version-log.md` | branch/commit traceability for code and experiments |
| `literature-matrix.md` | Literature groups, source status, paper-reading records, citation batches |
| `zotero-screening-loop.md` | candidate-paper screening, A/B/C/D labels, Zotero queue, and feedback learning |
| `zotero-collection-coverage.md` | Zotero collection coverage by section, claim, and verified citations |
| `paper-readings/` | Source-grounded full-paper readers with `paper.md`, `source_map.json`, notes, and assets |
| `section-citation-map.md` | Section and segment level citation matching |
| `section-citation-suggestions.md` | local-only citation candidate ranking for section coverage gaps |
| `citation-provenance.md` | citation metadata/support verification, Zotero status, and export trace |
| `deep-research-tasks.md` | chapter or section level literature search tasks |
| `section-research-packets/` | per-section citation precision packets |
| `idea-discovery.md` | Paper pool, idea matrix, novelty risk, shortlist |
| `experiment-architecture.md` | experiment code architecture, data/model/train/evaluate boundaries |
| `experiment-runbook.md` | run commands, expected outputs, monitoring, failure handling |
| `reproducibility-checklist.md` | environment, split, seed, config, artifacts, rerun commands |
| `evidence-promotion-policy.md` | ID naming, promotion gates, quick/advisor/final audit tiers |
| `id-lifecycle-policy.md` | lifecycle states and relationship rules for SEC/SEG/CLM/EXP/DATA/FIG/MAT/CIT/BMK/ZCOL/DRT/ZREV IDs |
| `evidence-graph.json` / `evidence-graph.mmd` | generated evidence relationship graph |
| `benchmark-report-schema.md` | baseline/new metric comparison schema and benchmark guard checklist |
| `experiment-registry.md` | Experiment IDs, configs, outputs, metrics, risks |
| `experiment-integrity-checklist.md` | leakage, fake ground truth, metric, config, artifact, and scope checks |
| `autoresearch-loop.md` | human-supervised iteration plan and verify/guard gate contract |
| `autoresearch-results.tsv` | iteration result log |
| `autoresearch-state.json` | resumable iteration state |
| `experiment-reports/` | baseline comparison and claim-promotion report for each formal run |
| `experiment-notebook-index.md` | Reproducible notebook records and console handoffs |
| `claim-evidence-map.md` | Claim-to-result-to-figure-to-citation traceability |
| `material-passport.md` | identity cards for datasets, experiment outputs, figures, readings, and document artifacts |
| `data-availability.md` | dataset provenance, access status, and claim-to-data traceability |
| `figure-plan.md` | Figures, tables, captions, input data, status |
| `diagram-replica-tasks.md` | Mac draw.io and Windows Visio reference-image replication tasks |
| `diagram-plans/` | draw.io and Visio JSON plans for structured diagram reconstruction |
| `network-architecture-figures.md` | model structure diagrams, draw.io redraw records, `.network.json` specs, renderer presets, outputs, QA |
| `spreadsheet-exports.md` | export registry for reviewable tables |
| `research-materials-index.md` | index of experiment, literature, notebook, figure, and writing materials |
| `final-artifact-manifest.md` | stage 11-12 Mac production and Windows compatibility-review manifest for final DOCX/PDF/PPTX/figure/table artifacts |
| `final-handoff-verify-report.md` | checksum verification report for the latest final handoff package |
| `writing-outline.md` | Chapter goals, evidence, citations, writing status |
| `final-audit.md` | Submission, defense, citation, figure, format, and claim audit |
| `defense-prep.md` | defense narrative, slide inventory, and Q&A |
| `skill-audit-report.md` | generated check of skill structure and outdated assumptions |

## Workflow

Read the reference files only as needed:

- `references/literature-and-citations.md` for Semantic Scholar, Scite, Zotero, BibTeX, and pyzotero fallback decisions.
- `references/experiment-records.md` for notebook and experiment registry workflows.
- `references/visualization-rules.md` for publication figure rules.
- `references/document-production.md` for DOCX/PDF/LaTeX production checks.
- `references/tool-integration.md` for Notion, GitHub, Superpowers, Build Web Data Visualization, CodeRabbit, Vercel, Scite, Zotero, Spreadsheets, draw.io, Presentations, Figma, BioRender, and optional Canva routing.
- `references/paper-iteration-loop.md` for iterative research-paper execution.
- `references/source-map.md` for provenance and license notes.

## Twelve-Stage Thesis Workflow

Use this stage model when explaining or coordinating the full workflow:

1. Paper planning: `$research-paper-plan` for Topic Intake -> Research Blueprint when a title is provided; optionally sync tasks to Notion; use `idea-discovery.md` for paper pool, idea matrix, novelty risk, and shortlist.
2. Literature discovery and review: `$semanticscholar-skill`, `$research-literature-review`, `$pdf` for source-grounded paper readers, Zotero, Scite, long-text citation batching, optional Zotero screening loop, `zotero-collection-coverage.md`, `citation-provenance.md`, `section-citation-map.md`, local `section-citation-suggestions.md`, and `deep-research-tasks.md` section packets when a chapter needs tighter citation matching.
3. Experiment question definition: map planned claims to required experiments.
4. Experiment architecture planning: `$research-experiment-engineering` and `$research-code-quality` for code boundaries, config-driven entrypoints, and experiment contracts.
5. Research code implementation: Codex coding workflow, Superpowers TDD/debugging, `$research-code-quality`, GitHub versioning, `plugin_gate_advisor.py` recommendations, Codex Security for security-sensitive Dashboard/API/remote/CI changes, optional CodeRabbit review before major merges when authenticated.
6. Experiment run and monitoring: `$research-experiment-engineering` for `local_mac` CPU-only smoke tests, `remote_desktop_4060` primary GPU formal runs, `cloud_autodl` fallback training with logs, exit code, run summary, artifact recovery, checksums, auto-shutdown policy, and git commit traceability; use `$research-autoresearch-loop` for human-supervised iterations and verify/guard gates. Use macOS Terminal, VS Code SSH, `ssh`, `scp`, or `rsync` for remote handoff.
7. Experiment recording and result scan: `$jupyter-notebook`, `$research-results-analysis`, `$research-autoresearch-loop`, Data Analytics for data quality and metric diagnostics, Spreadsheets for reviewable exports, and Build Web Data Visualization for result-chart choice and QA; create `experiment-reports/EXP-*.md` and update `benchmark-report-schema.md` for formal baseline comparisons; update `material-passport.md` and data availability when result artifacts become evidence.
8. Results analysis and claim mapping: `$research-results-analysis`, `$research-data-availability`, Data Analytics for baseline-delta/anomaly/uncertainty review, Scite for citation-support checks, Build Web Data Visualization for uncertainty chart design, Spreadsheets for claim tables, `material-passport.md`, `benchmark-report-schema.md`, `citation-provenance.md`, and `section-citation-map.md`.
9. Figure and table planning: `$research-paper-figures`, with `figure-audit-standard.md` for Nature-derived claim-first figure QA, Build Web Data Visualization for chart/dashboard/evidence graph design QA, and Product Design for advisor-facing readability and hierarchy review. For model architecture, method overview, workflow, and schematic figures, run the required visual-reference route first. Mac route: Image Gen Skill reference -> content-accuracy check -> formal redraw in draw.io from source-of-truth records -> SVG/PDF/PNG export -> optional PPTX packaging -> metadata/provenance check -> figure audit. Windows route: reference image -> Visio JSON plan -> `.vsdx` -> EMF/PDF/PNG export -> copy artifacts back -> audit. Use Python or the Nature-style renderer for data-backed plots, and Spreadsheets for manuscript tables.
10. Paper writing: `$research-paper-writing`, with `nature-polishing` rules for final section logic, hedging, sentence clarity, and English manuscript polish when appropriate; check `section-citation-map.md` before citation-heavy polishing.
11. Mac DOCX / PDF / PPTX main production: complete the thesis DOCX main document, PDF export candidate, and PPTX candidate on the Mac first, check evidence/citations/figures, register DOCX/PDF/PPTX/figure/table artifacts in `final-artifact-manifest.md`, package them with `scripts/package_final_handoff.py`, and record checksums; use WPS-compatible DOCX, `$research-data-availability`, Documents plugin for `.docx`, Pages when useful, Presentations for PPTX, LaTeX doctor first and LaTeX compile only when a TeX runtime is available, and `$pdf` for rendered checks.
12. Windows compatibility review and final submission preparation: verify the Mac-produced package on the Windows laptop with `scripts/verify_final_handoff.py` and `final-handoff-verify-report.md`; open DOCX/PDF/PPTX in Word/WPS/PowerPoint, check layout/export/playback compatibility, final submission details, and defense readiness; use `$research-final-audit`, `$research-data-availability`, Presentations, draw.io exports, optional Figma/BioRender visual refinement, optional Canva only when available, Notion task closure, and `nature-paper2ppt` structure when converting a paper or thesis chapter into a Chinese academic PPTX deck. Final audit must choose `quick`, `advisor`, or `final` tier and check workflow dashboard health, evidence graph gaps, ID lifecycle conflicts, final artifact manifest copied/verified/checksum status, final artifact package verification, material passport completeness, benchmark report schema, figure-audit status, source-grounded reading/citation provenance, Zotero collection coverage, data availability, autoresearch verify/guard status, code contract status, 4060/cloud environment snapshots and remote artifact URI/hash records, and network-architecture draw.io/`.network.json` plus QA reports.

## Output Contract

Always include:

- current project phase
- recommended skill sequence
- required artifacts
- next concrete actions
- risks or blockers
- suggested files to update

If the user asks for full execution, break the work into stages and handle the current stage first. If evidence is missing, name the missing artifact instead of inventing it.
