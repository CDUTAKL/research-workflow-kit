# EXP-108 统一外部基线冻结协议

## 实验身份

- 实验 ID：`EXP-108-standard-baselines`。
- 目标：在同一数据、切分、输入可见性、训练预算和评价程序下比较四个外部基线。
- 正式目标环境：AutoDL RTX 5090；本地 Mac 仅运行合同检查和 CPU smoke。
- 后续性能升级继续保留 `EXP-107`，本实验不改变本文方法。

## 唯一协议

- 数据：`data/processed/evcs_timeslice.csv`。
- 缓存：`data/processed/evcs_tensor_cache_optimized.npz`。
- 切分：`chronological_70_15_15`，测试集不得用于调参、早停、阈值或图构建。
- 输入窗口：96 个 15 分钟步；预测步长：4 步。
- 随机种子：`42、2026、3407`。三个种子是最终冻结政策；仅当任一种子方向反转或成组 bootstrap 置信区间跨 0 时，才追加两个种子。
- 事件定义：接入、离站、接入离站并发和历史负荷跃迁；活跃会话数与占用率是预测时刻可见状态，不单独扩张事件集合。
- 禁止输入：未来离站/完成时间、最终交付电量、未来事件、测试期统计量。

## 基线身份

1. `Persistence`：对所有 horizon 使用预测起点最后可见负荷，`y_hat[t+h]=y[t]`；确定性，只运行一次。
2. `LightGBM`：使用与行为基线一致的历史负荷、日历和预测时刻可见行为状态；不输入未来事件标签。
3. `GRU`：输入 `[batch,node,96,feature]`，直接输出 `[batch,node,4]`。
4. `STGCN`：输入与 GRU 相同；邻接矩阵仅由训练期负荷正相关构造，固定 top-k=5，不使用测试期统计。

`Historical Average` 为可选补充，不进入表 5-2 的必跑集合。

## 训练与评价

- GRU、STGCN 使用相同最大 epoch、早停、损失、验证主指标和 batch-size 量级。
- LightGBM 只搜索配置中冻结的有限网格。
- 主指标：MAE；补充 RMSE、WAPE。
- 分层：事件窗口、活跃稳定、非活跃零负荷、正负荷、节点宏平均、horizon 1-4。
- 保存逐预测起点、节点和 horizon 的预测；使用 forecast origin 成组 bootstrap 5000 次，timestamp 作敏感性复核。
- 正式结论只引用与最终冻结方法完全对齐的预测和统计文件。

## 产物合同

每个方法/种子输出 `config_resolved.json`、`environment.txt`、`metrics.json`、`stratified_metrics.csv`、`horizon_metrics.csv`、`node_macro_metrics.csv`、`predictions.csv.gz`、`logs/train.log`、checkpoint 或无 checkpoint 说明、`manifest.json`。汇总阶段另写主表、多种子汇总、成组 bootstrap、来源映射和校验和。
