# Benchmark Report Schema

## Purpose

Use this file to standardize baseline comparisons, 4060 formal experiment reports, and thesis benchmark claims.

This is a lightweight schema, not a tracking server. It keeps benchmark comparisons honest: same data split, same metric definition, known environment, clear baseline, and conservative claim promotion.

## Update Rules

- Create or update one benchmark report before promoting an `EXP-*` result to a strong `CLM-*`.
- Record baseline and new run under the same metric definition and split.
- Link the benchmark report to `experiment-registry.md`, `autoresearch-results.tsv`, `experiment-reports/`, `material-passport.md`, and `data-availability.md`.
- For `remote_desktop_4060` runs, environment snapshot status must be explicit.

## Benchmark Registry

| Benchmark ID | Claim ID | New Experiment | Baseline Experiment | Dataset / Split | Primary Metric | Baseline Value | New Value | Delta | Run Target | Environment Snapshot | Material Passport | Data ID | Guard Status | Promotion Decision | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BMK-001 | CLM-001 | EXP-001 | EXP-000/TBD | DATA-001/TBD | accuracy/F1/AUC/TBD | TBD | TBD | TBD | local_mac / remote_desktop_4060 / cloud_autodl / TBD | missing / recorded / not_applicable / TBD | MAT-001/TBD | DATA-001/TBD | pending | do_not_promote / weak_support / promote_with_caveat / promote / TBD |  |

## Metric Definition

| Benchmark ID | Metric | Definition | Direction | Aggregation | Confidence / Variance | Statistical Test | Notes |
|---|---|---|---|---|---|---|---|
| BMK-001 | TBD | exact formula / script / library / TBD | higher_is_better / lower_is_better / TBD | mean / median / per-class / TBD | CI/std/seeds/TBD | paired t-test / bootstrap / none / TBD |  |

## Guard Checklist

| Benchmark ID | Same Split? | Same Preprocessing? | Same Metric Code? | Leakage Checked? | Seed Recorded? | Config Resolved? | Output Manifest? | Guard Status |
|---|---|---|---|---|---|---|---|---|
| BMK-001 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | pending |

## Claim Promotion Rule

| Decision | Meaning |
|---|---|
| `do_not_promote` | Result is incomplete, not comparable, or failed guard checks |
| `weak_support` | Direction is promising but evidence is too weak for a strong thesis claim |
| `promote_with_caveat` | Supports claim with scope limits, variance, or dataset caveats |
| `promote` | Supports claim and passes verify/guard/data/material checks |
