# Experiment Runbook

## Update Rules

- Add a runbook entry before running important experiments.
- Keep exact commands copyable on Windows PowerShell when possible.
- Use `local_mac` runs for debug/smoke tests and AutoDL for formal training when remote access is provided.
- Record SSH alias, remote paths, and environment details only; do not record passwords, token values, or private-key contents.
- After the run, update actual outputs, status, and handoff target.

## Runbook Table

| Experiment ID | Target | Purpose | Command | Config | Expected Outputs | Monitoring Checklist | Success Criteria | Failure Handling | Result Recovery | Next Handoff | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EXP-001 | local_mac/cloud_autodl | TBD | TBD | TBD | metrics, logs, checkpoint, predictions/TBD | logs finite, output dir exists | TBD | record failure and rerun plan | TBD | `$research-results-analysis` | planned |

## Command Template

```powershell
python src\train.py --config configs\experiment\EXP-001.yaml --out outputs\EXP-001
python src\evaluate.py --config configs\experiment\EXP-001.yaml --checkpoint outputs\EXP-001\checkpoints\best.pt --out outputs\EXP-001
```

Adapt these commands to the project. Do not invent entrypoints when reviewing an existing codebase; record the real command.

## Execution Target Rules

| Target | Role | Use For | Do Not Use For |
|---|---|---|---|
| `local_mac` | debug and smoke test on this Mac | CPU / Apple Silicon / MPS when available, 1 epoch, small sample, output-format check, bug fixing | final thesis metrics when runtime is too slow |
| `cloud_autodl` | formal training | full data, full epochs, baselines, ablations, multi-seed runs | debugging unknown code from scratch |
| `cloud_other` | fallback cloud | RunPod, Colab, Kaggle, school server | unspecified credentials or unrecorded environments |

## AutoDL Connection Record

Record connection metadata here only after the user provides access. Do not store secrets.

| Field | Value | Notes |
|---|---|---|
| SSH alias / host label | TBD | no password here |
| Username | TBD | optional if alias handles it |
| Port | TBD | optional if alias handles it |
| Private key file path | TBD | path only, never key contents |
| AutoDL instance / GPU | TBD | instance ID or GPU model |
| Remote project path | TBD | code path |
| Remote data path | TBD | dataset path |
| Remote environment | TBD | conda/env activation command |
| Remote output path | TBD | experiment artifacts |
| Local download path | TBD | where recovered results are stored |
| Shutdown policy | ask_user / stop_after_recovery / keep_running | choose before long runs |

## AutoDL Formal Training Procedure

| Step | Action | Status | Notes |
|---|---|---|---|
| 1 | Confirm SSH login and GPU visibility | pending | `nvidia-smi` or equivalent |
| 2 | Confirm project, data, and environment paths | pending |  |
| 3 | Run `local_mac` smoke test or verify one already passed | pending |  |
| 4 | Run remote smoke test if environment is new | pending |  |
| 5 | Start formal training in a persistent session | pending | tmux/screen/nohup/platform default |
| 6 | Monitor logs and GPU usage | pending |  |
| 7 | Verify metrics/logs/checkpoints/predictions | pending |  |
| 8 | Download or sync required artifacts | pending |  |
| 9 | Update registry, reproducibility checklist, and claim map | pending |  |
| 10 | Stop/release instance if requested | pending | never assume without user instruction |

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
