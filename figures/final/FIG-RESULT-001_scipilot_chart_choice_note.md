# FIG-RESULT-001 chart-choice note

论证目标：展示 EXP-103 中事件触发式预测修正相对强行为基线的主结果，强调全局 MAE（平均绝对误差）降低、事件窗口收益更明显、稳定窗口不退化。

数据剖析：输入为冻结实验汇总表，主要变量为方法类别、评估窗口和连续型误差指标；分组数很少，适合柱状/哑铃式对比，不适合折线、饼图或复杂热力图。

选图决定：采用三面板论文式结果图。A 面板使用局部放大的水平柱状图展示全局 MAE 精确值；B 面板展示全局、事件窗口、稳定窗口的 MAE 相对下降；C 面板展示事件窗口 MAE、RMSE（均方根误差）和 WAPE（加权绝对百分比误差）的补充证据。

避免的问题：不把 0.021385 与 0.021164 直接画成从零开始的单一柱状图，因为肉眼几乎看不出差异；同时在 A 面板明确标注为局部放大坐标，避免夸大结论。

源数据目录：`/Users/xushuyuan/Documents/Codex/EVCS-EventGraph-Thesis/files-mentioned-by-the-user-research/research-workflow-kit/outputs/EXP-103-v6-event-deferral-rule-frozen`。
