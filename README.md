# Research Workflow Kit

A reusable Codex research workflow kit for thesis and paper projects.

This repository contains:

- reusable Codex research skills;
- a project-local `docs/thesis/` evidence console template;
- lightweight scripts for experiment registration, data hashing, result/claim audit, and figure workflows;
- figure folder templates for visual references, formal exports, and architecture diagrams;
- an initialization script for new research projects.

It is designed to be project-independent. It does **not** include private datasets, trained model weights, experiment outputs, API keys, SSH keys, Zotero credentials, or paper drafts.

## Repository Layout

```text
research-workflow-kit/
  skills/                       # Reusable Codex skills
  docs/thesis/                  # Project research console templates
  scripts/                      # Lightweight reusable automation scripts
  dashboard-web/                # Local React/Vite workflow dashboard
  .github/                      # CI, PR template, issue templates
  figures/                      # Figure reference/final/architecture folders
  .claude/                      # Optional Claude Code hook template
  AGENTS.md                     # Main AI/agent project context
  CLAUDE.md                     # Claude Code entry pointing to AGENTS.md
  init_research_workflow.py     # Initialize a project-local research console
```

## Included Skills

```text
research-workflow-orchestrator
research-paper-plan
research-literature-review
semanticscholar-skill
research-experiment-engineering
research-code-quality
research-autoresearch-loop
research-results-analysis
research-paper-figures
research-paper-writing
research-data-availability
research-final-audit
```

## Install Skills On A New Computer

