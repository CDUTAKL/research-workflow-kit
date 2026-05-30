# Claude Code Entry

Use `AGENTS.md` as the authoritative agent context for this repository. This file is only a short Claude Code entry point to avoid duplicating long instructions.

Start by reading:

1. `README.md`
2. `AGENTS.md`
3. `skills/research-workflow-orchestrator/SKILL.md`

Minimal verification before reporting a workflow change as ready:

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

For dashboard changes:

```bash
cd dashboard-web
PATH=/opt/homebrew/bin:$PATH pnpm run prepare:data
PATH=/opt/homebrew/bin:$PATH pnpm run build
```
