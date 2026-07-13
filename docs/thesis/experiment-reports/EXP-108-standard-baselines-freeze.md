# EXP-108 标准外部基线冻结与主表写回说明

## 1. 冻结身份

- 实验 ID：`EXP-108-standard-baselines`。
- 目的：在固定数据、时间切分、可见输入、训练预算和评价程序下，比较 Persistence、LightGBM、GRU、STGCN 与 V6。
- 数据与评价契约：`DATA-102`、`DATA-103`、`docs/thesis/EXP-108-frozen-protocol.md`、`docs/thesis/event-label-contract.md`。
- 对齐主键：`(seed, split, forecast_origin, timestamp, node_id, horizon)`。
- 主评价范围：`event_scope=exp108_target_timestamp`；所有点预测分层与 bootstrap 均使用同一范围。
- 测试集逐行配对数：11,753,940；forecast-origin 聚类数：53,427；bootstrap 重采样次数：5,000；timestamp 聚类为敏感性复核。

## 2. 冻结结果

表中为已对齐预测的全局 MAE；“相对 V6”以 \((\mathrm{MAE}_{baseline}-\mathrm{MAE}_{V6})/\mathrm{MAE}_{baseline}\) 计算。LightGBM、GRU 和 STGCN 的独立训练重复使用种子 42、2026、3407；V6 与各基线的主比较使用匹配预测键的配对聚合结果。

| 方法 | 全局 MAE | V6 相对改善 | 证据定位 |
|---|---:|---:|---|
| Persistence | 0.022746 | 7.11% | 最低时序参照 |
| LightGBM | 0.022106 | 4.42% | 最强外部通用基线 |
| GRU | 0.023477 | 10.01% | 纯时序深度基线 |
| STGCN | 0.033495 | 36.92% | 训练期静态图基线 |
| 强行为基线 `behavior_concat_v5` | 0.021384 | 1.20% | 内部回退锚点 |
| V6 | **0.021128** | — | 验证集冻结的规则式多路径修正 |

V6 相对四个外部基线的全局 MAE 差值均为负，forecast-origin 95% CI 与 timestamp 复核 CI 均不跨 0。例如，相对 LightGBM 的差值为 -0.000978，forecast-origin 95% CI 为 [-0.001085, -0.000873]。

## 3. 分层边界

外部基线的优势并非所有基线、所有子组均同向：V6 相对 LightGBM、GRU 和 STGCN 在全局、事件窗口、活跃稳定和正负荷范围内均具有更低的 MAE；相对 Persistence，V6 在全局和事件窗口更低，而 Persistence 在活跃稳定与正负荷范围内更低。因此，正文将“外部基线优势”限定为**相对 LightGBM、GRU 和 STGCN 的一致优势，以及相对 Persistence 的全局/事件优势**，不作所有子组全面支配的表述。

相对强行为基线，V6 的全局及目标时刻事件范围 MAE 更低，但活跃稳定和正负荷范围的 MAE 分别高 0.001480 和 0.002728。该结果将作为分层异质性报告，而不是被省略或用“无退化”概括。

## 4. 产物核验与冻结例外

三个 seed 均正常结束；每个 seed 含 3,917,980 条预测、17,809 个 forecast origin，每个 origin 固定 220 条。预测键一致、目标值差异仅为 CSV 浮点往返误差（最大绝对差 4.44e-16），不构成标签不一致。

已修复一个**非指标性产物归档例外**：初始清单曾将三个 `logs/train.log` 写入同一错误哈希。现已按实际文件重算并更新三个 seed 的 `checksums.sha256`：seed-42 为 `7e5522f9c193aa60fedcff8e4bd903f2507aecc69e6031ed88872b7900a0ab99`，seed-2026 为 `669a260d0770213a1987a2b3f1e089939f4dcb7026d3938ec6d135cbc83c9c1c`，seed-3407 为 `f205225312aed4cfde3b4c13be3a60116f423b344b8eac145201076e0fa16a99`。三个 seed 的整份 `checksums.sha256` 均已通过 `sha256sum -c`，不改变预测文件、指标或配对统计结果；EXP-108 的归档状态可更新为“已审阅并完成文件校验”。

## 5. 可主张范围

允许写入：

1. V6 在统一协议下相对 LightGBM、GRU 和 STGCN 获得较低的全局 MAE，并有配对成组 bootstrap 支持。
2. V6 相对强行为基线的全局 MAE 降低 1.20%，但该内部增益在活跃稳定和正负荷子组不完全同向。
3. 外部基线与内部回退锚点的比较回答不同问题：前者检验对通用预测模型的相对表现，后者检验事件触发式修正能否在已强化的行为预测上提供增量价值。

禁止写入：

1. “V6 在所有基线、所有分层上均占优”。
2. 将 target-time 的事件统计与旧版 origin-time 事件统计混合为同一排名。
3. 以日志哈希例外已修复为由作任何声明，除非最终归档清单已重算并复核。
