---
name: research-experiment-engineering
description: Use when planning, implementing, reviewing, or refactoring research experiment code, including experiment architecture, data pipelines, model or algorithm modules, training/evaluation scripts, config management, logging/output conventions, reproducibility checks, and mapping code runs to thesis experiments.
---

# Research Experiment Engineering

Use this skill before result analysis when a research project needs experiment code that can be implemented, run, traced, and reproduced. It turns a paper claim or experiment idea into code architecture, run conventions, and thesis-console records.

## Core Rules

- Design the experiment workflow before writing or changing code.
- Separate data pipeline, model/algorithm logic, training, evaluation, metrics, and reporting.
- Prefer the existing repo style and minimal dependencies over importing a full MLOps stack.
- Require machine-readable outputs for important runs: config, metrics, predictions when applicable, logs, and artifacts.
- Map every important run to an experiment ID in `docs/thesis/experiment-registry.md`.
- Use `local_mac` for orchestration and CPU-only smoke tests on this Mac; use `remote_desktop_4060` as the primary formal GPU experiment target; use `cloud_autodl` or another cloud target only as a fallback when the desktop 4060 is unavailable or insufficient.
- Treat the desktop CUDA/PyTorch profile as fixed when the user confirms it, but still save `outputs/EXP-*/environment.txt` for every formal 4060 evidence run.
- Treat `docs/thesis/experiment-architecture.md` as the global experiment blueprint: claim map, data flow, module boundaries, config/output contract, baseline/metric policy, and remote storage plan.
- Use the local-index plus remote-artifact model for formal runs: fetch lightweight `outputs/EXP-*` evidence to the Mac, keep full logs/checkpoints/predictions on `remote_desktop_4060` or another archive backend, and record URI/hash/status in `experiment-registry.md`.
- Use `$research-code-quality` or `scripts/check_experiment_contract.py` before expensive remote GPU runs.
- Use `$research-autoresearch-loop` when a run is part of iterative method improvement.
- Never write SSH passwords, private-key contents, or long-lived credentials into project files.
- Hand completed outputs to `$research-results-analysis`; do not make final paper claims inside this skill.

## Workflow

Read `references/workflow.md` for the six-stage engineering flow. Read `references/code-architecture.md` for module and file conventions. Read `references/run-and-reproducibility.md` for run, output, and reproducibility checks. Read `references/source-map.md` for provenance.

1. Identify the research question, planned claim, and experiment type.
2. Inspect or propose the project architecture.
3. Define the data pipeline contract.
4. Define the model or algorithm module contract.
5. Define train, evaluate, and predict script interfaces.
6. Define config, run naming, logging, metrics, checkpoints, predictions, and artifact outputs.
7. Define the experiment contract: config, seed, split, metric, output path, registry row, and smoke config.
8. Choose execution target: `local_mac` for smoke tests/debugging, `remote_desktop_4060` for primary formal GPU training/evaluation, `cloud_autodl` as fallback, or another cloud target when specified.
9. Define reproducibility requirements, remote artifact URI/hash policy, and local lightweight result recovery.
10. Map runs to `docs/thesis` experiment IDs and runbook entries.
11. Route code implementation, testing, and debugging through normal Codex coding workflows.
12. For iterative runs, record verify/guard outcomes through `$research-autoresearch-loop`.
13. Hand completed outputs to `$research-results-analysis`.

## Output Contract

Always include:

- experiment objective
- proposed or inspected code architecture
- data pipeline contract
- model/algorithm module contract
- training/evaluation/prediction entrypoints
- config and run naming convention
- logging and output directory convention
- experiment contract check command
- execution target plan: `local_mac` smoke test, `remote_desktop_4060` formal training with environment snapshot, `cloud_autodl` fallback, or a documented combination
- storage plan: local output index, remote artifact URI, remote status, and artifact hash/manifest
- reproducibility checklist
- autoresearch verify/guard handoff when the run is part of iteration
- result recovery and shutdown/release policy for remote or cloud runs
- thesis console files to update
- risks, blockers, and next implementation tasks

If the user only provides a paper idea, produce an architecture plan and runbook draft. If the user provides a codebase, inspect real files before proposing module boundaries.
