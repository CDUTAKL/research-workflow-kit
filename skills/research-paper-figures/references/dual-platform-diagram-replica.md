# Dual-Platform Diagram Replica Workflow

This reference adapts useful ideas from `uigiuf/codex-visio-replica-workflow` into the local thesis workflow.

## Rule

Reference images are not final figures. The formal diagram must be editable, source-traceable, exported, and audited.

## Mac Route: draw.io MCP

Use this route on the Mac research console.

```text
Image Gen / screenshot / paper example
-> content accuracy check
-> diagram plan under docs/thesis/diagram-plans/
-> draw.io MCP redraw
-> SVG/PDF/PNG export
-> optional PPTX packaging with Presentations
-> docs/thesis/diagram-replica-tasks.md
-> figure-plan.md / network-architecture-figures.md / final-audit.md
```

Use draw.io for:

- model architecture diagrams
- method pipelines
- system architecture diagrams
- process diagrams
- evidence graph views
- workflow diagrams

Use Mermaid when the diagram is simple. Use draw.io XML when positions, containers, or diagram-native editing matter.

## Windows Route: Visio Direct Use

Use this route on a Windows machine with Microsoft Visio and PowerShell 7+.

```text
Image Gen / screenshot / paper example
-> reference decomposition
-> Visio JSON plan
-> check_visio_environment.ps1 -TryCom
-> create_visio_from_plan.ps1
-> .vsdx + EMF/PDF/PNG export
-> copy artifacts back to project
-> docs/thesis/diagram-replica-tasks.md
```

The external workflow can be used directly on Windows, but keep it as a tool layer. Do not make Visio the source of truth for architecture facts.

Suggested Windows artifact names:

```text
figures/references/FIG-ARCH-001_reference.png
docs/thesis/diagram-plans/FIG-ARCH-001.visio-plan.json
figures/final/FIG-ARCH-001.vsdx
figures/final/FIG-ARCH-001.pdf
figures/final/FIG-ARCH-001.png
```

## Reference Decomposition

Before any redraw, record:

- canvas ratio and target figure size
- major regions and containers
- repeated modules
- text labels
- arrows and line routing
- color/style notes
- content risks such as hallucinated modules, wrong tensor shapes, or unsupported values

## QA Checklist

| Check | Mac draw.io | Windows Visio |
|---|---|---|
| source of truth recorded | required | required |
| reference image checked | required | required |
| editable shapes used | required | required |
| final export exists | SVG/PDF/PNG | VSDX + PDF/PNG/EMF |
| reference page preserved | optional | recommended |
| labels readable | required | required |
| claim/caption safe | required | required |
| final record updated | `figure-plan.md` | `figure-plan.md` |

## Tool Boundary

- draw.io / Visio are formal redraw tools, not evidence sources.
- Image Gen is a style/reference generator, not final manuscript evidence.
- Python or the Nature-style renderer remains the default for data plots.
- Figma/BioRender are optional polish tools after draw.io/Python output exists.
