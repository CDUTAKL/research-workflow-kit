# FIG-ARCH-001 Architecture Note

图表目标：解释最终主方法的模型结构细节，而不是重复总体技术路线或报告性能。

结构来源：
- `docs/thesis/method-event-deferral-v6.md`
- `configs/experiment/EXP-103-v6-event-deferral.yaml`
- `src/evcs/models/graph_tcn.py`
- `docs/thesis/experiment-reports/frozen-experiment-result-tables.md`

图面口径：稳定窗口默认采用行为基线专家；事件触发器在验证集定阈值，只有高置信事件窗口才递延到事件专家；区间校准和容量风险代理位于点预测输出之后。

QA 注意：本图只描述结构，不把 EXP-103 至 EXP-106 的性能结论写入架构图内部，避免结构图承担结果图功能。
