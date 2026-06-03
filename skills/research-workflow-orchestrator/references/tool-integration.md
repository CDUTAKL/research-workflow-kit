# Tool Integration

## Core Rule

Keep `docs/thesis/` as the local evidence archive. Use plugins and external tools for task management, code hosting, document production, table exports, and presentation work.

## Tool Routing

| Tool | Use when | Record |
|---|---|---|
| Notion | task boards, weekly planning, supervisor feedback, progress dashboards | `docs/thesis/task-board-sync.md` |
| GitHub | repository state, issues, PRs, CI, code review, version traceability | `docs/thesis/git-version-log.md` |
| Superpowers | TDD, systematic debugging, verification, code review, implementation discipline | linked task or git log |
| `$research-code-quality` | experiment contract, skeleton, smoke config, remote 4060 templates | `docs/thesis/experiment-integrity-checklist.md` |
| `$research-autoresearch-loop` | human-supervised experiment iteration, state, verify/guard gates | `docs/thesis/autoresearch-loop.md` |
| `$research-data-availability` | dataset provenance, access restrictions, claim-to-data traceability | `docs/thesis/data-availability.md` |
| Build Web Data Visualization | chart choice, statistical visual communication, dashboard/evidence graph design, accessibility and visual QA | `docs/thesis/figure-plan.md`, `docs/thesis/workflow-dashboard.md`, `docs/thesis/experiment-reports/` |
| Plugin gate advisor | stage-aware recommendations for Codex Security, Build Web Apps, Data Analytics, Product Design, and CodeRabbit | `docs/thesis/plugin-gate-policy.md`, `docs/thesis/plugin-review-log.md` |
| Codex Security | security-sensitive Dashboard/API/file-writing/remote-script/CI review | `docs/thesis/plugin-review-log.md` |
| Build Web Apps | Dashboard React/Vite frontend QA and responsive interaction review | `docs/thesis/dashboard-ux-qa.md` |
| Data Analytics | data quality, metric diagnostics, baseline delta, anomaly, uncertainty review | `docs/thesis/data-quality-report.md`, `docs/thesis/metric-diagnostics.md` |
| Product Design | advisor-facing visual/UX review for Dashboard, figures, diagrams, and defense slides | `docs/thesis/visual-design-review.md` |
| CodeRabbit | optional pre-merge AI code review for scripts, dashboard, CI, and skill changes | PR checklist, `docs/thesis/git-version-log.md` |
| Vercel | optional future read-only dashboard preview for advisor/demo review | future export notes in `docs/thesis/workflow-dashboard.md` |
| `local_mac` | stages 1-10 research console, literature/writing/remote-run control, CPU-only smoke tests | `docs/thesis/experiment-runbook.md`, `docs/thesis/reproducibility-checklist.md` |
| `remote_desktop_4060` | primary RTX 4060 GPU target for training, evaluation, tuning, and reproducibility artifacts | `docs/thesis/experiment-runbook.md`, `docs/thesis/experiment-registry.md` |
| `cloud_autodl` | fallback GPU target when the desktop 4060 is unavailable or insufficient | `docs/thesis/reproducibility-checklist.md` |
| Laptop finalization | stage 11-12 final DOCX/optional Word/optional LaTeX/PDF production and defense finishing | `docs/thesis/final-audit.md`, `docs/thesis/defense-prep.md` |
| Spreadsheets | reviewable literature/result/claim/audit tables | `docs/thesis/spreadsheet-exports.md` |
| Zotero screening loop | recurring literature intake, A/B/C/D screening, Zotero writeback queue, spreadsheet feedback learning | `docs/thesis/zotero-screening-loop.md` |
| Scite | support/contrast/mention checks for citation-backed claims | `docs/thesis/citation-provenance.md`, `docs/thesis/section-citation-map.md`, `docs/thesis/final-audit.md` |
| Image Gen Skill | mandatory visual reference for model architecture, method overview, workflow, and schematic figures when visual quality matters | `docs/thesis/figure-plan.md`, `figures/references/` |
| draw.io | default Mac formal redraw tool for model architecture, method overview, workflow, evidence graph, system architecture, and process diagrams | `docs/thesis/network-architecture-figures.md`, `docs/thesis/figure-plan.md`, `docs/thesis/diagram-replica-tasks.md` |
| Windows Visio | optional direct Windows route for editable `.vsdx` replication from JSON plans | `docs/thesis/diagram-replica-tasks.md`, `docs/thesis/diagram-plans/` |
| Figma | optional visual refinement, reusable components, and collaborative design polish after draw.io/source-of-truth records exist | `docs/thesis/network-architecture-figures.md`, `docs/thesis/figure-plan.md` |
| Presentations | defense PPTX creation, editing, rendering, and checking | `docs/thesis/defense-prep.md` |
| BioRender | scientific schematic and mechanism-style visual refinement when installed | `docs/thesis/figure-plan.md`, `docs/thesis/defense-prep.md` |
| Canva | optional visual polish only when available; not assumed on this Mac | `docs/thesis/defense-prep.md` |
| `nature-figure` source | publication-grade figure logic, multi-panel visual argument, SVG/PDF/TIFF export checks | `docs/thesis/figure-plan.md` |
| Network architecture renderer | CNN/ResNet/U-Net/Transformer/attention structure diagrams from `.network.json` specs | `docs/thesis/network-architecture-figures.md` |
| `nature-polishing` source | high-standard academic prose polish, section logic, hedging, overclaim checks | `docs/thesis/writing-outline.md`, `docs/thesis/final-audit.md` |
| `nature-paper2ppt` source | paper/thesis-to-PPT story spine, figure selection, Chinese slide logic, PPT QA | `docs/thesis/defense-prep.md` |
| external skill source registry | source commit/license/adaptation record for reference-only external projects | `docs/thesis/external-skill-sources.md` |

