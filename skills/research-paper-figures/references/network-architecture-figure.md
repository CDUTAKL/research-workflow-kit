# Network Architecture Figure Specification

Use this reference when drawing neural-network architecture figures for papers, theses, reports, presentations, or model diagrams.

## Core Principle

A network architecture figure should explain how representations change through the model. It is not a decorative flowchart. The main visual variables are feature-map size, channel depth, module grouping, shortcut/fusion paths, and task head.

## Rendering Workflow

Use a structure specification instead of improvising the figure each time.

```text
architecture source or model.py
-> .network.json structure spec
-> preset selection
-> skills/research-paper-figures/scripts/render_network_architecture.py
-> SVG/PDF/PNG and optional PPTX
-> QA report
-> figure-plan.md and network-architecture-figures.md
```

Default command:

```powershell
python skills\research-paper-figures\scripts\render_network_architecture.py `
  --spec skills\research-paper-figures\examples\resnet18.network.json `
  --preset ppt-template-rich `
  --out figures\architecture\resnet18_architecture `
  --formats svg,pdf,png,pptx `
  --pptx-mode image-backed `
  --qa-report
```

PPTX export is a formal target for presentation-style figures. Use `--pptx-mode image-backed` for the most stable first-pass PPTX, or `--pptx-mode native-shape` when an editable PowerPoint draft is more important than exact Matplotlib visual parity. If `python-pptx` is unavailable, use the Presentations plugin or install `python-pptx`; keep SVG/PDF/PNG as the immediate manuscript outputs.

Figma is useful after the renderer has produced a structurally correct diagram. Use Figma for visual refinement, reusable diagram components, collaborative review, and design-system consistency. Do not let Figma become the only source of architecture truth; update the `.network.json` spec whenever the model structure changes.

## Presets

| Preset | Use when | Visual behavior |
|---|---|---|
| `thesis-clean` | school thesis, conservative report, Word manuscript | clean labels, restrained color, compact layout |
| `nature-minimal` | high-impact manuscript, journal-style figure package | lighter labels, low saturation, stronger whitespace discipline |
| `ppt-template-rich` | DeepLearningDrawingTemplate-like model diagram, slides, method overview | richer feature-map stacks, PPT-like modules, more visible hierarchy |

## Tool Handoff

| Target | Best use | Source of truth |
|---|---|---|
| `.network.json` | architecture facts, shapes, stages, repeats, downsampling, heads | yes |
| SVG/PDF/PNG | manuscript assets and preview | generated from spec |
| PPTX | presentation asset; record whether image-backed or native editable shapes | generated or refined from spec |
| Figma | visual polish, component reuse, layout exploration, collaborative design | no; sync back to spec |

## `.network.json` Schema

Use this minimal schema for reusable architecture figures.

| Field | Meaning |
|---|---|
| `layout` | `linear`, `encoder_decoder`, `multi_branch`, or `transformer`; current renderer fully supports linear and records other layouts for QA |
| `model`, `title`, `subtitle` | model identity and visible title text |
| `core_conclusion` | narrow topology statement the figure should communicate |
| `input` | input name, shape, color role, and visual plane count |
| `operations` | stem or transition tags such as convolution, pooling, patch embedding, or projection |
| `stages` | ordered modules with name, shape, planes, repeat badge, block, and downsample note |
| `connections` | explicit residual, skip, concat, fusion, or attention paths with `from`, `to`, `type`, and optional label |
| `head` | pooling, classifier, decoder, regressor, or output blocks |
| `insets` | repeated block explanations such as residual BasicBlock |
| `panels` | optional side panels such as legend, block inset, or shape scale |
| `audit` | source paper, implementation source, caption-safe note, and claim boundary |
| `caption` | manuscript-safe caption |

Example connection:

```json
{"from": "layer2", "to": "layer4", "type": "skip", "label": "long skip", "offset": 1.35}
```

Rules:

- Keep `.network.json` next to generated outputs or record its path in `docs/thesis/network-architecture-figures.md`.
- Use `connections` for topology facts that must be visible; do not rely on decorative arrows.
- Put performance claims outside architecture captions unless the same figure also contains result evidence.
- Record whether PPTX output is `image-backed` or `native-shape`.

## When To Use

Use this specification for:

- CNN, VGG, ResNet, DenseNet, Inception, EfficientNet, MobileNet, and custom convolutional networks.
- U-Net, encoder-decoder, segmentation, reconstruction, or multi-scale networks.
- Transformer, ViT, Swin Transformer, attention, MLP-Mixer, and token-flow architectures.
- Feature-fusion, multi-branch, hierarchical decision, ensemble, or multi-modal models.
- Any request mentioning "PPT template style", "network structure diagram", "model architecture diagram", "feature map", "residual block", "attention module", or "论文级模型结构图".

