# Diagram Plans

Store lightweight diagram replication plans here.

## Mac draw.io Plan

Use this for draw.io MCP or manual draw.io redraws.

```json
{
  "figure_id": "FIG-ARCH-001",
  "platform_route": "local_mac_drawio",
  "canvas": {
    "ratio": "16:9",
    "width": 1440,
    "height": 900
  },
  "reference_image": "figures/references/FIG-ARCH-001_reference.png",
  "source_of_truth": ".network.json / model.py / claim map / paper note",
  "groups": [],
  "nodes": [],
  "edges": [],
  "style": {
    "palette": "thesis-clean",
    "font": "system sans",
    "export": ["svg", "pdf", "png"]
  },
  "qa": {
    "content_accuracy": "pending",
    "labels_readable": "pending",
    "source_trace": "pending"
  }
}
```

## Windows Visio Plan

Use this when moving a figure task to a Windows machine with Microsoft Visio and `codex-visio-replica-workflow`.

```json
{
  "page": {
    "name": "FIG-ARCH-001",
    "widthPx": 1440,
    "heightPx": 900,
    "scalePxPerInch": 100
  },
  "referenceImage": "C:/path/to/FIG-ARCH-001_reference.png",
  "shapes": [
    {
      "type": "rect",
      "x1": 100,
      "y1": 120,
      "x2": 300,
      "y2": 200,
      "text": "Module",
      "style": {
        "fill": "RGB(240,248,255)",
        "line": "RGB(40,80,120)",
        "weight": 1.2,
        "fontSize": 10
      }
    }
  ]
}
```

## Naming

| Artifact | Naming |
|---|---|
| draw.io plan | `FIG-ARCH-001.drawio-plan.json` |
| Visio plan | `FIG-ARCH-001.visio-plan.json` |
| draw.io source | `figures/final/FIG-ARCH-001.drawio` |
| Visio source | `figures/final/FIG-ARCH-001.vsdx` |
| exports | `figures/final/FIG-ARCH-001.svg`, `.pdf`, `.png`, optional `.pptx` |

## Rule

The plan is a reconstruction aid. The scientific source of truth must be recorded in `figure-plan.md` or `network-architecture-figures.md`.
