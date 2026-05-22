# Run And Reproducibility

## Minimum Run Record

Every important run should record:

| Field | Required value |
|---|---|
| Experiment ID | stable ID such as `EXP-001` |
| Purpose | claim, baseline, ablation, robustness, or error analysis |
| Command | exact command or notebook path |
| Config path | config file or parameter block |
| Resolved config | copied JSON/YAML in output directory when possible |
| Random seed | seed value or single-seed warning |
| Data split | train/validation/test source and rule |
| Code version | git branch/commit if available |
| Environment | requirements, conda env, uv lock, or package list |
| Metric definition | names and formulas |
| Output directory | stable artifact path |
| Checkpoint path | checkpoint used for evaluation |
| Prediction file | predictions or residuals when applicable |
| Execution target | `local`, `cloud_autodl`, or other named target |
| Known limitations | missing baseline, small scope, failed runs, unstable results |

## Execution Targets

Use these target labels consistently:

| Target | Meaning |
|---|---|
| `local` | user's local machine; use for debugging and smoke tests |
| `cloud_autodl` | AutoDL remote GPU instance; use for formal training when access is provided |
| `cloud_other` | RunPod, Colab, Kaggle, school server, or another remote target |

Default policy:

- Run local smoke tests before paid cloud training.
- Use AutoDL for formal runs only after the command, config, outputs, and data paths are known.
- Keep secrets out of repository files.

## Output Directory Checklist

Recommended files:

```text
outputs/<experiment_id>/
  manifest.json
  config_resolved.json
  metrics.json
  predictions.csv
  logs/
  checkpoints/
```

If a project cannot produce all files, record the reason in `reproducibility-checklist.md`.

## Monitoring Checklist

During or immediately after a run, check:

- command started with the intended config.
- output directory was created.
- logs are being written.
- loss/metric values are finite and plausible.
- checkpoint or final model is saved when expected.
- metrics file exists and is machine-readable.
- evaluation uses the intended split.
- failures are recorded rather than silently ignored.

## AutoDL Run Record

When using AutoDL, record these fields in `experiment-runbook.md` and `reproducibility-checklist.md`:

| Field | Record |
|---|---|
| SSH reference | SSH alias or host label; do not store password |
| Username/port | only if needed for reconnection |
| Private key | local file path only, never key contents |
| GPU model | for example RTX 4090, RTX 3090, A100 |
| Remote project path | code directory on AutoDL |
| Remote data path | dataset directory on AutoDL |
| Remote env | conda/env activation command |
| Remote command | train/evaluate command |
| Remote log path | log file or directory |
| Remote output path | metrics/checkpoints/predictions directory |
| Download destination | local artifact path after training |
| Shutdown policy | whether to stop/release instance after artifacts are recovered |

AutoDL execution sequence:

```text
1. Confirm SSH access and GPU.
2. Confirm project, data, and environment paths.
3. Run or verify a small remote smoke test if the environment is new.
4. Start formal training in tmux, screen, nohup, or the platform's preferred background method.
5. Monitor logs and GPU usage.
6. Verify metrics, logs, checkpoints, and predictions exist.
7. Download or sync required artifacts.
8. Update thesis console records.
9. Stop or release the instance if the user requested shutdown.
```

## Paper Mapping

Before using a result in writing, map:

```text
experiment ID -> output directory -> metric file -> claim ID -> figure/table ID -> manuscript section
```

Use:

- `experiment-runbook.md` for commands and expected outputs.
- `experiment-registry.md` for stable run records.
- `claim-evidence-map.md` for paper claims.
- `figure-plan.md` for tables and figures.

## Reproducibility Status

Use these status labels:

| Status | Meaning |
|---|---|
| `ready_to_run` | command/config exists, not executed |
| `running` | run is active |
| `completed_unreviewed` | outputs exist but are not audited |
| `reviewed` | outputs are traceable and safe for result analysis |
| `needs_rerun` | run failed, scope changed, or evidence is insufficient |
| `not_reproducible` | required reproduction information is missing |
| `cloud_running` | remote cloud run is active |
| `cloud_recovered` | remote artifacts were downloaded or synced locally |
