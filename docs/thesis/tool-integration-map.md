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
| Spreadsheets | 2, 7-9, 12 | export literature matrices, result tables, claim maps, audit tables | `spreadsheet-exports.md` | Use for reviewable tables; keep source records in Markdown/CSV |
| Documents | 10, 11 | DOCX thesis drafting, editing, and formatting | `writing-outline.md`, `final-audit.md` | In Codex plugin contexts this is `documents:documents`; Pages or Microsoft Word are optional local review tools |
| PDF | 11, 12 | rendered PDF checks | `final-audit.md` | Use for final visual/layout audit |
| Figma | 9, 12 | model architecture figure refinement, visual system, diagram layout review, reusable design components | `network-architecture-figures.md`, `figure-plan.md` | Best for polishing and collaborative design after spec/render outputs exist |
| BioRender | 9, 12 | scientific schematic and mechanism-style visual refinement | `figure-plan.md`, `defense-prep.md` | Use when available; still keep source data and claims in `docs/thesis/` |
| Presentations | 12 | defense slide deck and speaking structure | `defense-prep.md` | Slides must trace to supported claims |
| Canva | 12 optional | visual polish for defense or poster materials | `defense-prep.md` | Not assumed on this Mac; optional only when available, not a source of evidence |
| nature-figure source | 9, 12 | publication-grade figure contract, multi-panel logic, export QA | `figure-plan.md`, `final-audit.md` | Use as an enhancement layer through `$research-paper-figures` |
| Network architecture renderer | 9 | structure-spec to SVG/PDF/PNG/PPTX-target model diagrams | `network-architecture-figures.md`, `figure-plan.md` | Use for CNN/ResNet/U-Net/Transformer/attention diagrams |
| nature-polishing source | 10, 12 | final academic prose polish, hedging and overclaim checks | `writing-outline.md`, `final-audit.md` | Use after evidence and citations are stable |
| nature-paper2ppt source | 12 | paper/thesis-to-Chinese-PPT structure, figure selection, speaker-note logic | `defense-prep.md` | Use through Presentations and final audit |

## Stage Integration

| Stage | Main Skills | Tool Layer |
|---|---|---|
| 1. Paper planning | `$research-paper-plan` | Notion for task board |
| 2. Literature discovery and review | `$semanticscholar-skill`, `$research-literature-review`, Zotero, Scite | Spreadsheets for reviewable matrix exports |
| 3. Experiment question definition | `$research-paper-plan`, `$research-experiment-engineering` | Notion for task planning |
| 4. Experiment architecture planning | `$research-experiment-engineering` | GitHub issues/branches when useful |
| 5. Research code implementation | Codex coding, Superpowers | GitHub commits and code review |
| 6. Experiment run and monitoring | `$research-experiment-engineering` | GitHub commit trace, `local_mac` smoke tests, AutoDL over macOS Terminal / VS Code SSH / `ssh` / `scp` / `rsync`, Notion progress |
| 7. Experiment recording and result scan | `$jupyter-notebook`, `$research-results-analysis` | Spreadsheets for result tables |
| 8. Results analysis and claim mapping | `$research-results-analysis` | Scite for citation support, Spreadsheets for claim tables |
| 9. Figure and table planning | `$research-paper-figures`, Image Gen visual reference, nature-figure source, Figma/BioRender/PPTX/SVG/TikZ/Python formal redraw | Image Gen for attractive reference; Spreadsheets for table exports; Figma/BioRender/PPTX for model diagram redraw/refinement; Presentations for PPTX refinement |
| 10. Paper writing | `$research-paper-writing`, nature-polishing source, Documents | Zotero for citations |
| 11. DOCX / optional Word / optional LaTeX / PDF production | Documents, LaTeX doctor before LaTeX compile, PDF | Zotero/BibTeX; Pages or Microsoft Word optional for local review |
| 12. Final audit and defense preparation | `$research-final-audit`, Presentations, nature-paper2ppt source | Notion tasks, Figma/BioRender optional, Canva optional only if available |

## Non-Replacement Rules

| External tool | Must not replace |
|---|---|
| Notion | `docs/thesis/` evidence archive |
| GitHub | local reproducibility checklist and experiment registry |
| Spreadsheets | source Markdown/CSV records and notebooks |
| Figma / BioRender | `.network.json` specs, claim/evidence records, and figure QA |
| Presentations / Canva | supported claims and audited figures |
| Superpowers | domain-specific research review |
| nature-skills-derived style | raw evidence, citations, result analysis, or claim audit |
