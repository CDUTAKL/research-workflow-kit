# 论文图表终稿质检与冻结记录

更新时间：2026-06-30

## 质检口径

本轮质检按论文正文可插入标准执行，重点检查：

- 图内不出现论文图题、`图 X`、`EXP`、`专家`、`expert`、`selector`、`oracle`、`补充结果` 等不适合正文图面的字样；
- 每张数据图至少具备 SVG、PDF、PNG 预览和源数据 CSV；
- 多面板图的 A/B/C 标号、图例、坐标轴和标签不发生明显重叠；
- 图面说明不替代论文图注，图内仅保留必要的指标、样本量、单位和方法分组；
- 方法类图优先采用 PPT/WPS 手工精修版本，旧的自动生成结构图不进入正文。

## 正文推荐图表冻结清单

### 方法与机制图

| 顺序 | 图名建议 | 推荐文件 | 冻结状态 | 备注 |
|---|---|---|---|---|
| 1 | 方法总体流程图 | `论文图_终稿SVG转PPT可编辑版.pptx` 中的 PPT 模板路线图预览，或其最终导出 SVG/PDF | 待用户在 WPS 中最终导出 | 可替代旧 `FIG-METHOD-001_method_pipeline`。旧图不进入正文。 |
| 2 | 事件感知时空图预测修正模型结构 | `/Users/xushuyuan/Downloads/时间特征图结构事件触发预测机制图_终稿小修_可编辑.svg` | 待用户最终人工确认 | 可替代旧 `FIG-ARCH-001_event_deferral_model_structure`。旧图存在“专家/EXP”等可见词，不进入正文。 |
| 3 | 事件触发式预测修正机制 | `/Users/xushuyuan/Downloads/事件触发式预测修正机制图解.svg` | 可用，但建议从 PPT/WPS 再导出 PDF 终版 | 图面逻辑清楚；SVG 原文含隐藏 `EXP/V6` 字符，正式插入前建议以 WPS/PPT 重新导出 PDF 或清理 SVG 元数据。 |

### 数据与结构基础图

| 顺序 | 图名建议 | 推荐文件 | 冻结状态 | 备注 |
|---|---|---|---|---|
| 4 | 数据集样本构成 | `figures/final/FIG-DATA-001_dataset_sample_composition.svg` | 通过 | SVG/PDF/PNG/source 均存在，图内无标题。 |
| 5 | 负荷与事件状态分布 | `figures/final/FIG-DATA-002_load_event_state_distribution.svg` | 通过 | 图面较规整，可用于数据分析章节。 |
| 6 | 行为事件图结构 | `figures/final/FIG-GRAPH-001_behavior_event_adjacency.svg` | 通过 | SVG 内有嵌入图像数据字符串触发误报，但图面可见文本没有不规范词。 |
| 7 | 模型输入特征构成 | `figures/final/FIG-SUPP-009_input_feature_composition.svg` | 通过 | 新增。用于方法输入或数据特征小节，说明历史负荷、行为特征、事件状态和图结构输入如何进入预测与触发模块。 |
| 8 | 事件窗口样本分布 | `figures/final/FIG-SUPP-010_event_window_sample_distribution.svg` | 通过 | 新增。展示事件窗口与稳定窗口样本占比以及事件类型构成，可支撑事件窗口稀疏性与分窗口评价必要性。 |

### 实验评价体系图

| 顺序 | 图名建议 | 推荐文件 | 冻结状态 | 备注 |
|---|---|---|---|---|
| 9 | 实验评价指标体系 | `figures/final/FIG-SUPP-008_metric_system.svg` | 通过 | 新增。建议放在实验设置章节，用于承接“点预测误差、关键窗口误差、区间可靠性、风险代理指标、稳健性检查”的综合评价口径。 |

### 点预测与事件修正结果图

| 顺序 | 图名建议 | 推荐文件 | 冻结状态 | 备注 |
|---|---|---|---|---|
| 10 | 主点预测结果 | `figures/final/FIG-RESULT-001_exp103_main_result.svg` | 已返修，通过 | 图内“EXP-103 冻结结果”已改为“冻结点预测结果”。 |
| 11 | 分支消融与对照结果 | `figures/final/FIG-RESULT-002_exp103_ablation_comparator.svg` | 通过 | 图面支持“直接替换风险”和“事件触发修正收益”叙事。 |
| 12 | 多种子与统计显著性支持 | `figures/final/FIG-RESULT-004_exp103_multiseed_significance.svg` | 通过 | 适合作为主结果后的统计支撑图。 |
| 13 | 弱基线对照补充 | `figures/final/FIG-RESULT-005_exp103_weak_baseline_comparison.svg` 或 `figures/final/FIG-SUPP-001_weak_baseline_result.svg` | 通过 | 二选一即可，避免正文重复。若需要“弱基线补充”，优先用 `FIG-RESULT-005`。 |
| 14 | 事件窗口与稳定窗口分组误差 | `figures/final/FIG-SUPP-002_event_stable_grouped_error.svg` | 通过 | 可作为“稳定窗口不退化、事件窗口改善”的辅助图。 |
| 15 | 事件触发命中与误触发诊断 | `figures/final/FIG-SUPP-003_trigger_hit_false_alarm.svg` | 已返修，通过 | A/B 已统一坐标布局，右侧不再空旷。 |
| 16 | 预测误差分布对比 | `figures/final/FIG-SUPP-011_prediction_error_distribution.svg` | 通过 | 新增。展示行为基线分支与动态图结构分支的逐样本绝对误差分布和成对误差差值。 |
| 17 | 典型事件日预测案例 | `figures/final/FIG-SUPP-004_typical_event_day_case.svg` | 通过 | 优先用此图；弃用旧 `FIG-CASE-001`，因为旧图图内含“本地未保存冻结 V6...”说明。 |

