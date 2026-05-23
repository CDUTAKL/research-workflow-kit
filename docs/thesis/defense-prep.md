# Defense Prep

## Update Rules

- Use this file to prepare the defense narrative, slides, evidence backups, and likely Q&A.
- Every slide claim must trace to `claim-evidence-map.md`, `figure-plan.md`, `section-citation-map.md`, or `final-audit.md`.
- Use Presentations for PPTX creation/editing. Use nature-paper2ppt-derived structure when converting a paper or thesis chapter into a Chinese academic deck. Use Figma or BioRender for visual refinement when useful. Canva is optional only when available.
- Final stage 11-12 production is intended to happen on the user's laptop; keep slide/evidence versions traceable back to the Mac `docs/thesis/` console.

## Defense Narrative

| Section | Purpose | Evidence Source | Slide Status |
|---|---|---|---|
| Problem and motivation | explain why the topic matters | `thesis-brief.md`, literature matrix | planned |
| Related work gap | position the work | `literature-matrix.md` | planned |
| Method | explain core approach | `experiment-architecture.md`, `figure-plan.md` | planned |
| Experiments | show protocol and baselines | `experiment-registry.md`, `reproducibility-checklist.md` | planned |
| Results | present supported findings | `claim-evidence-map.md`, figures/tables | planned |
| Limitations and future work | show judgment and scope | `final-audit.md`, error analysis | planned |

## Slide Inventory

| Slide ID | Title | Claim / Purpose | Evidence | Figure/Table | Status | Notes |
|---|---|---|---|---|---|---|
| S01 | Title | introduce thesis | thesis metadata | none | planned |  |
| S02 | Motivation | TBD | `thesis-brief.md` | TBD | planned |  |
| S03 | Method overview | TBD | `experiment-architecture.md` | FIG-001/TBD | planned |  |
| S04 | Main results | CLM-001/TBD | `claim-evidence-map.md` | FIG-TABLE-001/FIG-001 TBD | planned |  |

## Paper-To-PPT Structure

Use this when building a PPTX from the thesis, a paper draft, or a source paper.

| Slide Role | Purpose | Evidence Input | Figure/Table Selection | Speaker Note Need | Status |
|---|---|---|---|---|---|
| Title | identify topic and presenter | thesis metadata | optional hero figure | low | planned |
| Background | why the problem matters | `thesis-brief.md`, literature | context figure optional | medium | planned |
| Gap / bottleneck | what is unresolved | `literature-matrix.md` | comparison table/diagram optional | medium | planned |
| Method / workflow | what was built or tested | `experiment-architecture.md` | method diagram | high | planned |
| Key evidence | what supports main claim | `claim-evidence-map.md`, `figure-plan.md`, `section-citation-map.md` | selected result figures only | high | planned |
| Validation / robustness | why the result is credible | registry, reproducibility checklist | ablation/error/robustness visual | high | planned |
| Limitations | where the claim stops | `final-audit.md` | optional limitation table | high | planned |
| Summary / Q&A | take-home message and backup evidence | final audit, claim map | optional synthesis figure | medium | planned |

## Q&A Preparation

| Question | Expected Answer | Evidence / Backup | Risk Level | Status |
|---|---|---|---|---|
| Why this method? | TBD | literature + experiment architecture | medium | pending |
| How do you know the result is reliable? | TBD | reproducibility checklist + result analysis | high | pending |
| What are the limitations? | TBD | final audit + error analysis | high | pending |

## Presentation Tool Rules

- Use Presentations for creating, editing, rendering, and verifying `.pptx`.
- Use nature-paper2ppt-derived rules to choose a small number of evidence-bearing figures instead of copying every figure.
- Choose slide citations from `section-citation-map.md` and important evidence figures from `figure-plan.md`; do not add uncited slide claims.
- Use Figma or BioRender when a slide needs visual refinement beyond PPTX layout.
- Use Canva only when it is available and a polished visual design or poster-style asset is needed.
- Do not create slide claims that are stronger than the audited thesis claims.
- Keep backup evidence paths visible in speaker notes or this file.
