# Tool Integration Map

## Update Rules

- Use this file to decide which plugin or skill belongs to each thesis stage.
- Keep `docs/thesis/` as the evidence archive. Use external tools for task management, code hosting, document production, presentation, or table exports.
- Do not put secrets, passwords, private keys, API tokens, or account recovery information in this file.

## Tool Roles

| Tool / Plugin / Skill | Primary Stages | Role | Primary Record | Notes |
|---|---|---|---|---|
| Notion | 1, 3, 4-6, 12 | task board, weekly plan, supervisor feedback, progress dashboard | `task-board-sync.md` | Does not replace `docs/thesis/` evidence files |
| GitHub | 4-6, 12 | code versioning, issue/PR review, branch/commit traceability | `git-version-log.md` | Formal experiments should record branch/commit |
| Superpowers | 5, 6 | planning, TDD, systematic debugging, verification, code review | linked tasks in `task-board-sync.md` or `git-version-log.md` | Engineering method layer, not evidence source |
| `$research-code-quality` | 4-6 | code skeleton, config-driven entrypoints, experiment contract, smoke config, remote 4060 templates | `experiment-architecture.md`, `experiment-runbook.md`, `experiment-integrity-checklist.md` | Run before expensive GPU work |
| `$research-autoresearch-loop` | 5-8 | human-supervised experiment iteration, resume state, verify/guard gates | `autoresearch-loop.md`, `autoresearch-results.tsv`, `autoresearch-state.json` | Not unattended autonomous research |
| `$research-data-availability` | 7-8, 11-12 | dataset provenance, access status, claim-to-data traceability | `data-availability.md`, `final-audit.md` | Required before final submission/defense materials |
| evidence promotion policy | 2-12 | ID naming, evidence promotion gates, quick/advisor/final audit tiers | `evidence-promotion-policy.md` | Use before promoting `SEC-*`, `CLM-*`, `EXP-*`, `DATA-*`, or `FIG-*` |
| workflow dashboard | 1-12 | one-page project status, blockers, recent experiments, missing evidence, audit tier | `workflow-dashboard.md` | Refresh manually or with `research_workflow_doctor.py --write-dashboard` |
| evidence graph export | 3-12 | machine-readable and visual relationship map across claims, experiments, data, sections, figures | `evidence-graph.json`, `evidence-graph.mmd` | Use before advisor/final review when evidence feels scattered |
| React/Vite dashboard | 1-12 | local web rendering of workflow health, stages, evidence graph, claims, experiments, and data availability | `dashboard-web/` | Run `pnpm run prepare:data`, then `pnpm run dev` |
| Zotero screening loop | 2, 10, 12 | candidate-paper intake, A/B/C/D labels, Zotero queue, spreadsheet feedback learning | `zotero-screening-loop.md`, `literature-matrix.md` | Inspired by `zotero-med-pipeline`; generalized beyond medical-only PubMed workflow |
| `local_mac` | 1-10 | research console, literature/writing/remote-run control, CPU-only smoke tests | `experiment-runbook.md`, `reproducibility-checklist.md` | Do not assume local GPU |
| `remote_desktop_4060` | 5-8 | primary CUDA/GPU experiment target | `experiment-runbook.md`, `reproducibility-checklist.md`, `experiment-registry.md` | Use for training, evaluation, tuning, and reproducibility artifacts; save `outputs/EXP-*/environment.txt` |
| `cloud_autodl` | 6-8 optional | stronger fallback GPU target | `experiment-runbook.md`, `reproducibility-checklist.md` | Use only when desktop 4060 is unavailable or insufficient |
| Laptop finalization | 11-12 | final DOCX/optional Word/optional LaTeX/PDF production and defense finishing | `final-audit.md`, `defense-prep.md` | Separate from Mac research-console workflow |
| Spreadsheets | 2, 7-9, 12 | export literature matrices, result tables, claim maps, audit tables | `spreadsheet-exports.md` | Use for reviewable tables; keep source records in Markdown/CSV |
| Documents | 10, 11 | DOCX thesis drafting, editing, and formatting | `writing-outline.md`, `final-audit.md` | In Codex plugin contexts this is `documents:documents`; Pages or Microsoft Word are optional local review tools |
| PDF | 11, 12 | rendered PDF checks | `final-audit.md` | Use for final visual/layout audit |
| draw.io / draw.io MCP | 9, 12 | default formal redraw for model architecture, method workflow, evidence graph, system architecture, and process diagrams | `network-architecture-figures.md`, `figure-plan.md` | Use after Image Gen reference/content check; export SVG/PDF/PNG and package into PPTX when needed |
| Windows Visio route | 9, 12 optional | direct Windows replication route for editable `.vsdx` diagrams from JSON plans | `diagram-replica-tasks.md`, `diagram-plans/`, `network-architecture-figures.md` | Use on Windows with Microsoft Visio + PowerShell 7; copy exports back to thesis project |
| Figma | 9, 12 optional | visual system, collaborative design polish, reusable design components | `network-architecture-figures.md`, `figure-plan.md` | Optional refinement after draw.io/source-of-truth records exist |
| BioRender | 9, 12 optional | scientific schematic and mechanism-style visual refinement | `figure-plan.md`, `defense-prep.md` | Optional; still keep source data and claims in `docs/thesis/` |
| Presentations | 12 | defense slide deck and speaking structure | `defense-prep.md` | Slides must trace to supported claims |
| Canva | 12 optional | visual polish for defense or poster materials | `defense-prep.md` | Not assumed on this Mac; optional only when available, not a source of evidence |
| nature-figure source | 9, 12 | publication-grade figure contract, multi-panel logic, export QA | `figure-plan.md`, `final-audit.md` | Use as an enhancement layer through `$research-paper-figures` |
| Network architecture renderer | 9 | structure-spec to SVG/PDF/PNG/PPTX-target model diagrams | `network-architecture-figures.md`, `figure-plan.md` | Use for CNN/ResNet/U-Net/Transformer/attention diagrams |
| nature-polishing source | 10, 12 | final academic prose polish, hedging and overclaim checks | `writing-outline.md`, `final-audit.md` | Use after evidence and citations are stable |
| nature-paper2ppt source | 12 | paper/thesis-to-Chinese-PPT structure, figure selection, speaker-note logic | `defense-prep.md` | Use through Presentations and final audit |
| External skill candidates | 1-12 | source-map references for controlled local adaptations | `external-skill-sources.md` | Do not install full external packs by default |

