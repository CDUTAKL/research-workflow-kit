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
- Use `local_mac` runs for debugging and smoke tests on this Mac; use AutoDL or another cloud GPU for formal training only when the user provides access and asks for remote execution.
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
7. Choose execution target: `local_mac` for smoke tests/debugging, `cloud_autodl` for formal training, or another cloud target when specified.
8. Define reproducibility requirements and remote result recovery.
9. Map runs to `docs/thesis` experiment IDs and runbook entries.
10. Route code implementation, testing, and debugging through normal Codex coding workflows.
11. Hand completed outputs to `$research-results-analysis`.

## Output Contract

Always include:

- experiment objective
- proposed or inspected code architecture
- data pipeline contract
- model/algorithm module contract
- training/evaluation/prediction entrypoints
- config and run naming convention
- logging and output directory convention
- execution target plan: `local_mac` smoke test, AutoDL formal training, or both
- reproducibility checklist
- result recovery and shutdown/release policy for cloud runs
- thesis console files to update
- risks, blockers, and next implementation tasks

If the user only provides a paper idea, produce an architecture plan and runbook draft. If the user provides a codebase, inspect real files before proposing module boundaries.
