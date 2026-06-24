# Figure Plan

Use `evidence-promotion-policy.md` for final visual IDs. Manuscript-facing figures, tables, and architecture diagrams should use `FIG-*`; legacy `Fig-*`, `Table-*`, or `Arch-*` labels can remain only as local notes until mapped.

## Update Rules

- Use this file to plan figures and tables before polishing visual style.
- Every figure/table should identify its purpose, input data, supported claim, and caption-safe wording.
- For model architecture, method overview, workflow, and schematic figures, create or select a visual reference first. Image Gen Skill is the preferred reference generator when visual quality matters.
- Reference images are not final thesis figures, but they are treated as the visual mother draft for formal redraw. They must therefore follow the same academic style, hierarchy, readability, and content-accuracy requirements as final figures before draw.io redraw begins.
- Check reference content accuracy, then redraw structured diagrams from source-of-truth records in draw.io by default on Mac, or Visio on Windows when editable `.vsdx` is needed.
- Use Python or the Nature-style renderer for data-backed plots. Use Figma/BioRender only as optional visual polish after draw.io/Python output exists.
- For complex charts, evidence graphs, Dashboard visuals, or advisor-facing visual reports, apply Build Web Data Visualization rules: simplest truthful chart, visible uncertainty or missingness when relevant, readable labels, accessible contrast, and responsive sanity checks.
- Use `network-architecture-figures.md` for model structure diagrams; do not manage them as generic result plots.
- Run the Nature-derived `figure-audit-standard.md` before marking final thesis, advisor-facing, or publication-ready figures as ready.
- Run `figure-style-qa.md` before advisor-facing or final figures are shown, exported, or inserted into DOCX/PDF/PPTX.
- Use `skills/research-paper-figures/scripts/nature_plot_templates.py` for common result figures when no project-specific plotting script already exists.

## Stage 9 Figure Production Workflow

The Stage 9 route is a source-traceable thesis figure pipeline, not a loose image-generation step. It adapts the useful parts of Nature-style figure contracts and audit checks into a Chinese master's thesis workflow.

```text
frozen result/source record
-> figure contract
-> data plot or Image Gen visual reference
-> content-accuracy and style check
-> Python or draw.io formal production
-> SVG/PDF/PNG export
-> figure-style QA and caption audit
-> DOCX/PDF/PPTX insertion check
```

### Method And Architecture Figure Route

Use this route for `FIG-METHOD-*`, `FIG-ARCH-*`, workflow diagrams, model mechanism diagrams, and capacity-risk explanation diagrams.

1. Write the figure contract first: figure claim, source of truth, modules, arrows, panel role, caption-safe wording, and export target.
2. Generate an Image Gen reference as a polished academic visual reference. It should be clean, restrained, Chinese thesis-facing, and easy to redraw.
3. Audit the reference before redraw. Check module names, causal direction, event trigger logic, stable fallback, expert selection, interval calibration, risk proxy, labels, and any numeric values.
4. Extract only reusable style decisions: layout, palette, spacing, hierarchy, icon grammar, arrow style, inset style, and typography.
5. Redraw in draw.io from source-of-truth records. Do not trace incorrect generated content.
6. Export SVG/PDF/PNG, then record metadata/provenance status and QA status.

### Data-Backed Result Figure Route

Use this route for `FIG-RESULT-*`, `FIG-INTERVAL-*`, `FIG-RISK-*`, `FIG-ROBUST-*`, and result tables.

1. Start from frozen CSV/Markdown result tables, not screenshots.
2. Write or reuse a Python/Nature-style figure spec and plotting script.
3. Keep metric names thesis-facing: for example `MAE（平均绝对误差）`, `RMSE（均方根误差）`, `WAPE（加权绝对百分比误差）`, `WIS（加权区间评分）`, and `PICP（预测区间覆盖率）`.
4. For small improvements, use paired markers, delta annotations, or grouped bars with honest axes. Do not exaggerate the global MAE difference by truncating axes without a clear note.
5. Export SVG/PDF plus PNG preview and record the source data and script path.

### Defense Slide Route

PPTX figures are downstream derivatives. The thesis source figure should be created first in draw.io or Python, then simplified for defense slides when needed. PPTX-only figures are allowed only for defense-specific explanation and should not become the thesis source of truth.

## Visual Reference To Formal Redraw Register

| Figure ID | visual_reference | reference_source | platform_route | reference_accuracy_check | style_to_reuse | source_of_truth | formal_redraw_tool | final_export_path | metadata_check | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| FIG-ARCH-001 | `figures/references/FIG-ARCH-001_reference.png` | imagegen/TBD | local_mac_drawio / windows_visio / TBD | pending | layout/palette/panel hierarchy/TBD | `.network.json` / model.py / paper source | draw.io/Visio/TBD | `figures/final/FIG-ARCH-001.*` | pending | planned |

