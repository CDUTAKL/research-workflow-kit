# Autoresearch Loop Reference

## Iteration Fields

Use these fields in `autoresearch-results.tsv`:

```text
iteration, date, experiment_id, branch, commit, target, change_summary,
primary_metric, baseline_value, new_value, delta, verify_status,
guard_status, decision, notes
```

## Verify Gate

The verify gate checks whether the iteration answered the intended question.

| Status | Meaning |
|---|---|
| `pass` | metric or evidence improved under the stated protocol |
| `fail` | no improvement or hypothesis rejected |
| `inconclusive` | result exists but cannot answer the question |
| `pending` | not reviewed |

## Guard Gate

The guard gate checks whether the result is safe to use.

| Guard Check | Failure Example |
|---|---|
| Data leakage | validation data appears in training |
| Config comparability | baseline and proposed run use different splits |
| Metric integrity | metric code does not match claim wording |
| Artifact reality | registry points to missing output files |
| Scope discipline | result from one seed is described as robust |

## Recording Command

```bash
python scripts/new_autoresearch_iteration.py \
  --experiment-id EXP-001 \
  --target-claim CLM-001 \
  --change-summary "TBD" \
  --primary-metric accuracy \
  --baseline-value 0.80 \
  --new-value 0.82 \
  --verify-status pass \
  --guard-status pending \
  --decision pending
```

