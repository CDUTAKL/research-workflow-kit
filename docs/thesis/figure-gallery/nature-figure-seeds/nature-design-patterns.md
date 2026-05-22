# Nature Design Patterns — 图表设计模式总结

> 从 nature-figure 的 chart-atlas、gallery 和设计理论中提炼的设计模式。
> 这些是"什么时候用什么图、怎么组织 panel"的决策框架。

---

## 一、图表分类体系 (Chart Atlas)

### Category 1: Comparison (比较)

| 子类型 | 图型 | 典型场景 |
|--------|------|---------|
| 分组比较 | grouped_bar | 3-8 个方法在 2-5 个指标上的表现 |
| 排序比较 | horizontal_bar / ablation_barh | 消融实验、特征重要性排序 |
| 多对一比较 | forest plot | 效应量 + 置信区间 |
| 配对比较 | scatter (对角线) | 两组条件下同一批样本的比较 |

### Category 2: Trend (趋势)

| 子类型 | 图型 | 典型场景 |
|--------|------|---------|
| 连续趋势 | line_trend | 训练曲线、消融曲线、scaling law |
| 多变量趋势 | multi_line | 多种方法随同一超参变化 |
| 增长率 | log_line | 指数增长数据 |

### Category 3: Distribution (分布)

| 子类型 | 图型 | 典型场景 |
|--------|------|---------|
| 单变量分布 | histogram / violin | 指标分布、不确定性可视化 |
| 多变量分布 | box / violin / raincloud | 多组样本的分布对比 |
| 二维分布 | scatter / hexbin / heatmap | 两个连续变量的关系 |
| 不确定性 | error_bar / confidence_band | 模型输出的置信范围 |

### Category 4: Relationship (关系)

| 子类型 | 图型 | 典型场景 |
|--------|------|---------|
| 相关性 | scatter + regression line | 预测 vs 真实、两个指标的相关性 |
| 网络/图 | network / adjacency_matrix | 基因调控网络、知识图谱 |
| 层次 | dendrogram / tree | 聚类结果、分类树 |

### Category 5: Composition (组成)

| 子类型 | 图型 | 典型场景 |
|--------|------|---------|
| 静态组成 | stacked_bar / pie (慎用) | 各部分占比 |
| 变化组成 | stacked_area | 组成随时间变化 |
| 矩阵组成 | heatmap / confusion_heatmap | 混淆矩阵、相关性矩阵 |

### Category 6: Flow / Process (流程)

| 子类型 | 图型 | 典型场景 |
|--------|------|---------|
| 流程 | flow_diagram | 方法论 overview |
| 架构 | network_diagram | 模型结构 |
| 决策 | flowchart / tree | 算法逻辑 |

---

## 二、Panel 布局模式

### Pattern A: Overview → Core → Support（最常用）

```
+------+------+------+
|  a   |  b   |  d   |
+------+------+------+
|     c    |  (e)  |
+----------+--------+
a = overview/context
b = core result (largest panel)
c = detailed view
d, e = support/ablation
```

**适用于**: 大多数论文的 Figure 1 或主实验图

### Pattern B: 对称比较

```
+------+------+
|  a1  |  a2  |
+------+------+
|  b1  |  b2  |
+------+------+
|    c     |
+-----------+
left column = method A, right column = method B
```

**适用于**: 两个方法的全面对比

### Pattern C: Qualitative + Quantitative

```
+------+------+
|  a (visual) |
+------+------+
|  b   |  c   |
+------+------+
a = qualitative example (image/schematic)
b = quantitative metric 1
c = quantitative metric 2
```

**适用于**: 同时展示"看起来怎么样"和"数字怎么样"

### Pattern D: 层级递进

```
+-------------------+
|   a (overview)    |
+-------------------+
|  b (zoom in) | c  |
+--------------+----+
|    d    |    e    |
+---------+---------+
a = 宏观结构
b = 关键模块的细节放大
c, d, e = 定量支撑
```

**适用于**: 复杂的模型架构图 + 实验验证

---

## 三、配色模式

### Mode 1: Hero + Grays（★最推荐★）

```
Hero (你的方法): 暖色 (C0 = #E64B35 红/橙)
Baselines: 灰色系 (C1-C4 = #7F7F7F → #BFBFBF)
```

**来源**: scGPT, InstructGPT, UMAP 等

### Mode 2: Qualitative Palette

```
10 类以内的分类数据: Tableau 10 或 Nature 色盲友好配色
优先使用饱和度不同的色版，而非色相差异
```

### Mode 3: Diverging

```
正/负/零值: 蓝(-) → 白(0) → 红(+)
确保零值对应的颜色明显可辨
```

### Mode 4: Sequential

```
单变量渐变: 浅色(low) → 深色(high)
首选 viridis / cividis / magma（perceptually uniform）
```

---

## 四、图例位置决策树

```
数据线/条数是否 <= 4？
  ├─ 是 → 直接在图内标注（在线上/bar 旁边）
  └─ 否 → 图例是否影响数据可读性？
           ├─ 是 → 图例放在图外（右侧或底部）
           └─ 否 → 图例放在图内左上角
```

**原则**: 图例越靠近数据越好，但不遮盖数据。

---

## 五、坐标轴处理

### 轴的范围

| 图型 | X 轴 | Y 轴 |
|------|------|------|
| Bar chart | 类别，不需从 0 开始 | 必须从 0 开始 |
| Line chart | 数据范围，可裁剪 | 可以从最小值附近开始 |
| Scatter | 数据范围 ± 5% padding | 同左 |
| Heatmap | 类别 | 类别 |
| Histogram | 数据范围 | 必须从 0 开始 |

### 轴标签

- 每个轴必须有标签
- 标签必须包含单位（如 "Accuracy (%)", "Time (ms)"）
- 标签不应是变量名（如 "val_loss"），而应是人类可读的描述
- Log scale 必须明确标注

### 刻度

- 刻度数字不应过多（通常 4-6 个为宜）
- 刻度线向内（tick direction = in）
- 不保留不必要的上轴和右轴（matplotlib 默认有四条边框，只留左+下）

---

## 六、视觉层次

一个好的论文图有三个视觉层次：

| 层次 | 内容 | 视觉权重 |
|------|------|---------|
| 第 1 层 | 核心数据（最重要的结果） | 最深色/最大/最前 |
| 第 2 层 | 支撑数据（baseline、参考线） | 中等色/中等 |
| 第 3 层 | 辅助元素（轴、网格、标签） | 最浅色/最细线 |

检查方式：眯眼看图，第一时间看到的是核心数据吗？如果不是，调整视觉权重。

---

> 这些设计模式应直接指导 nature_plot_templates.py 中模板的默认参数。
