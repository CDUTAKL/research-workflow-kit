# Research Experiment Engineering Workflow

## 4A. Experiment Architecture Planning

Start by turning a thesis claim or research question into an executable experiment plan.

| Output | Required content |
|---|---|
| Design decision | What experiment answers the question and why |
| Target files/modules | Existing or proposed source files |
| Expected command | How a run should start |
| Expected outputs | Config, metrics, predictions, logs, artifacts |
| Thesis console update | `experiment-architecture.md`, `experiment-runbook.md` |
| Risks/blockers | Missing data, unclear metric, missing baseline, unstable scope |

Architecture questions:

- What claim will this experiment support or reject?
- What data split and metric are required?
- What baseline or ablation is needed?
- What code modules need to exist before running?
- What output files must exist before `$research-results-analysis` can evaluate the result?

## 4B. Data Pipeline Design

Define the contract between raw data and train/evaluate scripts.

| Decision | Requirement |
|---|---|
| Input format | raw files, tables, tensors, images, signals, text, or domain-specific format |
| Split contract | train/validation/test source, seed, stratification, leakage checks |
| Transform contract | preprocessing, feature extraction, augmentation, normalization |
| Output contract | dataset object, arrays, files, or cached features |
| Audit handoff | `notebooks/thesis/01_data_audit.ipynb` and `experiment-registry.md` |

Rules:

- Data code must not know paper claims.
- Data splits must be stable and recorded.
- Preprocessing decisions that affect metrics must be configurable or documented.
- Cache files must record their source data and transform version when possible.

## 4C. Model / Algorithm Module Design

Define model and algorithm boundaries before training scripts are written.

| Component | Contract |
|---|---|
| Baseline | minimal method needed for comparison |
| Proposed method | new or improved component under test |
| Ablation switches | feature flags or config keys that remove key components |
| Inference interface | input shape/type, output shape/type, postprocessing |
| Metric dependency | what predictions and labels metrics need |

Rules:

- Model code must not know output folders.
- Baselines and proposed methods should share the same evaluation path.
- Ablation controls should be explicit rather than hidden code edits.
- Domain-specific assumptions should be documented near config or method notes.

## 4D. Training / Evaluation Script Design

Define stable command-line or config-driven entrypoints.

| Entrypoint | Purpose | Required outputs |
|---|---|---|
| `train.py` | fit model and save checkpoint/metrics | resolved config, log, checkpoint, train/val metrics |
| `evaluate.py` | compute final metrics on fixed split | metrics JSON/CSV, predictions when applicable |
| `predict.py` | produce predictions for analysis or figures | predictions CSV/JSON and metadata |
| `metrics.py` | shared metric definitions | documented formulas and names |

Rules:

- Important scripts must fail loudly when required paths or config keys are missing.
- Evaluation should be runnable without retraining when checkpoints exist.
- Machine-readable metrics are required for thesis evidence.
- Human-readable logs are useful but not sufficient.

## 4E. Config, Logging, And Output Convention

Default to plain JSON/YAML and stable output directories. Use Hydra, MLflow, DVC, or W&B only when the project already uses them or the user explicitly wants them.

Recommended output shape:

```text
outputs/<experiment_id>/
  config_resolved.json
  metrics.json
  predictions.csv
  checkpoints/
  figures/
  logs/
  manifest.json
```

Run naming rules:

- Use stable experiment IDs such as `EXP-001`.
- Include timestamp or run suffix only below the experiment ID, not instead of it.
- Record seed, split, config, and output path in `experiment-registry.md`.
- Keep comparable runs under consistent config and output conventions.

## 4F. Local Smoke Test And AutoDL Formal Training

Use a two-level execution strategy when this Mac is only suitable for smoke tests and the user has access to AutoDL.

| Target | Role | Typical scope | Record |
|---|---|---|---|
| `local_mac` | debug and smoke test | CPU / Apple Silicon / MPS when supported, small sample, 1 epoch, short run, output-format check | local command, local output path, known failures |
| `cloud_autodl` | formal training | full dataset, full epochs, baselines, ablations, multi-seed runs | SSH alias, remote paths, GPU/env, run command, result recovery |

Local smoke test must verify:

- code starts with the intended config.
- data can be loaded.
- forward/backward or evaluation step runs.
- loss and metrics are finite.
- output directory, log, and metrics files are created.
- the command is ready to move to AutoDL.

AutoDL formal training must record:

- SSH alias or host label, not the password or private-key contents.
- GPU model and AutoDL image/environment when available.
- remote project path and remote data path.
- conda/env activation command.
- exact train/evaluate command.
- remote log path and remote output path.
- artifact download destination.
- shutdown/release policy after completion.

Safe credential rule:

```text
Record only SSH alias, host label, username, port, and private-key file path when needed.
Never record passwords, token values, or private-key contents in docs/thesis or git-tracked files.
```

## 4G. Run, Monitor, Reproduce, And Paper Mapping

Every important experiment should have a runbook row before or immediately after execution.

| Step | Record |
|---|---|
| Run | command, config, seed, expected duration |
| Monitor | log path, early failure signs, checkpoint expectations |
| Reproduce | environment, data split, code version, rerun command |
| Map to paper | claim ID, figure/table ID, result-analysis handoff |

Handoff sequence:

```text
$research-experiment-engineering
  -> code implementation/debugging with Codex
  -> local_mac smoke test
  -> AutoDL formal training when needed
  -> result download/recovery
  -> run outputs and registry updates
  -> $research-results-analysis
  -> $research-paper-figures
  -> $research-paper-writing
```

## Final Output Checklist

- Architecture separates data, model, train, evaluate, metrics, and outputs.
- Every run has an experiment ID and output directory.
- Metrics are machine-readable.
- Config and seed are recorded.
- Data split and metric definitions are visible.
- Local smoke test passes before paid cloud training.
- AutoDL runs have remote paths, result recovery, and shutdown policy recorded.
- Reproducibility risks are explicit.
- Completed outputs are ready for `$research-results-analysis`.
