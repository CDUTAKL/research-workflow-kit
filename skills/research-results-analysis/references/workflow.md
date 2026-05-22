# Results Analysis Workflow

## Artifact Inventory

Start with a table.

| Artifact | Path/source | Type | Run/config | Metric coverage | Status |
|---|---|---|---|---|---|
| output file | path | log/csv/json/figure | model/dataset/seed | metrics | usable/questionable/missing |

Check for:

- train/validation/test split names.
- seed count.
- baseline identity.
- model variant names.
- hyperparameter differences.
- preprocessing differences.
- checkpoint or run timestamp.

## Result Scan Script

When the user provides a result directory or asks for a first-pass experiment summary, use the bundled scanner before interpreting claims:

```bash
python ~/.codex/skills/research-results-analysis/scripts/scan_results.py --root . --out-dir docs/thesis
```

For local development before global sync, use:

```bash
python skills/research-results-analysis/scripts/scan_results.py --root . --out-dir docs/thesis
```

The scanner recursively inspects `.json`, `.csv`, `.tsv`, `.txt`, and `.log` files. It extracts common fields such as `accuracy`, `acc`, `f1`, `macro_f1`, `macro avg`, `precision`, `recall`, `loss`, `auc`, `rmse`, `mae`, and `r2`.

Generated files:

| File | Purpose |
|---|---|
| `docs/thesis/result-scan-summary.md` | Human-readable scan summary, anomaly notes, and next steps |
| `docs/thesis/result-scan-table.csv` | Traceable metric rows with file, metric, value, location, status, and notes |

Important limits:

- Treat scanner output as an initial inventory, not final evidence.
- Review metric scale, split, seed, and protocol before writing claims.
- Copy reviewed results into `docs/thesis/experiment-registry.md`.
- Promote only audited findings into `docs/thesis/claim-evidence-map.md`.
- If scanner warnings appear, resolve them before using words such as robust, significant, or best.

## Result Scan To Experiment Registry

After `result-scan-table.csv` exists, convert scanned metric rows into candidate experiment registry entries:

```bash
python ~/.codex/skills/research-results-analysis/scripts/result_scan_to_registry.py --scan-table docs/thesis/result-scan-table.csv --registry docs/thesis/experiment-registry.md
```

For local development before global sync, use:

```bash
python skills/research-results-analysis/scripts/result_scan_to_registry.py --scan-table docs/thesis/result-scan-table.csv --registry docs/thesis/experiment-registry.md
```

The converter:

- groups scanned metrics by parent result directory.
- assigns candidate IDs such as `EXP-AUTO-001`.
- summarizes candidate best and mean values per metric.
- writes an idempotent auto-generated block in `experiment-registry.md`.
- marks rows as `candidate` or `candidate_review`, never as final evidence.

Use the generated rows as a review queue:

| Review step | Destination |
|---|---|
| Confirm dataset split, seed, config, and metric code | manual `Experiment Table` in `experiment-registry.md` |
| Confirm comparable baseline and protocol | `claim-evidence-map.md` |
| Identify needed plots/tables | `figure-plan.md` |
| Find anomalies or invalid results | `final-audit.md` or experiment risks |

Do not cite `EXP-AUTO-*` rows directly in the paper. Promote them to stable experiment IDs only after review.

## Exploratory Data Analysis Gate

Run this gate before interpreting metrics. It is inspired by scientific EDA workflows and should be as concrete as the available artifacts allow.

| Check | What to inspect | Risk if missing |
|---|---|---|
| File structure | columns, keys, tensor shapes, sheets, nested fields | metrics may be parsed from the wrong field |
| Sample count | total samples and per-split counts | reported results may use too small or mismatched scope |
| Label/class distribution | train/validation/test distribution | imbalance can make accuracy misleading |
| Missing/invalid values | NaN, blank labels, impossible metric values | metrics may be corrupted |
| Duplicates | repeated IDs, repeated spectra/images/samples | train/test leakage risk |
| Outliers | extreme feature values, metric spikes, run-time anomalies | unstable result or preprocessing issue |
| Split integrity | no sample overlap across train/validation/test | leakage can invalidate conclusions |
| Data provenance | raw data, preprocessing scripts, derived features | unclear lineage blocks strong claims |

