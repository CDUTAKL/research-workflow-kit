# EXP-103 V5 稳赢策略

生成日期：2026-06-16

## 当前判定

按本地 `final-full` 三 seed evidence 重新汇总后，`seed_count` 已恢复为 3。以 MAE 为主指标时：

- `event_graph_dynamic_v5` 是当前三 seed 平均 MAE 最优模型：MAE=0.021467，相比 `behavior_concat_v5` 提升约 1.041%，相比 `historical_correlation_graph_v5` 提升约 1.004%。
- `event_dtw_fusion_graph_v5` 是当前最稳的第二梯队：MAE=0.021486，三 seed 排名为 2/3/2，相比 `behavior_concat_v5` 提升约 0.954%。
- `historical_event_dual_graph_v5` 的 MAE 均值不是第一，但 RMSE 均值最优：RMSE=0.299998，相比 `behavior_concat_v5` 提升约 0.914%。

结论：已经过线，但还不是“稳赢”。现在的优势来自真实 event graph 族模型整体站在 `behavior_concat_v5` 和多数结构对照模型前面；风险来自三点：seed 数仍少、单 seed 中个别 disturbed control 曾经很强、当前 evidence 主要是聚合 CSV，还缺少全量 paired prediction 误差来支撑统计检验。

## 模型分组

我们的主模型：

- `event_graph_dynamic_v5`：动态事件图，当前 MAE 主冠军。
- `event_dtw_fusion_graph_v5`：事件图和 DTW demand 图融合，当前排名最稳定。
- `historical_event_dual_graph_v5`：历史相关图和事件上下文双路条件融合，当前 RMSE 最优。

强对照模型：

- `behavior_concat_v5`：只拼接行为/事件特征，不做图消息传递，是最关键非图深度 baseline。
- `historical_correlation_graph_v5`：历史负荷相关图，是最关键非事件图 baseline。
- `dtw_demand_graph_v5`：DTW 需求形状图，是需求相似性 baseline。
- `no_graph_v5`：无事件、无图的基础模型。

扰动/负控模型：

- `random_event_graph_v5`：保留图稀疏形态但随机化权重。
- `shuffled_event_graph_v5`：打乱事件图语义。
- `deleted_event_graph_v5`：事件图结构被置零。

## 立即能提高胜率的动作

1. 全量 prediction 导出，而不是只导出 samples。

   现在 `prediction_count` 约 3,917,980，但 evidence 中通常只保存 sample。要把每个 baseline、每个 seed、每个 horizon/node/time 的真实值和预测值保存为 `predictions_full.parquet` 或压缩 CSV。这样才能做 paired MAE 差值、bootstrap CI、Diebold-Mariano 类预测精度检验和 validation stacking。没有全量 paired 误差，就很难证明 0.5%-1.0% 的优势不是偶然。

2. 用 validation MAE 选 checkpoint。

   当前训练主要围绕 training/validation loss 早停，但论文主结论锁定 MAE。应增加 `checkpoint_metric: val_MAE_raw`，并让 best checkpoint 与主指标一致。这个改动不改变模型创新，只减少“用代理损失选错 checkpoint”的风险。

3. 做不碰 test 的 validation stacking。

   用 validation predictions 学一个非负 convex ensemble：

   `dynamic + fusion + dual + historical_correlation`

   权重只在 validation 上确定，test 只评一次。目标不是替代单模型结论，而是给“最终部署模型”一个更稳版本。当前 `event_graph_dynamic_v5` 与 `event_dtw_fusion_graph_v5` 的误差结构很可能互补：前者 MAE 最优，后者 RMSE/排名更稳，dual 又在 RMSE 上强。预测组合是 forecasting 领域常见的稳健化手段。

4. seed ensemble。

   同一模型跨 seed 平均预测通常比单 seed 更稳。最终可以报告两层结果：单模型三/五 seed 平均用于科学结论；seed ensemble 用于展示可部署性能上界。前提仍然是不在 test 上调权。

5. 保存 event-window 与 stable-window 的分层主指标。

   如果全局 MAE 只提升 1%，但 event-window MAE 提升明显更大，就能把贡献点讲得更稳：EVCS 的价值不是“所有时刻都魔法般更好”，而是在事件扰动时更能利用跨站关系。

## 更强的模型侧手段

