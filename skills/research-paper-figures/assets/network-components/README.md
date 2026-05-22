# Network Components

This directory documents the reusable visual components used by the network architecture renderer.

The first implementation generates components programmatically as editable vector shapes in SVG/PDF:

- `feature_map_stack`: stacked planes representing spatial size and channel depth.
- `operation_tag`: compact operation labels such as `7x7 conv` or `maxpool`.
- `skip_connection`: residual or fusion path with optional add node.
- `block_inset`: compact repeated-block diagram such as ResNet BasicBlock.
- `classifier_head`: global pooling, dense layer, logits, or task output.
- `shape_label`: tensor shape and channel label.
- `repeat_badge`: `x2`, `x3`, or `xN` repeated module badge.

Do not copy pixels or paid template assets from external preview repositories. Use external templates only as visual grammar references.
