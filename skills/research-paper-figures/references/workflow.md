# Research Figure Workflow

## Figure Inventory

| Visual | Type | Claim supported | Input data | Output format | Status |
|---|---|---|---|---|---|
| Figure 1 | pipeline/overview | method clarity | method notes | SVG/PDF/PNG | planned |
| Figure 2 | result plot | main claim | metrics table | PDF/PNG | data needed |

## Common Visual Types

| Evidence need | Recommended visual |
|---|---|
| Method flow | pipeline diagram or Mermaid flowchart |
| Model architecture | network architecture figure with feature-map stacks, module groups, and inset blocks; read `network-architecture-figure.md` |
| Main comparison | table plus `grouped_bar` or point plot |
| Trend over parameter/time | `line_trend` with markers and optional uncertainty |
| Ablation | table plus grouped/horizontal bar with consistent alpha or family palette |
| Confusion/error structure | `heatmap`, confusion matrix, or error breakdown |
| Robustness | line/box/violin/distribution plot with variability |
| Relationship | `scatter` or bubble plot with reference guides |
| Multi-metric profile | `radar` only when metrics are balanced and caption explains scaling |
| Effect estimates | `forest` interval plot |
| Multi-panel result story | `multi_panel` with unique evidence per panel |
| Case study | small multiples or annotated examples |

## Style Rules

- For advisor-facing or final thesis figures, record the check in `docs/thesis/figure-style-qa.md`.
- Use the same font family and sizing across related figures.
- Use labels with units.
- Prefer direct labels or clear legends.
- Avoid unnecessary 3D effects, gradients, and decorative backgrounds.
- Use colorblind-aware palettes.
- Keep important comparisons readable in grayscale.
- Prefer vector export for diagrams and final manuscript plots.
- Keep line widths and marker sizes readable after paper scaling.
- Export vector formats for diagrams and PDF/SVG where possible; use high-DPI PNG only when raster is necessary.
- Trace every data-driven figure back to a data file, notebook, or script.
- For multi-panel figures, keep panel labels, axis scales, and legends consistent.

## Nature-Derived Figure Contract

Use this contract when the user asks for a publication-quality figure, Nature-style figure, SCI figure, journal-ready figure, or final thesis figure.

| Item | Requirement |
|---|---|
| Core conclusion | State the one sentence the figure must defend before choosing chart types |
| Evidence chain | Map every panel to a unique piece of evidence; remove redundant panels |
| Figure role | Mark discovery, method, comparison, robustness, error analysis, or synthesis |
| Panel hierarchy | Prefer one hero panel plus supporting panels over equal-weight clutter |
| Data traceability | Record input file, notebook/script, experiment ID, and metric definition |
| Statistics | Record sample count, seed/fold count, error-bar definition, and test if used |
| Export | Prefer editable SVG/PDF for plots and high-DPI PNG/TIFF only when raster is needed |
| Caption safety | Caption must state what the visual shows, not a broader claim than the evidence |

For this Mac + Codex workflow, use Python/Matplotlib/Seaborn by default for data-backed plots when the project is Python-based. Use R/ggplot only when the user explicitly requests R or supplies an R plotting workflow.

## Mandatory Visual Reference Route

Use this route for model architecture diagrams, method overview figures, workflow diagrams, process schematics, conceptual mechanism figures, and other visuals where composition and visual hierarchy matter.

```text
Figure intent
-> Image Gen Skill visual reference
-> content-accuracy check
-> style decision extraction
-> formal redraw in draw.io from source of truth
-> SVG/PDF/PNG/PPTX export
-> metadata/provenance check
-> figure audit
```

Rules:

- Image Gen Skill is the preferred first pass for attractive composition, palette, layout, and visual hierarchy.
- The generated image is a reference, not a source of scientific truth.
- Check the reference before redrawing: module names, arrows, layer order, tensor shapes, labels, symbols, legends, and any numeric values.
- If the reference is visually strong but contains mistakes, keep the useful style decisions and correct the scientific content during formal redraw.
- Redraw structured model, method, workflow, evidence graph, and architecture diagrams in draw.io by default. Use Python or the Nature-style renderer for data-backed plots. Use Figma/BioRender only as optional polish layers after the source-traceable draw.io/Python output exists.
- The final thesis/manuscript figure must trace to source-of-truth records such as `.network.json`, `model.py`, experiment CSV/JSON, figure spec JSON, or a paper/code source note.
- Before final use, check that exported manuscript assets do not contain unwanted Image Gen C2PA/OpenAI provenance metadata.

Record the route in `docs/thesis/figure-plan.md`:

| Field | Meaning |
|---|---|
| `visual_reference` | path to Image Gen reference image or other style reference |
| `reference_source` | imagegen, paper-example, Figma draft, hand sketch, or existing figure |
| `reference_accuracy_check` | pass/revise/failed, with exact content issues |
| `style_to_reuse` | layout, palette, panel hierarchy, icon style, typography notes |
| `source_of_truth` | `.network.json`, `model.py`, experiment data, or cited source |
| `formal_redraw_tool` | draw.io by default for structured diagrams; Python/Nature-style renderer for data plots; Figma/BioRender/PPTX/SVG/TikZ only when justified |
| `final_export_path` | manuscript-ready output path |
| `metadata_check` | pending/pass/revise for C2PA/OpenAI/provenance metadata |

