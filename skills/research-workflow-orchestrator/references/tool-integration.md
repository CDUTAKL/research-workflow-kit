# Tool Integration

## Core Rule

Keep `docs/thesis/` as the local evidence archive. Use plugins and external tools for task management, code hosting, document production, table exports, and presentation work.

## Tool Routing

| Tool | Use when | Record |
|---|---|---|
| Notion | task boards, weekly planning, supervisor feedback, progress dashboards | `docs/thesis/task-board-sync.md` |
| GitHub | repository state, issues, PRs, CI, code review, version traceability | `docs/thesis/git-version-log.md` |
| Superpowers | TDD, systematic debugging, verification, code review, implementation discipline | linked task or git log |
| Spreadsheets | reviewable literature/result/claim/audit tables | `docs/thesis/spreadsheet-exports.md` |
| Image Gen Skill | mandatory visual reference for model architecture, method overview, workflow, and schematic figures when visual quality matters | `docs/thesis/figure-plan.md`, `figures/references/` |
| Figma | formal redraw and refinement of architecture/method diagrams after Image Gen reference and source-of-truth records exist | `docs/thesis/network-architecture-figures.md` |
| Presentations | defense PPTX creation, editing, rendering, and checking | `docs/thesis/defense-prep.md` |
| Canva | optional visual polish for defense, poster, or presentation assets | `docs/thesis/defense-prep.md` |
| `nature-figure` source | publication-grade figure logic, multi-panel visual argument, SVG/PDF/TIFF export checks | `docs/thesis/figure-plan.md` |
| Network architecture renderer | CNN/ResNet/U-Net/Transformer/attention structure diagrams from `.network.json` specs | `docs/thesis/network-architecture-figures.md` |
| `nature-polishing` source | high-standard academic prose polish, section logic, hedging, overclaim checks | `docs/thesis/writing-outline.md`, `docs/thesis/final-audit.md` |
| `nature-paper2ppt` source | paper/thesis-to-PPT story spine, figure selection, Chinese slide logic, PPT QA | `docs/thesis/defense-prep.md` |

## Stage Rules

- Stage 1 planning: Notion can mirror tasks, but `thesis-brief.md` remains the local source of evidence.
- Stages 4-6 engineering: GitHub and Superpowers should be considered for major code changes, debugging, and formal experiment traceability.
- Stages 7-9 tables: Spreadsheets can export review-friendly tables from Markdown/CSV/notebook outputs.
- Stage 9 figures: `nature-figure` rules can be used when a visual needs publication-grade panel logic, editable vector export, and source-data traceability.
- Stage 9 visual reference: use Image Gen Skill first for model architecture, method overview, workflow, and schematic figures when visual quality matters; store reference assets under `figures/references/`.
- Stage 9 formal redraw: check the Image Gen reference for content accuracy, then redraw with Figma/PPTX/SVG/TikZ/Python from source-of-truth records.
- Stage 9 model diagrams: keep `.network.json`, `model.py`, paper source, or manual architecture spec as topology source of truth; generated references are not topology truth.
- Stage 10 writing: `nature-polishing` rules can be used for the final wording pass after claims, evidence, and citations are already stable.
- Stage 12 defense: Presentations handles PPTX work; `nature-paper2ppt` supplies paper-to-slide structure; Canva is optional for design polish.

## Safety Rules

- Do not store credentials, API tokens, private keys, or account recovery data in `docs/thesis/`.
- Do not treat Notion, Spreadsheets, Canva, or slides as primary evidence sources.
- Before formal experiments, record git branch/commit or dirty state.
- Before final defense slides, ensure every slide claim traces to `claim-evidence-map.md`.
- Do not use Nature-derived style rules to strengthen scientific claims. They may improve presentation, but evidence still comes from results, citations, and the thesis console.
- Do not use architecture diagrams as performance evidence. They explain topology and tensor flow only.