Rules:

- `visual_reference` records the attractive reference image, usually generated by Image Gen Skill.
- `reference_accuracy_check` must name any incorrect module, arrow, tensor shape, symbol, or label before redraw.
- `style_to_reuse` records what should be copied stylistically: layout, palette, spacing, side legend, inset style, typography, or panel hierarchy.
- `source_of_truth` records what controls scientific accuracy.
- `platform_route` records whether the figure uses `local_mac_drawio` or `windows_visio`.
- `formal_redraw_tool` should be draw.io for Mac structured diagrams, or Visio for Windows `.vsdx` replication, unless a justified exception is recorded.
- `metadata_check` confirms the final export does not carry unwanted generated-image provenance such as C2PA/OpenAI metadata.

## Figure And Table List

| ID | Type | Purpose | figure_claim | panel_role | source_data | script_or_notebook | Recommended Form | Visual QA | Caption Draft | export_status | audit_status | revision_needed | Status | Export Target |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FIG-001 | figure | TBD | CLM-001/TBD | hero/support/TBD | TBD | TBD | flowchart/line/bar/heatmap/TBD | chart choice / uncertainty / contrast / labels pending | TBD | planned | pending | TBD | planned | PDF/SVG/PNG/TBD |
| FIG-TABLE-001 | table | TBD | CLM-001/TBD | table/TBD | TBD | TBD | metric table/ablation table/TBD | readable columns / footnotes pending | TBD | planned | pending | TBD | planned | DOCX/optional LaTeX/TBD |
| FIG-ARCH-001 | network architecture | explain model topology | method clarity | architecture main + inset | `.network.json` / model.py / paper source | draw.io, Windows Visio, or skills/research-paper-figures/scripts/render_network_architecture.py | feature-map stack diagram | label hierarchy / contrast / source-truth pending | structure-only caption | planned | pending | TBD | planned | SVG/PDF/PNG/PPTX/VSDX |
| FIG-METHOD-001 | figure | Explain the complete thesis method pipeline from charging-session data to event-triggered correction, interval calibration, and capacity-risk proxy. | CLM-102..CLM-106 | method overview / hero figure | `docs/thesis/experiment-reports/frozen-experiment-result-tables.md`, `docs/thesis/experiment-architecture.md`, `docs/thesis/experiment-runbook.md` | draw.io formal redraw after visual reference | multi-stage pipeline diagram | needs visual reference, source-truth check, draw.io redraw, and figure-style QA | 图 X 展示本文总体技术路线：首先构建行为事件特征与候选图专家，然后通过事件触发式预测修正机制在稳定窗口回退强行为基线、在事件窗口调用事件专家，最后进行事件状态分组区间校准与容量风险代理解释。 | planned | pending | create visual reference and formal draw.io source | planned | SVG/PDF/PNG/DOCX/PPTX |
| FIG-METHOD-002 | figure | Explain the event-triggered forecast correction mechanism without claiming a single dynamic graph backbone dominates all baselines. | CLM-102, CLM-103 | mechanism inset | `outputs/EXP-103-v6-event-deferral-rule-frozen/manifest.json`, `outputs/EXP-103-v6-event-deferral-rule-frozen/offline_deferral_metrics.csv`, `docs/thesis/experiment-reports/frozen-experiment-result-tables.md` | draw.io formal redraw | gated switch / fallback diagram | must label stable fallback, event trigger, expert choice, and residual calibration clearly | 图 X 展示事件触发式预测修正机制：稳定状态默认采用强行为基线；仅在保守事件触发条件满足时，模型转向事件专家并进行小幅修正，从而降低事件窗口误差且避免稳定窗口退化。 | planned | pending | create source-traceable mechanism diagram | planned | SVG/PDF/PNG/DOCX/PPTX |
| FIG-RESULT-001 | figure | Show the main EXP-103 point-prediction win in global, event-window, and stable-window scopes. | CLM-102, CLM-103 | result main panel | `outputs/EXP-103-v6-event-deferral-rule-frozen/offline_deferral_metrics.csv`, `outputs/EXP-103-v6-event-deferral-rule-frozen/wape_nmae_nrmse_delta.csv` | Python / Nature-style grouped bar or slope chart | grouped bar or paired dot plot | y-axis must not exaggerate small global MAE difference; show relative improvement text and event-window emphasis | 图 X 比较强行为基线与本文方法在测试集上的预测误差。本文方法使全局 MAE（平均绝对误差）降低 1.04%，事件窗口 MAE（平均绝对误差）降低 3.76%，同时稳定窗口误差未发生退化。 | planned | pending | render data-backed plot and QA labels | planned | SVG/PDF/PNG/DOCX |
| FIG-RESULT-002 | figure | Explain why direct graph experts are not safe as global replacements and why event-triggered correction is the defensible main method. | CLM-102, CLM-103 | ablation / comparator panel | `outputs/EXP-103-v6-event-deferral-rule-frozen/offline_deferral_metrics.csv` | Python / Nature-style ablation barh | horizontal ablation bar with global/event/stable MAE columns or faceted dot plot | include caveat that single event experts improve some event rows but hurt stable/global performance | 图 X 展示 EXP-103 消融结果。单独使用事件图专家可改善部分事件窗口，但会引入稳定窗口误差；本文方法通过事件触发和行为回退取得整体更优结果。 | planned | pending | render comparator plot from frozen metrics | planned | SVG/PDF/PNG/DOCX |
| FIG-INTERVAL-001 | figure | Show EXP-104 interval calibration improves event-window coverage and WIS（加权区间评分）. | CLM-104 | interval result panel | `outputs/EXP-104-v6-interval-adaptive-fast/interval_comparison_summary.csv`, `outputs/EXP-104-v6-interval-adaptive-fast/event_state_interval_metrics.csv` | Python / two-axis small multiples or table-like plot | coverage-WIS paired chart | show target 90% coverage reference line; do not claim strict conditional coverage | 图 X 展示事件状态分组区间校准效果。相比全局校准，分组保守校准显著修复事件窗口欠覆盖，并降低 WIS（加权区间评分）。 | planned | pending | verify local CSV availability before plotting | planned | SVG/PDF/PNG/DOCX |
| FIG-RISK-001 | figure | Show EXP-105 capacity-risk proxy results at q95/q98 and explain the recall/false-alarm tradeoff. | CLM-105 | risk explanation panel | `outputs/EXP-105-capacity-risk-v6/risk_metrics.csv`, `outputs/EXP-105-capacity-risk-v6/capacity_threshold_manifest.csv` | Python / grouped bar with q95 and q98 panels | grouped recall vs missed-risk chart | label as capacity-risk proxy / conservative screening, not real grid safety | 图 X 展示容量风险代理结果。与点预测阈值相比，基于区间上界的风险信号显著提高事件窗口高负荷风险召回率和严重度捕获率，但会带来一定误报率。 | planned | pending | render q95/q98 risk proxy plot | planned | SVG/PDF/PNG/DOCX |
| FIG-ROBUST-001 | figure/table | Summarize EXP-106 robustness and downgrade-decision guard results. | CLM-106 | robustness guard panel | `outputs/EXP-106/robustness_matrix.csv`, `outputs/EXP-106/sensitivity_summary.csv`, `outputs/EXP-106/downgrade_decision.md` | Python heatmap or manuscript table | pass/warn/fail matrix | avoid overclaiming; use as guardrail evidence | 图 X 汇总稳健性与降级决策检查。EXP-103、EXP-104 和 EXP-105 的关键守门项均通过，因此当前主线结论可保留，但仍需保持容量风险代理和区间校准的限定口径。 | planned | pending | verify output files and render matrix | planned | SVG/PDF/PNG/DOCX |
| FIG-TABLE-EXP103 | table | Manuscript-ready point-prediction main result and ablation table. | CLM-102, CLM-103 | main table | `docs/thesis/experiment-reports/frozen-experiment-result-tables.md` | manual table from frozen source | thesis metric table | metric acronyms must include Chinese explanations in heading or note | 表 X 报告 EXP-103 点预测主结果和消融对照。本文方法在强行为基线之上降低全局 MAE（平均绝对误差），并在事件窗口取得更明显收益。 | planned | pending | convert to DOCX-ready table | planned | DOCX/optional LaTeX |
| FIG-TABLE-EXP104-106 | table | Manuscript-ready interval, capacity-risk, and robustness summary table. | CLM-104..CLM-106 | support table | `docs/thesis/experiment-reports/frozen-experiment-result-tables.md` | manual table from frozen source | thesis summary table | split into separate tables if too wide for DOCX | 表 X 汇总 EXP-104 至 EXP-106 结果，说明本文方法从点预测延伸到区间校准、容量风险代理和稳健性守门。 | planned | pending | convert to DOCX-ready table | planned | DOCX/optional LaTeX |