EDA output template:

```text
Data sources inspected:
Structure summary:
Sample/split counts:
Label or outcome distribution:
Missing/invalid values:
Duplicate/leakage risks:
Outliers/anomalies:
Recommended downstream analysis:
```

## Metric Table

Use one row per comparable condition.

| Model | Dataset/split | Seed(s) | Metric | Value | Baseline | Difference | Comparable? |
|---|---|---|---|---:|---|---:|---|
| model | test | 0,1,2 | accuracy | 0.000 | baseline | +0.000 | yes/no |

Comparison rules:

- Compare only the same split, metric, label space, and evaluation protocol.
- Keep single-seed results separate from multi-seed summaries.
- Do not treat the best checkpoint as a final test result unless the evaluation protocol permits it.
- Prefer mean plus variability when multiple seeds exist.

## Statistical Analysis Decision Gate

Use this gate before writing strong claims. If the experiment design lacks replication or comparable conditions, report descriptive results instead of statistical significance.

| Situation | Minimum summary | Optional test/report | Claim strength |
|---|---|---|---|
| Single run per method | exact value and protocol | no significance test | descriptive only |
| Multiple seeds, same split | mean, standard deviation, per-seed values | paired or unpaired comparison if design allows | trend or supported improvement |
| Same samples evaluated by two methods | paired differences | paired t-test or Wilcoxon signed-rank depending on assumptions | stronger comparison |
| Independent groups | group summaries | t-test/Mann-Whitney or ANOVA/Kruskal-Wallis | group comparison |
| Class imbalance | per-class metrics, macro averages | confidence intervals or bootstrap if possible | metric-specific claim |
| Threshold sweep | operating points and tradeoff curve | sensitivity analysis | threshold-dependent claim |

Assumption checks:

- Independence: samples/runs are not duplicated or nested without accounting for it.
- Normality: only required for parametric tests; otherwise use non-parametric or bootstrap summaries.
- Equal variance: check before standard t-test/ANOVA.
- Multiple comparisons: avoid claiming many significant improvements without correction.
- Effect size: report practical magnitude, not only p-values.

Use cautious wording:

- `significant`: only with an appropriate test and reported threshold.
- `robust`: only across seeds, splits, datasets, perturbations, or operating conditions.
- `consistent`: only when most comparable runs support the trend.
- `outperforms`: only under the same protocol and metric.

## Claim Categories

| Category | Meaning | How to write |
|---|---|---|
| Supported | Directly backed by results | "The method improves X under Y setting." |
| Weak | Directional but missing robustness/baseline | "Preliminary results suggest..." |
| Unsupported | Not backed by provided artifacts | Do not include as a result claim |
| Missing | Needed for story but absent | Add to experiment plan |

## Common Audit Checks

- Data leakage: train/test contamination, duplicated samples, target-derived features.
- Metric mismatch: accuracy vs F1 vs macro-F1, micro vs macro averages.
- Baseline mismatch: different preprocessing, training budget, or data split.
- Selection bias: reporting only the best seed, best time slice, or best threshold.
- File mismatch: table values not traceable to logs or scripts.
- Overclaiming: "robust", "generalizes", "state of the art", or "significant" without evidence.

## Experiment Integrity Audit

Run this before promoting results into the paper. It adapts experiment-integrity checks into a Codex-native read-and-report workflow.

| Check | Evidence to inspect | PASS | WARN | FAIL |
|---|---|---|---|---|
| Ground truth provenance | dataset loaders, labels, eval scripts | labels come from dataset or documented annotation | proxy labels are documented | targets are derived from model outputs without disclosure |
| Score normalization | metric code, result files | denominator is independent of predictions | normalization is unusual but reported with raw scores | score divided by prediction max/min/mean to inflate results |
| Result file existence | claimed output paths, logs, CSV/JSON | every metric is traceable | trace exists but naming/config is ambiguous | claimed file/key does not exist |
| Dead metric code | metric functions and call sites | reported metrics are actually computed | unused metric code exists | paper relies on a metric that is never called |
| Scope assessment | dataset count, seed count, settings | scope matches wording | wording slightly exceeds evidence | "comprehensive/robust/extensive" contradicts small scope |
| Evaluation type | protocol notes, labels, human/simulation setup | evaluation type is explicit | mixed evaluation needs explanation | proxy/simulation is presented as real ground truth |

