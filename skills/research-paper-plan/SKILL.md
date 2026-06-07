---
name: research-paper-plan
description: Use when planning a research paper, graduation thesis, dissertation, journal manuscript, conference paper, or project report before drafting; especially when the user has an advisor-given topic/title, needs Topic Intake to Research Blueprint, or needs a research question, contribution story, chapter outline, experiment-to-claim map, figure plan, or missing-materials checklist.
---

# Research Paper Plan

Use this skill to turn an advisor-given title, research idea, codebase, experiment set, or rough thesis topic into a concrete research blueprint. Keep the output decision-oriented: what the title means, what the paper claims, what evidence supports it, what each section must do, and what work remains.

## Core Rules

- Start from available evidence, not from a desired conclusion.
- Separate `claim`, `evidence`, `experiment`, `figure/table`, and `citation` so weak links are visible.
- Prefer a conservative contribution statement that can survive review.
- Do not invent completed experiments, citations, datasets, or metrics.
- For graduation theses, include school-facing sections such as abstract, related work, method, experiment, conclusion, appendix, acknowledgments, and defense preparation when relevant.
- When a title or topic is provided, run Topic Intake before normal paper planning.
- Treat a fixed or tentative title as a draft research hypothesis. Record title survival, causal availability, node/structure definition, and downgrade/rename routes in `docs/thesis/project-scope-control.md`.
- For early-stage idea exploration, use `docs/thesis/idea-discovery.md` to record paper pools, idea matrices, novelty risks, and shortlists.

## Workflow

Read `references/workflow.md` for the detailed planning checklist and output templates. Use `scripts/generate_topic_intake.py` when the user gives a title and wants the thesis console updated. Read `references/source-map.md` only when attribution, license provenance, or source inspiration matters.

1. If a title/topic is provided, perform Topic Intake: decompose the title, identify research object/task, keywords, routes, risks, and advisor questions.
2. For title-first projects, create or update the project-scope control: title phrase evidence requirements, stage 1/3/4/8/10 review gates, causal availability, node/structure definition, and downgrade/rename policy.
3. If the topic is still open, build an idea-discovery record: paper pool, idea matrix, novelty risk, feasibility, and shortlist.
4. Identify the paper type, audience, target venue/school format if known, and current materials.
5. Extract the research problem, technical challenge, proposed method, available results, and expected contribution.
6. Build a section-level outline where every section has a purpose and required evidence.
7. Map each major claim to experiments, figures/tables, citations, and missing work.
8. When required experiments need code architecture, data pipelines, training/evaluation entrypoints, or reproducibility planning, route that work to `$research-experiment-engineering`.
9. Update or propose updates for `docs/thesis/topic-intake.md`, `project-scope-control.md`, `idea-discovery.md`, `thesis-brief.md`, `writing-outline.md`, `literature-matrix.md`, and `experiment-architecture.md`.
10. Return a prioritized next-action list that separates advisor clarification, literature, experiment engineering, result analysis, figures, and writing.

## Output Contract

Always include:

- topic decomposition when a title/topic is provided
- title survival and downgrade/rename checkpoints when a title is provided first
- research object
- research task
- keywords and synonyms
- possible technical routes
- idea-discovery paper pool or shortlist when topic exploration is requested
- preliminary innovation candidates
- paper question tree
- literature search directions
- research question
- core contribution
- paper or thesis outline
- section goals
- required experiments
- experiment engineering gaps when code, run commands, outputs, or reproducibility are missing
- required figures and tables
- risks and infeasible directions
- questions to confirm with the advisor
- available materials
- missing materials
- next actions

If the user provides a codebase or result folders, inspect them before planning. If evidence is insufficient, mark it as missing instead of smoothing over the gap.
