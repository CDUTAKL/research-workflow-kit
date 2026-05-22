# Code Patterns Summary — 跨仓库代码模式总结

> 从 15 个开源科研绘图资源中提取的共性最佳实践、可复用的代码模式，以及可以直接集成到 nature_plot_templates.py 的改进建议。

---

## 一、跨仓库共性模式

### 1.1 颜色管理

所有高质量绘图库都在三个层次上管理颜色：

| 层次 | 代表实现 | 用途 |
|------|---------|------|
| 离散色板 | Seaborn `color_palette()`, colorcet `glasbey_*` | 分类数据的分组着色 (最多 20+ 类) |
| 连续 colormap | cmocean, colorcet, ProPlot | 连续数值到颜色的映射 |
| 发散 colormap | cmocean `balance`, Seaborn `diverging_palette()` | 有正负中心的数据 |

**共同设计决策**：
1. 默认禁用 jet/rainbow — SciencePlots, cmocean, ProPlot 都提供感知均匀替代
2. 色盲友好优先 — SciencePlots `high-vis` 和 cmocean CUD 验证
3. 灰度打印兼容 — 所有推荐 colormap 在转灰度后保持单调
4. 调色板工厂模式 — 从基础色调生成完整色板，不硬编码 RGB

**对 nature_plot_templates.py 的建议**：
```python
COLORS = {
    'categorical': sns.color_palette('husl', 8),
    'sequential': cmocean.cm.thermal,
    'diverging': cmocean.cm.balance,
}

def validate_colormap(name: str):
    if name in ('jet', 'rainbow', 'hsv', 'gist_rainbow'):
        raise ValueError(
            f"'{name}' is perceptually non-uniform. "
            f"Use cmocean.cm.thermal or similar."
        )
```

### 1.2 布局管理

三种抽象层级，从低到高：

1. **原生 GridSpec**: `gs = fig.add_gridspec(3, 3); ax = fig.add_subplot(gs[0, :2])`
2. **声明式数组** (ProPlot): `pplt.subplots([[1,1,2],[3,3,4]])`
3. **分面网格** (Seaborn): `FacetGrid(col='treatment', row='dose')`

**共同设计决策**：
- 使用 `constrained_layout` 而非手动 `subplots_adjust`
- Share x/y axes 时自动隐藏内部轴标签
- Colorbar 放在网格外侧，不挤占数据区域

**建议**：
```python
def make_panel_layout(layout_array, figsize=None):
    """二维数组定义面板占位:
    [[1, 1, 2],
     [3, 3, 4]]
    → axs[0] 占(0, :2), axs[1] 占(0, 2), axs[2] 占(1, :2), axs[3] 占(1, 2)
    """
```

### 1.3 数据集成

所有高质量绘图库都遵循 "数据框架优先" (DataFrame-first) 原则：
- Seaborn: 所有 API 接受 DataFrame + 列名字符串
- ProPlot: 接受 xarray DataArray 并自动读取 metadata
- 论文仓库最佳实践: 绘图函数参数是 numpy arrays, 数据预处理在外部

### 1.4 导出系统

**共性**:
1. 矢量格式优先: PDF (印刷), SVG (网页), EPS (LaTeX)
2. 光栅至少 300 DPI, 推荐 600 DPI
3. `bbox_inches='tight'` + `pad_inches=0.05` 精确裁剪
4. 多格式同时输出: PDF + PNG
5. 文件命名规范: `{fig_number}_{description}.{format}`

**建议**：
```python
def save_figure(fig, name, formats=('pdf', 'png'), dpi=300, output_dir='output'):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for fmt in formats:
        path = output_dir / f"{name}.{fmt}"
        fig.savefig(path, dpi=dpi, bbox_inches='tight', pad_inches=0.05)
    return [output_dir / f"{name}.{fmt}" for fmt in formats]
```

### 1.5 样式与字体管理

**共性**:
1. 组合式配置: `plt.style.use(['base', 'journal', 'color'])` 层层覆盖
2. LaTeX 双轨: 检测可用性，不可用时降级到 mathtext + STIX 字体
3. 字体回退链: `Times New Roman, STIXGeneral, DejaVu Serif, serif`
4. 上下文管理器: `with plt.style.context(...)` 隔离局部样式修改

**建议**：
```python
def setup_style(journal='nature', use_latex=None):
    if use_latex is None:
        use_latex = shutil.which('latex') is not None
    base = ['science', journal] if use_latex else ['science', journal, 'no-latex']
    plt.style.use(base)
    plt.rcParams.update({
        'figure.dpi': 150, 'savefig.dpi': 300,
        'savefig.bbox': 'tight', 'savefig.pad_inches': 0.05,
    })
```

