# Source Map

## External Inspiration

- `external-skill-candidates/aris`
  - MIT licensed.
  - Used as inspiration for code review before GPU, monitoring discipline, and experiment integrity checks.
- `external-skill-candidates/codex-autoresearch`
  - MIT licensed.
  - Used as inspiration for preflight checks and iteration artifacts.
- `external-skill-candidates/AI-research-SKILLs`
  - MIT licensed.
  - Used as a technical reference for evaluation, optimization, inference, and MLOps when a project needs deeper tooling.

## Local Adaptation

- Local script: `scripts/check_experiment_contract.py`.
- Local skeleton renderer: `scripts/render_project_skeleton.py`.
- Local remote templates: `scripts/remote_*_4060.sh.template`.
- Local AutoDL fallback templates: `scripts/remote_sync_to_autodl.sh.template`, `scripts/remote_run_autodl_autoshutdown.sh.template`, `scripts/remote_fetch_autodl_results.sh.template`.
- Integrated with `$research-experiment-engineering`, `remote_desktop_4060`, and `cloud_autodl` fallback workflows.
