# Figure Gallery — 本地图表案例库

> 不是素材库，是**设计模式库**。每个案例记录图的结构、配色、布局、caption，以及可复现性。
> 目标: 积累 30-50 个高质量案例后，本地模板库的实用性接近甚至超过原生 nature-figure。

---

## 目录结构

```
figure-gallery/
  index.md                 ← 你在这里
  source-log.md             ← 案例来源追踪
  paper-figure-notes.md     ← 待迁移到 paper-examples/
  template-evaluation.md    ← 待创建

  nature-figure-seeds/      ← 第一批种子案例 + 官方规范
  paper-examples/           ← 真实论文图拆解
  reproduced-templates/     ← 有代码的可复现模板
  rejected-examples/        ← 不适合参考的案例
```

## 浏览入口

### Nature 规范与设计模式
- [Nature 官方图表规范](nature-figure-seeds/nature-official-specs.md) — 字号、色彩、格式、caption 规范
- [Nature 设计模式](nature-figure-seeds/nature-design-patterns.md) — Panel 布局、配色、图例位置决策框架

### 论文图案例拆解
- [论文图结构化拆解](paper-examples/paper-figure-notes.md) — 8 个高水平论文案例
- [跨案例设计模式总结](paper-examples/paper-figure-summary.md) — 共性规律 + 常见错误 + 速查表

### 开源代码模板库
- [开源代码仓库拆解](reproduced-templates/open-source-code-notes.md) — 7 个绘图相关仓库
- [代码模式总结](reproduced-templates/code-patterns-summary.md) — 可集成的改进建议 + Top 5 推荐

---

## 快速查询

按图型查询 → 看 [Nature 设计模式](nature-figure-seeds/nature-design-patterns.md) 第一章"图表分类体系"

按配色查询 → 看 [Nature 设计模式](nature-figure-seeds/nature-design-patterns.md) 第三章"配色模式"

按 panel 布局查询 → 看 [Nature 设计模式](nature-figure-seeds/nature-design-patterns.md) 第二章"Panel 布局模式"

画图前检查 → 看 [Nature 官方图表规范](nature-figure-seeds/nature-official-specs.md) 第七章"QA 检查清单"

---

## 案例统计

| 来源 | 案例数 | 状态 |
|------|--------|------|
| Nature 官方规范 | 1 份完整规范 | 已入库 |
| 论文图拆解 | 8 个案例 | 已入库 |
| 开源代码仓库 | 15 个资源 | 已入库 |
| 设计模式总结 | 3 份跨案例分析 | 已入库 |

**目标**: 30-50 个案例（当前: 24 等效案例 + 评估矩阵）
