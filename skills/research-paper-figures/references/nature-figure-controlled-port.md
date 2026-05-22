# Nature Figure Controlled Port

Use this reference when turning `nature-figure` ideas into local, reproducible thesis figures.

This is a controlled port, not a direct copy. The original `external-skill-candidates/nature-skills/skills/nature-figure` remains a source reference. Local work must keep the `research-paper-figures` workflow as the source of truth for claims, source data, scripts, exports, and audit records.

## Porting Goal

Move from "figure advice" to a local figure production layer:

```text
figure claim
-> figure spec JSON or data table
-> skills/research-paper-figures/scripts/nature_plot_templates.py
-> SVG/PDF/PNG
-> figure QA notes
-> docs/thesis/figure-plan.md
```

## Chart Atlas

| Evidence need | Local template | Best use | Avoid |
|---|---|---|---|
| Method comparison across metrics | `grouped_bar` | accuracy/F1/AUC comparisons across models | too many categories without legend panel |
| Training or threshold trend | `line_trend` | loss curves, threshold scans, time/accuracy trends | smoothing away variance |
| Confusion or metric matrix | `heatmap` | confusion matrices, metric grids, ablation matrices | using colors without numeric labels when exact values matter |
| Relationship between variables | `scatter` | error vs confidence, speed vs accuracy, feature relationships | claiming causality from correlation |
| Multi-axis benchmark profile | `radar` | compact method profile across balanced metrics | many metrics with unrelated scales |
| Distribution or error spread | `distribution` | per-class errors, fold variance, score distributions | hiding sample counts |
| Estimate with uncertainty | `forest` | effect sizes, confidence intervals, per-group deltas | using interval plots without explaining interval definition |
| Multi-panel story | `multi_panel` | hero result plus ablation/robustness/error support | panels that repeat the same evidence |
| Order-of-magnitude comparison | `log_bar` | runtime, parameter count, memory, loss, complexity | log scale hiding absolute interpretation |
| Component ablation | `ablation_barh` | module contribution and controlled ablation | treating uncontrolled differences as component effects |
| Threshold or parameter scan | `threshold_curve` | threshold selection, sensitivity, training curves | selecting thresholds without validation protocol |
| Classifier error structure | `confusion_heatmap` | class-wise confusion counts or proportions | unclear normalization or swapped axes |
| Asymmetric paper panel | `asymmetric_hero` | one hero result plus support panels | decorative hero panel without evidence |
| Image/case plate | `image_plate` | qualitative cases, image examples, error cases | anecdotal overclaim |

## Local Style Rules

- SVG is the primary editable output. PDF and PNG are secondary outputs.
- Always preserve SVG text as editable text.
- Use top/left axes only for ordinary plots; remove top/right spines.
- Use a shared legend or dedicated legend panel when several panels reuse the same categories.
- Tighten y-axis ranges only when the axis label and caption make the range honest.
- Use hatch or direct labels when color alone would fail grayscale review.
- Keep green/red mostly for gain/drop or positive/negative direction, not arbitrary method identity.
- Use one semantic color map across all panels in a figure.

## Multi-Panel Rule

Every panel must answer a unique question.

| Panel role | Question |
|---|---|
| hero | What is the main result or mechanism? |
| comparison | How does the proposed method compare? |
| ablation | Which component matters? |
| robustness | Does the result hold across settings? |
| error | Where does the method fail? |
| synthesis | How should the reader interpret the evidence together? |

If removing a panel does not remove a unique piece of evidence, drop or replace the panel.

## Spec Fields

`skills/research-paper-figures/scripts/nature_plot_templates.py` accepts a JSON spec with these fields:

| Field | Meaning |
|---|---|
| `template` | grouped_bar, line_trend, heatmap, scatter, radar, distribution, forest, multi_panel, log_bar, ablation_barh, threshold_curve, confusion_heatmap, asymmetric_hero, or image_plate |
| `title` | optional title for previews; omit or keep short for manuscript figures |
| `figure_id` | stable ID used in `docs/thesis/figure-plan.md` |
| `claim` | one sentence the figure can support |
| `caption` | caption-safe description |
| `data` | inline values for the first version, or a clear pointer to source data |
| `style` | palette, figsize, font size, axis labels, legend behavior |
| `audit` | source data, script/notebook, experiment ID, metric definition |

Use inline demo data only for templates and examples. Real thesis figures should point to experiment outputs or curated CSV/JSON files.

## Output Contract

When producing a figure from this controlled port, return:

- spec path.
- generated SVG/PDF/PNG paths.
- claim supported.
- source data path or demo-data warning.
- caption draft.
- figure-plan fields to update.
- audit issues if any.

## Provenance

This reference is derived from the current local `nature-figure` candidate repository, especially its chart atlas, common patterns, design theory, and tutorials. It is rewritten for macOS/Codex + `docs/thesis/` use. Do not copy original gallery images or paid/commercial template assets.