### macOS / Codex

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
.venv/bin/python install_skills.py --overwrite
```

This installs the bundled research skills into `~/.codex/skills`. The repository
`.venv` is used for local script execution and keeps dependencies out of the
system Python and Codex runtime cache.

Recommended verification:

```bash
.venv/bin/python -c "import requests, matplotlib, pandas, pptx, numpy"
test -f ~/.codex/skills/research-workflow-orchestrator/SKILL.md
test -f ~/.codex/skills/semanticscholar-skill/s2.py
```

### macOS / Linux Manual Copy

```bash
mkdir -p ~/.codex/skills
cp -R skills/* ~/.codex/skills/
```

Use the installer above when possible because it copies each skill directory
including internal `references/`, `scripts/`, `examples/`, `presets/`, and
assets.

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codex\skills"
Copy-Item -Recurse -Force .\skills\* "$env:USERPROFILE\.codex\skills\"
```

## Initialize A New Research Project

### macOS / Linux

```bash
.venv/bin/python init_research_workflow.py --project "/path/to/my-research-project"
```

### Windows PowerShell

```powershell
python .\init_research_workflow.py --project "E:\path\to\my-research-project"
```

This creates or updates:

```text
docs/thesis/
scripts/
figures/
.claude/settings.local.template.json
```

Use `--overwrite` only when you intentionally want template files to replace existing project files.

## Workflow Summary

The workflow has 12 stages:

1. Paper planning
2. Literature discovery and review
3. Experiment question definition
4. Experiment architecture planning
5. Research code implementation
6. Experiment run and monitoring
7. Experiment recording and result scan
8. Results analysis and claim mapping
9. Figure, table, and model diagram production
10. Paper writing and polishing
11. Laptop-based DOCX / optional Word / optional LaTeX / PDF production
12. Laptop-based final audit and defense preparation

`docs/thesis/` is the project evidence source of truth. Notion or other task tools should be used for progress tracking only, not as the primary evidence archive.

The workflow includes optional enhancement layers:

- `research-code-quality` checks config-driven code, experiment contracts, smoke configs, output manifests, and 4060 handoff templates before expensive runs.
- `research-autoresearch-loop` records human-supervised experiment iterations in `autoresearch-results.tsv` and `autoresearch-state.json` with verify/guard gates.
- `research-data-availability` checks dataset provenance, access restrictions, hashes, and claim-to-data traceability before final audit.
- `$research-literature-review` supports section-level citation matching through `section-citation-map.md`, Zotero screening loops through `zotero-screening-loop.md`, citation provenance through `citation-provenance.md`, Zotero collection coverage through `zotero-collection-coverage.md`, and source-grounded readers.
- `$research-paper-figures` supports dual-platform diagram replication: Mac draw.io MCP by default and Windows Visio when editable `.vsdx` output is useful.
- Build Web Data Visualization is used as a design and QA guide for chart choice, statistical visual communication, dashboard views, evidence graphs, accessibility, and visual testing.
- `plugin-gate-policy.md` and `plugin-review-log.md` route Codex Security, Build Web Apps, Data Analytics, Product Design, and CodeRabbit as lightweight quality gates. They recommend checks by stage without turning plugins into evidence sources.
- `docs/thesis/evidence-promotion-policy.md` defines when `SEC-*`, `CLM-*`, `EXP-*`, `DATA-*`, and `FIG-*` records can be promoted from candidate material to thesis evidence.
- `docs/thesis/material-passport.md` identifies evidence-critical materials, while `benchmark-report-schema.md` standardizes baseline/new experiment comparisons before claim promotion.
- `docs/thesis/workflow-dashboard.md` plus the legacy-compatible `daily-workflow-entry.md` are the current research workspace records for current stage, blockers, recommended actions, recent experiments, missing evidence, and audit tier.
- `docs/thesis/console-file-index.md` keeps console files layered into current workspace, evidence core, stage workspace, final handoff, and audit/maintenance so daily work stays focused.
- `docs/thesis/weekly-review.md` keeps a short weekly review: what became stronger/weaker, current best experiment, next 1-3 actions, and files to ignore next week.
- The local React/Vite Dashboard opens with a Chinese current research workspace, tabbed workflow views, an evidence chain inspector, gap-first section citation coverage, baseline experiment comparison, file-layer guidance, and weekly review. The evidence chain inspector defaults to `SEC/SEG -> CLM -> EXP/DATA/FIG/CIT`, collapses duplicate/reverse relations, and keeps the full-project graph as an advanced view. It is a view/editor over `docs/thesis/`, not a replacement source of truth.
- `scripts/suggest_section_citations.py` gives offline citation suggestions from existing local records, helping each `SEC-*` section move from “missing coverage” to manually confirmed citations.
- `scripts/package_final_handoff.py` and `scripts/verify_final_handoff.py` package only manifest-registered final artifacts and verify checksums for Mac-to-laptop stages 11-12.

## Engineering Quality Gates

This repository includes GitHub Actions CI for lightweight Python, skill, smoke, and dashboard checks. CI intentionally does not run CodeRabbit, Vercel deploys, Supabase, Overleaf, reviewer-response automation, or arXiv submission because those require account-specific state or are outside the current workflow scope.

Before merging workflow changes, run:

```bash
.venv/bin/python -m py_compile scripts/*.py
.venv/bin/python -m ruff check scripts tests init_research_workflow.py install_skills.py
.venv/bin/python -m unittest tests.test_research_workflow_scripts -v
.venv/bin/python -m coverage run -m unittest tests.test_research_workflow_scripts -v
.venv/bin/python -m coverage combine
.venv/bin/python -m coverage report --fail-under=60
.venv/bin/python scripts/audit_skills.py
.venv/bin/python scripts/research_workflow_doctor.py --warn-only
.venv/bin/python scripts/plugin_gate_advisor.py --audit-only
```

Install development-only tools with:

```bash
.venv/bin/pip install -r requirements-dev.txt
```

For dashboard changes, also run:

```bash
cd dashboard-web
PATH=/opt/homebrew/bin:$PATH pnpm install --frozen-lockfile
PATH=/opt/homebrew/bin:$PATH pnpm run prepare:data
PATH=/opt/homebrew/bin:$PATH pnpm run build
```

For template compatibility:

```bash
.venv/bin/python init_research_workflow.py --project /private/tmp/rwk-ci-smoke
cd /private/tmp/rwk-ci-smoke
python scripts/research_workflow_doctor.py --warn-only
```

Use `AGENTS.md` as the main context file for Codex, Claude Code, CodeRabbit, or other coding agents. `CLAUDE.md` is a short Claude Code entry that points back to `AGENTS.md` to avoid duplicated project instructions.

## Skill Metadata Policy

Codex skills in this kit follow the current Codex skill format: `SKILL.md` frontmatter uses `name` and `description` as the supported trigger metadata. Do not add unsupported `triggers`, `allowed-tools`, or `model` fields to local skills. Put concrete trigger contexts into the `description`; keep tool-routing and safety boundaries in the skill body, `research-workflow-orchestrator`, and repository checks.

Optional pre-merge review:

```bash
coderabbit review --agent -c AGENTS.md
```

Run it only when CodeRabbit is installed and authenticated. It is not part of default CI.

## macOS Toolchain Notes

- `local_mac` is the research console and orchestration machine for stages 1-10: planning, literature, code editing, remote run control, result analysis, figure planning, and writing drafts. It may run CPU-only smoke tests, but GPU work is not assumed.
- `remote_desktop_4060` is the primary GPU experiment target for training, evaluation, tuning, reproducibility runs, and artifact generation.
- Formal `remote_desktop_4060` runs should write `outputs/EXP-*/environment.txt` with `scripts/write_environment_snapshot.py`; the CUDA and PyTorch versions may be fixed on the desktop, but the snapshot is still required evidence.
- `cloud_autodl` is an optional stronger fallback when the desktop 4060 is unavailable or insufficient.
- Remote training uses macOS Terminal, VS Code SSH, `ssh`, `scp`, and `rsync`; MobaXterm is a Windows-only convenience and is not assumed.
- Stages 11-12 are intended to move to the user's laptop for final DOCX/optional Word/optional LaTeX/PDF production, final audit, and defense material finishing.
- Before stages 11-12 move to the laptop, register DOCX/PDF/PPTX/figure/table deliverables in `docs/thesis/final-artifact-manifest.md`.
- DOCX work uses the Documents plugin and local `.docx` files. Pages can open or review documents locally; Microsoft Word is optional when installed.
- LaTeX is optional. Run the LaTeX doctor first, then compile only when a TeX runtime is available.
- Diagram polish uses draw.io / draw.io MCP as the default formal redraw route for model architecture, method workflow, system architecture, and process diagrams. Presentations handles PPTX; Figma and BioRender are optional visual refinement tools when available. Canva is not assumed on this Mac.
- Windows can be used as an optional diagram replication workstation when Microsoft Visio and PowerShell 7+ are available. In that case, use the Visio JSON-plan route, export `.vsdx` plus PDF/PNG/EMF, then copy artifacts back to the project.

## Script Locations

- Project bootstrap scripts live in root `scripts/`.
- Experiment contract checks live in `scripts/check_experiment_contract.py`.
- Autoresearch iteration logging lives in `scripts/new_autoresearch_iteration.py`.
- Citation and data audits live in `scripts/audit_section_citations.py` and `scripts/audit_data_availability.py`.
- Environment snapshots live in `scripts/write_environment_snapshot.py`.
- One-command workflow health checks live in `scripts/research_workflow_doctor.py`.
- Evidence graph export lives in `scripts/export_evidence_graph.py`.
- Dashboard local control service lives in `scripts/dashboard_control_server.py`.
- Dashboard flow-editor writes live in `scripts/edit_workflow_record.py`.
- Weekly review writes live in `scripts/update_weekly_review.py`.
- Daily workflow updates live in `scripts/update_daily_workflow.py`.
- Offline section citation suggestions live in `scripts/suggest_section_citations.py`.
- Final artifact handoff audits live in `scripts/audit_final_artifacts.py`.
- Final artifact handoff packaging and verification live in `scripts/package_final_handoff.py` and `scripts/verify_final_handoff.py`.
- ID lifecycle audits live in `scripts/audit_id_lifecycle.py`.
- Deep research task packets are created with `scripts/new_deep_research_task.py`.
- Experiment reports and baseline comparisons are created with `scripts/new_experiment_report.py`.
- Skill consistency audits live in `scripts/audit_skills.py`.
- React/Vite web dashboard lives in `dashboard-web/`.
- 4060 remote handoff templates live in `scripts/remote_*_4060.sh.template`.
- Result scanning lives in `skills/research-results-analysis/scripts/scan_results.py` and `skills/research-results-analysis/scripts/result_scan_to_registry.py`.
- Figure rendering lives in `skills/research-paper-figures/scripts/nature_plot_templates.py` and `skills/research-paper-figures/scripts/render_network_architecture.py`.
- Root `scripts/render_network_architecture.py` is a legacy placeholder; use the skill-local renderer for formal architecture figures.

## Web Dashboard

The Markdown dashboard remains the source-of-truth project homepage, and the React/Vite dashboard renders the same console data as a local web app.

```bash
cd dashboard-web
pnpm run prepare:data
pnpm run dev
```

On macOS, the best daily route is a fixed local URL. Install the background launcher once:

```bash
./scripts/install_dashboard_fixed_url_macos.sh
```

Then open this fixed page from your browser bookmark or pinned tab:

```text
http://127.0.0.1:5173/
```

This creates a user LaunchAgent that starts the dashboard service at login and checks it every 5 minutes. It does not require a desktop shortcut.

Manual launchers are still available:

```bash
./scripts/open_dashboard.sh
./scripts/install_dashboard_app_macos.sh
```

`open_dashboard.sh` shows terminal logs. `install_dashboard_app_macos.sh` creates an optional app under `~/Applications/`.

The launcher also starts a local-only control service on `http://127.0.0.1:8765`.
The web dashboard can then refresh workflow data, export the evidence graph, run
the quick health check, open whitelisted source files, copy the next terminal
command, update the current research workspace, generate offline citation suggestions,
package final handoff artifacts, verify the latest handoff package, show an
interactive evidence graph, summarize section citation coverage as a heatmap,
and use the Chinese flow editor to append standard records. Flow-editor
writes are limited to known Markdown source files, create backups under
`tmp/dashboard-edits/backups/`, and append `docs/thesis/workflow-edit-log.md`.
The service does not expose remote access, does not store credentials, and does
not execute arbitrary commands.

