# Diagram Replica Tasks

## Purpose

Use this file for structured diagram replication tasks inspired by `codex-visio-replica-workflow`, adapted into a dual-platform route:

- Mac default: Image Gen / reference image -> content check -> draw.io MCP redraw -> SVG/PDF/PNG -> optional PPTX.
- Windows enhancement: Image Gen / reference image -> Visio JSON plan -> `.vsdx` -> EMF/PDF/PNG -> optional PPTX.

Do not treat the reference image, draw.io file, Visio file, or screenshot as the scientific source of truth. The source of truth remains `model.py`, `.network.json`, experiment records, claim maps, data records, or cited paper/source notes.

## Platform Routes

| Platform | Default Tool | Best Use | Output | Notes |
|---|---|---|---|---|
| `local_mac` | draw.io MCP | model architecture, method workflow, system architecture, evidence graph, process diagram | `.drawio`/SVG/PDF/PNG, optional PPTX packaging | preferred daily route |
| `windows_visio` | Microsoft Visio + PowerShell 7 + Visio COM | high-fidelity editable Visio replication, tutorial/demo recording, Windows-native diagram handoff | `.vsdx`, EMF/PDF/PNG, optional PPTX | may directly use external `codex-visio-replica-workflow` scripts |

## Task Registry

| Task ID | Figure ID | Platform Route | Diagram Type | Reference Image | Source Of Truth | Plan Path | Editable Source | Export Paths | QA Status | Final Audit Status | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DRT-DIAG-001 | FIG-ARCH-001 | local_mac_drawio / windows_visio / TBD | architecture/workflow/process/system/evidence/TBD | `figures/references/FIG-ARCH-001_reference.png` | `.network.json` / model.py / paper / claim map / TBD | `docs/thesis/diagram-plans/FIG-ARCH-001.json` | draw.io `.drawio` or Visio `.vsdx` / TBD | SVG/PDF/PNG/PPTX/TBD | pending | pending | create plan |

## Reference Image Decomposition

| Figure ID | Canvas Ratio | Main Regions | Repeated Modules | Text Labels | Arrows / Routes | Color / Style Notes | Content Risks |
|---|---|---|---|---|---|---|---|
| FIG-ARCH-001 | 16:9 / paper-wide / TBD | TBD | TBD | TBD | TBD | TBD | hallucinated modules / wrong arrows / unreadable labels / TBD |

## Mac draw.io Plan Checklist

| Check | Status | Notes |
|---|---|---|
| Reference image is saved under `figures/references/` | pending |  |
| Source-of-truth record is identified | pending |  |
| draw.io diagram uses editable shapes, not a pasted screenshot | pending |  |
| Text labels are readable at thesis size | pending |  |
| Arrows and group boundaries match the source of truth | pending |  |
| SVG/PDF/PNG exports exist | pending |  |
| Optional PPTX packaging is recorded when used | pending |  |

## Windows Visio Plan Checklist

| Check | Status | Notes |
|---|---|---|
| Windows machine has PowerShell 7+ and Microsoft Visio | pending |  |
| `check_visio_environment.ps1 -TryCom` passes | pending |  |
| JSON plan is UTF-8 and uses reference-image pixel coordinates | pending |  |
| Generated `.vsdx` contains editable Visio shapes | pending |  |
| Reference page is present or separately preserved | pending |  |
| EMF/PDF/PNG preview exports exist | pending |  |
| `.vsdx` and exports are copied back to project figure folders | pending |  |

## QA Notes

| Figure ID | Issue | Severity | Fix | Owner | Status |
|---|---|---|---|---|---|
| FIG-ARCH-001 | TBD | P0/P1/P2/TBD | TBD | TBD | open |
