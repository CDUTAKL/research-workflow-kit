# Writing Outline

## Current Stage

当前进入 12 流程第 10A 阶段：论文写作蓝图与正文初稿。

10A-1 已生成详细目录与写作骨架：

- `docs/thesis/stage10a-1-detailed-outline-and-writing-skeleton.md`

10A-2 已生成第 4 章方法章初稿：

- `docs/thesis/chapter-drafts/chapter4-event-aware-spatiotemporal-graph-correction-draft.md`

10A-3 已生成第 5 章点预测实验章初稿：

- `docs/thesis/chapter-drafts/chapter5-point-forecast-event-trigger-validation-draft.md`

10A-4 已生成第 6 章区间校准、容量风险代理与稳健性分析初稿：

- `docs/thesis/chapter-drafts/chapter6-interval-risk-robustness-draft.md`

10A-5 已生成第 3 章数据构建与问题定义初稿：

- `docs/thesis/chapter-drafts/chapter3-data-problem-definition-draft.md`

10A-6 已生成第 2 章相关理论与研究现状初稿：

- `docs/thesis/chapter-drafts/chapter2-related-work-draft.md`

10A-7 已生成第 1 章绪论初稿：

- `docs/thesis/chapter-drafts/chapter1-introduction-draft.md`

10A-8 已生成第 7 章总结与展望初稿：

- `docs/thesis/chapter-drafts/chapter7-conclusion-outlook-draft.md`

10A-9 已生成中文摘要、英文摘要和关键词初稿：

- `docs/thesis/chapter-drafts/abstract-keywords-draft.md`

后续正文写作应以该文件为主入口，避免沿用早期“动态专家/专家池/EXP 编号”口径。

## Update Rules

- Keep chapter goals, evidence, figures, tables, and citation needs visible before drafting.
- Use evidence-backed wording; do not promote weak claims into thesis conclusions.
- Use branch terminology: 行为基线预测分支、图结构预测分支、候选预测分支、事件触发式预测修正机制。
- Do not use informal or code-facing terms in the manuscript body: 专家模型、selector、oracle、EXP-103、V6、后处理脚本、测试集标签。
- Prefer writing evidence-heavy chapters first, then related work, introduction, abstract, and conclusion.
- Before polishing a section, check `section-citation-map.md`, `claim-evidence-map.md`, and `data-availability.md`.

## Recommended Drafting Order

```text
第 4 章 方法
第 5 章 点预测实验
第 6 章 区间校准、容量风险代理与稳健性分析
第 3 章 数据构建与问题定义
第 2 章 相关理论与研究现状
第 7 章 总结与展望
摘要
```

## Chapter Outline

| Chapter / Section | Writing Goal | Required Evidence | Figures / Tables | Citations Needed | Status | Notes |
|---|---|---|---|---|---|---|
| Abstract | Summarize problem, method, supported results, and bounded contribution | final claim map and key metrics | none | minimal | draft_ready | Compressed from chapters 1-7; keeps event-window, interval calibration, capacity-risk proxy, and limitation boundaries evidence-bounded |
| 第 1 章 绪论 | Motivate event-driven EVCS load uncertainty and state bounded contributions | topic intake, thesis brief, literature gap, frozen result summary | optional technical-route figure | EVCS forecasting, behavior events, uncertainty, graph forecasting | draft_ready | Reverse-organized from chapters 2-6; keeps contribution and risk boundaries explicit |
| 第 2 章 相关理论与研究现状 | Position the work among EVCS forecasting, behavior modeling, graph temporal forecasting, interval forecasting, and risk proxy literature | literature matrix, Zotero hub, citation provenance | related-work comparison table | verified core and near-neighbor citations | draft_ready | Organizes five literature lines and bounds the contribution as behavior-event correction evidence chain |
| 第 3 章 数据构建与问题定义 | Define dataset, features, event/stable windows, graph construction, tasks, and metrics | data availability, experiment architecture, final figure freeze | data composition, distribution, event-window distribution, graph structure, metric system | ACN-Data and metric citations | draft_ready | Emphasize causally available features |
| 第 4 章 事件感知时空图预测修正方法 | Explain time feature extraction, behavior baseline branch, graph-structure branches, conservative trigger, and correction rule | method spec, claim-evidence map, final method figures | PPT system architecture, model structure, event-trigger mechanism | graph temporal, EVCS graph, interval/risk adjacent citations | draft_ready | Core term: 事件触发式预测修正机制 |
| 第 5 章 点预测实验与事件触发机制验证 | Report point prediction, weak baselines, ablations, event/stable windows, trigger diagnostics, cases, and error distributions | frozen result tables, final figures, experiment reports | main result, ablation, multiseed, weak baseline, grouped errors, diagnostics, case, error distribution | dataset, baseline, metric citations | draft_ready | Main story: key-window and stable-fallback advantage |
| 第 6 章 区间校准、容量风险代理与稳健性分析 | Report interval reliability, risk proxy, feature contribution, and robustness boundaries | EXP-104/105/106 frozen tables, final figures | interval calibration, tradeoff, risk proxy, risk level, risk case, feature contribution, robustness sensitivity | interval scoring, hosting capacity, risk proxy citations | draft_ready | Do not claim strict conditional coverage or real grid safety |
| 第 7 章 总结与展望 | Summarize supported contributions, limitations, and future work | final claim map, final audit | none | optional | draft_ready | Explicitly states dataset, proxy-risk, graph-meaning, and generalization limits |