You can open a specific tab directly with a URL hash, for example
`http://127.0.0.1:5173/#graph` for the evidence chain inspector.

For this Mac, prefer the Homebrew Node toolchain when running dashboard commands:

```bash
PATH=/opt/homebrew/bin:$PATH pnpm run build
```

The web app reads generated files under `dashboard-web/public/data/`, which are ignored by git because they represent the current project state. Regenerate them with `pnpm run prepare:data` after important workflow changes.

Useful lightweight commands:

```bash
python3 scripts/new_deep_research_task.py --section-id SEC-INTRO-001 --topic "your section topic"
python3 scripts/suggest_section_citations.py --section-id SEC-INTRO-001
python3 scripts/new_experiment_report.py --experiment-id EXP-001 --baseline EXP-000
python3 scripts/audit_final_artifacts.py --tier quick --warn-only
python3 scripts/package_final_handoff.py --update-manifest-checksums
python3 scripts/verify_final_handoff.py --latest --write-report docs/thesis/final-handoff-verify-report.md
python3 scripts/audit_id_lifecycle.py --warn-only
python3 scripts/audit_skills.py --warn-only --write-report
```

## Figure Workflow

For model architecture, method pipeline, workflow, and schematic figures:

1. Use Image Gen only to create a visual reference.
2. Check the reference for technical accuracy.
3. Mac route: redraw the final structured diagram in draw.io from source-of-truth information.
4. Windows route: optionally generate a Visio JSON plan, create editable `.vsdx`, and export PDF/PNG/EMF.
5. Export final thesis-ready SVG/PDF/PNG files, and use Presentations/PPTX when the diagram belongs in defense slides.
6. Record provenance and audit status in `docs/thesis/figure-plan.md`, `diagram-replica-tasks.md`, and `network-architecture-figures.md`.

