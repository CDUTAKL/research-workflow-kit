# Experiment Records

## Notebook Role

Use `$jupyter-notebook` when an experiment needs exploratory analysis, reproducible metric summaries, ablation notes, or tutorial-style documentation for future readers.

Recommended thesis notebook index:

| Notebook | Purpose | Inputs | Outputs | Related claim | Status |
|---|---|---|---|---|---|

## Experiment Engineering Role

Use `$research-experiment-engineering` before result analysis when the work involves architecture planning, data pipeline design, model or algorithm module boundaries, training/evaluation entrypoints, config management, local smoke tests, AutoDL/cloud formal training, logging/output conventions, artifact recovery, or reproducibility.

Engineering console files:

| File | Purpose |
|---|---|
| `docs/thesis/experiment-architecture.md` | planned data/model/train/evaluate architecture |
| `docs/thesis/experiment-runbook.md` | exact commands, expected outputs, monitoring and failure handling |
| `docs/thesis/reproducibility-checklist.md` | environment, split, seed, config, code version, artifacts, rerun command |

Execution target policy:

| Target | Role |
|---|---|
| `local` | debug, smoke test, small sample, output-format check |
| `cloud_autodl` | formal full-data training, baselines, ablations, multi-seed runs |
| `cloud_other` | RunPod, Colab, Kaggle, school server, or another remote target |

For AutoDL, record only SSH alias/host label, remote paths, environment, GPU, result recovery path, and shutdown policy. Do not record passwords, token values, or private-key contents.

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
- `cloud-running`
- `cloud-recovered`

## Result Handoff

After experiment code is planned and runs are recorded:

1. Use `$research-experiment-engineering` to define architecture, execution target, run commands, outputs, and reproducibility checks.
2. Use Codex coding workflows to implement or refactor the data/model/train/evaluate code.
3. Run local smoke tests before paid or long-running cloud training.
4. Use AutoDL/cloud only after command, config, data path, output path, and recovery plan are known.
5. Use `$jupyter-notebook` for reproducible exploratory checks when needed.
6. Use `$research-results-analysis` to normalize metrics and identify supported claims.
7. Use `$research-paper-figures` to plan and generate visuals from the same traceable data.
8. Update the claim-evidence map before drafting result prose.

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
- remote path and recovered artifact path for cloud runs
- date or run identifier
- known limitations
