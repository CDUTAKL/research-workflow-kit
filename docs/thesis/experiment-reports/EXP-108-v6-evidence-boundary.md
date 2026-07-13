# EXP-108/V6 Evidence Boundary

## Evidence identity

- Proposed method: `event_deferral_v6_aligned` (V6).
- Strong internal comparator: `behavior_concat_v5`.
- Prediction join key: `(seed, split, forecast_origin, timestamp, node_id, horizon)`.
- Audited paired rows: 11,753,940.
- Evaluation contract: `docs/thesis/event-label-contract.md`, with `event_scope=exp108_target_timestamp`.

## Supported results

| Comparison / scope | V6 MAE | Comparator MAE | Delta (V6 - comparator) | Interpretation |
|---|---:|---:|---:|---|
| `behavior_concat_v5`, global | 0.021127672 | 0.021384258 | -0.000256586 | 1.1999% relative reduction |
| `behavior_concat_v5`, target-time event | 1.601056512 | 1.606118403 | -0.005061892 | small event-scope reduction |
| `behavior_concat_v5`, active stable | 0.259417970 | 0.257937975 | +0.001479995 | 内部锚点在该子组略低；应作为分层异质性报告 |
| `behavior_concat_v5`, positive load | 0.438207324 | 0.435479162 | +0.002728163 | 内部锚点在该子组略低；应作为分层异质性报告 |

The global paired grouped-bootstrap CI is below zero under both forecast-origin and timestamp clustering. This supports a global MAE improvement over the internal comparator under the stated protocol.

## Conditional component effects

The counterfactual effects are conditional, not an additive causal decomposition:

| Toggle added to the stated comparator | Global MAE change | Relative reduction |
|---|---:|---:|
| Event switching: full V6 vs no-event-switch (calibration retained) | -0.000198718 | 0.9318% |
| Bounded calibration: full V6 vs no-residual-calibration (switching retained) | -0.000057577 | 0.2718% |

Thus the current V6 global improvement is mostly associated with the frozen event-switching path under this counterfactual design. Bounded calibration improves global MAE but is not supported as uniformly beneficial across every stratified target-time scope.

## Permitted thesis claims

1. V6 reduces global MAE relative to `behavior_concat_v5` by 1.1999% under the EXP-108 aligned protocol.
2. V6 is superior to the reported external baselines on global MAE under the same aligned protocol, subject to the external-baseline report and its bootstrap results.
3. V6 is a validation-frozen, rule-based event-triggered multi-path prediction correction with bounded calibration.

## Prohibited claims

1. Do not call V6 a learned trigger, learned MoE, or independent event detector.
2. Do not claim V6 has no active-stable or positive-load degradation.
3. Do not mix origin-time EXP-103 event metrics with target-time EXP-108 event metrics.
4. Do not describe the counterfactual deltas as an exact additive causal attribution.

## Promotion status

The EXP-108 registry row is now updated for thesis writeback. The three train-log hashes were subsequently recomputed and all three seed archives passed `sha256sum -c`; this archival remediation does not alter the aligned predictions, metrics, or paired bootstrap results.
