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
- Promote results according to `evidence-promotion-policy.md`: `EXP-*` evidence should map to `CLM-*`, `DATA-*`, and any `FIG-*` that visualizes the result.
- Never average incompatible settings or compare runs with different data splits unless explicitly justified.
- For iterative experiments, update or request `autoresearch-results.tsv` verify/guard records before promoting a result.
- For baseline comparisons, create or update `docs/thesis/experiment-reports/EXP-*.md` with `scripts/new_experiment_report.py` before promoting a result.
- For formal benchmark comparisons, update `docs/thesis/benchmark-report-schema.md` with baseline/new values, metric definition, guard checklist, material passport link, and promotion decision.
- For formal `remote_desktop_4060` or cloud runs, confirm the local output index, remote artifact URI, remote status, and artifact hash/manifest before using metrics as thesis evidence.
- For data-backed claims, route dataset traceability gaps to `$research-data-availability`.
- When results may become thesis claim evidence, use Data Analytics-style checks and update `docs/thesis/data-quality-report.md` and `docs/thesis/metric-diagnostics.md` for data quality, metric definitions, baseline deltas, anomaly risks, uncertainty, and failed-run handling.
- Use Build Web Data Visualization as a design and QA guide when turning metrics into charts, dashboard views, baseline-delta visuals, uncertainty displays, or evidence-graph summaries.
- Visual polish must not hide weak baselines, missing variance, incompatible splits, or unsupported claims.

## Workflow

Read `references/workflow.md` for result tables, claim classification, and audit checklists. Read `references/source-map.md` for source provenance.

1. Inventory result files, run configs, metrics, figures, and logs.
2. When a directory of mixed results is provided, optionally run the skill-local `scripts/scan_results.py` to create `docs/thesis/result-scan-summary.md` and `docs/thesis/result-scan-table.csv`.
3. When a thesis console exists, optionally run the skill-local `scripts/result_scan_to_registry.py` to add candidate `EXP-AUTO-*` rows to `docs/thesis/experiment-registry.md`.
4. Check data quality, split integrity, sample/label distributions, missing values, anomaly risks, and leakage risks; record formal checks in `data-quality-report.md` when the result supports a claim.
5. Normalize metric names, datasets/splits, seeds, baselines, and model variants; record formal metric definitions and deltas in `metric-diagnostics.md`.
6. Choose the right statistical summary or test before using words such as significant, robust, or consistent.
7. Audit ground-truth provenance, metric computation, result file existence, scope, and dead-code risks.
8. For advisor-facing or dashboard-facing result visuals, apply Build Web Data Visualization checks: truthful chart choice, readable labels, uncertainty or sample-size visibility when relevant, accessible contrast, and mobile/desktop layout sanity.
9. Update `docs/thesis/experiment-registry.md`, `docs/thesis/claim-evidence-map.md`, `docs/thesis/autoresearch-results.tsv`, `docs/thesis/experiment-reports/`, `docs/thesis/benchmark-report-schema.md`, `docs/thesis/material-passport.md`, and `docs/thesis/data-availability.md` when a thesis console exists and the result is used as evidence; for remote/cloud runs, include storage backend, remote URI, remote status, and hash/manifest.
10. Build a claim table with supported, weak, unsupported, and missing-evidence claims.
11. If code architecture, run commands, machine-readable metrics, or reproducibility records are missing, route fixes to `$research-experiment-engineering`.
12. Hand off figure/table requirements to `$research-paper-figures` and propose follow-up experiments only when they unblock a paper claim.

## Output Contract

Always include:

- experiment inventory
- metric table
- local/remote artifact trace
- best result summary
- comparison conclusions
- ablation conclusions
- exploratory data quality notes
- data quality report status when results become evidence
- statistical analysis decision
- metric diagnostics status for baseline or formal comparisons
- experiment integrity risks
- anomalies and risks
- figure/table handoff
- chart/design QA notes when a result visual or dashboard chart is requested
- thesis console update targets when applicable
- supported claims
- unsupported claims
- missing experiments
- experiment-engineering fixes when outputs are not traceable or reproducible
- autoresearch verify/guard status when results are part of iterative improvement
- experiment report path and baseline delta when a formal comparison exists
- benchmark report schema update when a result is compared against a baseline
- material passport follow-ups for evidence-critical outputs
- data availability follow-ups for claim-supporting artifacts

If the user supplies only prose without artifacts, state that the analysis is provisional and ask for result files or tables.
