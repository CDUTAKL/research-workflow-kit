# Figure Audit Standard

Use this standard when a figure package is described as final, publication-ready, thesis-ready, Nature-style, advisor-facing, or submission-ready.

This reference adapts the useful parts of `external-skill-candidates/nature-skills/skills/nature-figure` into the local research workflow. It is an audit layer, not a replacement for `research-paper-figures`.

## Audit Principle

A figure is ready only when it has a defensible claim, traceable source data, non-redundant panels, safe caption wording, and export files that remain readable in the final manuscript.

Do not let visual polish hide unsupported science. A polished but untraceable figure fails the audit.

## Figure Contract

Record these fields before generating or accepting a final figure.

| Field | Required content |
|---|---|
| Figure ID | Stable ID used in `docs/thesis/figure-plan.md` |
| Figure claim | One sentence the figure can defend |
| Figure role | method, comparison, ablation, robustness, error analysis, synthesis, or architecture |
| Evidence chain | input data, experiment ID, script/notebook, metric definition |
| Panel plan | panel label, panel role, unique question answered |
| Source data | raw file or derived table path |
| Output files | SVG/PDF for vector, PNG/TIFF only when raster is needed |
| Caption-safe note | what the figure shows without expanding beyond evidence |
| Audit status | pass, revise, blocked |

## Nature-Style Audit Checklist

| Check | Pass condition | Common failure |
|---|---|---|
| Claim clarity | Figure has one explicit claim or method explanation | figure is decorative or vague |
| Panel uniqueness | Every panel answers a different evidence question | repeated bar/table panels |
| Evidence traceability | Source data, script/notebook, experiment ID, and metric are known | only screenshot or copied image exists |
| Caption safety | Caption describes the visual and avoids broader causal claims | caption says "proves", "robust", or "best" without evidence |
| Quantitative honesty | axes, scales, error bars, sample counts, and aggregation are stated | hidden uncertainty or cherry-picked run |
| Typography | labels remain readable after Word/PDF scaling | text too small or embedded as raster pixels |
| Color and contrast | colorblind-aware palette and grayscale readability | one-hue gradients, low contrast, decorative colors |
| Layout hierarchy | hero panel and support panels have clear priority | equal-weight clutter |
| Export quality | editable SVG/PDF exists unless raster is justified | only low-DPI PNG exists |
| Manuscript fit | filename, caption, and insertion target are recorded | figure cannot be tied to manuscript section |

## Panel Audit

Use this table for multi-panel figures.

| Panel | Role | Unique evidence question | Source data | Risk | Decision |
|---|---|---|---|---|---|
| A | overview/comparison/ablation/error/robustness | TBD | TBD | duplicate/weak/unclear | keep/revise/drop |

Rules:

- Keep one hero panel when possible.
- Drop panels that repeat the same comparison without adding evidence.
- Put method schematics before result panels only when the method is needed to interpret the result.
- Do not combine unrelated panels just to make a figure look dense.

## Caption Audit

Caption text should:

- identify what is shown.
- name the data or condition being compared.
- define abbreviations, metrics, units, and error bars when needed.
- state only the observation directly visible in the figure.
- avoid unsupported scope words such as `robust`, `general`, `significant`, `state of the art`, `proves`, or `always`.

Safe pattern:

```text
Figure X. [What is shown]. Panels compare/analyze [conditions] using [metric/data]. Error bars denote [definition]. The key visible observation is [narrow claim supported by the plotted data].
```

## Output Requirements

For final thesis or paper figures, record:

- source data path.
- plotting script or notebook path.
- generated SVG/PDF/PNG path.
- figure-plan row.
- claim-evidence-map row when the figure supports a result claim.
- audit result and required revision if not passing.

## Routing

| Audit result | Route |
|---|---|
| missing source data | `$research-results-analysis` or experiment registry update |
| unsupported caption | `$research-paper-writing` and `$research-paper-figures` |
| misleading plot type | `$research-paper-figures` |
| unreadable rendering | `$pdf`, `$doc`, or final manuscript preview |
| model topology uncertainty | `network-architecture-figure.md` and `.network.json` update |
