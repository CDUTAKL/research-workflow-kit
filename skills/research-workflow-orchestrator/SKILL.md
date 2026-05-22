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
- Literature discovery, source-grounded paper reading, related work, and citation batches: use `$research-literature-review`; use `$semanticscholar-skill` for real Semantic Scholar searches when exact papers, citations, or BibTeX candidates matter; use `$pdf` when full-paper PDF reading, original/translation alignment, figure/table extraction, or source anchors matter.
- Experiment architecture, code design, `local_mac` smoke tests, AutoDL/cloud training, training/evaluation scripts, config/log/output conventions, reproducibility, and mapping code runs to thesis experiments: use `$research-experiment-engineering`.
- Experiment recording and exploration: use `$jupyter-notebook`.
- Result interpretation: use `$research-results-analysis`.
- Figures, tables, diagrams, captions, Nature-style figure audit, and model-architecture rendering: use `$research-paper-figures`.
- Drafting and revision: use `$research-paper-writing`.
- DOCX thesis/manuscript production: use the Documents plugin (`documents:documents` in Codex plugin contexts). Pages or Microsoft Word may be used locally for human review, but Word is optional.
- PDF review or final rendering checks: use `$pdf`.
- Final submission or defense checks: use `$research-final-audit`.
- Task planning and progress dashboards: use Notion when the user wants project tasks, weekly plans, or supervisor feedback synced outside the repo.
- Code versioning and GitHub work: use GitHub for repository state, issues, PRs, CI, and version traceability around major code changes or formal experiments.
- Engineering discipline: use Superpowers for TDD, systematic debugging, verification, and code review during implementation work.
- Spreadsheet exports: use Spreadsheets for reviewable literature, result, claim, and audit tables without replacing source records.
- Defense slides: use Presentations for PPTX creation/editing; use Figma or BioRender for visual refinement when available. Canva is optional only if explicitly available and useful.
- Image Gen Skill is used in stage 9 as the mandatory visual-reference generator for model architecture, method overview, workflow, and schematic figures when visual quality matters. Its output is checked for content accuracy and then redrawn formally; it is not treated as final manuscript evidence.
- Figma can be used in stage 9 or 12 for model architecture diagram refinement, reusable diagram components, and visual system work after the source-of-truth architecture record and visual reference are established.
- Nature-derived high-standard enhancements: use downloaded `nature-figure`, `nature-reader`, `nature-citation`, `nature-polishing`, and `nature-paper2ppt` source material as reference layers. `nature-figure` strengthens figure audit, `nature-reader` strengthens source-grounded paper reading, `nature-citation` strengthens long-text citation batching, `nature-polishing` strengthens final prose, and `nature-paper2ppt` strengthens defense slides. They do not replace the local `research-*` evidence workflow.

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
  git-version-log.md
  literature-matrix.md
  paper-readings/
  experiment-architecture.md
  experiment-runbook.md
  reproducibility-checklist.md
  experiment-registry.md
  experiment-notebook-index.md
  claim-evidence-map.md
  figure-plan.md
  network-architecture-figures.md
  spreadsheet-exports.md
  writing-outline.md
  final-audit.md
  defense-prep.md
