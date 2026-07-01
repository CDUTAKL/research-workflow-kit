# 论文图表终稿冻结清单（2026-06-30）

## 冻结结论

本轮将 `FIG-SUPP-009_input_feature_composition` 从正文图库移出，原因是其内容与 PPT 第 1 页系统架构图和模型结构细节图存在功能重复。相关 SVG/PDF/PNG/source/note 已归档至 `figures/final/excluded_from_thesis/`，不再作为正文插图候选。

`FIG-ROBUST-001_exp106_robustness_downgrade` 不作为正文必用图，最多作为附录备选。正式正文采用 `FIG-ROBUST-002_exp106_sensitivity_summary` 或文字/表格说明稳健性。

## 正文推荐用图

1. FIG-DATA-001_dataset_sample_composition
2. FIG-DATA-002_load_event_state_distribution
3. FIG-SUPP-010_event_window_sample_distribution
4. FIG-GRAPH-001_behavior_event_adjacency
5. PPT-FINAL-001 第 1 页：系统架构与事件预测触发机制图
6. 时间特征图结构事件触发预测机制图_终稿小修_可编辑
7. 事件触发式预测修正机制图解
8. PPT-FINAL-001 第 2 页：预测修正方法综合评价体系图
9. FIG-RESULT-001_exp103_main_result
10. FIG-RESULT-002_exp103_ablation_comparator
11. FIG-RESULT-004_exp103_multiseed_significance
12. FIG-SUPP-001_weak_baseline_result
13. FIG-RESULT-005_exp103_weak_baseline_comparison
14. FIG-SUPP-002_event_stable_grouped_error
15. FIG-RESULT-003_event_trigger_diagnostics
16. FIG-SUPP-003_trigger_hit_false_alarm
17. FIG-SUPP-004_typical_event_day_case
18. FIG-SUPP-011_prediction_error_distribution
19. FIG-INTERVAL-001_exp104_interval_calibration
20. FIG-INTERVAL-002_exp104_interval_calibration_detail
21. FIG-SUPP-005_interval_coverage_width_tradeoff
22. FIG-RISK-001_exp105_capacity_risk_proxy
23. FIG-SUPP-006_capacity_risk_level_distribution
24. FIG-RISK-002_exp105_risk_case_tradeoff
25. FIG-SUPP-007_feature_event_contribution
26. FIG-ROBUST-002_exp106_sensitivity_summary

## 排除项

- FIG-SUPP-009_input_feature_composition：与系统架构图和模型结构图重复，已归档。
- FIG-ROBUST-001_exp106_robustness_downgrade：不放正文必用图，附录备选。
- FIG-METHOD-001_method_pipeline：旧版方法图，版式和口径不如 PPT 新图。
- FIG-ARCH-001_event_deferral_model_structure：旧版模型结构图，存在旧口径风险。
- FIG-METHOD-002_event_triggered_correction：旧版机制图，被新机制图替代。
- FIG-OVERVIEW-001_experiment_chain_summary：旧版实验链条图，被 PPT/新图替代。
- FIG-SUPP-008_metric_system：被 PPT 第 2 页评价体系图替代。

## 质检状态

- 正文候选文件存在性：通过。
- 正文候选 SVG 不规范词扫描：通过，未发现“专家、selector、oracle、后处理脚本、测试集标签”等可见文本。
- 图题规范：正文插图应在 Word/WPS 图注中编号，图内不再额外放“图 X”。
- 插入建议：正文优先使用 PDF；SVG/PPTX 作为可编辑源文件保留；PNG 仅用于预览或答辩快速展示。