## Stage Integration

| Stage | Main Skills | Tool Layer |
|---|---|---|
| 1. Paper planning | `$research-paper-plan` | Notion for task board; `idea-discovery.md` for paper pool, idea matrix, novelty risk |
| 2. Literature discovery and review | `$semanticscholar-skill`, `$research-literature-review`, Zotero, Scite | Spreadsheets for reviewable matrix exports; `zotero-screening-loop.md` for candidate screening; `section-citation-map.md` for section-level citation matching |
| 3. Experiment question definition | `$research-paper-plan`, `$research-experiment-engineering` | Notion for task planning |
| 4. Experiment architecture planning | `$research-experiment-engineering`, `$research-code-quality` | GitHub issues/branches when useful; contract checks before implementation |
| 5. Research code implementation | Codex coding, Superpowers, `$research-code-quality` | Mac research console, GitHub commits and code review; heavy tests can run on `remote_desktop_4060` |
| 6. Experiment run and monitoring | `$research-experiment-engineering`, `$research-autoresearch-loop` | GitHub commit trace, `local_mac` CPU-only smoke tests, `remote_desktop_4060` primary GPU runs, `cloud_autodl` fallback, macOS Terminal / VS Code SSH / `ssh` / `scp` / `rsync`, Notion progress |
| 7. Experiment recording and result scan | `$jupyter-notebook`, `$research-results-analysis`, `$research-autoresearch-loop` | Spreadsheets for result tables; update data availability and autoresearch logs |
| 8. Results analysis and claim mapping | `$research-results-analysis`, `$research-data-availability` | Scite for citation support, Spreadsheets for claim tables, section citation coverage |
| 9. Figure and table planning | `$research-paper-figures`, Image Gen visual reference, draw.io formal redraw, optional Windows Visio route, Python/Nature-style renderer, nature-figure source | Image Gen for attractive reference; Mac draw.io for structured diagrams; Windows Visio for editable `.vsdx`; Python for data-backed plots; Presentations for PPTX packaging |
| 10. Paper writing | `$research-paper-writing`, nature-polishing source, Documents | Zotero for citations; check `section-citation-map.md` before polishing |
| 11. Laptop DOCX / optional Word / optional LaTeX / PDF production | Documents, `$research-data-availability`, LaTeX doctor before LaTeX compile, PDF | Move final production to laptop; Zotero/BibTeX; Pages or Microsoft Word optional for local review |
| 12. Laptop final audit and defense preparation | `$research-final-audit`, `$research-data-availability`, Presentations, draw.io exports, nature-paper2ppt source | Move final finishing to laptop; Notion tasks, Figma/BioRender optional, Canva optional only if available |

## Non-Replacement Rules

| External tool | Must not replace |
|---|---|
| Notion | `docs/thesis/` evidence archive |
| GitHub | local reproducibility checklist and experiment registry |
| Spreadsheets | source Markdown/CSV records and notebooks |
| draw.io / Windows Visio / Figma / BioRender | `.network.json` specs, claim/evidence records, and figure QA |
| Presentations / Canva | supported claims and audited figures |
| Superpowers | domain-specific research review |
| nature-skills-derived style | raw evidence, citations, result analysis, or claim audit |
