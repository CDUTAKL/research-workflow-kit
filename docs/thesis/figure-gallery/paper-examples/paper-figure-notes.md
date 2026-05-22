# Paper Figure Notes — 高水平论文图结构化拆解

> 每篇论文只选 1-3 张最优秀的图，拆解其设计决策，不照搬图像。
> 来源涵盖 Nature Machine Intelligence、Nature Methods、Nature Communications、IEEE TPAMI/TNNLS 等。

---

## 案例 1: AlphaFold2 (Nature 2021, Jumper et al.)

- **来源**: Nature 596, 583–589 (2021). DOI: 10.1038/s41586-021-03819-2
- **图编号**: Figure 1 (schematic overview)
- **图型类型**: multi-panel schematic + flow diagram
- **Panel 结构**: 4 panels (a-d)，从左到右、从上到下阅读顺序
  - a: 输入序列 → MSA → 结构数据库检索（信息流概览）
  - b: Evoformer 模块的内部结构
  - c: Structure module 的迭代精修过程
  - d: 最终输出的循环精修示意
- **主 panel 内容**: panel b（核心算法架构）
- **支撑 panel 内容**: a（上下文）、c/d（细节放大）
- **配色**: 
  - 蓝色系 = 序列/遗传信息
  - 橙色系 = 结构/3D 信息
  - 灰色 = 辅助元素
  - 色彩数量控制在 5 种以内，色盲友好
- **图例位置**: 直接在图中标注，无独立图例框
- **caption 结构**: 
  - 第一句: 概述整张图展示什么
  - 后续: a, ... b, ... c, ... d, ... 逐 panel 描述
  - 不解释方法细节（留给正文），只说"展示了什么"
- **坐标轴处理**: schematic 图无坐标轴；结构图中用简洁的 N→C 方向标注
- **可借鉴点**:
  1. 信息流从左到右、从上到下，符合阅读习惯
  2. 颜色编码一致（序列=蓝，结构=橙），全文统一
  3. 复杂模块用半透明框分组，降低认知负荷
  4. panel 间用箭头连接，明确因果关系
  5. caption 克制——只描述"是什么"，不解释"为什么"
- **不适合点**:
  1. 这种级别的 schematic 需要专业插画师参与
  2. 过度简化可能让读者误解实际计算流程
- **对应本地模板**: multi_panel（结构示意部分需要 Figma 后期精修）

---

## 案例 2: Swin Transformer (ICCV 2021 best paper, Liu et al.)

- **来源**: ICCV 2021 / IEEE TPAMI. arXiv: 2103.14030
- **图编号**: Figure 2 (architecture overview)
- **图型类型**: network architecture diagram
- **Panel 结构**: 2 个主 panel + 2 个细节 panel
  - a: 整体层级架构（4 个 stage，patch merging）
  - b: 两个连续的 Swin Transformer blocks
  - c: 移位窗口的注意力计算示意
- **主 panel 内容**: panel a（宏观架构一眼看清）
- **支撑 panel 内容**: b/c（关键创新点的技术细节）
- **配色**: 
  - 不同 stage 用不同底色区分
  - W-MSA / SW-MSA 用不同颜色块
  - 整体控制在 4 种主色
- **图例位置**: 直接标注在图中各模块上
- **caption 结构**: 先概述架构，再逐 panel 描述，最后缩略词解释
- **可借鉴点**:
  1. 层级递进式展示：先大局(a)，再细节(b)，再关键创新(c)
  2. 用虚线框表示窗口分区，视觉区分度高
  3. 每个模块内标注维度信息 (H×W×C)，方便复现
  4. 颜色不冗余——每个颜色有明确的语义
- **不适合点**:
  1. 图中信息密度很高，小尺寸打印时标签可读性差
  2. panel c 的窗口移位概念对不熟悉的读者不够直观
- **对应本地模板**: render_network_architecture.py + multi_panel

---

## 案例 3: UMAP (McInnes et al., 2018, Nature Methods)

