# Experiment Records

## Notebook Role

Use `$jupyter-notebook` when an experiment needs exploratory analysis, reproducible metric summaries, ablation notes, or tutorial-style documentation for future readers.

Recommended thesis notebook index:

| Notebook | Purpose | Inputs | Outputs | Related claim | Status |
|---|---|---|---|---|---|

## Experiment Engineering Role

Use `$research-experiment-engineering` before result analysis when the work involves architecture planning, data pipeline design, model or algorithm module boundaries, training/evaluation entrypoints, config management, `local_mac` CPU-only smoke tests, `remote_desktop_4060` primary GPU runs, `cloud_autodl` fallback training, logging/output conventions, artifact recovery, or reproducibility. Use `$research-code-quality` for experiment contracts and `$research-autoresearch-loop` for iterative verify/guard records.

Engineering console files:

| File | Purpose |
|---|---|
| `docs/thesis/experiment-architecture.md` | planned data/model/train/evaluate architecture |
| `docs/thesis/experiment-runbook.md` | exact commands, expected outputs, monitoring and failure handling |
| `docs/thesis/reproducibility-checklist.md` | environment, split, seed, config, code version, artifacts, rerun command |
| `docs/thesis/experiment-integrity-checklist.md` | leakage, metric, config, artifact, and scope checks |
| `docs/thesis/autoresearch-results.tsv` | iteration result log and verify/guard status |
| `docs/thesis/autoresearch-state.json` | resumable iteration state |
| `docs/thesis/data-availability.md` | source data, processed data, artifacts, access, and hash records |

Execution target policy:

| Target | Role |
|---|---|
| `local_mac` | Mac research console, CPU-only smoke test, small sample, output-format check |
| `remote_desktop_4060` | primary formal GPU target on the user's RTX 4060 desktop |
| `cloud_autodl` | stronger fallback GPU target when the desktop 4060 is unavailable or insufficient |
| `cloud_other` | RunPod, Colab, Kaggle, school server, or another remote target |

For remote targets, record only SSH alias/host label, remote paths, environment, GPU, result recovery path, and shutdown/release policy when relevant. Do not record passwords, token values, or private-key contents.

## Experiment Registry

Track experiments in `docs/thesis/experiment-registry.md` or an equivalent project file.

| Experiment | Config/run path | Data split | Metrics | Figure/table | Claim supported | Status |
|---|---|---|---|---|---|---|

Status values:

- `planned`
- `running`
- `complete`
- `failed`
- `needs-rerun`
- `not-comparable`
- `ready-to-run`
- `completed-unreviewed`
- `remote-running`
- `remote-recovered`

## Result Handoff

After experiment code is planned and runs are recorded:

1. Use `$research-experiment-engineering` to define architecture, execution target, run commands, outputs, and reproducibility checks.
2. Use Codex coding workflows to implement or refactor the data/model/train/evaluate code.
3. Run `$research-code-quality` or `scripts/check_experiment_contract.py` before remote GPU training.
4. Run `local_mac` CPU-only smoke tests before long-running remote GPU training.
5. Use `remote_desktop_4060` as the primary formal GPU target only after command, config, data path, output path, and recovery plan are known.
6. Use `cloud_autodl` only as a fallback when the desktop 4060 is unavailable or insufficient.
7. Use `$research-autoresearch-loop` when the run is part of a method-improvement iteration.
8. Use `$jupyter-notebook` for reproducible exploratory checks when needed.
9. Use `$research-results-analysis` to normalize metrics and identify supported claims.
10. Use `$research-data-availability` when outputs become claim evidence.
11. Use `$research-paper-figures` to plan and generate visuals from the same traceable data.
12. Update the claim-evidence map before drafting result prose.

## Minimum Reproducibility Notes

Each important result should have:

- data source or split
- configuration path or key hyperparameters
- random seed count or single-seed warning
- metric definition
- command or notebook
- execution target and hardware
- code version when available
- output path
- remote path and recovered artifact path for desktop or cloud GPU runs
- date or run identifier
- known limitations