## Section Evidence Coverage

| Section ID | Chapter / Section | Claim Coverage | Citation Coverage | Data Availability | Ready To Polish? | Notes |
|---|---|---|---|---|---|
| SEC-INTRO-001 | 第 1 章 绪论 | CLM-101 foundation, CLM-102/103 preview | core_shortlist_ready | DATA-101..DATA-103 mixed | no | Write after method/results stabilize. |
| SEC-METHOD-001 | 第 4 章 方法 | CLM-102, CLM-103, CLM-104 interface, CLM-105 interface | near_neighbor_readers_partial | DATA-101..DATA-103 mixed | no | Use branch/correction terminology only. |
| SEC-EXP-001 | 第 5 章 点预测实验 | CLM-101 weak foundation; CLM-102/103/106 supported_with_caveat | core_shortlist_ready | DATA-101..DATA-104 mixed | no | Global gain modest; emphasize event-window and stable-window evidence. |
| SEC-RISK-001 | 第 6 章 区间/风险 | CLM-104/105 supported_with_caveat; CLM-106 supported | core_shortlist_ready_but_cautious | DATA-104 planned/available through EXP-104/105 | no | Keep wording as interval calibration and capacity-risk proxy. |

## Required Writing Records

| Record | Purpose | Status |
|---|---|---|
| `stage10a-1-detailed-outline-and-writing-skeleton.md` | Main detailed outline and writing skeleton | created |
| `chapter-drafts/chapter1-introduction-draft.md` | Chapter 1 introduction draft | created |
| `chapter-drafts/chapter3-data-problem-definition-draft.md` | Chapter 3 data construction and problem definition draft | created |
| `chapter-drafts/chapter2-related-work-draft.md` | Chapter 2 related theory and research status draft | created |
| `chapter-drafts/chapter4-event-aware-spatiotemporal-graph-correction-draft.md` | Chapter 4 method draft | created |
| `chapter-drafts/chapter5-point-forecast-event-trigger-validation-draft.md` | Chapter 5 point prediction experiment draft | created |
| `chapter-drafts/chapter6-interval-risk-robustness-draft.md` | Chapter 6 interval calibration, capacity-risk proxy, and robustness draft | created |
| `chapter-drafts/chapter7-conclusion-outlook-draft.md` | Chapter 7 conclusion and outlook draft | created |
| `chapter-drafts/abstract-keywords-draft.md` | Chinese abstract, English abstract, and keywords draft | created |
| `claim-evidence-map.md` | Claim boundaries and evidence gates | available, use before prose |
| `final-figure-freeze-20260630.md` | Frozen figure list and exclusions | available |
| `experiment-reports/frozen-experiment-result-tables.md` | Frozen numeric result tables | available |
| `section-citation-map.md` | Citation coverage and reader queue | available |
| `nature-style-writing-checklist.md` | Final polish checklist | use after draft |

## Revision Log