## Visual Grammar

| Model element | Preferred representation | Avoid |
|---|---|---|
| Input | small image/spectrum/table glyph with shape annotation | large text-only box |
| Feature map | stacked semi-transparent planes or slabs; size follows spatial resolution | equal-size rectangles for all layers |
| Channel depth | stack count, depth offset, or numeric channel label | hiding channel changes |
| Convolution block | compact module tag attached to feature stack | verbose operation list inside a large box |
| Pooling/downsampling | narrow arrow with stride or scale label | unexplained jump in size |
| Residual/skip path | curved path over or under the main stream, with add node if needed | crossing lines with no endpoint |
| Attention/fusion | separate branch with gate/weight/fusion node | mixing branches without visual junction |
| Classifier head | global pooling icon plus FC/logits block | oversized final block |
| Repeated block | `x2`, `x3`, or `xN` badge, plus inset showing block internals | drawing every repeated conv layer in full |

## Figure Contract

Before drawing, define:

| Field | Requirement |
|---|---|
| Core conclusion | What the architecture figure should make clear |
| Architecture source | Paper, code, model printout, or user-provided spec |
| Input shape | Example: `224 x 224 x 3`, `1024 x 1`, or `T x C` |
| Stage list | Module name, repeated blocks, output shape, channels |
| Downsampling points | Stride/pooling/fusion points |
| Shortcut/fusion paths | Start, end, operation, and purpose |
| Head | Global pooling, classifier/regressor, decoder, or output classes |
| Caption-safe wording | Explain structure only; do not imply performance |
| Export | SVG/PDF for manuscript; PNG preview; PPTX when user wants editable PowerPoint |

## Style Rules

- Prefer 16:9 or wide manuscript proportions for full architecture diagrams.
- Use one restrained palette: neutral input, blue/green early features, warm mid features, violet deep features, red output.
- Use feature-map planes to show spatial resolution changes: larger and flatter early, smaller and deeper later.
- Put detailed operations in concise tags or an inset, not in the main stream.
- Use repeated-block badges such as `x2 BasicBlock` to reduce clutter.
- Keep all arrows thin and purposeful; avoid decorative curves.
- Use direct labels near modules instead of a separate legend when possible.
- Keep labels short enough for Word/PDF rendering at final size.
- Preserve editable vector text in SVG/PDF where possible.
- Keep a `.network.json` spec next to generated outputs or in the thesis console so the figure can be regenerated after model changes.
- When PPTX output is requested, record whether it is native editable shapes or image-backed PPTX.
- When Figma is used, record the Figma file/node and exported asset paths in `docs/thesis/network-architecture-figures.md`.
- When QA reports unresolved connections, fix the `.network.json` node names before using the figure.

## Recommended Layouts

### CNN / ResNet

```text
input glyph -> stem -> stage1 -> stage2 -> stage3 -> stage4 -> global pooling -> classifier
                     residual block inset below or beside main stream
```

The main stream shows feature-map stacks and output shapes. An inset explains the repeated residual block.

### U-Net / Encoder-Decoder

```text
encoder down path on left -> bottleneck -> decoder up path on right
skip connections bridge matching scales
```

Use symmetric stage placement. Make skip paths visually lighter than the main path.

### Transformer / ViT

```text
input image/text -> patch/token embedding -> repeated transformer encoder xN -> pooling/class token -> head
```

Show token sequence or patch grid, then repeated block inset with MSA, MLP, residual, and layer norm.

### Multi-Branch Fusion

```text
branch A input -> encoder A
branch B input -> encoder B
fusion node -> shared head
```

Use branch color only to distinguish modalities or streams. The fusion node must state concat/add/attention/gating.

## Caption Template

```text
Figure X. Architecture of [model name]. The diagram shows the representation flow from [input shape] through [main stages], where spatial resolution is reduced from [start] to [end] and channel depth increases from [start channels] to [end channels]. The inset illustrates the repeated [block name]. This schematic describes model structure only and does not report performance.
```

## Source And License Notes

- `external-skill-candidates/DeepLearningDrawingTemplate` is Apache-2.0 licensed but contains only README previews and commercial links in the local clone. Use it as style inspiration for editable PPT-like visual grammar; do not copy screenshot pixels, watermarked images, or paid template assets.
- `external-skill-candidates/nature-skills/skills/nature-figure` is used for claim-first figure contracts and export QA.
- When drawing a known architecture such as ResNet-18, cite the original paper and the implementation source used for layer details.
