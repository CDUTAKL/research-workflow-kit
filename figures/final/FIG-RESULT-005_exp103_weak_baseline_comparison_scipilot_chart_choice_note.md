# FIG-RESULT-005 chart-choice note

## Figure claim

This supplement shows that EXP-103 already contains a weak-baseline ladder: removing event and graph information gives the highest error, behavior features form a strong baseline, and graph-structure branches improve over that baseline in the early optimized comparison. The frozen event-triggered method is shown as a positioning note rather than a strict same-run ranking item.

## Source data

- `outputs/EXP-103-train-optimized-42-5090/baseline_metrics.csv`
- `outputs/EXP-103-train-optimized-42-5090/graph_ablation_table.csv`
- `outputs/EXP-103-v6-event-deferral-rule-frozen/offline_deferral_metrics.csv`

## Chart choice

- Panel A uses horizontal bars for absolute MAE because method names are long and the figure needs to read at thesis width.
- Panel B uses relative percentage change against the behavior baseline to make weak-baseline and graph-branch differences interpretable.
- The frozen V6 method is included only as an annotated reference to avoid over-claiming across different run scopes.

## Caption-safe wording

图 X 展示 EXP-103 弱基线与图结构分支的补充对照。无图/无事件基线误差最高，行为特征基线显著降低误差，多个图结构分支在早期同口径对照中进一步改善 MAE。右侧注释给出冻结规则主方法相对强行为基线的定位结果，用于说明本文方法是在强行为基线和图结构分支证据基础上的事件触发式修正，而非仅与弱基线比较。
