# Agent Context

This repository is a reusable Codex research workflow kit for thesis and paper projects. It provides local skills, Markdown/TSV/JSON console templates, lightweight scripts, and a local React/Vite dashboard. It is not a data repository and should not contain private datasets, trained model weights, API keys, SSH keys, Zotero credentials, or private thesis drafts unless the owner intentionally publishes them.

## Source Of Truth

- `docs/thesis/` is the evidence source of truth.
- `dashboard-web/` is a local view and light editor for those source records; it can update the daily workspace, generate local citation suggestions, and package final handoff files, but it must not become the only copy of any research decision.
- External tools such as Notion, Zotero, Spreadsheets, draw.io, BioRender, Vercel, or presentation tools are convenience layers unless a source record in `docs/thesis/` points to their exported artifact.
- If a generated or external artifact supports a thesis claim, record the relevant `SEC-*`, `SEG-*`, `CLM-*`, `EXP-*`, `DATA-*`, `FIG-*`, `MAT-*`, `CIT-*`, or `BMK-*` relationship before treating it as evidence.

## Main Workflow

The kit keeps a 12-stage workflow:

1. Paper planning.
2. Literature discovery and review.
3. Experiment question definition.
4. Experiment architecture planning.
5. Research code implementation.
6. Experiment run and monitoring.
7. Experiment recording and result scan.
8. Results analysis and claim mapping.
9. Figure, table, and model diagram production.
10. Paper writing and polishing.
11. Laptop-based DOCX / optional Word / optional LaTeX / PDF production.
12. Laptop-based final audit and defense preparation.

Keep new features inside this stage model unless the maintainer explicitly asks to change it.

## Local Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -r requirements-dev.txt
```

Install or refresh local Codex skills with:

```bash
.venv/bin/python install_skills.py --overwrite
```

The web dashboard uses the lightweight `dashboard-web/` app. It should open to the Chinese daily workspace first, with lower-frequency views in tabs. Interactive evidence graph and section citation heatmap views must remain backed by generated JSON from Markdown source records.

```bash
cd dashboard-web
PATH=/opt/homebrew/bin:$PATH pnpm install --frozen-lockfile
PATH=/opt/homebrew/bin:$PATH pnpm run prepare:data
PATH=/opt/homebrew/bin:$PATH pnpm run build
```

Daily workflow and final handoff helpers:

```bash
.venv/bin/python scripts/update_daily_workflow.py --stage "2 文献发现与综述" --next-action "confirm citations"
.venv/bin/python scripts/suggest_section_citations.py --section-id SEC-INTRO-001
.venv/bin/python scripts/package_final_handoff.py --update-manifest-checksums
.venv/bin/python scripts/verify_final_handoff.py --latest --write-report docs/thesis/final-handoff-verify-report.md
```

## Verification Commands

Run the smallest relevant subset while developing, and run the full set before merging:

```bash
.venv/bin/python -m py_compile scripts/*.py
.venv/bin/python -m ruff check scripts tests init_research_workflow.py install_skills.py
.venv/bin/python -m unittest tests.test_research_workflow_scripts -v
.venv/bin/python -m coverage run -m unittest tests.test_research_workflow_scripts -v
.venv/bin/python -m coverage combine
.venv/bin/python -m coverage report --fail-under=60
.venv/bin/python scripts/audit_skills.py
.venv/bin/python scripts/research_workflow_doctor.py --warn-only
```

## Skill Metadata Policy

Local skills use the current Codex `SKILL.md` frontmatter contract: `name` and `description`. Put trigger phrases in `description`, which should start with `Use when...`. Do not add unsupported `triggers`, `allowed-tools`, or `model` fields; `scripts/audit_skills.py` treats them as metadata warnings.

For a project initialization smoke test:

```bash
.venv/bin/python init_research_workflow.py --project /private/tmp/rwk-ci-smoke
cd /private/tmp/rwk-ci-smoke
python scripts/research_workflow_doctor.py --warn-only
```

## Plugin Routing

- Build Web Data Visualization: use for chart choice, statistical visual design, dashboard/evidence-graph interaction design, accessibility checks, and visual QA. It improves visual communication and testing rules; it is not a source of scientific evidence.
- Codex Security: use as a local/PR security gate when changes touch Dashboard APIs, local file writing, remote 4060 scripts, CI, or other security-sensitive code. Record outcomes in `docs/thesis/plugin-review-log.md`; do not store secrets or private scan details.
- Build Web Apps: use for Dashboard frontend implementation and QA, especially React/Vite components, interaction bugs, responsive layout, and Browser/Safari checks. Record outcomes in `docs/thesis/dashboard-ux-qa.md`.
- Data Analytics: use for result data-quality review, metric diagnostics, baseline deltas, uncertainty, and anomaly checks in stages 7-8. Record outcomes in `docs/thesis/data-quality-report.md` and `docs/thesis/metric-diagnostics.md`.
- Product Design: use for advisor-facing Dashboard, figure, and defense-slide visual/UX review. Record outcomes in `docs/thesis/visual-design-review.md`; it is a readability check, not scientific evidence.
- CodeRabbit: optional pre-merge AI code review for important script, dashboard, CI, or skill changes. Use `coderabbit review --agent -c AGENTS.md` when authenticated. Do not put CodeRabbit in default CI because it depends on external account state.
- Vercel: optional future route for a read-only dashboard preview. Do not expose the local dashboard write API, private research files, secrets, or unpublished thesis evidence through Vercel.
- Scite: use in stages 2, 8, 10, and 12 for support/contrast/mention checks on citation-backed claims.
- Zotero: use in stage 2 and citation-heavy writing for library organization, metadata export, BibTeX/RIS/ENW/Zotero RDF handoff, and `citation-provenance.md`.
- BioRender: optional stage 9 or 12 scientific schematic polish. Keep source data, claims, and figure provenance in `docs/thesis/`.
- Supabase database migration, Overleaf synchronization, reviewer-response workflow, and arXiv auto-submit are intentionally out of scope for the current kit.

## Safety

Do not commit:

- `data/`, large `outputs/`, checkpoints, or model weights;
- `.venv/`, `node_modules/`, dashboard build artifacts, generated dashboard data, or caches;
- `.env` files, API tokens, SSH keys, cookies, credentials, or recovery codes;
- external reference repositories cloned under `external-skill-candidates/`.
- generated handoff packages under `handoff-packages/`.

When a change touches skills, update installed skills only after repository tests pass, then run `scripts/audit_skills.py` again.

## Change Discipline

- Prefer existing script and Markdown table conventions.
- Keep scripts offline by default unless their purpose is explicitly a search or API integration.
- Use version-traceable branches and commits for formal workflow changes.
- If a new plugin is added, document its stage, role, primary record, and non-replacement rule in `docs/thesis/tool-integration-map.md`.
- For plugin-related changes, run `python scripts/plugin_gate_advisor.py --audit-only` and check the Dashboard plugin suggestions before merging.