Integrity output template:

```text
Integrity status: PASS/WARN/FAIL
Ground truth source:
Metric computation risks:
Result traceability:
Dead-code or unused-metric risks:
Scope language risk:
Required fixes before writing:
```

## Result-to-Claim Template

```text
Observed result:
Experimental condition:
Comparison:
Supported claim:
Limitations:
Do not claim:
Needed follow-up:
```

## Visualization Recommendation Gate

Use this gate to decide what should be plotted during analysis and what should be handed off for publication figures.

| Analysis need | Exploratory visual | Paper-ready handoff |
|---|---|---|
| Distribution or imbalance | histogram, KDE, ECDF | distribution panel with clear units |
| Category comparison | boxplot, violinplot, stripplot | box/point plot with variability |
| Metric across settings | lineplot or pointplot | line/point plot with confidence or seed spread |
| Confusion/error structure | heatmap | annotated confusion matrix |
| Multiple variables | pairplot or faceted plot | selected panels only |
| Main comparison | quick bar/point plot | table plus controlled matplotlib figure |

Plotting rules:

- Use seaborn-style exploratory plots for quick diagnosis.
- Use matplotlib object-oriented figures for final, reproducible plots.
- Prefer vector output (PDF/SVG) for paper figures and high-DPI PNG when raster is necessary.
- Every figure must identify the source data and the claim it supports.

## Result-to-Figure Handoff

Send this to `$research-paper-figures` after analysis.

| Claim | Metric/data | Recommended visual | Input path | Caption-safe wording | Do not show/claim |
|---|---|---|---|---|---|
| claim | metric/table | plot type | file path | conservative caption claim | unsupported wording |

Handoff template:

```text
Figure purpose:
Claim supported:
Input data files:
Variables/metrics:
Recommended plot type:
Uncertainty to show:
Caption-safe claim:
Risks or caveats:
```

## Experiment-Paper Feedback Loop

Results analysis is part of an iterative paper loop, not a one-way report.

| Finding | Route |
|---|---|
| Main claim lacks evidence | return to experiment planning or weaken the claim |
| Baseline missing | add baseline before writing comparison |
| Result unstable across seeds | add seeds/robustness analysis or write as preliminary |
| Scope too narrow | restrict claim language or add data/settings |
| Figure unclear | hand off to `$research-paper-figures` |
| Result not relevant to paper story | move to appendix or omit |
| Citation needed for interpretation | hand off to `$research-literature-review` or `$semanticscholar-skill` |

## Notebook and Thesis Records

For exploratory analysis, metric summaries, and ablation review, use `$jupyter-notebook` to create or update a reproducible experiment notebook. Keep each notebook linked from a registry such as:

```text
docs/thesis/experiment-notebook-index.md
docs/thesis/experiment-registry.md
docs/thesis/claim-evidence-map.md
```

Recommended notebook set:

| Notebook | Purpose |
|---|---|
| `notebooks/thesis/01_data_audit.ipynb` | inspect data structure, splits, missingness, leakage risks |
| `notebooks/thesis/02_result_summary.ipynb` | load scan CSV or manual result tables and compute reviewed summaries |
| `notebooks/thesis/03_error_analysis.ipynb` | inspect misclassifications, hard cases, residuals, or failure groups |
| `notebooks/thesis/04_figure_preparation.ipynb` | prepare publication figure/table input data before final styling |

Use this handoff:

```text
$jupyter-notebook for exploration and computed summaries
  -> $research-results-analysis for metric normalization and claim support
  -> $research-paper-figures for traceable figures and tables
```

## Final Output Checklist

- Results are traceable to artifacts.
- EDA risks are reported before metrics are interpreted.
- Comparable results are separated from non-comparable results.
- Statistical wording matches the experiment design.
- Integrity checks are PASS or clearly marked with required fixes.
- Claims are conservative.
- Figure handoff identifies data, visual type, caption-safe claim, and caveats.
- Missing experiments are prioritized by paper impact.
- Any risks are visible before writing starts.
