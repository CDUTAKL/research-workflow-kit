# Research Paper Planning Workflow

## Topic Intake -> Research Blueprint

Run this first when the user provides an advisor-given title, tentative thesis title, or fixed research topic.

Required output:

| Item | Purpose |
|---|---|
| 1. Topic decomposition | parse title phrases and hidden assumptions |
| 2. Research object | what data, system, material, population, or phenomenon is studied |
| 3. Research task | classification, prediction, detection, optimization, comparison, review, design, or analysis |
| 4. Keywords and synonyms | Chinese/English terms, method terms, data terms, metric terms |
| 5. Possible technical routes | conservative candidate routes with dependencies and risks |
| 6. Preliminary innovation candidates | possible contributions that still need evidence |
| 7. Paper question tree | main question, subquestions, experiment questions |
| 8. Literature search directions | foundational, recent, method, dataset, metric, limitation literature |
| 9. Experiment needs | baseline, main experiment, ablation, robustness, error analysis |
| 10. Figure/table needs | method diagram, data overview, main table, ablation, error analysis |
| 11. Risks and infeasible directions | data, time, compute, novelty, baseline, scope risks |
| 12. Questions for advisor | decisions that should be confirmed before deep implementation |

Console handoff:

| Destination | What to write |
|---|---|
| `docs/thesis/topic-intake.md` | full topic intake and advisor-confirmation questions |
| `docs/thesis/thesis-brief.md` | working title, research question, contribution candidates, scope |
| `docs/thesis/writing-outline.md` | topic-derived chapter goals and writing dependencies |
| `docs/thesis/literature-matrix.md` | first search directions, keywords, paper role gaps |
| `docs/thesis/experiment-architecture.md` | first experiment objectives, data/model/evaluation needs |

Use the helper script when a structured first draft is useful:

```bash
python skills/research-paper-plan/scripts/generate_topic_intake.py --title "advisor title here" --out-dir docs/thesis
```

For Chinese or other non-ASCII titles, prefer a UTF-8 title file when shell encoding is uncertain:

```bash
python skills/research-paper-plan/scripts/generate_topic_intake.py --title-file title.txt --out-dir docs/thesis
```

The script scaffolds the console. The skill must still reason about the title and fill or revise the generated sections.

## Inputs to Gather

- Working title or topic.
- Paper type: graduation thesis, journal article, conference paper, report, survey, benchmark, or proposal.
- Current artifacts: code, data, results, figures, draft text, notes, target template.
- Intended audience: advisor, thesis committee, journal reviewers, conference reviewers, technical readers.
- Hard constraints: language, page/word limit, required chapters, submission deadline, target venue or school template.
- Advisor notes, required methods, forbidden directions, available data, and available compute when known.

## Planning Template

```text
Working title:
Paper type:
Audience:
Research question:
Technical challenge:
Core contribution:
What is new:
What is already proven:
What is not yet proven:
```

## Claim-Evidence Map

Use this table before drafting.

| Claim | Evidence needed | Current evidence | Figure/table | Citation need | Status |
|---|---|---|---|---|---|
| Main claim | Main experiment | Available/missing | Figure X/Table Y | Related method | Ready/weak/missing |
| Secondary claim | Ablation/error analysis | Available/missing | Figure X/Table Y | Supporting work | Ready/weak/missing |

Status rules:

- `Ready`: supported by concrete results and a clear comparison.
- `Weak`: plausible but needs clearer evidence, baseline, or citation.
- `Missing`: do not write as a conclusion yet.

## Thesis Outline Pattern

1. Abstract
   - Problem, method, result, contribution.
2. Introduction
   - Background, challenge, gap, approach, contribution, thesis structure.
3. Related Work
   - Group by problem, method family, dataset/task, evaluation, not by isolated paper summaries.
4. Method
   - Problem formulation, data pipeline, model/algorithm, training/inference, design rationale.
5. Experiments
   - Dataset, metrics, baselines, implementation details, main results, ablation, robustness/error analysis.
6. Discussion
   - Why results happen, limitations, practical meaning.
7. Conclusion
   - Contributions, limitations, future work.
8. Appendix
   - Extra tables, hyperparameters, proofs, additional figures, code/data notes.

## Figure and Table Plan

Minimum useful set:

- Problem/data overview.
- Method pipeline or model architecture.
- Main comparison table.
- Key result figure.
- Ablation table or figure.
- Error analysis, confusion matrix, robustness, or case study.

For each planned visual:

```text
Figure/table:
Purpose:
Input data:
Claim supported:
Caption claim:
Current status:
```

## Final Output Checklist

- Topic intake is completed when a title/topic is provided.
- The core contribution is one sentence.
- Every section has a purpose.
- Every major claim has evidence or is marked missing.
- Figures and tables are tied to claims.
- Literature tasks are separated from writing tasks.
- Advisor-confirmation questions are explicit.
- Next actions are ordered by blocking risk.

## Orchestrator Handoff

For full-project or multi-week thesis planning, start with `$research-workflow-orchestrator` and then route into this skill for the paper blueprint. Use this skill directly when the user already knows they need a research question, contribution story, chapter outline, or claim-evidence map.
