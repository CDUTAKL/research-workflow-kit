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
| Execution target | `local_mac`, `remote_desktop_4060`, `cloud_autodl`, or other named target |
| Known limitations | missing baseline, small scope, failed runs, unstable results |

## Execution Targets

Use these target labels consistently:

| Target | Meaning |
|---|---|
| `local_mac` | this Mac; use CPU / Apple Silicon / MPS when supported for orchestration, debugging, and smoke tests only |
| `remote_desktop_4060` | the user's desktop with RTX 4060; primary formal GPU experiment target |
| `cloud_autodl` | AutoDL remote GPU instance; stronger fallback when the desktop 4060 is unavailable or insufficient |
| `cloud_other` | RunPod, Colab, Kaggle, school server, or another remote target |

Default policy:

- Run `local_mac` CPU-only smoke tests before any long-running remote GPU training.
- Use `remote_desktop_4060` as the default formal GPU target after the command, config, outputs, and data paths are known.
- Use `cloud_autodl` for formal runs only when the desktop 4060 is unavailable, insufficient, or explicitly bypassed.
- For `cloud_autodl`, the user creates/starts the instance manually. The workflow connects after SSH is available, saves evidence, archives outputs, and runs `/usr/bin/shutdown` by default.
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

## Remote Desktop 4060 Run Record

When using the desktop RTX 4060, record these fields in `experiment-runbook.md` and `reproducibility-checklist.md`:

| Field | Record |
|---|---|
| SSH reference | SSH alias or host label; do not store password |
| Username/port | only if needed for reconnection |
| Private key | local file path only, never key contents |
| GPU model | RTX 4060, with VRAM when known |
| Fixed CUDA version | desktop CUDA version once confirmed |
| Fixed PyTorch version | desktop PyTorch version once confirmed |
| Environment snapshot | `outputs/EXP-*/environment.txt` or `environment_snapshot.json` |
| Remote project path | code directory on the desktop |
| Remote data path | dataset directory on the desktop |
| Remote env | conda/env activation command |
| Remote command | train/evaluate command |
| Remote log path | log file or directory |
| Remote output path | metrics/checkpoints/predictions directory |
| Remote artifact URI | full run folder or archive URI |
| Remote artifact status | pending/synced/verified/archived/blocked |
| Artifact hash / manifest | checksum file or `manifest.json` |
| Download destination | local artifact path after training |
| Recovery policy | whether to fetch lightweight index only or sync full outputs back to the Mac |

Use macOS Terminal, VS Code SSH, `ssh`, `scp`, and `rsync` for remote desktop handoff. Do not assume MobaXterm on this Mac.

Remote GPU execution sequence:

```text
1. Confirm SSH access and GPU.
2. Confirm project, data, and environment paths.
3. Run or verify a small remote smoke test if the environment is new.
4. Save `outputs/EXP-*/environment.txt` or `environment_snapshot.json` with `scripts/write_environment_snapshot.py`.
5. Start formal training in tmux, screen, nohup, or the platform's preferred background method.
6. Monitor logs and GPU usage.
7. Verify metrics, logs, checkpoints, predictions, and environment snapshot exist.
8. Fetch lightweight result indexes to the Mac and keep full artifacts remote/cloud when appropriate.
9. Update thesis console records with storage backend, remote artifact URI, remote status, and hash/manifest.
10. Stop temporary jobs or free cloud instances if the fallback cloud target was used.
```

## AutoDL Fallback Run Record

When `cloud_autodl` is used instead of `remote_desktop_4060`, record the same remote fields plus the AutoDL instance/image, billed resource, and shutdown/release policy. Treat AutoDL as a fallback target, not the default path.

AutoDL-specific policy:

- The user creates and starts the AutoDL instance manually in the AutoDL web console.
- The kit connects through SSH alias or terminal password prompt; do not store passwords, tokens, account data, or private-key contents in repo files.
- Use `scripts/remote_sync_to_autodl.sh.template` to sync code/config after the instance is reachable.
- Use `scripts/remote_run_autodl_autoshutdown.sh.template` with `AUTO_SHUTDOWN=1` by default. The remote job should write `train.log`, `exit_code.txt`, `autodl_run_summary.json`, an environment snapshot, an archive folder, and `checksums.sha256`, then call `/usr/bin/shutdown`.
- Use `scripts/remote_fetch_autodl_results.sh.template` only after restarting the instance when lightweight evidence needs to be recovered locally.
- Do not mark AutoDL results `reviewed` until the run summary, exit code, checksum file, remote archive URI, local lightweight index, and shutdown status are recorded.

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
| `remote_running` | remote desktop or cloud run is active |
| `remote_recovered` | remote artifacts were downloaded or synced locally |
