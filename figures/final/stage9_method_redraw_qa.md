# Stage 9 Method Figure Redraw QA

Date: 2026-06-25

## Scope

This QA record covers the two method figures that replaced the rejected automatic drafts:

- `FIG-METHOD-001`: 总体技术路线图
- `FIG-METHOD-002`: 事件触发式预测修正机制图

## Production Route

| Step | FIG-METHOD-001 | FIG-METHOD-002 | Status |
|---|---|---|---|
| Controlled Image Gen visual reference | `figures/references/FIG-METHOD-001_reference.png` | `figures/references/FIG-METHOD-002_reference.png` | used as reference only |
| Formal redraw source | `figures/final/drawio/FIG-METHOD-001_method_pipeline.drawio` | `figures/final/drawio/FIG-METHOD-002_event_triggered_correction.drawio` | pass |
| SVG export | `figures/final/FIG-METHOD-001_method_pipeline.svg` | `figures/final/FIG-METHOD-002_event_triggered_correction.svg` | pass |
| PDF export | `figures/final/FIG-METHOD-001_method_pipeline.pdf` | `figures/final/FIG-METHOD-002_event_triggered_correction.pdf` | pass |
| PNG preview | `figures/final/png-preview/FIG-METHOD-001_method_pipeline.png` | `figures/final/png-preview/FIG-METHOD-002_event_triggered_correction.png` | pass |

## Reference Accuracy Notes

| Figure | Reference issue | Formal redraw decision |
|---|---|---|
| FIG-METHOD-001 | Image Gen reference used loose wording such as candidate expert generation and simplified the interval stage. | Formal redraw uses thesis-facing labels: `候选预测专家`, `事件状态分组区间校准`, `容量风险代理解释`, and `稳健性检验`. |
| FIG-METHOD-002 | Image Gen reference was structurally correct but still treated as a bitmap reference. | Formal redraw keeps only the stable fallback and event-window expert-selection structure; all labels and arrows are source-traceable. |

## Figure-Style QA

| Check | Result | Notes |
|---|---|---|
| Academic tone | pass | White background, restrained palette, no poster-style decoration. |
| Redraw feasibility | pass | Final source is draw.io, not a bitmap. |
| Chinese readability | pass | Labels use thesis-facing Chinese terms. |
| Module accuracy | pass | No extra model layers, formulas, servers, or decorative modules are included. |
| Arrow discipline | pass | Main flow is readable; mechanism details are moved to FIG-METHOD-002 rather than overloading FIG-METHOD-001. |
| Export completeness | pass | SVG, PDF, PNG preview, and `.drawio` source all exist. |
| Remaining risk | advisor review | Visual polish may still be adjusted after advisor preference, but the route now satisfies the Stage 9 production contract. |

## Caption-Safe Wording

FIG-METHOD-001: 本图展示本文从充电行为数据处理、候选预测专家构建、事件触发式预测修正，到区间校准、容量风险代理解释与稳健性检验的总体技术路线。

FIG-METHOD-002: 本图展示事件触发式预测修正机制：稳定窗口默认回退强行为基线，只有在保守事件触发条件满足时才选择事件专家并进行预测修正。

## Academic Draw.io Skill Redraw Candidate

Date: 2026-06-26

This candidate redraw uses the installed `drawio-academic-skills` and `drawio-skill` route instead of the earlier project-local draw.io script. The purpose is to move the method figures closer to thesis-style editable vector diagrams while keeping Chinese labels and source-traceable modules.

| Figure | YAML Spec | Editable Source | SVG | PDF | PNG Preview | QA Result |
|---|---|---|---|---|---|---|
| FIG-METHOD-001-academic-v3 | `figures/final/drawio-academic/FIG-METHOD-001_method_pipeline_academic_v3.spec.yaml` | `figures/final/drawio-academic/FIG-METHOD-001_method_pipeline_academic_v3.drawio` | `figures/final/drawio-academic/FIG-METHOD-001_method_pipeline_academic_v3.svg` | `figures/final/drawio-academic/FIG-METHOD-001_method_pipeline_academic_v3.pdf` | `figures/final/png-preview/FIG-METHOD-001_method_pipeline_academic_v3.png` | candidate; structure is cleaner, but figure width and label scale need advisor-facing manual polish |
| FIG-METHOD-002-academic-v3 | `figures/final/drawio-academic/FIG-METHOD-002_event_triggered_correction_academic_v3.spec.yaml` | `figures/final/drawio-academic/FIG-METHOD-002_event_triggered_correction_academic_v3.drawio` | `figures/final/drawio-academic/FIG-METHOD-002_event_triggered_correction_academic_v3.svg` | `figures/final/drawio-academic/FIG-METHOD-002_event_triggered_correction_academic_v3.pdf` | `figures/final/png-preview/FIG-METHOD-002_event_triggered_correction_academic_v3.png` | candidate; module overlap removed, mechanism path is readable, but typography should still be checked at Word insertion size |

Additional QA notes:

| Check | Result | Notes |
|---|---|---|
| Skill route | pass | Generated from YAML-first draw.io academic workflow with draw.io Desktop exports. |
| Source editability | pass | `.drawio` sources are available for manual refinement. |
| Content accuracy | pass | No extra model layers or unsupported formulas were added. |
| Thesis readability | partial | The diagrams are cleaner than the rejected drafts, but final thesis figures should still be manually adjusted for page-width readability. |
