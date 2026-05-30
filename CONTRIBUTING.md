# Contributing

This repository is a lightweight research workflow kit. Keep changes small, traceable, and compatible with the Markdown/TSV/JSON evidence console.

## Development Setup

Create a branch from `main`:

```bash
git switch main
git pull --ff-only
git switch -c codex/your-change-name
```

Create the local Python environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

For dashboard work, use the local Node toolchain:

```bash
cd dashboard-web
PATH=/opt/homebrew/bin:$PATH pnpm install --frozen-lockfile
```

## Required Checks

Before opening or merging a PR, run:

```bash
.venv/bin/python -m py_compile scripts/*.py
.venv/bin/python -m unittest tests.test_research_workflow_scripts -v
.venv/bin/python scripts/audit_skills.py
.venv/bin/python scripts/research_workflow_doctor.py --warn-only
```

For dashboard changes:

```bash
cd dashboard-web
PATH=/opt/homebrew/bin:$PATH pnpm run prepare:data
PATH=/opt/homebrew/bin:$PATH pnpm run build
```

For template compatibility:

```bash
.venv/bin/python init_research_workflow.py --project /private/tmp/rwk-ci-smoke
cd /private/tmp/rwk-ci-smoke
python scripts/research_workflow_doctor.py --warn-only
```

## Skill Changes

When editing `skills/`:

- keep every skill's `SKILL.md` concise and route deeper instructions to `references/`;
- ensure referenced `references/`, `scripts/`, `examples/`, or `templates/` paths exist;
- avoid old assumptions such as default local GPU, required Microsoft Word, default Canva, or Mac reliance on MobaXterm;
- run `scripts/audit_skills.py`;
- refresh installed skills only after repository checks pass:

```bash
.venv/bin/python install_skills.py --overwrite
```

## Plugin Changes

Plugin integrations must describe:

- workflow stage;
- role;
- primary source record;
- safety boundary;
- whether the plugin is default or optional.

Current explicit non-goals are Supabase database migration, Overleaf synchronization, reviewer-response workflow, and arXiv auto-submit.

## Data And Secret Safety

Do not commit private research data, model weights, large experiment outputs, generated dashboard data, local virtual environments, dependency folders, or credentials. Check `git status` carefully before committing.

## Optional CodeRabbit Review

For important changes, run CodeRabbit locally when authenticated:

```bash
coderabbit review --agent -c AGENTS.md
```

If it is unavailable, mark it as not applicable in the PR template.
