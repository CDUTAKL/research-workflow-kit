# Code Architecture Guide

## Default Lightweight Structure

Prefer adapting the existing repository. When creating or reorganizing experiment code, use this shape as the default reference:

```text
src/
  data/ or dataset.py
  models/ or model.py
  train.py
  evaluate.py
  predict.py
  metrics.py
  utils.py

configs/
  data/
  model/
  experiment/

outputs/
  <experiment_id>/
    config_resolved.json
    metrics.json
    predictions.csv
    checkpoints/
    figures/
    logs/

docs/thesis/
  experiment-architecture.md
  experiment-runbook.md
  experiment-registry.md
  claim-evidence-map.md
```

## Boundary Rules

| Boundary | Rule |
|---|---|
| Data code | must not know paper claims |
| Model code | must not know output folders |
| Training code | coordinates data, model, optimizer, logging, checkpointing |
| Evaluation code | computes metrics from fixed model and fixed split |
| Metrics code | defines names and formulas shared by training, evaluation, and tables |
| Reporting code | reads artifacts and prepares tables/figures without changing results |

## Data Pipeline Contract

Each data pipeline should define:

- input paths and expected formats.
- split source and split creation rule.
- preprocessing and feature extraction steps.
- cache/output format if derived data is saved.
- validation checks for missing labels, duplicates, leakage, and shape/schema.

## Model / Algorithm Contract

Each model or algorithm module should define:

- constructor/config keys.
- input and output shapes or schemas.
- training-time behavior.
- evaluation-time behavior.
- baseline/proposed/ablation identity.
- dependencies that affect reproducibility.

## Entry Point Contract

Training and evaluation commands should be stable and copyable into `experiment-runbook.md`.

Minimal command fields:

```text
python src/train.py --config configs/experiment/EXP-001.yaml --out outputs/EXP-001
python src/evaluate.py --config configs/experiment/EXP-001.yaml --checkpoint outputs/EXP-001/checkpoints/best.pt --out outputs/EXP-001
```

Adapt command names to the repo. Do not invent files when reviewing an existing project; propose the nearest local equivalent.

## Optional Tooling

| Tool | Useful for | Default policy |
|---|---|---|
| Hydra | config composition, overrides, multirun sweeps | optional |
| MLflow | run tracking, metrics, artifacts, comparisons | optional |
| DVC | data pipeline stages, params, metrics, plots, reproducibility | optional |
| W&B | dashboards, sweeps, hosted tracking | optional |
| Plain JSON/YAML | simple local reproducibility | default |

Do not add optional tooling unless it removes real project friction.
