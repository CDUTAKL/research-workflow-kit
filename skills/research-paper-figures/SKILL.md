---
name: research-paper-figures
description: Use when planning, designing, reviewing, or generating research-paper figures, thesis figures, experiment plots, result tables, model diagrams, method pipelines, architecture schematics, Mermaid diagrams, captions, or publication-quality visualizations.
---

# Research Paper Figures

Use this skill to plan and produce figures and tables that support paper claims. Figures should explain evidence, not decorate the paper.

## Core Rules

- Every figure/table must support a specific claim or clarify a necessary method detail.
- Use manuscript-facing `FIG-*` IDs for final figures, tables, and architecture visuals; map legacy `Fig-*`, `Table-*`, or `Arch-*` labels before final audit.
- Prefer reproducible plots from data over screenshots.
- For data-backed figures, confirm source data or data-availability status when `docs/thesis/data-availability.md` exists.
- For model architecture, method pipeline, workflow, and other schematic figures, first create or select a strong visual reference. Image Gen Skill is the preferred fast reference generator when the user wants an attractive layout, palette, or composition.
- Treat Image Gen outputs as visual references only. Check their content accuracy, then redraw formal structured diagrams from source-of-truth records in draw.io by default. Export SVG/PDF/PNG from draw.io; use Presentations/PPTX for defense-slide packaging.
- Use Python or the Nature-style renderer for data-backed plots. Use Figma or BioRender only as optional polish/refinement tools when draw.io/Python output needs a stronger visual finish.
- Use Build Web Data Visualization rules for chart choice, dashboard charts, evidence graphs, interaction design, accessible contrast, label readability, responsive layout, and visual regression/QA planning.
- Do not insert Image Gen outputs directly into a thesis or manuscript as final figures unless the user explicitly accepts AI-generated bitmap provenance. Formal figures should be redrawn, source-traceable, and free of generated-image metadata when possible.
- Keep visual style consistent across figures.
- Use accessible contrast, readable labels, and publication-ready export formats.
- Do not use chart types that hide uncertainty or exaggerate small differences.

## Workflow

Read `references/workflow.md` for figure planning, plotting conventions, Nature-derived figure-readiness rules, and caption templates. Read `references/dual-platform-diagram-replica.md` when adapting reference images into Mac draw.io or Windows Visio redraw workflows. Read `references/nature-figure-controlled-port.md` when generating Nature-style bar, line, heatmap, scatter, radar, distribution, forest, log-scale, ablation, threshold, confusion-matrix, image-plate, or multi-panel figures. Read `references/nature-figure-template-roadmap.md` when extending the local template library. Read `references/figure-audit-standard.md` when reviewing publication-ready, thesis-ready, Nature-style, or final submission figures. Read `references/network-architecture-figure.md` when drawing CNN, ResNet, U-Net, Transformer, attention, feature-fusion, or other neural-network architecture figures. Read `references/source-map.md` for source provenance.

1. Build a figure/table inventory tied to paper claims.
2. Identify required input data for every visual, including experiment runbook, registry, output paths, claim-evidence map, section-citation map, and data availability records when available.
3. Choose chart or diagram types based on the evidence.
4. Specify caption claims, labels, units, scales, uncertainty display, accessibility constraints, and export formats.
5. For publication-level or "Nature-style" figures, establish the figure contract before plotting: core conclusion, evidence chain, panel hierarchy, backend, dimensions, editable text, source-data traceability, and export formats.
6. For final or advisor-facing figures, run the figure audit standard before presenting them as ready.
7. For schematic figures, run the visual-reference route before formal drawing:
   - generate/select a visual reference, preferably with Image Gen Skill when the target is a polished model/method diagram;
   - audit the reference for architecture/content mistakes;
   - preserve the style decisions that work;
   - redraw the final structured diagram from source-of-truth records in draw.io by default;
   - export SVG/PDF/PNG and, when needed, place the exported asset into PPTX slides.
   - when working on Windows with Microsoft Visio, optionally use the Visio JSON-plan route and record `.vsdx` plus exports.
8. For common result figures, prefer the local Nature-style template renderer in `skills/research-paper-figures/scripts/nature_plot_templates.py` or the installed equivalent under `~/.codex/skills/research-paper-figures/scripts/`: write or inspect a figure spec JSON, render SVG/PDF/PNG, and review the QA report.
9. For network architecture diagrams, prefer editable vector/PPT-style shapes, feature-map stacks, module grouping, and clean hierarchy over generic rectangular flowcharts.
10. For network architecture diagrams, record the source of truth (`model.py`, paper, `.network.json`, or manual architecture spec), then redraw formally in draw.io by default. Use SVG/PDF/PNG exports for the thesis and PPTX packaging for defense. Figma/BioRender remain optional polish tools; legacy renderers may remain structure helpers.
11. When asked to generate plots, inspect available data and use project-standard Python tooling if present unless the user explicitly requests R.
12. For web dashboard or interactive evidence visuals, keep the source record in `docs/thesis/`, use the local dashboard only as a rendering/action layer, and verify that the chart remains legible on desktop and mobile.

## Output Contract

Always include:

- figure/table list
- purpose of each visual
- required input data
- experiment/runbook source for data-backed figures when applicable
- data availability or section citation source when the figure supports a data-backed or literature-backed claim
- recommended visual type
- Build Web Data Visualization QA notes for chart/dashboard/evidence graph work
- caption draft
- plotting/style rules
- publication-grade figure contract when relevant
- visual reference path, content-accuracy check, and style-to-redraw notes when a schematic/model/method figure is involved
- Nature-style figure audit findings when reviewing final figures
- Nature-style figure spec, template type, generated files, and QA report when a common result figure is produced
- network-architecture visual grammar when relevant
- formal redraw tool, draw.io source/export paths, source-of-truth record, generated files, metadata/C2PA check, and QA report when a network architecture figure is produced
- platform route: `local_mac_drawio` or `windows_visio` when a reference image is replicated
- LaTeX or Word insertion advice

If data is missing, return a figure specification and data requirements instead of inventing values.
