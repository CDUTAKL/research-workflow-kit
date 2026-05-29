# Network Architecture Figures

Use `FIG-ARCH-*` as the final manuscript-facing ID. Older `ARCH-*` labels can be kept only as internal renderer/spec notes.

## Update Rules

- Use this file for CNN, ResNet, U-Net, Transformer, attention, feature-fusion, and other model structure diagrams.
- Store the figure contract, visual reference, source-of-truth architecture record, formal redraw tool, generated outputs, metadata check, and QA status.
- Do not treat architecture diagrams as performance evidence. They describe model topology and information flow.
- Prefer editable vector/PPT-style outputs over screenshots.
- Use Image Gen Skill first for an attractive visual reference when visual quality matters, then check content accuracy and redraw formally.
- Keep `.network.json`, `model.py`, paper source, or manual architecture spec as the source of truth. Image Gen references, draw.io files, Visio `.vsdx`, PPTX, Figma, PNG, and screenshots are outputs or refinements, not topology records.
- Run the QA report before marking any architecture figure as ready.

## Visual Reference To Formal Architecture Workflow

```text
architecture source or model.py
-> source-of-truth architecture spec
-> Image Gen Skill reference image
-> content accuracy check
-> style decisions to reuse
-> formal redraw in draw.io on Mac or Visio on Windows
-> SVG/PDF/PNG/PPTX export
-> metadata/provenance check
-> QA report
-> figure-plan.md / final-audit.md
```

Legacy renderers may be used as structure helpers, but draw.io is the default Mac formal redraw path for structured diagrams. Windows Visio is an optional direct-use route when `.vsdx` editability is useful. Use Python or the Nature-style renderer for data-backed plots; use Figma/BioRender only as optional visual refinement.

## Spec Fields

| Field | Requirement |
|---|---|
| `layout` | linear / encoder_decoder / multi_branch / transformer |
| `connections` | residual, skip, concat, fusion, or attention paths with source and target |
| `panels` | main structure, inset, legend, or shape-scale panel plan |
| `audit` | source paper, implementation source, caption-safe note, claim boundary |

## Figure Registry

| Figure ID | Model | visual_reference | reference_accuracy_check | Source Of Truth | Formal Redraw Tool | Outputs | metadata_check | QA Report | Status |
|---|---|---|---|---|---|---|---|---|---|
| FIG-ARCH-001 | TBD | `figures/references/FIG-ARCH-001_reference.png` | pending | paper/code/`.network.json`/TBD | draw.io or Windows Visio/TBD | SVG/PDF/PNG/PPTX/VSDX/TBD | pending | TBD.qa.md | planned |

## draw.io Handoff

Use draw.io when the Image Gen reference has a strong style and the architecture facts are known. draw.io should recreate the useful visual structure while correcting any reference mistakes against the source-of-truth architecture.

| Figure ID | draw.io File / Diagram | Input Reference | Source Of Truth | Redraw Goal | Export Back To | Status |
|---|---|---|---|---|---|
| FIG-ARCH-001 | TBD | Image Gen reference/TBD | `.network.json`/model.py/TBD | match reference structure and correct topology | SVG/PDF/PNG/PPTX | planned |

Rules:

- Keep source-of-truth records as the authority for model topology.
- Use draw.io for formal redraw, not for changing architecture facts without updating the source record.
- Export refined assets back to the project and record final paths in this file.
- Final manuscript still uses source-traceable SVG/PDF/PNG, not an untracked screenshot.

## Windows Visio Handoff

Use this route only on a Windows machine with Microsoft Visio and PowerShell 7+ when editable `.vsdx` output is useful.

| Figure ID | Visio Plan | VSDX Output | Preview Export | Source Of Truth | Status |
|---|---|---|---|---|---|
| FIG-ARCH-001 | `docs/thesis/diagram-plans/FIG-ARCH-001.visio-plan.json` | `figures/final/FIG-ARCH-001.vsdx` | PDF/PNG/EMF/TBD | `.network.json`/model.py/TBD | planned |

Rules:

- Check the Windows Visio environment before generation.
- The `.vsdx` is editable output, not topology truth.
- Copy final `.vsdx` and preview exports back to the project and record them here.
- Keep the same caption and `FIG-*` ID across draw.io and Visio variants.

## Architecture Contract

| Figure ID | Core Conclusion | Input Shape | Main Stages | Downsampling / Fusion | Head / Output | Caption-Safe Note |
|---|---|---|---|---|---|---|
| FIG-ARCH-001 | TBD | TBD | TBD | TBD | TBD | Describes topology only; does not claim performance |

## Visual QA

| Check | Status | Notes |
|---|---|---|
| Feature-map stacks show scale/channel changes | pending |  |
| Module groups are visually separated | pending |  |
| Skip/fusion paths have clear start and end | pending |  |
| Repeated blocks use badges or insets | pending |  |
| `.network.json` records layout, connections, panels, and audit fields | pending |  |
| QA report has no unresolved connections | pending |  |
| Labels fit at final manuscript size | pending |  |
| SVG/PDF vector output exists | pending |  |
| PNG preview is readable | pending |  |
| PPTX mode is recorded as image-backed or native-shape | pending |  |
| Caption does not imply performance | pending |  |
