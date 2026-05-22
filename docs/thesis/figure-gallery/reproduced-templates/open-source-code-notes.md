# Open Source Code Notes — 论文图生成代码仓库拆解

> 搜集 GitHub 上带有完整画图代码的论文仓库和绘图模板库，做代码级拆解。
> 重点不是收藏 star，而是拆解代码模式和可集成到 nature_plot_templates.py 的改进点。

---

## 资源 1: SciencePlots (garrettj403/SciencePlots) — 6,800+ stars

- **来源**: https://github.com/garrettj403/SciencePlots
- **图型类型**: 通过 rcParams 全局设定所有 matplotlib 图的风格
- **代码结构**:
  - `styles/` 目录下按期刊/用途分类: `science.mplstyle`, `nature.mplstyle`, `ieee.mplstyle`
  - 一个 `import scienceplots; plt.style.use(['science', 'nature', 'high-vis'])` 全局生效
  - 组合式配置: 多个 .mplstyle 层层覆盖
- **关键设计**: Journal 栏宽硬编码 (IEEE 3.4in single / 7.0in double); Nature, Science, IEEE 各一套预设
- **LaTeX 双轨**: `no-latex` style 切换到 `mathtext.fontset: stix` 作为 LaTeX 不可用时的降级方案
- **CJK 策略**: 单独字体族，数学字体保持 STIX (不被 CJK 污染)
- **色盲友好**: `high-vis` style 硬编码 CUD-compliant 7-color cycle
- **数据格式**: 不涉及数据，只改变 matplotlib 渲染
- **可复现性**: 极高，pip install + 一行代码
- **与本地模板对比**: SciencePlots 负责全局样式，本地模板负责图型结构——互补
- **可借鉴的代码模式**:
  1. 组合式样式配置: `['base', 'journal', 'color']` 层层覆盖
  2. 按期刊分类: Nature / IEEE / Elsevier 各一套风格
  3. LaTeX 自动检测和降级方案
  4. 网格和边框处理: 自动隐藏上/右 spine，向内刻度
  5. 颜色循环预设: 期刊常用的离散配色循环
- **不适合借鉴的**:
  1. 全局 rcParams 状态泄漏
  2. Times New Roman 依赖在 Docker 上破坏
  3. 2021 起低维护
- **推荐优先级**: 高 — 应作为 nature_plot_templates.py 的默认样式引擎

---

## 资源 2: ProPlot (lukelbd/proplot) — 1,100+ stars

- **来源**: https://github.com/lukelbd/proplot
- **图型类型**: 所有 matplotlib 图型 + 声明式 subplot 布局
- **代码结构**: 核心创新是 subplot spanning via 2D array syntax
- **关键设计**:
  - `pplt.subplots([[1,1,2],[3,3,4]])` — 每个整数 ID 占一个 cell，同 ID = 同一 subplot
  - `fig.colorbar(m, loc='b', span=2)` — colorbar 统一放在网格外侧
  - `ax.format()` — 一个方法替代 10+ 行 matplotlib 样板代码
  - xarray DataArray 自动读取 dims/attrs 作为轴标签
- **可复现性**: 高，但 monkey-patches matplotlib 内部，大版本升级可能破坏
- **与本地模板对比**: ProPlot 的 subplot 数组语法可直接集成到 multi_panel 模板
- **可借鉴的代码模式**:
  1. 声明式 subplot 布局: 二维数组定义面板占位
  2. Colorbar 统一定位: `loc='b'` + `span=2` 放在网格外侧
  3. `format()` 统一格式化: title, labels, limits, scale, grid 合并为一个方法
  4. xarray metadata 自动传播到图表标签
- **不适合借鉴的**:
  1. API 范围太大，学习曲线陡
  2. monkey-patches matplotlib 内部，社区小
- **推荐优先级**: 中 — 提取 subplot 数组语法和 colorbar loc/span 设计

---

## 资源 3: Seaborn (mwaskom/seaborn) — 12,500+ stars