1. 图门控正则从“有图即可”改为“有用才开”。

   当前 disturbed control 有时接近主模型，说明模型可能在部分 seed 中学到了泛化的图平滑，而不是充分利用事件语义。可以加入 gate sparsity / entropy / event-contrast regularization：事件窗口允许更高 gate，稳定窗口限制过度开门。

2. 图 DropEdge / graph dropout。

   训练时随机丢边，验证/测试时用完整图，可以降低对偶然边的依赖，缓解图模型过拟合和过平滑风险。对事件图尤其适合，因为我们希望模型利用稳定语义，而不是记住某些高权重边。

3. 动态 top-k 和温度搜索。

   当前 top-k 固定，可能让事件图在不同事件强度下过稀或过密。可以搜索 `top_k in {3,5,8,10}`、softmax temperature、rho smoothing 和 edge floor，并以 validation MAE 选择。重点不是扩大模型容量，而是让图结构强度与事件强度匹配。

4. 事件-需求混合图的可学习混合系数。

   `event_dtw_fusion_graph_v5` 已显示稳定性。下一步可以把 event/DTW/historical 三类图的混合系数做成 validation 约束下的 learnable simplex 或轻量 gate，而不是固定融合。这样能避免某一个图在某个 seed 失效时拖累整体。

5. SWA 或 EMA checkpoint averaging。

   对每个强模型在后期若干 epoch 做权重平均，常能降低 seed variance。它不改变模型结构，工程风险低，适合作为 V5 稳定性增强项。

6. 以 MAE 为中心的损失调度。

   可尝试 SmoothL1 到 L1 的 curriculum，或增加 validation MAE 驱动的 scheduler。目标是让训练目标、早停目标、论文主指标三者一致。

## 证据侧“稳赢”协议

最低可发表协议：

- 修复 `seed_count` 后重生成三 seed summary。
- 主结论只写 MAE；RMSE 作为补充，强调 dual 在 RMSE 上最优。
- 对 `event_graph_dynamic_v5`、`event_dtw_fusion_graph_v5`、`historical_event_dual_graph_v5` 与强对照做 paired bootstrap CI。
- 对所有模型做 3 seed mean/std/min/max，并报告每 seed 排名。

稳赢协议：

- 追加 2 个 seed，达到 5 seed。
- 导出全量 predictions，按同一 test instance 做 paired absolute-error difference。
- 对 `event_graph_dynamic_v5` vs `behavior_concat_v5`、`event_graph_dynamic_v5` vs `historical_correlation_graph_v5`、`event_dtw_fusion_graph_v5` vs `behavior_concat_v5` 做 bootstrap CI；CI 下界仍小于 0 才称稳。
- 做 validation stacking ensemble，若 ensemble 的 test MAE 同时优于全部单模型和全部 baseline，则作为“工程最优模型”；论文创新仍以 dynamic/fusion/dual 三个结构解释。
- 使用 Holm 或 Model Confidence Set 控制多模型比较问题，避免“十个模型里挑一个看起来最好”的质疑。

## 不建议做的事

- 不要用 test 集调 ensemble 权重、top-k 或学习率。
- 不要只报告最优 seed。
- 不要把 `random_event_graph_v5` 或 `shuffled_event_graph_v5` 的单 seed 强表现藏起来；应该用负控解释说明：它们证明图归纳偏置有帮助，但真实事件语义在平均和稳定性上仍更优。
- 不要把 RMSE 最优模型和 MAE 最优模型混成一个结论。主结论锁定 MAE，RMSE 作为补充发现。

## 调研依据

- Diebold-Mariano 预测精度比较：<https://doi.org/10.1080/07350015.1995.10524599>
- Model Confidence Set 多模型比较：<https://doi.org/10.3982/ECTA5771>
- Rolling-origin time-series cross-validation：<https://otexts.com/fpp3/tscv.html>
- Forecast combinations：<https://otexts.com/fpp3/combinations.html>
- Deep ensembles：<https://arxiv.org/abs/1612.01474>
- Stochastic Weight Averaging：<https://arxiv.org/abs/1803.05407>
- Graph WaveNet adaptive adjacency：<https://arxiv.org/abs/1906.00121>
- DropEdge graph regularization：<https://arxiv.org/abs/1907.10903>
- Temporal Fusion Transformers：<https://arxiv.org/abs/1912.09363>
- DCRNN traffic graph forecasting：<https://arxiv.org/abs/1707.01926>
