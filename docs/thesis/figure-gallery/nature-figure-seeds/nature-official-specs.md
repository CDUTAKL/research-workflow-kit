# Nature 官方图表规范摘要

> 来源: Nature 期刊官方 artwork guidelines、figure specifications、submission instructions。
> 这是 Nature 系列期刊的图表标准，也是本地 QA 清单的基准。

---

## 一、图表基本规格

### 尺寸

| 图幅类型 | 宽度 | 说明 |
|---------|------|------|
| 单栏 (single column) | 89 mm | 最常用，适合大多数 bar/line/scatter |
| 1.5 栏 | 120 mm | 中等复杂度 |
| 双栏 (double column) | 183 mm | 仅用于非常复杂的 multi-panel 图 |

**高度**：与宽度成比例，通常不超过 230 mm。

### 字号

| 元素 | 最小字号（最终尺寸） | 推荐 |
|------|---------------------|------|
| 轴标签 | 6 pt | 7-8 pt |
| 刻度数字 | 5 pt | 6-7 pt |
| 图例 | 6 pt | 7 pt |
| Panel 字母 (a, b, c) | 8 pt | 9-10 pt bold |
| 图中的标注文字 | 5 pt | 6 pt |

**关键原则**：最终出版尺寸下，所有文字必须可读。如果你的图在 Word/LaTeX 中缩放到最终尺寸时字看不清，那就太大了。

### 分辨率

| 阶段 | 分辨率 | 格式 |
|------|--------|------|
| 初次提交 | 150-300 dpi | PDF (矢量优先) / JPEG / PNG |
| 最终接受 | 300-600 dpi (光栅) | TIFF / EPS / PDF / AI |
| 线图/图表 | 矢量优先 | PDF / EPS / SVG → 转为 PDF/EPS |

### 色彩模式

- **线上**: RGB
- **印刷**: CMYK（但 Nature 会自动转换）
- **推荐**: 初始提交用 RGB，最终接受时提供 CMYK

---

## 二、图例和标注规范

### Panel 标注

- 用小写粗体字母：**a**, **b**, **c**（不是 A, B, C 或 (a), (b)）
- 放在每个 panel 的左上角或左下角
- 全文所有图的 panel 字母风格统一

### 图例 (Legend)

- 图例应放在图中，尽量靠近对应数据
- 不推荐在图外单独放一个 legend box（除非不可避免）
- 图例文字简洁，尽量用缩写后用 caption 解释

### 误差条

- 必须注明误差条的含义（SD / SEM / CI）
- 在 caption 中明确说明（如 "Error bars represent s.e.m."）
- 如果使用 CI，注明置信水平

### 统计显著性

- 标注方式: *P < 0.05, **P < 0.01, ***P < 0.001
- 在 caption 中说明统计检验方法
- 不要夸大 P 值的视觉呈现

---

## 三、文件格式和导出要求

### 矢量图（优先）

| 格式 | 适用场景 |
|------|---------|
| PDF | 首选，嵌入字体，可编辑 |
| EPS | 传统矢量格式 |
| SVG | Web 优先，可换为 PDF/EPS 提交 |
| AI (Adobe Illustrator) | 可编辑源文件（最好） |

### 光栅图（必要时）

| 格式 | 适用场景 |
|------|---------|
| TIFF (LZW 压缩) | 照片、microscopy、凝胶图像 |
| JPEG (最高质量) | 备选（不推荐，有损） |
| PNG | 截图、UI 界面 |

### 字体嵌入

- PDF 必须嵌入所有字体
- 推荐字体: Helvetica, Arial, Times New Roman, Symbol
- 避免使用未嵌入的专有字体

---

## 四、色彩使用建议

### 色盲友好

- 5-8% 的男性有某种形式的色盲
- 避免仅靠红/绿区分关键信息
- 推荐配色方案:
  - 橙 + 蓝（而不是红 + 绿）
  - 用线型/标记形状辅助颜色区分
- 色盲模拟检查：用 Color Oracle 或类似工具

### 色彩一致性

- 同一篇论文中，相同类型的数据使用相同颜色
- 同一变量在不同图中保持配色一致
- 方法名和颜色的映射应全局唯一

---

## 五、Caption 规范

### 结构

1. **第一句**: 概述图的内容（非标题，是完整的描述句）
2. **后续**: 逐 panel 描述
3. **结尾**: (可选) 缩略词说明、统计检验说明、误差条含义

### 示例

```
Figure 1 | Overview of the proposed framework. a, The input data
pipeline processes raw sequences through three preprocessing stages.
b, The core architecture consists of four stacked modules with
residual connections. c, Performance comparison on benchmark
datasets (n = 5 independent runs; error bars, s.d.; *P < 0.05,
**P < 0.01, two-sided t-test). d, Ablation study showing the
contribution of each component.
```

### 禁忌

- caption 中不重复正文内容（两个地方中有一处就够了）
- 不包含参考文献引用（除非必要）
- 不做过度解读（"significantly outperforms" → 留给正文）

---

## 六、Multi-panel 布局

### 排列规则

- Panel 从左到右、从上到下排列
- 用 a, b, c, d 标注
- 理想 panel 数: 3-6 个
- 超过 8 个 panel: 考虑拆分到 Supplemental

### 间距和对齐

- Panel 之间留白均匀
- 所有 panel 的边界对齐
- 同类型图（如多个 bar chart）保持相同尺寸

### 坐标轴

- 同一行/列的 panel，坐标轴刻度字体、范围应统一
- 相邻 panel 可以共享坐标轴标签（节省空间）
- 如果多个 bar chart 对比同一组 baseline，Y 轴范围应一致

---

## 七、QA 检查清单

在提交前逐项检查（也适合作为 figure-audit-standard.md 的补充）：

- [ ] 所有文字在最终尺寸下 >= 5 pt
- [ ] 图中没有多余元素（默认的 matplotlib 边框、上/右轴线）
- [ ] 图例不遮挡任何数据点
- [ ] 彩色图和灰阶图都可以正确诠释
- [ ] 所有 panel 的 a/b/c 标签存在、位置统一
- [ ] 误差条的含义在 caption 中注明
- [ ] 坐标轴有标签和单位
- [ ] Bar chart 的 baseline 是 0（如果有特殊原因不从 0，在 caption 中说明）
- [ ] 散点图有透明度控制，避免 overplotting
- [ ] 字体已嵌入 PDF
- [ ] 文件命名有含义（不是 figure1.png），包含版本号

---

> 这些标准应作为 figure-audit-standard.md 的基准线。每张生成的图都应逐项通过此清单。
