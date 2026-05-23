# Autoresearch Loop

## Update Rules

- Use this file to run human-supervised experiment iteration, not unattended autonomous research.
- Every loop should have a claim, hypothesis, expected artifact, verify gate, guard gate, and human decision.
- Record iteration rows in `autoresearch-results.tsv` and resume state in `autoresearch-state.json`.
- Formal GPU work should use `remote_desktop_4060`; `cloud_autodl` remains fallback.

## Loop Contract

| Field | Value |
|---|---|
| Target claim | CLM-001/TBD |
| Current best experiment | EXP-001/TBD |
| Primary metric | TBD |
| Verify gate | metric/claim improvement to check |
| Guard gate | tests, leakage, config, stability, and overclaim checks |
| Human confirmation needed? | yes |

## Iteration Plan

| Iteration | Candidate Experiment | Change | Expected Improvement | Smoke Test | Remote Target | Verify Gate | Guard Gate | Decision | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | EXP-001/TBD | TBD | TBD | local_mac | remote_desktop_4060 | pending | pending | pending | planned |

## Integrity Audit

| Risk | Check | Status | Notes |
|---|---|---|---|
| Fake ground truth | labels/splits come from real source | pending |  |
| Data leakage | train/val/test separation verified | pending |  |
| Phantom result | output files and metrics exist on disk | pending |  |
| Scope inflation | claim wording matches datasets/seeds/settings | pending |  |
| Config drift | compared runs use compatible configs | pending |  |

