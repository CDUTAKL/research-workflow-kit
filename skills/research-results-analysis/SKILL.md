---
name: research-results-analysis
description: Use when analyzing experiment outputs, logs, metrics, result folders, ablation tables, baseline comparisons, robustness checks, error analysis, or when turning empirical results into conservative research-paper claims.
---

# Research Results Analysis

Use this skill to transform raw experiment artifacts into trustworthy summaries and defensible paper claims. Treat result files, configs, logs, and plots as evidence that must be traced before it becomes prose.

## Core Rules

- Inspect real artifacts whenever paths are provided.
- Run an exploratory data quality pass before interpreting metrics.
- Distinguish main results, baselines, ablations, robustness checks, and error analysis.
- Report uncertainty, missing baselines, failed runs, inconsistent metrics, and statistical limitations.
- Audit experiment integrity before turning results into paper claims.
- Convert results into conservative claims only when the evidence supports them.
- Never average incompatible settings or compare runs with different data splits unless explicitly justified.

## Workflow

Read `references/workflow.md` for result tables, claim classification, and audit checklists. Read `references/source-map.md` for source provenance.

1. Inventory result files, run configs, metrics, figures, and logs.
2. When a directory of mixed results is provided, optionally run `scripts/scan_results.py` to create `docs/thesis/result-scan-summary.md` and `docs/thesis/result-scan-table.csv`.
3. When a thesis console exists, optionally run `scripts/result_scan_to_registry.py` to add candidate `EXP-AUTO-*` rows to `docs/thesis/experiment-registry.md`.
4. Check data quality, split integrity, sample/label distributions, missing values, and anomaly risks.
5. Normalize metric names, datasets/splits, seeds, baselines, and model variants.
6. Choose the right statistical summary or test before using words such as significant, robust, or consistent.
7. Audit ground-truth provenance, metric computation, result file existence, scope, and dead-code risks.
8. Update `docs/thesis/experiment-registry.md` and `docs/thesis/claim-evidence-map.md` when a thesis console exists.
9. Build a claim table with supported, weak, unsupported, and missing-evidence claims.
10. If code architecture, run commands, machine-readable metrics, or reproducibility records are missing, route fixes to `$research-experiment-engineering`.
11. Hand off figure/table requirements to `$research-paper-figures` and propose follow-up experiments only when they unblock a paper claim.

## Output Contract

Always include:

- experiment inventory
- metric table
- best result summary
- comparison conclusions
- ablation conclusions
- exploratory data quality notes
- statistical analysis decision
- experiment integrity risks
- anomalies and risks
- figure/table handoff
- thesis console update targets when applicable
- supported claims
- unsupported claims
- missing experiments
- experiment-engineering fixes when outputs are not traceable or reproducible

If the user supplies only prose without artifacts, state that the analysis is provisional and ask for result files or tables.
