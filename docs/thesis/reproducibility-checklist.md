# Reproducibility Checklist

## Update Rules

- Complete this checklist for every experiment that may support a thesis claim.
- A result should not move from `candidate` to `done` until required reproduction information is available.
- Record exceptions explicitly instead of leaving fields blank.

## Checklist

| Experiment ID | Target | Environment | GPU / Hardware | Data Split | Seed | Config | Code Version | Metrics | Artifacts | Rerun Command | Claim Mapping | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EXP-001 | local_mac/cloud_autodl | TBD | TBD | TBD | TBD | TBD | branch/commit/TBD | TBD | TBD | TBD | CLM-001/TBD | pending |

## Required Evidence

| Evidence | Required For | Example |
|---|---|---|
| Environment | rerun and debugging | `requirements.txt`, conda env, uv lock, package list |
| GPU / Hardware | interpret runtime and reproducibility | local Mac CPU / Apple Silicon / MPS when available, AutoDL RTX 4090, A100 |
| Data split | fair comparison | split file, seed, stratification rule |
| Config | method identity | `configs/experiment/EXP-001.yaml` |
| Resolved config | exact run state | `outputs/EXP-001/config_resolved.json` |
| Metrics | result analysis | `outputs/EXP-001/metrics.json` |
| Predictions | error analysis and figures | `outputs/EXP-001/predictions.csv` |
| Code version | traceability | git branch/commit if available |
| Rerun command | reproduction | command from `experiment-runbook.md` |

## AutoDL Reproducibility Evidence

| Evidence | Value | Status | Notes |
|---|---|---|---|
| AutoDL instance / GPU | TBD | pending | record GPU model; instance ID optional |
| Remote project path | TBD | pending | no credentials |
| Remote data path | TBD | pending |  |
| Remote environment | TBD | pending | conda/env activation command |
| CUDA / PyTorch version | TBD | pending | record when available |
| Remote output path | TBD | pending |  |
| Local recovered artifact path | TBD | pending | metrics/logs/checkpoints/predictions |
| Shutdown/release status | TBD | pending | only after user instruction |

## macOS Local And Remote Notes

- `local_mac` means local CPU, Apple Silicon acceleration when the project supports it, and short smoke tests for shapes, configs, and output files.
- `cloud_autodl` is the default label for formal CUDA/GPU training when the user provides temporary access.
- Use macOS Terminal, VS Code SSH, `ssh`, `scp`, or `rsync` for remote upload/run/download workflows. Do not assume MobaXterm on this Mac.

## Status Legend

| Status | Meaning |
|---|---|
| `pending` | not checked |
| `ready_to_run` | command/config exists, not executed |
| `completed_unreviewed` | outputs exist but are not audited |
| `reviewed` | outputs are traceable and safe for result analysis |
| `needs_rerun` | result must be rerun or scope changed |
| `not_reproducible` | required reproduction information is missing |
| `cloud_running` | AutoDL or other remote run is active |
| `cloud_recovered` | remote artifacts have been downloaded or synced |
