# Experiment Runbook

## Update Rules

- Add a runbook entry before running important experiments.
- Keep exact commands copyable on macOS shell or the remote target shell when possible.
- Use `local_mac` for orchestration and CPU-only smoke tests, `remote_desktop_4060` as the primary GPU experiment target, and AutoDL only as a stronger fallback.
- Record SSH alias, remote paths, and environment details only; do not record passwords, token values, or private-key contents.
- Run the experiment contract check before expensive remote GPU work.
- Record human-supervised iteration decisions in `autoresearch-results.tsv` when the run changes a claim or method.
- After the run, update actual outputs, status, and handoff target.

## Runbook Table

| Experiment ID | Target | Purpose | Command | Config | Expected Outputs | Monitoring Checklist | Success Criteria | Failure Handling | Result Recovery | Next Handoff | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EXP-001 | local_mac/remote_desktop_4060/cloud_autodl | TBD | TBD | TBD | metrics, logs, checkpoint, predictions/TBD | logs finite, output dir exists | TBD | record failure and rerun plan | TBD | `$research-results-analysis` | planned |

## Contract Check

```bash
python scripts/check_experiment_contract.py \
  --experiment-id EXP-001 \
  --config configs/experiment/EXP-001.yaml \
  --smoke-config configs/smoke/EXP-001-smoke.yaml \
  --registry docs/thesis/experiment-registry.md
```

After a run, add `--require-outputs` to require `manifest.json`, `config_resolved.json`, `metrics.json`, and `logs/`.

## Command Template

```bash
python src/train.py --config configs/experiment/EXP-001.yaml --out outputs/EXP-001
python src/evaluate.py --config configs/experiment/EXP-001.yaml --checkpoint outputs/EXP-001/checkpoints/best.pt --out outputs/EXP-001
```

Adapt these commands to the project. Do not invent entrypoints when reviewing an existing codebase; record the real command.

## Execution Target Rules

| Target | Role | Use For | Do Not Use For |
|---|---|---|---|
| `local_mac` | research console and light smoke test | stages 1-10 planning/literature/code control/result analysis/figure planning/writing drafts; CPU-only shape and output-format checks | assuming local GPU availability or final formal metrics |
| `remote_desktop_4060` | primary GPU experiment target | training, evaluation, tuning, ablations, multi-seed runs, reproducibility artifacts | storing secrets in console files or replacing result review |
| `cloud_autodl` | optional stronger fallback | full data or larger GPU runs when 4060 is insufficient/unavailable | default first choice when desktop 4060 can run the experiment |
| `cloud_other` | fallback cloud | RunPod, Colab, Kaggle, school server | unspecified credentials or unrecorded environments |

## Remote Desktop 4060 Connection Record

Record connection metadata here only after the user provides access. Do not store secrets.

| Field | Value | Notes |
|---|---|---|
| SSH alias / host label | TBD | no password here |
| Username | TBD | optional if alias handles it |
| Port | TBD | optional if alias handles it |
| Private key file path | TBD | path only, never key contents |
| GPU | RTX 4060/TBD | record exact model and VRAM when available |
| Remote project path | TBD | code path on desktop |
| Remote data path | TBD | dataset path on desktop |
| Remote environment | TBD | conda/env activation command |
| Remote output path | TBD | experiment artifacts |
| Local download path | TBD | where recovered results are stored |
| Shutdown policy | ask_user / stop_after_recovery / keep_running | choose before long runs |

## Remote GPU Formal Training Procedure

| Step | Action | Status | Notes |
|---|---|---|---|
| 1 | Confirm SSH login and GPU visibility | pending | `nvidia-smi` or equivalent |
| 2 | Confirm project, data, and environment paths | pending |  |
| 3 | Run experiment contract check and `local_mac` CPU-only smoke test | pending |  |
| 4 | Run `remote_desktop_4060` smoke test if environment is new | pending |  |
| 5 | Start formal training in a persistent session | pending | tmux/screen/nohup/platform default |
| 6 | Monitor logs and GPU usage | pending |  |
| 7 | Verify metrics/logs/checkpoints/predictions | pending |  |
| 8 | Download or sync required artifacts | pending |  |
| 9 | Update registry, reproducibility checklist, and claim map | pending |  |
| 10 | Stop/release instance if requested | pending | never assume without user instruction |

## Autoresearch Iteration Handoff

| Iteration | Experiment | Verify Gate | Guard Gate | Result Log | State Update | Decision |
|---|---|---|---|---|---|---|
| 1 | EXP-001/TBD | pending | pending | `autoresearch-results.tsv` | `autoresearch-state.json` | pending |

## AutoDL Fallback Record

Use this section only when `remote_desktop_4060` is unavailable or insufficient.

| Field | Value | Notes |
|---|---|---|
| AutoDL instance / GPU | TBD | instance ID or GPU model |
| Remote project path | TBD | code path |
| Remote data path | TBD | dataset path |
| Remote environment | TBD | conda/env activation command |
| Remote output path | TBD | experiment artifacts |
| Local download path | TBD | where recovered results are stored |
| Shutdown/release status | TBD | only after user instruction |

## Monitoring Checklist

| Check | Expected | Actual | Status |
|---|---|---|---|
| Command uses intended config | yes | TBD | pending |
| Output directory created | yes | TBD | pending |
| Logs are written | yes | TBD | pending |
| Metrics are finite | yes | TBD | pending |
| Checkpoint saved when expected | yes | TBD | pending |
| Metrics JSON/CSV exists | yes | TBD | pending |
| Evaluation uses intended split | yes | TBD | pending |
| Result artifacts recovered locally | yes for cloud runs | TBD | pending |

## Failure Log

| Experiment ID | Failure | Evidence | Fix | Rerun Needed |
|---|---|---|---|---|
| EXP-001 | TBD | TBD | TBD | yes/no |