- **来源**: Nature Methods (2018). DOI: 10.1038/s41592-018-0041-x
- **图编号**: Figure 1 (method demonstration)
- **图型类型**: scatter + comparison multi-panel
- **Panel 结构**: 5 panels
  - a: t-SNE vs UMAP on MNIST
  - b: t-SNE vs UMAP on FMNIST
  - c: t-SNE vs UMAP on Flow cytometry
  - d: 运行时间对比 bar chart
  - e: 聚类效果定量对比
- **主 panel 内容**: a（最经典数据集，第一印象）
- **支撑 panel 内容**: b/c（验证泛化性）、d/e（效率+定量）
- **配色**: 
  - scatter: 10 类离散色（分类数据）
  - bar chart: 统一的低饱和度色
  - t-SNE 在左、UMAP 在右，形成对称比较
- **图例位置**: a 中有图例，其他 panel 省略（颜色含义一致）
- **caption 结构**: 先说明比较目的，再逐一列出 panel 内容和关键发现
- **可借鉴点**:
  1. 比较型图表的关键：左右对称布局，让读者直接对比
  2. 定性（scatter）+ 定量（bar）组合论证
  3. 颜色在 a 中定义一次，b/c 继承，减少重复
  4. 运行时间用 log scale bar chart（处理数量级差异）
- **不适合点**:
  1. 5 panels 在小图幅下很拥挤
  2. 散点图在黑白打印时区分度下降
- **对应本地模板**: multi_panel + scatter + log_bar

---

## 案例 4: Attention Is All You Need (Vaswani et al., NeurIPS 2017)

- **来源**: NeurIPS 2017. arXiv: 1706.03762
- **图编号**: Figure 1 (Transformer architecture)
- **图型类型**: network architecture diagram
- **Panel 结构**: 单张大图，左右对称（Encoder / Decoder）
- **主 panel 内容**: 整体 Transformer 结构
- **配色**: 
  - 橙色 = 注意力相关
  - 蓝色 = FFN 相关
  - 灰色 = Embedding / Positional Encoding
- **图例位置**: 直接在图中标注层名称
- **caption 结构**: 极简——"The Transformer — model architecture."
- **可借鉴点**:
  1. 左右对称布局完美传达 Encoder-Decoder 结构
  2. 残差连接用弧形箭头，视觉优雅
  3. N× 标注表示层数复用，简洁
  4. 输入/输出用非框化文本，区分数据流和模块
  5. 颜色克制——3 种语义色 + 灰色
- **不适合点**:
  1. 对完全不了解 attention 的读者不够友好
  2. 缺少维度标注（后续论文如 Swin 补上了这个缺陷）
- **对应本地模板**: render_network_architecture.py

---

## 案例 5: scGPT (Cui et al., Nature Methods 2024)

- **来源**: Nature Methods 21, 1470–1480 (2024)
- **图编号**: Figure 1 (overview + benchmark)
- **图型类型**: schematic + bar chart + scatter multi-panel
- **Panel 结构**: 6 panels
  - a: 预训练 + 微调流程 schematic
  - b: 细胞类型注释 benchmark bar chart
  - c: 基因扰动预测 scatter
  - d: 多组学整合 UMAP
  - e: GRN 推断对比
  - f: 批次效应校正评估
- **主 panel 内容**: b（核心 benchmark，bar chart 最直观）
- **配色**: 
  - scGPT = 统一的高亮色（橙色/红色）
  - 其他方法 = 灰色系
  - 让自己的方法在视觉上"弹出"
- **图例位置**: b 的图例在顶部，scatter 中直接标在图中
- **caption 结构**: 先 overview，再逐 panel 描述，claim 克制
- **可借鉴点**:
  1. "自己=高亮，别人=灰色"是最有效的比较策略
  2. 每个 benchmark 用最适合的图型（bar/scatter/UMAP）
  3. 6 panels 但逻辑清晰：schematic → 任务1 → 任务2 → ... 
  4. 星号(*)标注统计显著性，直观
- **不适合点**:
  1. 6 panels 在小图幅下信息过载
  2. 多个 UMAP 的配色方案不统一
- **对应本地模板**: multi_panel + grouped_bar + scatter + heatmap

---

## 案例 6: ChatGPT/InstructGPT (Ouyang et al., NeurIPS 2022)

