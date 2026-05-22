# Experiment Architecture

## Update Rules

- Use this file before writing or refactoring experiment code.
- Keep the architecture project-specific but claim-aware: each experiment should support, weaken, or reject a thesis claim.
- Update this file when data, model, training, evaluation, config, or output conventions change.
- When a new advisor topic is received, import the initial experiment needs from `topic-intake.md`.

## Research Question And Experiment Objective

| Item | Content | Status |
|---|---|---|
| Research question | TBD | draft |
| Experiment objective | TBD | draft |
| Target claim ID | CLM-001/TBD | draft |
| Experiment family | baseline/proposed/ablation/robustness/error-analysis/TBD | draft |

## Data Pipeline

| Component | Decision | Target Files / Modules | Risks |
|---|---|---|---|
| Raw input format | TBD | TBD | TBD |
| Split rule | TBD | TBD | leakage/scope/TBD |
| Preprocessing | TBD | TBD | TBD |
| Feature extraction | TBD | TBD | TBD |
| Data audit | `notebooks/thesis/01_data_audit.ipynb` | TBD | TBD |

## Model / Algorithm Modules

| Module | Role | Target Files / Modules | Config Keys | Notes |
|---|---|---|---|---|
| Baseline | comparison | TBD | TBD |  |
| Proposed method | main method | TBD | TBD |  |
| Ablation switch | remove/test component | TBD | TBD |  |
| Metric code | shared evaluation | TBD | TBD |  |

## Entrypoints

| Entrypoint | Purpose | Expected Command | Expected Outputs | Status |
|---|---|---|---|---|
| Train | fit model | TBD | config, logs, checkpoint, train/val metrics | planned |
| Evaluate | final metrics | TBD | metrics.json/csv, predictions if applicable | planned |
| Predict | prediction export | TBD | predictions.csv/json | planned |

## Config And Output Structure

| Area | Convention | Example / Path |
|---|---|---|
| Config location | TBD | `configs/experiment/EXP-001.yaml` |
| Output location | stable experiment ID | `outputs/EXP-001/` |
| Metrics | machine-readable | `metrics.json` |
| Logs | human-readable | `logs/` |
| Checkpoints | reusable for evaluation | `checkpoints/` |
| Predictions | error analysis and figures | `predictions.csv` |

## Implementation Tasks

| Task | Target Files | Owner | Status | Notes |
|---|---|---|---|---|
| Define data loader | TBD | TBD | planned |  |
| Define baseline | TBD | TBD | planned |  |
| Define proposed method | TBD | TBD | planned |  |
| Define train/evaluate entrypoints | TBD | TBD | planned |  |
| Define output manifest | TBD | TBD | planned |  |

## Risks And Blockers

| Risk | Impact | Detection | Mitigation | Status |
|---|---|---|---|---|
| Missing baseline | weak comparison | experiment plan review | implement baseline | open |
| Split leakage | invalid result | data audit | fixed split and duplicate checks | open |
| No machine-readable metrics | cannot scan/analyze results | output check | save metrics JSON/CSV | open |
