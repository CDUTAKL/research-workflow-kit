# EXP-108 Thesis Backfill Record

Date: 2026-07-13
Experiment: `EXP-108-standard-baselines`
Status: archived results backfilled into a reviewable thesis copy

## Scope

- Evaluation scope: `event_scope=exp108_target_timestamp`
- Seeds: `42`, `2026`, `3407`
- Forecast horizon: four 15-minute steps
- Paired bootstrap: 5,000 resamples, clustered by `forecast_seed_origin`
- Front matter: intentionally unchanged and left for the author to complete

## Backfilled content

- Table 5-2: Persistence, LightGBM, GRU, STGCN, strong behavioral baseline, and V6 method; three-seed mean and standard deviation are shown for stochastic methods.
- Section 5.6: target-time event, active-stable, inactive-zero-load, and positive-load strata.
- Section 5.9: three-seed stability summary and paired bootstrap confidence intervals are written into the prose to avoid a fragile cross-page table fragment.
- Nine result figures: horizon metrics, event-type gain, node-level error difference, route distribution, error quantiles, representative event case, interval coverage/bias, risk-threshold sensitivity, and risk confusion.

## Evidence boundary

V6 improves global MAE relative to the strong behavioral baseline and LightGBM. The target-time event-window gain is smaller than the earlier origin-time result, while active-stable and positive-load MAE increase. The thesis wording therefore preserves subgroup heterogeneity and does not claim universal non-degradation.

## Source files

- Backfill tables: `outputs/EXP-108-standard-baselines/backfill/`
- Figure sources and exports: `figures/final/exp108_backfill/`
- Figure insertion manifest: `figure_insertion_manifest_exp108_backfill.json` in the thesis output directory
- WPS-refreshed DOCX: `r21_scientific_consistency_with_37_figures_v6_exp108-backfill-figures-unfilled-frontmatter.docx`
- WPS-exported PDF: `r21_scientific_consistency_with_37_figures_v6_exp108-backfill-figures-unfilled-frontmatter_20260713131025.pdf`
- WPS PDF SHA-256: `76aef827c0b629c364abaff60677239633aee835a18fa83cdf13d563de3319c3`
- WPS PDF page count: 103 (A4)
- Local render directory: `outputs/r21_render_v6_exp108/` (engineering preview only)
