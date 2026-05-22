# Nature Figure Template Roadmap

This roadmap records the controlled port from the original `nature-figure` references into local, reusable `research-paper-figures` templates.

Source references:

- `external-skill-candidates/nature-skills/skills/nature-figure/references/api.md`
- `external-skill-candidates/nature-skills/skills/nature-figure/references/chart-types.md`
- `external-skill-candidates/nature-skills/skills/nature-figure/references/common-patterns.md`
- `external-skill-candidates/nature-skills/skills/nature-figure/references/design-theory.md`
- `external-skill-candidates/nature-skills/skills/nature-figure/references/tutorials.md`
- `external-skill-candidates/nature-skills/skills/nature-figure/references/nature-2026-observations.md`

Do not copy the original gallery images or chart atlas PNGs into this skill. Extract reusable visual grammar, data contracts, and QA rules.

## Porting Map

| Original pattern | Local template | Research question | Data input | Caption risk | QA focus | Status |
|---|---|---|---|---|---|---|
| grouped comparison bars | `grouped_bar` | Which method performs better across settings? | categories + named series + optional errors | overclaiming "best" without same protocol | source data, error definition, same evaluation protocol | ported |
| line trend with uncertainty | `line_trend` | How does a metric change over epochs, time, or parameter values? | x + named series, optional repeated runs | treating smoothed trend as proof | x meaning, uncertainty, event labels | ported |
| heatmap with annotations | `heatmap` | Which cells are high/low in a matrix? | 2D matrix + row/column labels | color-only interpretation | annotations, colorbar, labels | ported |
| scatter/bubble relationship | `scatter` | How do two variables co-vary? | x, y, optional color/size | causal wording from correlation | axes, median guides, colorbar | ported |
| radar/polar | `radar` | What is the multi-metric profile? | labels + named metric series + optional bounds | area/shape misinterpretation | axis normalization warning | enhanced |
| violin/box/strip | `distribution` | How are scores/errors distributed? | groups with values | hiding sample count or spread | strip points, median, sample count | enhanced |
| forest interval | `forest` | What is the estimated effect and interval? | labels + estimate + low/high interval | interval not defined | reference line, grouping, sorting | enhanced |
| 2x2 evidence story | `multi_panel` | How do several evidence panels support one claim? | panel specs | repeated evidence | unique panel roles | enhanced |
| log-scale bar | `log_bar` | How do quantities differ by orders of magnitude? | categories + positive values + optional errors | log axis hiding absolute differences | log label, positive values, annotations | ported |
| horizontal ablation | `ablation_barh` | Which component contributes most? | labels + values + optional errors | implying causality without controlled protocol | order, alpha encoding, errors | ported |
| line trend + event annotation | `threshold_curve` | Which threshold/parameter value is selected? | x + series + optional best point/events | selecting threshold without validation set | selected point, reference/event labels | ported |
| confusion matrix | `confusion_heatmap` | Where does a classifier make mistakes? | matrix + labels, optional normalization | confusing counts vs proportions | axis labels, normalization note | ported |
| asymmetric hero layout | `asymmetric_hero` | What is the main evidence plus support? | panel specs with one hero panel | decorative hero without evidence | panel uniqueness and hierarchy | ported |
| dark image plate | `image_plate` | What visual cases or qualitative examples matter? | image paths or demo generated images | anecdotal overclaim | labels, scale bar, case role | ported |

## Data Contract Rules

- Every template accepts a JSON spec with `figure_id`, `template`, `claim`, `caption`, `data`, `style`, and `audit`.
- Demo specs may use inline data, but manuscript figures must point to experiment CSV/JSON/notebooks.
- SVG is the primary output for editable text. PDF and PNG are secondary.
- QA reports must flag demo data as non-evidence.

## Local Implementation Files

- Renderer: `scripts/nature_plot_templates.py`
- Example specs: `examples/figure_specs/*.json`
- Generated previews: `figures/templates/*`
- Thesis control: `docs/thesis/figure-plan.md`

## Deferred Items

- R/ggplot templates are intentionally not ported in this Python-first workflow.
- Original gallery and chart atlas image assets are not copied.
- Domain-specific templates should be added only after a project has stable result files.
