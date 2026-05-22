# Research Paper Writing Workflow

## Section Jobs

| Section | Job |
|---|---|
| Abstract | State problem, method, evidence, result, contribution in compressed form |
| Introduction | Motivate problem, expose gap, preview method and contribution |
| Related work | Position the work among method families and open gaps |
| Method | Explain what was done and why it is appropriate |
| Experiments | Show how claims are tested fairly |
| Results | Report evidence without exaggeration |
| Discussion | Explain meaning, limitations, and practical implications |
| Conclusion | Summarize contribution and bounded future work |

## Paragraph Pattern

Use this structure for most technical paragraphs:

```text
Topic sentence: what this paragraph claims.
Evidence or mechanism: result, method detail, or cited support.
Interpretation: why it matters for the paper.
Transition: how it connects to the next point.
```

## Introduction Pattern

1. Broad problem and importance.
2. Specific technical challenge.
3. Limitations in existing work.
4. Proposed approach.
5. Main contributions.
6. Thesis or paper organization.

Avoid:

- Starting with generic global importance for too long.
- Claiming novelty without comparing existing work.
- Listing contributions that are actually implementation details.
- Reporting results that are not later supported.

## Method Pattern

```text
Problem formulation:
Input/output:
Pipeline:
Model or algorithm:
Training/inference details:
Design rationale:
Complexity or practical notes if relevant:
```

## Experiment Pattern

```text
Dataset:
Baselines:
Metrics:
Implementation details:
Main comparison:
Ablation:
Robustness/error analysis:
Threats to validity:
```

## Revision Checklist

- The first sentence tells the reader why the paragraph exists.
- Each claim has evidence or a citation marker.
- There are no unsupported superlatives such as "best", "robust", "significant", or "state of the art" unless proven.
- Terms are consistent across sections.
- Contributions are not repeated in inconsistent forms.
- Chinese text keeps formal academic tone without empty slogans.
- English text uses active, direct sentences where possible.

## Nature-Derived Polishing Pass

Use this pass after the section's evidence, citations, and structure are stable. It improves clarity and academic force, but must not invent novelty, results, mechanisms, citations, or causal explanations.

| Check | Action |
|---|---|
| Paper type | Identify whether the work is research, methods, algorithmic, device, dataset, or review-like |
| Section job | Confirm the section answers the correct reader question before sentence polish |
| Hourglass logic | Introduction narrows from field problem to gap; discussion/conclusion widens from finding to meaning and boundary |
| Results vs discussion | Results report observations and numbers; discussion interprets and states limits |
| Hedging | Match wording strength to evidence: avoid prove, always, first, robust, and significant unless justified |
| Sentence clarity | Split overloaded sentences; prefer one main claim per sentence |
| Citation integrity | Keep citation markers attached to the exact supported sentence |
| Language target | Chinese thesis keeps formal Chinese academic tone; English manuscript can use Nature-leaning concise prose when requested |

For English journal-style polishing, prefer direct sentences, concrete subjects, and defensible verbs. For Chinese graduation-thesis polishing, keep the same logic but do not force British English or Nature house style unless the user explicitly requests an English manuscript.

## Output Template

```text
Revised text:

Key changes:

Evidence/citation gaps:

Polishing checks applied:

Optional next edit:
```

## Iteration Rule

Treat writing as part of an iterative research loop:

- If new results change the story, update the outline and affected sections.
- If audit finds an unsupported claim, weaken the wording or return to experiments.
- If a figure reveals a clearer pattern, revise the result narrative and caption together.
- If related work changes the gap, revise the introduction before polishing the abstract.

Use `$research-workflow-orchestrator` for multi-stage coordination and `$research-final-audit` before treating a section as submission-ready.
