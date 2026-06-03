## Summary

- 

## Workflow Impact

- [ ] No workflow-stage impact
- [ ] Updates one or more 12-stage workflow routes
- [ ] Updates skills
- [ ] Updates dashboard or local control service
- [ ] Updates scripts or CI

Notes:

## Evidence / Docs Updated

- [ ] README / docs updated
- [ ] `docs/thesis/` templates updated
- [ ] Skill references updated
- [ ] Not applicable

## Test Plan

- [ ] `python -m py_compile scripts/*.py`
- [ ] `python -m ruff check scripts tests init_research_workflow.py install_skills.py`
- [ ] `python -m unittest tests.test_research_workflow_scripts -v`
- [ ] `python -m coverage run -m unittest tests.test_research_workflow_scripts -v`
- [ ] `python -m coverage combine`
- [ ] `python -m coverage report --fail-under=60`
- [ ] `python scripts/audit_skills.py`
- [ ] `python scripts/research_workflow_doctor.py --warn-only`
- [ ] `python init_research_workflow.py --project /tmp/rwk-ci-smoke`
- [ ] Dashboard: `pnpm run prepare:data`
- [ ] Dashboard: `pnpm run build`
- [ ] Not applicable, reason:

## Data And Secrets Safety

- [ ] No private data, model weights, large outputs, tokens, keys, cookies, or local dependency folders are committed
- [ ] Generated dashboard data and build outputs are not committed

## CodeRabbit Review

- [ ] Ran `coderabbit review --agent -c AGENTS.md`
- [ ] Not applicable, reason:

## Plugin Gates

- [ ] Checked `docs/thesis/plugin-gate-policy.md`
- [ ] Recorded required plugin checks in `docs/thesis/plugin-review-log.md`
- [ ] Codex Security diff scan needed and completed
- [ ] Codex Security not applicable, reason:
- [ ] Build Web Apps / Dashboard UX QA needed and recorded
- [ ] Data Analytics quality or metric diagnostics needed and recorded
- [ ] Product Design visual review needed and recorded