- **来源**: https://github.com/mwaskom/seaborn
- **图型类型**: 统计图型（violin, box, heatmap, pairplot, jointplot, FacetGrid 等）
- **代码结构**: 高度封装的 API，一个函数调用完成数据分组 + 着色 + 统计量
- **关键设计**:
  - **Figure-level vs Axes-level 双轨 API**: `relplot()` 创建 figure + subplots; `lineplot()` 画在给定 axes 上
  - **Semantic mapping**: `hue='species', size='petal_length', style='species'` 字符串引用 DataFrame 列
  - **Error bar 抽象**: `errorbar=('ci', 95), err_style='band', n_boot=1000` 封装 bootstrap CI
  - **FacetGrid**: `col='treatment', row='dose'` 自动创建分组 subplot grid
  - **调色板工厂**: `cubehelix_palette()`, `diverging_palette()`, `light_palette()` 生成感知均匀的色序
- **数据格式**: pandas DataFrame (long format 优先)
- **可复现性**: 极高
- **与本地模板对比**: seaborn 适合探索分析，默认输出不是论文级；本地模板用 matplotlib 底层 + seaborn 调色板
- **可借鉴的代码模式**:
  1. Figure-level / Axes-level 双轨 API 设计 — 每个模板函数都应该遵循
  2. Semantic mapping: 用字符串引用列名进行自动分组
  3. Error bar 封装: 一行参数替代手动计算
  4. FacetGrid: 数据驱动的自动布局
  5. `despine()` 函数 — 一行去掉上/右 spine
- **不适合借鉴的**:
  1. 灰色网格默认主题不适合论文
  2. bootstrap 在 >100k 点上慢
  3. Figure-level 函数是闭盒，难以自定义
- **推荐优先级**: 高 — 研究 `palettes.py` 和 `_core/properties.py` 的颜色映射逻辑

---

## 资源 4: mpltex (lichengzhang/mpltex) — 400+ stars

- **来源**: https://github.com/lichengzhang/mpltex
- **图型类型**: ACS/APS 期刊专用样式 + 装饰器模式
- **代码结构**: `@mpltex.acs_decorator` 装饰器包装绘图函数，自动应用期刊样式
- **关键设计**:
  - ACS single column = (3.25, 2.5) inches; APS single = (3.4, 2.5) — 直接来自期刊 author guidelines
  - 装饰器自动设置 figure size + 样式 + 保存
- **可复现性**: 高
- **与本地模板对比**: mpltex 的装饰器模式可用于包装本地模板函数
- **可借鉴的代码模式**:
  1. 装饰器模式: 一个装饰器搞定样式 + 尺寸 + 导出
  2. 期刊尺寸预设: 硬编码期刊 author guidelines 的精确尺寸
- **不适合借鉴的**:
  1. 仅支持 ACS/APS
  2. 无 LaTeX 降级方案
  3. 装饰器隐藏太多内部细节
- **推荐优先级**: 中 — 装饰器模式和期刊尺寸预设值得移植

---

## 资源 5: cmocean — 350+ stars, 2,000+ 引用

- **来源**: https://github.com/matplotlib/cmocean
- **图型类型**: 感知均匀的连续/发散/循环 colormap
- **代码结构**: 基于 Kovesi 理论的 colormap RGB 数据 + 诊断工具
- **关键设计**:
  - 全部 Linear Delta-E, colorblind-safe, grayscale-safe
  - 推荐映射: temperature → thermal, anomaly → balance, velocity → speed, phase → phase
  - 运行时检查: 主动拒绝 jet/rainbow 并给出错误信息
- **可复现性**: 极高，pip install
- **与本地模板对比**: cmocean 应作为所有模板的默认 colormap 来源
- **可借鉴的代码模式**:
  1. 数据类型 → colormap 的推荐映射
  2. 运行时 jet/rainbow 检查和拒绝
  3. 灰度诊断工具 — 验证所有 colormap 转灰度后仍保持单调
- **推荐优先级**: 高 — 应作为强制性依赖，替代所有默认 colormap

---

## 资源 6: colorcet (holoviz/colorcet) — 700+ stars

- **来源**: https://github.com/holoviz/colorcet
- **图型类型**: 64+ Kovesi colormaps + glasbey 分类调色板
- **代码结构**: RGB 数据嵌入为 Python lists (零外部依赖)
- **关键设计**:
  - glasbey_bw, glasbey_cool, glasbey_warm, glasbey_dark, glasbey_light — 用于 20+ 类别的分类配色
- **可复现性**: 极高
- **可借鉴的代码模式**:
  1. 零依赖的 colormap 嵌入
  2. glasbey 系列: 20+ 类别的可区分配色
