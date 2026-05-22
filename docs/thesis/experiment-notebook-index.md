# Experiment Notebook Index

## Update Rules

- Register every thesis notebook here before using its outputs in the manuscript.
- Keep notebooks reproducible: record inputs, expected outputs, and linked console files.
- Do not treat exploratory notebook observations as paper claims until they are reviewed in `claim-evidence-map.md`.

## Notebook Registry

| Notebook | Purpose | Inputs | Outputs | Linked Experiments | Linked Claims | Status | Notes |
|---|---|---|---|---|---|---|---|
| `notebooks/thesis/01_data_audit.ipynb` | Data audit and leakage checks | raw data / split files | audit notes | TBD | TBD | template | Fill project paths before running |
| `notebooks/thesis/02_result_summary.ipynb` | Reviewed metric summaries | `result-scan-table.csv` / manual result tables | candidate summaries | TBD | TBD | template | Use after result scan |
| `notebooks/thesis/03_error_analysis.ipynb` | Failure-mode analysis | predictions / residuals / confusion data | error groups and limitations | TBD | TBD | template | Use after stable predictions exist |
| `notebooks/thesis/04_figure_preparation.ipynb` | Prepare figure/table input data | reviewed result tables | `docs/thesis/figure-data/` | TBD | TBD | template | Styling is deferred |

## Handoff Rules

| Notebook Output | Review Destination | Final Use |
|---|---|---|
| Data audit findings | `experiment-registry.md` and `final-audit.md` | Methods and experiment validity |
| Metric summaries | `experiment-registry.md` | Result tables and comparisons |
| Error analysis observations | `claim-evidence-map.md` | Limitations and future work |
| Figure input data | `figure-plan.md` | Publication figures and tables |
