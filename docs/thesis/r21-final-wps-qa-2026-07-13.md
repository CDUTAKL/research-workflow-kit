# R21 WPS 终检记录（2026-07-13）

## 归档修复

EXP-108 三个正式 seed 的 `logs/train.log` 哈希已按实际文件重算，并更新本机归档目录：

| Seed | SHA-256 | 校验 |
|---|---|---|
| 42 | `7e5522f9c193aa60fedcff8e4bd903f2507aecc69e6031ed88872b7900a0ab99` | `sha256sum -c` 通过 |
| 2026 | `669a260d0770213a1987a2b3f1e089939f4dcb7026d3938ec6d135cbc83c9c1c` | `sha256sum -c` 通过 |
| 3407 | `f205225312aed4cfde3b4c13be3a60116f423b344b8eac145201076e0fa16a99` | `sha256sum -c` 通过 |

归档目录：`/Users/xushuyuan/Downloads/EXP-108-standard-baselines/`。

该修复只涉及日志清单，不改变预测、指标、配对键或 bootstrap 结果。

## WPS 文档终检

- 终检副本：`r21_scientific_consistency_with_37_figures_v6_exp108-backfill-figures-unfilled-frontmatter.docx`
- WPS 操作：解锁目录字段后，使用全选加 F9，在更新目录对话框选择“更新整个目录”；随后使用 WPS“输出为 PDF”。
- PDF：`r21_scientific_consistency_with_37_figures_v6_exp108-backfill-figures-unfilled-frontmatter_20260713131025.pdf`
- DOCX SHA-256：`988d01e2e55e95e0963d3d59e23824c0685582cecda6dd270ff3c8bbdf826529`
- PDF SHA-256：`76aef827c0b629c364abaff60677239633aee835a18fa83cdf13d563de3319c3`
- 页数：103 页；A4；WPS Quartz PDFContext 导出。
- 目录页码：已与正文实际页码重新对齐。
- 图表：图 1-1 至图 6-10、表 1-1 至表 6-6 均在 PDF 中可检索到。
- 当前 QA：已核对 WPS 成功输出、A4 页面尺寸、103 页页数及目录页码样本；尚未把本次导出的 103 页 PDF 宣称为完成逐页视觉终检。

## 按用户要求保留的事项

- 未填写封面、声明、授权等真实信息。
- 第 4 页空白模板页保留，待用户后续决定是否按学校模板填写或删除。
- 第 101 页“在读期间发表的学术论文与研究成果”保留“无”。

## 仍需人工完成

1. 在 WPS 中填写封面、声明、授权和日期等真实字段。
2. 填写或确认在读期间成果页内容。
3. 填写后重新在 WPS 更新目录、交叉引用和页码，并重新导出最终 PDF。

本记录对应的是“EXP-108 结果回填、封面信息留空”的审阅版，不是填写真实封面信息后的最终学位提交版。