## Nature-Style Template Handoff

Use `nature-figure-controlled-port.md` and `skills/research-paper-figures/scripts/nature_plot_templates.py` for common result figures:

```text
figure claim
-> figure spec JSON
-> skills/research-paper-figures/scripts/nature_plot_templates.py
-> SVG/PDF/PNG
-> .qa.md report
-> docs/thesis/figure-plan.md
```

Default command:

```bash
python skills/research-paper-figures/scripts/nature_plot_templates.py \
  --spec skills/research-paper-figures/examples/figure_specs/grouped_bar_demo.json \
  --out figures/templates/grouped_bar_demo \
  --formats svg,pdf,png \
  --qa-report
```

Available first-wave templates:

| Template | Use for |
|---|---|
| `grouped_bar` | model/metric comparisons |
| `line_trend` | curves, threshold scans, training/validation trends |
| `heatmap` | confusion matrices, score grids, ablation matrices |
| `scatter` | relationship and tradeoff plots |
| `radar` | balanced multi-metric profiles |
| `distribution` | error/score spread and fold variance |
| `forest` | estimates with intervals |
| `multi_panel` | compact evidence stories with non-redundant panels |
| `log_bar` | runtime, memory, parameter count, or loss values spanning orders of magnitude |
| `ablation_barh` | component ablation and incremental module contributions |
| `threshold_curve` | threshold scans, sensitivity curves, and selected operating points |
| `confusion_heatmap` | classifier confusion matrix with count/proportion annotation |
| `asymmetric_hero` | one main result panel plus smaller support panels |
| `image_plate` | qualitative examples, image plates, or error-case grids |

Real thesis figures should replace demo inline data with source data from experiment outputs, curated CSV/JSON, or notebooks.

## Figure Audit Handoff

Use `figure-audit-standard.md` before calling a figure final. The audit is mandatory for:

- final thesis figures.
- advisor-facing figure packages.
- Nature-style or publication-ready figures.
- multi-panel result figures.
- figures used as core evidence for a manuscript claim.

Audit outputs should update `docs/thesis/figure-plan.md` with:

| Field | Meaning |
|---|---|
| `figure_claim` | one sentence the figure can defend |
| `panel_role` | role of each panel, such as hero, ablation, robustness, error, or synthesis |
| `source_data` | raw or derived data path |
| `script_or_notebook` | code or notebook that regenerates the visual |
| `export_status` | SVG/PDF/PNG/PPTX status and raster/vector rationale |
| `audit_status` | pass, revise, or blocked |
| `revision_needed` | exact change required before use |

Do not mark a figure as ready if the audit cannot trace it to data, code, or a safe caption.

## Multi-Panel Figure Planning

| Panel type | Use for | Common risk |
|---|---|---|
| Hero panel | main result, model overview, or key comparison | too much text or too many categories |
| Supporting panel | ablation, robustness, error category, example case | duplicates hero panel instead of adding evidence |
| Validation panel | held-out test, OOD, seed/fold variance, sensitivity | lacks protocol notes or uncertainty |
| Synthesis panel | mechanism, workflow, or final conceptual model | turns into decoration without evidence mapping |

Before generating a final multi-panel visual, update `docs/thesis/figure-plan.md` with the figure ID, supported claim, input data, script/notebook, export target, and caption-safe wording.

## Network Architecture Rule

Neural-network architecture figures are not ordinary flowcharts. Use `references/network-architecture-figure.md` when the visual includes CNN feature maps, residual blocks, encoder-decoder paths, transformers, attention modules, feature fusion, or classification heads. The default visual grammar should be editable vector/PPT-style shapes with clear module hierarchy, not generic boxes.

When producing a neural-network architecture figure, use this handoff:

```text
Image Gen Skill visual reference
  -> reference accuracy check
  -> source-of-truth architecture spec
  -> draw.io formal redraw
  -> SVG/PDF/PNG/PPTX target
  -> metadata and figure audit
  -> docs/thesis/network-architecture-figures.md
```

If a legacy `render_network_architecture.py` exists, treat it as a draft/structure helper unless the current project explicitly promotes it as the formal renderer.

## Caption Template

```text
Figure X. [What is shown]. The figure compares/analyzes [conditions] using [metric/data]. The key observation is [claim supported]. Higher/lower values indicate [meaning] where relevant.
```

## Table Template

```text
Table X. [What is compared]. Rows show [models/settings], columns show [metrics]. Bold indicates the best comparable result under the same evaluation protocol.
```

## LaTeX/Word Insertion Advice

- For LaTeX: prefer `\includegraphics` with PDF/SVG-converted PDF for vector graphics.
- For Word: use high-resolution PNG or SVG if supported by the template.
- Keep filenames stable and descriptive, for example `fig_method_pipeline.svg`, `fig_main_results.pdf`, `tab_ablation.csv`.
- Write captions in the manuscript source, not only inside image pixels.

## Final Output Checklist

- Every figure/table has a purpose.
- Every visual has known input data.
- Captions state evidence without overclaiming.
- Visual style is consistent.
- Export format matches the submission medium.
- Data-driven figures are reproducible from a traceable source.
- Publication-grade figures have editable vector output or a documented raster reason.
- Multi-panel figures have non-redundant panels and a clear evidence hierarchy.
- Final or advisor-facing figures have passed `figure-audit-standard.md` or have explicit revision items.
