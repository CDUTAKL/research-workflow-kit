# Spreadsheet Exports

## Update Rules

- Use spreadsheets for reviewable tables, manual filtering, supervisor sharing, and manuscript table preparation.
- Keep source records in Markdown, CSV, notebooks, or result files; spreadsheets are export/review artifacts.
- Record every spreadsheet export and whether it is derived from reviewed data.

## Export Registry

| Export ID | Spreadsheet | Source File(s) | Purpose | Owner | Review Status | Last Updated | Notes |
|---|---|---|---|---|---|---|---|
| XLS-001 | `literature-matrix.xlsx` | `literature-matrix.md` | literature review table | TBD | pending | TBD |  |
| XLS-002 | `experiment-results.xlsx` | `experiment-registry.md`, `result-scan-table.csv` | result review and table drafting | TBD | pending | TBD |  |
| XLS-003 | `claim-evidence-map.xlsx` | `claim-evidence-map.md` | claim audit and supervisor review | TBD | pending | TBD |  |

## Recommended Spreadsheet Uses

| Use | Source | Destination |
|---|---|---|
| Literature matrix review | `literature-matrix.md` | `literature-matrix.xlsx` |
| Main result table | reviewed metrics CSV / notebook summary | `main-results.xlsx` |
| Ablation table | reviewed experiment outputs | `ablation-results.xlsx` |
| Claim-evidence review | `claim-evidence-map.md` | `claim-evidence-map.xlsx` |
| Final audit issue table | `final-audit.md` | `final-audit.xlsx` |

## Review Rules

- Mark spreadsheets as `draft`, `reviewed`, or `stale`.
- Do not paste unreviewed scan output directly into the thesis table.
- If a spreadsheet value differs from the source file, fix the source or record the reason.
- For final manuscript tables, trace every number back to an experiment ID and output path.
