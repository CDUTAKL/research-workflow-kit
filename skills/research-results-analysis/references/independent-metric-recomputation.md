# Independent Metric Recalculation

Use this procedure for the primary numeric claims that may be promoted into the thesis. It checks arithmetic and sample alignment from saved predictions independently of the training run's aggregate `metrics.json`.

## Input Contract

Prepare a long-format UTF-8 CSV with one row per sample and model:

```csv
sample_id,model_id,y_true,y_pred,cluster_id
origin-001,baseline,0.25,0.27,day-001
origin-001,candidate,0.25,0.24,day-001
```

`sample_id` must identify a unique forecast or observation within each model. `cluster_id` must name the prespecified independent/dependence unit, such as a day or site. Keep the same truth values and sample set for paired model comparisons.

## Run

```bash
python scripts/recompute_prediction_metrics.py \
  --input outputs/EXP-001/predictions.csv \
  --out outputs/EXP-001/independent-metrics.json \
  --baseline-model baseline \
  --candidate-model candidate \
  --cluster-column cluster_id \
  --bootstrap-resamples 2000 \
  --seed 20261016 \
  --experiment-id EXP-001 \
  --protocol-sha256 <frozen-protocol-sha256>
```

The script reports `n`, MAE, RMSE, and mean prediction error per model. With a paired comparison, it reports candidate-minus-baseline deltas and 95% paired cluster-bootstrap percentile intervals. Negative deltas favor the candidate for MAE and RMSE. The interval is descriptive evidence, not an automatic significance verdict.

## Review And Record

1. Confirm that the metric, direction, comparison, analysis unit, and cluster column match the frozen protocol in `experiment-integrity-checklist.md`.
2. Confirm that both models have identical sample IDs, truth values, and cluster assignments. The script rejects mismatched paired inputs.
3. Compare the recomputed values against run-level metrics, experiment reports, tables, figures, and manuscript text. Record discrepancies; never overwrite raw run files to make them agree.
4. If the predictions or protocol do not support the planned uncertainty calculation, report the limitation and route the statistical choice to `$nature-statistics` or a domain statistician.
5. Record the script version, command, input hash, output path/hash, seed, and comparison in the experiment report and `claim-evidence-map.md` before promoting a numeric claim.

This tool covers regression predictions. It does not validate target construction, causal availability, data leakage, calibration, classification metrics, or the scientific appropriateness of the chosen cluster unit; those checks remain in the experiment protocol and integrity review.