Do not use AI-generated raster images directly as final thesis figures unless the project explicitly accepts that provenance.

Use Python or the Nature-style renderer for data-backed statistical plots. Use Figma or BioRender only as optional polish layers when draw.io/Python output needs additional design refinement.

For complex charts, evidence graphs, dashboard charts, or advisor-facing visual reports, apply Build Web Data Visualization rules: choose the simplest truthful chart, show uncertainty when relevant, avoid decorative chart effects, check accessible contrast, and verify labels on desktop and mobile views.

## Literature Screening Workflow

For recurring literature intake:

1. Collect candidates from Semantic Scholar, Zotero, Scite, Web, arXiv/PubMed/publisher pages, or stable RSS feeds.
2. Deduplicate by DOI/arXiv/S2/PMID/title.
3. Screen as `A-core`, `B-section`, `C-background`, or `D-exclude`.
4. Queue useful papers for Zotero and BibTeX.
5. Export or review with Spreadsheets when useful.
6. Convert feedback into cautious screening preferences, not automatic citation decisions.
7. Hand strong candidates to `section-citation-map.md` and `deep-research-tasks.md`.

Use `docs/thesis/zotero-screening-loop.md` to record this loop. Zotero and spreadsheets are convenience layers; `docs/thesis/` remains the evidence source of truth.

## Plugin Integration Boundaries

- Scite: use for citation support/contrast/mention checks in literature review, claim mapping, writing, and final audit.
- Zotero: use for local library management, metadata export, citation provenance, and section citation coverage.
- BioRender: optional scientific schematic polish after source records and figure provenance exist.
- Vercel: future optional route for a read-only dashboard preview only. Do not expose the local write API or private research evidence.
- CodeRabbit: optional local or PR pre-merge code review. Do not require it for CI.
- Codex Security: use for security-sensitive Dashboard/API/file-writing/remote-script/CI changes; record outcomes in `plugin-review-log.md`.
- Build Web Apps: use for Dashboard frontend QA and React/Vite interaction or responsive-layout checks; record outcomes in `dashboard-ux-qa.md`.
- Data Analytics: use for result data-quality, metric diagnostics, baseline-delta, and anomaly checks; record outcomes in `data-quality-report.md` and `metric-diagnostics.md`.
- Product Design: use for advisor-facing Dashboard, figure, and defense-slide UX/visual review; record outcomes in `visual-design-review.md`.
- Supabase database migration, Overleaf sync, reviewer-response workflow, and arXiv auto-submit are intentionally not included.

## Sensitive Information Policy

Do not commit:

- SSH keys or AutoDL temporary passwords;
- API keys or tokens;
- browser cookies;
- Zotero credentials;
- private datasets;
- trained checkpoints or model weights;
- large experiment outputs;
- private thesis drafts unless intentionally published.

## License

MIT License. See [LICENSE](LICENSE).