## Publication-Grade Figure Contract

Use this section when a figure needs Nature-style or high-impact-journal polish.

| Figure ID | Core Conclusion | Evidence Chain / Panels | Hero Panel | Source Data / Script | Statistics / Uncertainty | Export Plan | QA Status |
|---|---|---|---|---|---|---|---|
| FIG-001 | TBD | panel a/b/c TBD | TBD | TBD | n/seed/fold/error bar TBD | SVG/PDF + PNG preview/TBD | planned |

## Network Architecture Figure Handoff

| Architecture Figure | Spec File | draw.io / Visio / Renderer Record | Generated Outputs | QA Report | Console Record |
|---|---|---|---|---|---|
| FIG-ARCH-001 | TBD.network.json | draw.io file, `.vsdx`, or thesis-clean/nature-minimal/ppt-template-rich | SVG/PDF/PNG/PPTX/VSDX/TBD | TBD.qa.md | `network-architecture-figures.md`, `diagram-replica-tasks.md` |

## Nature-Style Template Handoff

| Figure ID | Template | Spec File | Generated Outputs | QA Report | Source Data | Status |
|---|---|---|---|---|---|---|
| FIG-TEMPLATE-001 | grouped_bar/line_trend/heatmap/scatter/radar/distribution/forest/multi_panel/log_bar/ablation_barh/threshold_curve/confusion_heatmap/asymmetric_hero/image_plate | skills/research-paper-figures/examples/figure_specs/TBD.json | SVG/PDF/PNG/TBD | TBD.qa.md | demo/experiment CSV/TBD | planned |