| Date | Section | Change | Evidence Checked | Next Action |
|---|---|---|---|---|
| 2026-06-11 | Stage-1 outline | Imported DOCX mother plan into planning-level chapter goals and evidence gates. | `topic-intake.md`, `thesis-brief.md`, `project-scope-control.md` | Start Stage 2 literature pressure review and Stage 3 research-question mapping. |
| 2026-06-11 | Stage-3 experiment questions | Extracted DOCX research questions, hypotheses, ablations, metrics, and downgrade routes into workflow records. | `experiment-question-definition.md`, `claim-evidence-map.md`, `experiment-registry.md`, `data-availability.md` | Start Stage 4 experiment architecture and code/config contract planning. |
| 2026-06-30 | Stage-10A-1 writing blueprint | Replaced outdated dynamic-expert outline with branch-based event-triggered correction writing skeleton. | `claim-evidence-map.md`, `final-figure-freeze-20260630.md`, `frozen-experiment-result-tables.md`, `section-citation-map.md` | Start 10A-2: draft Chapter 4 method section. |
| 2026-06-30 | Stage-10A-2 method draft | Drafted Chapter 4 with locked terminology, formulas, and method boundaries. | `method-event-deferral-v6.md`, `exp103-v6-model-design.md`, `claim-evidence-map.md`, `section-citation-map.md` | Start 10A-3: draft Chapter 5 point prediction experiment section. |
| 2026-06-30 | Stage-10A-3 point prediction draft | Drafted Chapter 5 around main point-prediction results, basic baselines, branch ablations, event/stable windows, trigger diagnostics, typical event-day cases, and error distributions. | `experiment-reports/frozen-experiment-result-tables.md`, `experiment-reports/thesis-result-tables-and-narrative-update.md`, `final-figure-freeze-20260630.md`, `outputs/EXP-103-*` | Start 10A-4: draft Chapter 6 interval calibration, capacity-risk proxy, and robustness analysis. |
| 2026-07-01 | Stage-10A-4 interval/risk draft | Drafted Chapter 6 around event-state interval calibration, coverage-width tradeoff, capacity-risk proxy, risk-level distribution, feature contribution, and robustness boundaries. | `experiment-reports/frozen-experiment-result-tables.md`, `EXP-104-v6-interval-calibration.md`, `EXP-105-capacity-risk-proxy.md`, `EXP-106-robustness-downgrade-decision.md`, final figure source CSVs | Start 10A-5: draft Chapter 3 data construction and problem definition, then move to related work and introduction. |
| 2026-07-01 | Stage-10A-5 data/problem draft | Drafted Chapter 3 covering data source, chronological split, time-slice reconstruction, event-window definition, behavior-event graph construction, causal feature availability, prediction task, and evaluation metrics. | `data-availability.md`, `experiment-architecture.md`, `experiment-question-definition.md`, `metric-diagnostics.md`, `outputs/EXP-101/*`, `outputs/EXP-103-*/graph_manifest.json`, final figure source CSVs | Start 10A-6: draft Chapter 2 related work and theory review with citation placeholders. |
| 2026-07-01 | Stage-10A-6 related work draft | Drafted Chapter 2 around EV charging load forecasting, charging behavior modeling, spatiotemporal graph prediction, interval calibration, capacity-risk proxy, and evaluation/baseline design. | `core-literature-shortlist-and-review-structure.zh.md`, `section-citation-map.md` | Start 10A-7: draft Chapter 1 introduction, then abstract and conclusion after all chapters stabilize. |
| 2026-07-01 | Stage-10A-7 introduction draft | Drafted Chapter 1 by reverse-organizing the locked related-work positioning, data definition, method mechanism, point prediction results, interval calibration, and capacity-risk proxy evidence into background, problem statement, research content, technical route, contributions, and boundaries. | `chapter2-related-work-draft.md`, `chapter3-data-problem-definition-draft.md`, `chapter4-event-aware-spatiotemporal-graph-correction-draft.md`, `chapter5-point-forecast-event-trigger-validation-draft.md`, `chapter6-interval-risk-robustness-draft.md`, `frozen-experiment-result-tables.md` | Start 10A-8: draft abstract or Chapter 7 conclusion after confirming chapter order with advisor preference. |
| 2026-07-01 | Stage-10A-8 conclusion/outlook draft | Drafted Chapter 7 to summarize supported work, main results, contributions, limitations, and future directions while preserving capacity-risk proxy and generalization boundaries. | `chapter1-introduction-draft.md`, `chapter5-point-forecast-event-trigger-validation-draft.md`, `chapter6-interval-risk-robustness-draft.md`, `frozen-experiment-result-tables.md`, `claim-evidence-map.md` | Start 10A-9: generate Chinese and English abstracts from chapters 1-7, then enter 10B citation/caption/cross-reference polish. |
| 2026-07-01 | Stage-10A-9 abstract and keywords draft | Drafted Chinese abstract, English abstract, and Chinese/English keywords from chapters 1-7 with frozen metrics and bounded contribution wording. | `chapter1-introduction-draft.md`, `chapter7-conclusion-outlook-draft.md`, `experiment-reports/frozen-experiment-result-tables.md`, `claim-evidence-map.md` | Enter 10B-1: citation replacement, figure/table numbering, captions, cross-references, and integrated manuscript assembly. |
| 2026-07-01 | Stage-10B-0 school template style lock | Converted the Chengdu University of Technology 20230905 master's thesis template into executable style constraints, DOCX assembly checks, and format compliance audit gates. Locked sequential numeric references and mapped the Chapter 7 draft to the final unnumbered `结  论` section. | `school-template-format-audit-20260701.md`, `school-template-format-crosscheck-20260701.md`, `school-template-style-map.md`, `docx-assembly-checklist.md`, `format-compliance-audit.md` | Enter 10B-1: unify formal citations, figure/table numbering, captions, and cross-references under the school template style map. |