---

## 二、分优先级的集成建议

### 优先级 1 (立即实施, 代码量小, 收益大)

1. **集成 SciencePlots 作为默认样式引擎** — 添加 `try: import scienceplots`, 预定义 Nature/Science/IEEE 尺寸预设
2. **预置 cmocean colormap 推荐映射** — 替换所有默认 colormap, 添加 jet/rainbow 运行时警告
3. **实现 Figure-level / Axes-level 双轨 API** — 每个函数接受 `ax=None` 参数，返回 `(fig, ax)` 元组
4. **添加 `save_figure()` 统一导出函数** — 多格式同时输出，自动创建目录

### 优先级 2 (中期实施, 需要设计)

5. **实现声明式子图布局系统** — `make_panel_layout()` 接受二维数组语法
6. **添加 Semantic Mapping 支持** — `hue_col`, `size_col`, `style_col` 参数自动处理分组
7. **添加 `format_axes()` 统一格式化函数** — 合并 ProPlot 和 seaborn 的精华

### 优先级 3 (长期增强)

8. 支持 xarray/pandas metadata 自动传播
9. 实现 FacetGrid 分面系统
10. 添加 `add_direct_labels()` (在线标注替代图例)
11. 添加 `add_significance_brackets()` (统计显著性标注)
12. 提供 `save_for_latex()` tikzplotlib 桥接

---

## 三、代码质量检查清单

在研究/集成这些仓库时，逐项对照：

- [ ] 是否有单元测试覆盖绘图输出 (pixel-level comparison)?
- [ ] 是否使用 `plt.style.context()` 而非裸 `rcParams.update()`?
- [ ] 是否有完整的 type hints?
- [ ] 是否处理了 matplotlib 版本兼容性?
- [ ] docstring 是否包含可运行的示例代码?
- [ ] 是否有 CI 在多平台和多 matplotlib 版本下测试?
- [ ] 是否分离了数据层和视图层?
- [ ] 是否有 Figure 对象的内存泄漏处理 (`plt.close(fig)` after save)?

---

## 四、推荐本地研究的 Top 5 仓库

按代码可读性 + 模式可迁移性 + 对项目的直接价值排序：

| 排名 | 仓库 | 理由 | 重点研究文件 |
|------|------|------|-------------|
| 1 | **garrettj403/SciencePlots** | 最直接的样式参考；纯 .mplstyle 零学习成本 | `styles/journals/nature.mplstyle` |
| 2 | **mwaskom/seaborn** | 工业级 API 设计标准；调色板工厂模式 | `palettes.py`, `_core/properties.py` |
| 3 | **matplotlib/cmocean** | 理解什么才是正确的 colormap | `cm.py`, `tools.py` |
| 4 | **lukelbd/proplot** | Subplot 布局语法和 colorbar 对齐 | `gridspec.py` |
| 5 | **lichengzhang/mpltex** | 装饰器模式 + 期刊规范精确翻译 | `mpltex.py` |

**建议学习顺序** (总计 ~3 小时):
1. SciencePlots 的 `nature.mplstyle` — 理解一个 rcParams 文件如何让整张图看起来像 Nature (30 min)
2. seaborn 的 `palettes.py` — 理解调色板工厂的设计哲学 (1 hr)
3. cmocean 的 colormap 列表 — 运行诊断脚本看灰度/色盲表现 (30 min)
4. ProPlot 的 `gridspec.py` — 声明式布局语法实现 (1 hr)
5. mpltex 的装饰器实现 (30 min)

---

## 五、核心收获

1. **不要造轮子**: SciencePlots 已解决 80% 样式问题。`nature_plot_templates.py` 应专注于"图型结构模板"而非"视觉样式定义"
2. **API 分层是关键**: Seaborn 的 Figure-level/Axes-level 双轨制是最优雅的设计模式
3. **颜色是最被低估的问题**: 大多数论文图问题不在布局，在使用 jet colormap 或不可区分的离散配色
4. **可复现性从目录结构开始**: `figures/` / `plotting/` / `data/` / `output/` 分离不是过度工程，是科学诚信
5. **矢量格式是出版标准**: 默认输出 PDF, PNG 仅用于快速预览
6. **LaTeX 是加分项不是必需品**: SciencePlots 的 `no-latex` 降级方案是最佳实践
7. **代码即文档**: Seaborn 和 matplotlib gallery 的每个示例都是独立可运行的 .py 文件

---

*分析范围: 15 个资源, 12 个代码仓库, 跨 6 个领域的绘图模式*