- **推荐优先级**: 中高 — 当 >10 类时使用

---

## 资源 7: Matplotlib 官方 Gallery

- **来源**: https://matplotlib.org/stable/gallery/
- **关键示例**: `broken_axis.py` (截断轴), `gridspec_multicolumn.py` (复杂 subplot spanning), `connectionstyle_demo.py` (注释箭头样式), `colormap_normalizations.py` (PowerNorm, BoundaryNorm)
- **核心模式**: GridSpec slicing, `twinx()/twiny()`, `constrained_layout`
- **推荐优先级**: 高 — 必读参考

---

## 资源 8: 论文仓库画图代码模式提取

### 理想目录结构
```
paper-repo/
  figures/          # 每张图一个脚本
  plotting/         # 共享基础设施 (config.py, utils.py, style.py, save.py)
  data/processed/   # 仅预处理后的数据
  output/           # 生成的 PDF/PNG
  Makefile          # `make figures` 一键复现
```

### 5 条核心原则
1. **数据/绘图分离**: 绘图函数接受 numpy arrays, 数据加载在外部
2. **参数集中管理**: `config.py` 作为 dataclass 或 dict
3. **声明式布局**: subplot 配置为 dict, 不硬编码 `(2,3)`
4. **矢量优先**: PDF 默认, PNG@300dpi 可选
5. **Makefile 驱动的可复现性**

### 5 个常见反模式
1. 数据加载写在绘图函数内
2. 文件路径硬编码
3. Bootstrap 不设随机种子
4. 只通过 notebook 保存, 无版本控制
5. rcParams 在绘图函数内直接修改(不用 context manager)

---

## 资源 9: Papers with Code — 各学科图型模式

### ML/DL 特定图型
- 学习曲线 (多 run + std shading + best-checkpoint marker)
- 混淆矩阵 (annotated heatmaps)
- 消融矩阵 (row=component, col=metric)
- 注意力 heatmaps
- 嵌入散点图

### 物理/工程特定图型
- 波形图 + inset zoom
- 频谱图 (log-freq + dB intensity + plasma colormap)
- 相位图 (2D colormaps)
- 时空偏移图

---

## 资源 10: Matplotlib 内置 Style Sheets

14 个内置 style 可用: `seaborn-v0_8-paper` (草稿就绪), `seaborn-v0_8-talk` (幻灯片), `seaborn-v0_8-poster` (海报), `grayscale` (打印测试), `fast` (大数据)。结合自定义 rcParams 可快速达出版级输出。

---

## 资源 11-15: 专业领域绘图库

| 资源 | Stars | 用途 | 优先级 |
|------|-------|------|--------|
| **ComplexHeatmap** (R) + **PyComplexHeatmap** (Python) | 1,200+ / 400+ | 带注释的 heatmap 金标准 | 高 |
| **cartopy** + **xarray plot()** | 1,400+ | 地理投影图 | 低 (除非需要) |
| **astropy.visualization** | — | 天文图像拉伸 | 低 |
| **tikzplotlib** | 2,500+ | matplotlib → LaTeX 桥接 | 中 |
| **statannotations** | 1,200+ | 统计显著性标注(箱线图上加括号) | 中 |
| **matplotx** | 500+ | `line_labels()` 在线标注, `ylabel_top()` 省空间 | 中 |
| **Plotly** | 16,000+ | 交互式可视化, `write_image()` 导出静态图 | 低 |

---

## 评估矩阵 (1-5 分)

| 维度 | SciencePlots | ProPlot | Seaborn | mpltex | cmocean | colorcet |
|------|-------------|---------|---------|--------|---------|----------|
| 样式控制 | 5 | 4 | 3 | 4 | — | — |
| 布局 | — | 5 | 4 | — | — | — |
| 颜色/调色板 | 3 | 4 | 5 | 2 | 5 | 5 |
| 数据集成 | — | 4 | 5 | — | — | — |
| 出版就绪 | 5 | 3 | 3 | 5 | — | — |
| 学习曲线 | 5 | 2 | 4 | 4 | 5 | 5 |
| 社区健康度 | 2 | 4 | 5 | 2 | 3 | 3 |
| 生态适配 | 4 | 3 | 5 | 3 | 4 | 4 |

---

> 持续更新：每发现一个好仓库，追加一个新案例到此文件。