```

When the user asks to update thesis status, view thesis progress, resume thesis work, review thesis materials, or decide what to do next, inspect `docs/thesis/` first. If the files exist, summarize the current state from the console before recommending next steps. If they do not exist, suggest creating the console, or create it directly when the user asks for implementation.

The core console files are:

| File | Primary use |
|---|---|
| `topic-intake.md` | advisor title intake, topic decomposition, first research blueprint |
| `thesis-brief.md` | Topic, research question, contributions, constraints, timeline |
| `tool-integration-map.md` | plugin/skill roles by workflow stage |
| `task-board-sync.md` | Notion task board and progress sync |
| `git-version-log.md` | branch/commit traceability for code and experiments |
| `literature-matrix.md` | Literature groups, source status, paper-reading records, citation batches |
| `paper-readings/` | Source-grounded full-paper readers with `paper.md`, `source_map.json`, notes, and assets |
| `experiment-architecture.md` | experiment code architecture, data/model/train/evaluate boundaries |
| `experiment-runbook.md` | run commands, expected outputs, monitoring, failure handling |
| `reproducibility-checklist.md` | environment, split, seed, config, artifacts, rerun commands |
| `experiment-registry.md` | Experiment IDs, configs, outputs, metrics, risks |
| `experiment-notebook-index.md` | Reproducible notebook records and console handoffs |
| `claim-evidence-map.md` | Claim-to-result-to-figure-to-citation traceability |
| `figure-plan.md` | Figures, tables, captions, input data, status |
| `network-architecture-figures.md` | model structure diagrams, `.network.json` specs, renderer presets, outputs, QA |
| `spreadsheet-exports.md` | export registry for reviewable tables |
| `writing-outline.md` | Chapter goals, evidence, citations, writing status |
| `final-audit.md` | Submission, defense, citation, figure, format, and claim audit |
| `defense-prep.md` | defense narrative, slide inventory, and Q&A |

## Workflow

Read the reference files only as needed:

- `references/literature-and-citations.md` for Semantic Scholar, Scite, Zotero, BibTeX, and pyzotero fallback decisions.
- `references/experiment-records.md` for notebook and experiment registry workflows.
- `references/visualization-rules.md` for publication figure rules.
- `references/document-production.md` for DOCX/PDF/LaTeX production checks.
- `references/tool-integration.md` for Notion, GitHub, Superpowers, Spreadsheets, Presentations, Figma, BioRender, and optional Canva routing.
- `references/paper-iteration-loop.md` for iterative research-paper execution.
- `references/source-map.md` for provenance and license notes.

## Twelve-Stage Thesis Workflow

Use this stage model when explaining or coordinating the full workflow:

1. Paper planning: `$research-paper-plan` for Topic Intake -> Research Blueprint when a title is provided; optionally sync tasks to Notion.
2. Literature discovery and review: `$semanticscholar-skill`, `$research-literature-review`, `$pdf` for source-grounded paper readers, Zotero, Scite, and long-text citation batching.
3. Experiment question definition: map planned claims to required experiments.
4. Experiment architecture planning: `$research-experiment-engineering`.
5. Research code implementation: Codex coding workflow, Superpowers TDD/debugging, GitHub versioning.
6. Experiment run and monitoring: `$research-experiment-engineering` for `local_mac` smoke tests, AutoDL/cloud formal training, logs, artifact recovery, shutdown/release policy, and git commit traceability. Use macOS Terminal, VS Code SSH, `ssh`, `scp`, or `rsync` for remote handoff.
7. Experiment recording and result scan: `$jupyter-notebook`, `$research-results-analysis`, Spreadsheets for reviewable exports.
8. Results analysis and claim mapping: `$research-results-analysis`, Scite for citation-support checks, Spreadsheets for claim tables.
9. Figure and table planning: `$research-paper-figures`, with `figure-audit-standard.md` for Nature-derived claim-first figure QA. For model architecture, method overview, workflow, and schematic figures, run the required visual-reference route first: Image Gen Skill reference -> content-accuracy check -> formal redraw with Figma/PPTX/SVG/TikZ/Python from source-of-truth records -> metadata/provenance check -> figure audit. Use Spreadsheets for manuscript tables.
10. Paper writing: `$research-paper-writing`, with `nature-polishing` rules for final section logic, hedging, sentence clarity, and English manuscript polish when appropriate.
11. DOCX / optional Word / optional LaTeX / PDF production: Documents plugin for `.docx`; Pages or Microsoft Word only when installed; LaTeX doctor first, then LaTeX compile only when a TeX runtime is available; `$pdf` for rendered checks.
12. Final audit and defense preparation: `$research-final-audit`, Presentations, optional Figma/BioRender visual refinement, optional Canva only when available, Notion task closure, and `nature-paper2ppt` structure when converting a paper or thesis chapter into a Chinese academic PPTX deck. Final audit must check figure-audit status, source-grounded reading/citation evidence, Zotero/Scite statuses, and network-architecture `.network.json` plus QA reports.

## Output Contract

Always include:

- current project phase
- recommended skill sequence
- required artifacts
- next concrete actions
- risks or blockers
- suggested files to update

If the user asks for full execution, break the work into stages and handle the current stage first. If evidence is missing, name the missing artifact instead of inventing it.
