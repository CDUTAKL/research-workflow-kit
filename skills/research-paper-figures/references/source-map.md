# Source Map

This skill is a lightweight Codex-native synthesis for research figures and visual communication.

## Primary MIT Sources

- `external-skill-candidates/wanshuiyin-auto-research-skills/skills/paper-figure`
  - Used as inspiration for paper figure/table planning.
- `external-skill-candidates/wanshuiyin-auto-research-skills/skills/figure-spec`
  - Used as inspiration for structured figure specifications.
- `external-skill-candidates/k-dense-scientific-agent-skills/scientific-skills/scientific-visualization`
  - Used as inspiration for scientific visualization norms.
- `external-skill-candidates/k-dense-scientific-agent-skills/scientific-skills/markdown-mermaid-writing`
  - Used as inspiration for Mermaid diagram workflows.
- `external-skill-candidates/k-dense-scientific-agent-skills/scientific-skills/matplotlib`
  - Used as inspiration for Python plotting conventions.
- `external-skill-candidates/nature-skills/skills/nature-figure`
  - MIT licensed. Used as inspiration for claim-first figure contracts, chart atlas categories, common plotting patterns, multi-panel hierarchy, editable SVG/PDF export, source-data traceability, and publication-grade QA. Local files rewrite these ideas into `nature-figure-controlled-port.md`, `nature-figure-template-roadmap.md`, `figure-audit-standard.md`, and `skills/research-paper-figures/scripts/nature_plot_templates.py` for macOS/Codex + `docs/thesis/`.
- `external-skill-candidates/DeepLearningDrawingTemplate`
  - Apache-2.0 licensed repository. The local clone contains README previews and commercial links, not editable PPT source files. Used only as style inspiration for PPT-like neural-network architecture visual grammar: feature-map stacks, module grouping, residual paths, and editable vector emphasis. No screenshot pixels, watermarked images, or paid template assets are copied.
- `external-skill-candidates/codex-visio-replica-workflow`
  - No license file was observed in the referenced snapshot. Used as reference-only inspiration for reference-image decomposition, JSON diagram plans, Visio COM generation, export preview QA, and tutorial workflow boundaries. No external source code is copied into this skill.

## Local Adaptation Notes

- Original gallery images and chart-atlas PNGs are not copied into this skill.
- The local plotting templates are newly written adapters, not direct copies of the original scripts.
- Prefer local project plotting scripts when they already exist.
- Use `skills/research-paper-figures/scripts/nature_plot_templates.py` for common result figures when no project-specific plotting script exists.
- Nature-derived rules are adapted as workflow guidance, not as a mandatory Nature submission template.
- Network architecture figures should use the dedicated `network-architecture-figure.md` specification instead of generic block-flow diagrams.
- `skills/research-paper-figures/scripts/render_network_architecture.py` is the formal local renderer created for this workflow. It uses JSON structure specs and local presets to generate network architecture SVG/PDF/PNG outputs, optional PPTX when dependencies are available, and a QA report.
- `dual-platform-diagram-replica.md` rewrites the reference-image replication idea into a Mac draw.io route and a Windows Visio route, both tied back to `docs/thesis/` evidence records.
