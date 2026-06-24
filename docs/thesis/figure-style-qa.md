# Figure Style QA

## Purpose

Use this checklist before marking advisor-facing, final thesis, or publication-style figures as ready.

This file adapts useful `nature-figure` quality ideas into the local workflow. It does not replace `figure-plan.md`, source data, draw.io, Python plots, or PPTX export records.

## Figure QA Table

| Figure ID | Figure Role | Source Data / Script | Export Formats | Panel Hierarchy | Uncertainty / n | Caption Safety | Accessibility | Source Trace | QA Status | Required Fix |
|---|---|---|---|---|---|---|---|---|---|---|
| FIG-001 | hero/support/table/architecture/TBD | TBD | SVG/PDF/PNG/PPTX/TBD | pending | pending | pending | pending | pending | pending | TBD |

## Image Gen Reference QA

Use this checklist before using an Image Gen output as the visual mother draft for draw.io or Figma redraw. The reference can be visually ambitious, but it must remain scientifically conservative.

| Check | Requirement |
|---|---|
| Academic tone | reference looks like a thesis or journal method figure, not a marketing poster |
| Redraw feasibility | layout can be reconstructed with editable shapes, arrows, labels, and grouped modules |
| Source consistency | modules, arrows, labels, and metric names match `figure-plan.md`, experiment reports, or source code |
| Chinese readability | key labels use Chinese thesis wording, with metric acronyms explained where needed |
| Visual hierarchy | one main reading path is visible; support modules do not compete with the core mechanism |
| Style reuse | palette, spacing, icon grammar, arrow style, and panel hierarchy are recorded before redraw |
| Content correction | generated mistakes are listed explicitly and corrected during formal redraw |
| Provenance boundary | generated bitmap is stored only as reference unless explicitly accepted as final evidence |

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

- Image Gen may create attractive visual references and should be treated as the visual mother draft for method and architecture diagrams.
- draw.io is the default Mac redraw route for structured diagrams; it is where scientific accuracy becomes final.
- Python or the Nature-style renderer is preferred for data-backed result figures.
- PPTX / Presentations packages final visuals for defense and should not replace the thesis source figure.
- BioRender and Figma remain optional polish tools after source-traceable outputs exist.

## Stage 9 QA Gates

| Gate | Applies To | Pass Condition |
|---|---|---|
| Figure contract | all figures and tables | figure claim, source data, caption-safe wording, and export target are recorded |
| Reference QA | method, architecture, workflow, mechanism figures | Image Gen or other reference passes academic tone, source consistency, and redraw feasibility checks |
| Data traceability | result plots and tables | plotted values trace to frozen experiment outputs or documented scripts |
| Quantitative honesty | result plots | scales, deltas, uncertainty, and sample counts do not exaggerate small improvements |
| Final export QA | all advisor/final figures | SVG/PDF/PNG exports are readable in DOCX/PDF/PPTX |
| Caption audit | all final figures | caption says what the figure shows and does not overclaim beyond evidence |
