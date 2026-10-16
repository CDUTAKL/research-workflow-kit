# Experiment Integrity Checklist

## Update Rules

- Use this file before expensive remote GPU runs and before promoting results into claims.
- This checklist catches experimental validity issues that normal code tests may miss.
- Link each serious issue to `experiment-registry.md`, `reproducibility-checklist.md`, or `claim-evidence-map.md`.

## Integrity Checks

| Check | Affected Experiment | Evidence | Status | Required Fix |
|---|---|---|---|---|
| Ground truth source is real and documented | EXP-001/TBD | TBD | pending |  |
| No train/validation/test leakage | EXP-001/TBD | TBD | pending |  |
| Metric code matches claim wording | EXP-001/TBD | TBD | pending |  |
| Compared methods use compatible configs | EXP-001/TBD | TBD | pending |  |
| Result files exist and match registry paths | EXP-001/TBD | TBD | pending |  |
| Claim scope matches datasets/seeds/settings | CLM-001/TBD | TBD | pending |  |

## Frozen Protocol Record

Create one record per confirmatory experiment before its first formal run. Keep later versions and deviations as dated entries; do not replace the original protocol.

| Field | Frozen value |
|---|---|
| Experiment ID | EXP-001/TBD |
| Freeze date, author, and protocol version | TBD |
| Code commit and config/protocol SHA-256 | TBD |
| Research question and primary hypothesis | TBD |
| Primary outcome, metric definition, and direction | TBD |
| Primary baseline and planned comparison | TBD |
| Analysis unit and paired/cluster structure | TBD |
| Dataset, split, exclusions, and preprocessing | TBD |
| Seeds, model-selection rule, and compute budget | TBD |
| Stopping rule and handling of failed runs | TBD |
| Planned secondary analyses and multiplicity handling | TBD |
| Planned test-set access and release condition | TBD |

The primary metric, comparison, analysis unit, and selection/stopping rules must be fixed before test results are inspected. Changes after results become visible require a dated deviation entry with reason and affected analyses.

## Test-Set Access Log

Record each event that exposes test-set rows or summaries, including automated scripts and dashboard reports. Do not record credentials or private raw data here.

| Date/time | Experiment ID | Stage / actor | Access level | Purpose and output exposed | Decision made after access | Protocol changed? | Evidence path |
|---|---|---|---|---|---|---|---|
| TBD | EXP-001 | TBD | not_loaded / summary_seen / row_level | TBD | TBD | no / yes + deviation link | TBD |

`not_loaded` means the test split was not read; `summary_seen` means aggregate test results were visible; `row_level` means per-sample results were inspected. If the test set informed model, threshold, feature, or protocol selection, mark that exposure and treat later test metrics as selection-informed rather than untouched confirmation.