## Template Library Coverage

| Template | Best Use | Demo Spec | Demo Output | Status |
|---|---|---|---|---|
| `grouped_bar` | model/metric comparison | `grouped_bar_demo.json` | `figures/templates/grouped_bar_demo.*` | available |
| `line_trend` | training or time trends | covered by `threshold_curve_demo.json` style | TBD | available |
| `heatmap` | metric matrix | `heatmap_demo.json` | `figures/templates/heatmap_demo.*` | available |
| `scatter` | relationship/tradeoff | covered by `asymmetric_hero_demo.json` | TBD | available |
| `radar` | multi-metric profile | `radar_demo.json` | `figures/templates/radar_demo.*` | available |
| `distribution` | seed/fold/class spread | `distribution_demo.json` | `figures/templates/distribution_demo.*` | available |
| `forest` | estimates with intervals | `forest_demo.json` | `figures/templates/forest_demo.*` | available |
| `multi_panel` | compact 2x2 evidence story | `multi_panel_demo.json` | `figures/templates/multi_panel_demo.*` | available |
| `log_bar` | order-of-magnitude comparisons | `log_bar_demo.json` | `figures/templates/log_bar_demo.*` | available |
| `ablation_barh` | component ablation | `ablation_barh_demo.json` | `figures/templates/ablation_barh_demo.*` | available |
| `threshold_curve` | threshold/parameter scan | `threshold_curve_demo.json` | `figures/templates/threshold_curve_demo.*` | available |
| `confusion_heatmap` | classification errors | `confusion_heatmap_demo.json` | `figures/templates/confusion_heatmap_demo.*` | available |
| `asymmetric_hero` | hero + support panels | `asymmetric_hero_demo.json` | `figures/templates/asymmetric_hero_demo.*` | available |
| `image_plate` | qualitative cases | `image_plate_demo.json` | `figures/templates/image_plate_demo.*` | available |

## Data Requirements

| Figure/Table ID | Required Columns / Fields | Source File | Missing Data | Owner / Next Action |
|---|---|---|---|---|
| FIG-001 | TBD | TBD | TBD | TBD |

## Caption Safety Checklist

| Check | Status | Notes |
|---|---|---|
| Caption matches actual metric and split | pending |  |
| Claim wording is supported by evidence | pending |  |
| Units, sample counts, and conditions are clear | pending |  |
| Figure source file is traceable | pending |  |
| Export format is suitable for DOCX / optional Word / optional LaTeX | pending |  |
| Editable vector or raster reason is recorded | pending |  |
| Multi-panel layout has no redundant panels | pending |  |
| Figure conclusion does not exceed evidence | pending |  |
| Network structure figures are tracked in `network-architecture-figures.md` | pending |  |
| Chart choice is the simplest truthful form for the data | pending |  |
| Uncertainty, missingness, sample counts, or limitations are visible when relevant | pending |  |
| Labels and contrast remain readable in DOCX/PDF/PPTX and dashboard contexts | pending |  |

## Figure Audit Log

| Figure ID | Audit Date | Figure Claim | Source Data | Script/Notebook | Export Status | Audit Status | Revision Needed |
|---|---|---|---|---|---|---|---|
| FIG-001 | TBD | TBD | TBD | TBD | SVG/PDF/PNG/TBD | pending | TBD |