### 区间校准与容量风险图

| 顺序 | 图名建议 | 推荐文件 | 冻结状态 | 备注 |
|---|---|---|---|---|
| 18 | 区间校准结果 | `figures/final/FIG-INTERVAL-001_exp104_interval_calibration.svg` | 通过 | 适合放入区间预测实验小节。 |
| 19 | 区间校准细节 | `figures/final/FIG-INTERVAL-002_exp104_interval_calibration_detail.svg` | 通过 | 若正文篇幅紧，可放附录。 |
| 20 | 区间覆盖与宽度权衡 | `figures/final/FIG-SUPP-005_interval_coverage_width_tradeoff.svg` | 已返修，通过 | A/B 对齐、图例横置、无重叠。 |
| 21 | 容量风险代理结果 | `figures/final/FIG-RISK-001_exp105_capacity_risk_proxy.svg` | 通过 | 可作为容量风险代理主图。 |
| 22 | 容量风险等级分布 | `figures/final/FIG-SUPP-006_capacity_risk_level_distribution.svg` | 通过 | 可用于补充说明风险分布结构。 |
| 23 | 特征重要性或事件特征贡献 | `figures/final/FIG-SUPP-007_feature_event_contribution.svg` | 通过 | Lollipop + 环形贡献图比纯柱状图更适合作为解释图。 |

### 稳健性与降级相关图

| 顺序 | 图名建议 | 推荐文件 | 冻结状态 | 备注 |
|---|---|---|---|---|
| 24 | 稳健性敏感性摘要 | `figures/final/FIG-ROBUST-002_exp106_sensitivity_summary.svg` | 附录候选 | 图内仍使用 EXP 编号口径，正文不建议直接使用；若放附录，应重写标签为“点预测主实验/区间校准/容量风险代理”。 |
| 25 | 稳健性与降级决策 | `figures/final/FIG-ROBUST-001_exp106_robustness_downgrade.svg` | 不建议正文使用 | 图内文字偏流程化，且可见 `EXP` 编号，不符合当前正文图面口径。建议用表格或正文文字替代。 |

## 弃用或仅保留备份的图

| 文件 | 决策 | 原因 |
|---|---|---|
| `figures/final/FIG-METHOD-001_method_pipeline.svg` | 弃用 | 旧版方法流程图，图面风格和术语不如 PPT 精修版本。 |
| `figures/final/FIG-METHOD-002_event_triggered_correction.svg` | 弃用 | 旧版机制图含“事件专家”等旧口径，被 `/Users/xushuyuan/Downloads/事件触发式预测修正机制图解.svg` 替代。 |
| `figures/final/FIG-ARCH-001_event_deferral_model_structure.svg` | 弃用 | 旧版模型结构图含“专家/EXP”等旧口径，被时间特征图结构事件触发预测机制图替代。 |
| `figures/final/FIG-OVERVIEW-001_experiment_chain_summary.svg` | 弃用 | 图面含 `EXP-101` 至 `EXP-106` 和“专家”旧叙事，不进入正式正文。 |
| `figures/final/FIG-CASE-001_typical_event_day_prediction_case.svg` | 弃用 | 图内含“本地未保存冻结 V6...”说明，正式论文不宜使用；用 `FIG-SUPP-004` 替代。 |
| `figures/final/FIG-RISK-002_exp105_risk_case_tradeoff.svg` | 附录或弃用 | 图内 case id 仍含 `v6_` 字样，正文不建议使用。 |

## 当前结论

现有论文图表已经进入 Stage 9 终稿冻结状态。补充四张图后，正文主线候选图约 23 张，其中方法/机制图 3 张、数据与输入基础图 5 张、实验评价体系图 1 张、点预测与事件修正结果图 8 张、区间和风险解释图 6 张。若正文篇幅偏紧，可将“区间校准细节”“预测误差分布对比”“容量风险等级分布”等作为附录候选。稳健性与降级图不建议作为正文图直接使用，可改为正文表述、表格或附录材料。

正式插入 Word/WPS 前仍需做最后一步人工版面检查：按论文正文实际宽度插入 PDF 或 SVG，导出 PDF 后确认文字、图例和面板标签清晰可读。