## Stage Rules

- Stage 1 planning: Notion can mirror tasks, but `thesis-brief.md` remains the local source of evidence; use `idea-discovery.md` for early paper-pool and idea-matrix work.
- Stage 2 literature: use `section-citation-map.md` when matching papers to thesis chapters or paragraphs; use `zotero-screening-loop.md` when recurring paper intake and feedback learning are useful.
- Stages 4-6 engineering: GitHub and Superpowers should be considered for major code changes, debugging, and formal experiment traceability. Use `local_mac` for CPU-only smoke tests, `remote_desktop_4060` for primary GPU runs, and `cloud_autodl` only as fallback.
- Stages 4-6 code quality: use `$research-code-quality` before remote GPU runs; use Codex Security when Dashboard/API/file-writing/remote/CI changes are security-sensitive; use CodeRabbit as an optional pre-merge reviewer when authenticated, not as a default CI dependency.
- Stages 5-8 iteration: use `$research-autoresearch-loop` for iteration logging and verify/guard decisions.
- Stages 7-12 data availability: use `$research-data-availability` before finalizing data-backed claims.
- Stages 7-9 tables and charts: Spreadsheets can export review-friendly tables from Markdown/CSV/notebook outputs. Use Data Analytics for data quality and metric diagnostics, Build Web Data Visualization to choose simple truthful charts, and Product Design for advisor-facing readability.
- Stage 9 figures: `nature-figure` rules can be used when a visual needs publication-grade panel logic, editable vector export, and source-data traceability.
- Stage 9 visual reference: use Image Gen Skill first for model architecture, method overview, workflow, and schematic figures when visual quality matters; store reference assets under `figures/references/`.
- Stage 9 formal redraw: check the Image Gen reference for content accuracy, then redraw structured diagrams in draw.io from source-of-truth records on Mac; export SVG/PDF/PNG and package into PPTX when needed.
- Stage 9 Windows Visio route: on Windows with Microsoft Visio and PowerShell 7+, use JSON plans to create editable `.vsdx`, export preview files, and copy artifacts back to the project.
- Stage 9 data plots: use Python or the Nature-style renderer for charts, ablations, heatmaps, distributions, and metric comparisons.
- Stage 9 dashboard/evidence visuals: use Build Web Data Visualization for interaction design, accessibility, responsive layout, and visual QA. Keep source data and evidence records in `docs/thesis/`.
- Stage 9 model diagrams: keep `.network.json`, `model.py`, paper source, or manual architecture spec as topology source of truth; generated references are not topology truth.
- Stage 10 writing: `nature-polishing` rules can be used for the final wording pass after claims, evidence, and citations are already stable.
- Stage 11-12 laptop finalization: move final DOCX/optional Word/optional LaTeX/PDF production and defense finishing to the user's laptop; keep artifact paths or versions traceable in `final-audit.md` and `defense-prep.md`.
- Stage 12 defense: Presentations handles PPTX work; draw.io or Visio exports supply structured diagrams; `nature-paper2ppt` supplies paper-to-slide structure; Figma/BioRender handle optional visual refinement when useful; Canva is optional only when available.
- Vercel route: only consider a future read-only dashboard preview. Never deploy the local write API, private research artifacts, unpublished thesis evidence, or credentials.
- Exclusions: Supabase database migration, Overleaf synchronization, reviewer-response workflow, and arXiv auto-submit are outside the current workflow.

## Safety Rules

- Do not store credentials, API tokens, private keys, or account recovery data in `docs/thesis/`.
- Do not treat Notion, Spreadsheets, Zotero screening labels, Scite summaries, Codex Security, Build Web Apps, Data Analytics, Product Design, Build Web Data Visualization, CodeRabbit, Vercel, draw.io, Windows Visio, Figma, BioRender, Canva, or slides as primary evidence sources.
- Before formal experiments, record git branch/commit or dirty state.
- Before final defense slides, ensure every slide claim traces to `claim-evidence-map.md`.
- Do not use Nature-derived style rules to strengthen scientific claims. They may improve presentation, but evidence still comes from results, citations, and the thesis console.
- Do not use architecture diagrams as performance evidence. They explain topology and tensor flow only.
