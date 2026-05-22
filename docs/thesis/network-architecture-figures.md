# Network Architecture Figures

## Update Rules

- Use this file for CNN, ResNet, U-Net, Transformer, attention, feature-fusion, and other model structure diagrams.
- Store the figure contract, visual reference, source-of-truth architecture record, formal redraw tool, generated outputs, metadata check, and QA status.
- Do not treat architecture diagrams as performance evidence. They describe model topology and information flow.
- Prefer editable vector/PPT-style outputs over screenshots.
- Use Image Gen Skill first for an attractive visual reference when visual quality matters, then check content accuracy and redraw formally.
- Keep `.network.json`, `model.py`, paper source, or manual architecture spec as the source of truth. Image Gen references, PPTX, Figma, PNG, and screenshots are outputs or refinements, not topology records.
- Run the QA report before marking any architecture figure as ready.

## Visual Reference To Formal Architecture Workflow

```text
architecture source or model.py
-> source-of-truth architecture spec
-> Image Gen Skill reference image
-> content accuracy check
-> style decisions to reuse
-> formal redraw in Figma/PPTX/SVG/TikZ/Python
-> SVG/PDF/PNG/PPTX export
-> metadata/provenance check
-> QA report
-> figure-plan.md / final-audit.md
```

Legacy renderers may be used as structure helpers, but they are not required when Figma/TikZ/PPTX is the formal redraw path.

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
| Arch-001 | TBD | `figures/references/Arch-001_reference.png` | pending | paper/code/`.network.json`/TBD | Figma/PPTX/SVG/TikZ/Python/TBD | SVG/PDF/PNG/PPTX/TBD | pending | TBD.qa.md | planned |

## Figma Handoff

Use Figma when the Image Gen reference has a strong style and the architecture facts are known. Figma should recreate the useful visual style while correcting any reference mistakes against the source-of-truth architecture.

| Figure ID | Figma File / Node | Input Reference | Source Of Truth | Redraw Goal | Export Back To | Status |
|---|---|---|---|---|---|
| Arch-001 | TBD | Image Gen reference/TBD | `.network.json`/model.py/TBD | match reference style and correct topology | SVG/PDF/PNG/PPTX | planned |

Rules:

- Keep source-of-truth records as the authority for model topology.
- Use Figma for formal redraw and visual refinement, not for changing architecture facts without updating the source record.
- Export refined assets back to the project and record final paths in this file.
- Final manuscript still uses source-traceable SVG/PDF/PNG, not an untracked screenshot.

## Architecture Contract

| Figure ID | Core Conclusion | Input Shape | Main Stages | Downsampling / Fusion | Head / Output | Caption-Safe Note |
|---|---|---|---|---|---|---|
| Arch-001 | TBD | TBD | TBD | TBD | TBD | Describes topology only; does not claim performance |

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
