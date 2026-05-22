# Visualization Rules

Use these rules with `$research-paper-figures`.

## Figure Principles

- Every figure or table must support a specific claim or clarify a necessary method detail.
- Prefer reproducible plots from data over screenshots.
- Tie every figure to input data and, when possible, a script or notebook.
- Use colorblind-safe palettes and strong grayscale readability.
- Prefer vector formats for diagrams and final paper plots.
- Export high-DPI PNG only when raster output is necessary.

## Publication Style

- Use consistent font sizes, line widths, marker sizes, and panel labels.
- Use units in axis labels.
- Avoid chart decorations that do not encode information.
- Use error bars, confidence intervals, or seed variability when variation matters.
- Do not hide weak comparisons with selective axes or cropped scales.

## Common Figure Types

| Need | Recommended visual |
|---|---|
| Method flow | pipeline diagram or Mermaid flowchart |
| Model architecture | block diagram or schematic |
| Main comparison | table plus grouped bar or point plot |
| Ablation | table, bar plot, or line plot |
| Time/threshold trend | line plot with markers |
| Error structure | confusion matrix or error breakdown |
| Robustness | line, box, or violin plot with variability |

## Caption Claim Template

```text
Figure X. [What is shown]. The figure compares [conditions] using [metric/data]. The key observation is [supported claim]. Higher/lower values indicate [meaning] where relevant.
```
