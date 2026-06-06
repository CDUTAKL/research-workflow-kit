# Figure Style QA

## Purpose

Use this checklist before marking advisor-facing, final thesis, or publication-style figures as ready.

This file adapts useful `nature-figure` quality ideas into the local workflow. It does not replace `figure-plan.md`, source data, draw.io, Python plots, or PPTX export records.

## Figure QA Table

| Figure ID | Figure Role | Source Data / Script | Export Formats | Panel Hierarchy | Uncertainty / n | Caption Safety | Accessibility | Source Trace | QA Status | Required Fix |
|---|---|---|---|---|---|---|---|---|---|---|
| FIG-001 | hero/support/table/architecture/TBD | TBD | SVG/PDF/PNG/PPTX/TBD | pending | pending | pending | pending | pending | pending | TBD |

## Visual Standards

| Check | Requirement |
|---|---|
| Claim-first design | figure has one clear conclusion and does not decorate unsupported claims |
| Panel hierarchy | panel order follows the evidence story, not generation order |
| Source trace | each plotted value traces to `DATA-*`, `EXP-*`, `CIT-*`, or a documented source |
| Export quality | final or advisor-facing figures export as SVG/PDF plus PNG preview when possible |
| Text readability | labels remain readable in DOCX, PDF, PPTX, and Dashboard contexts |
| Color and contrast | colors distinguish groups without relying only on hue |
| Uncertainty | error bars, intervals, sample counts, folds, seeds, or caveats are visible when relevant |
| Caption safety | caption describes what the figure shows and avoids stronger claims than the evidence |
| Metadata hygiene | AI-generated references are redrawn or explicitly accepted before final use |

## Route Notes

- Image Gen may create attractive visual references.
- draw.io is the default Mac redraw route for structured diagrams.
- Python or the Nature-style renderer is preferred for data-backed result figures.
- PPTX / Presentations packages final visuals for defense.
- BioRender and Figma remain optional polish tools after source-traceable outputs exist.