- **来源**: NeurIPS 2022. arXiv: 2203.02155
- **图编号**: Figure 2 (training pipeline + evaluation)
- **图型类型**: flow diagram + grouped bar chart + line trend
- **Panel 结构**: 4 panels
  - a: RLHF 三阶段训练流程
  - b: 人类偏好对比（win rate bar chart）
  - c: 不同模型大小的 scaling trend
  - d: 不同 KL 约束下的 reward 曲线
- **主 panel 内容**: b（win rate 是最核心的 claim 证据）
- **支撑 panel 内容**: a（方法背景）、c/d（消融分析）
- **配色**: 
  - 不同方法用离散色
  - PPO-ptx = 蓝色（最终方案），其他方法 = 灰色/绿色
  - 和图 5 scGPT 类似的"高亮自己"策略
- **图例位置**: b 图例在底部，c/d 直接标在曲线旁
- **caption 结构**: 描述性为主，数字在正文中
- **可借鉴点**:
  1. Flow diagram (a) + 定量对比 (b) + 消融分析 (c/d) 的经典三段式
  2. Bar chart 顶部直接标数值，不需要读者估算
  3. Error bar 清晰可见
  4. Panel c 的 log scale 处理了跨数量级数据
- **不适合点**:
  1. 三阶段流程图中步骤的边界不够清晰
  2. Bar 的颜色和 flow diagram 中的阶段颜色没有对应关系
- **对应本地模板**: grouped_bar + line_trend + multi_panel

---

## 案例 7: ImageNet Classification with Deep CNN (Krizhevsky et al., NeurIPS 2012)

- **来源**: NeurIPS 2012 (AlexNet). DOI: 10.1145/3065386
- **图编号**: Figure 2 (architecture) + Figure 4 (visualization)
- **图型类型**: architecture diagram + image plate
- **Panel 结构**: 
  - Figure 2: 上下两路 GPU 的 CNN 架构
  - Figure 4: 8 行 × 8 列的卷积核可视化 + 检索结果
- **主 panel 内容**: Figure 2 的架构图
- **配色**: 
  - GPU 1 / GPU 2 用不同颜色区分
  - 卷积核可视化保留了原始色彩空间
- **图例位置**: 架构图中在模块上直接标注
- **caption 结构**: 简短描述 + 关键发现（如"columns show similar image patches"）
- **可借鉴点**:
  1. 架构图的"堆叠式"画法——数据从下往上流动，每层横向展开，至今仍是标准
  2. 卷积核可视化(image plate)以网格排列，每格一张图，便于比较
  3. 架构图中层的宽度编码了通道数信息
- **不适合点**:
  1. 双 GPU 拆分在现代单 GPU 上不再必要
  2. 图中缺少维度标注
- **对应本地模板**: image_plate + render_network_architecture.py

---

## 案例 8: scVI (Lopez et al., Nature Methods 2018)

- **来源**: Nature Methods 15, 1053–1058 (2018)
- **图编号**: Figure 1 (probabilistic model + evaluation)
- **图型类型**: graphical model + scatter + bar
- **Panel 结构**: 4 panels
  - a: 概率图模型（graphical model notation）
  - b: latent space visualization (scatter)
  - c: imputation accuracy (bar chart)
  - d: differential expression comparison (scatter)
- **配色**: 
  - 概率图中不同变量类型用不同形状/颜色（观察变量=灰色，隐变量=白色，参数=点状）
  - scatter 中按细胞类型着色，配色来自 standard 生物信息学约定
- **图例位置**: graphical model 不需要图例（notation 自解释），scatter 有独立图例
- **caption 结构**: 前半解释 a 的 notation，后半描述 b-c-d 的实验发现
- **可借鉴点**:
  1. Graphical model 用标准统计符号（圆=变量，箭头=依赖），学科内读者无需图例
  2. 概率模型 + 实验验证的经典结构：先告诉读者"模型长什么样"(a)，再证明"它有用"(b-d)
  3. Scatter plot 的透明度和点大小经过仔细调节，避免 overplotting
- **不适合点**:
  1. Graphical model notation 对非统计背景读者不友好
  2. 4 panels 中 b 和 d 都是 scatter，区分度不够
- **对应本地模板**: multi_panel + scatter + grouped_bar

---

> 持续更新：每读到一篇好论文的好图，追加一个新案例到此文件。
