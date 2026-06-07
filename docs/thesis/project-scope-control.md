# Project Scope Control

## Purpose

Use this file when the thesis starts from a fixed or tentative title. The title is allowed to guide the project, but it must remain a testable research hypothesis until literature, data, experiments, and writing evidence support it.

This file prevents four common thesis risks:

- title locked too early while evidence is still weak.
- research claims drifting beyond available data.
- causal leakage in time-series or prediction tasks.
- graph/model terminology becoming heavier than the actual experiment can support.

## Update Rules

- Update this file at stages 1, 3, 4, 8, and 10.
- Keep the advisor or original title unchanged in `topic-intake.md`; use this file to decide whether the working title should be kept, narrowed, or renamed.
- Do not promote a title phrase such as dynamic graph, causal, risk explanation, or interval prediction unless the related evidence gate is at least `candidate`.
- If a key gate remains weak after pilot experiments, record a downgrade route instead of forcing the original title.

## Title Status Register

| Item | Current Value | Status | Evidence Link | Notes |
|---|---|---|---|---|
| Original title | TBD | draft | `topic-intake.md` | Preserve original wording |
| Working title | TBD | draft | `thesis-brief.md` | May change after stage 3 / 8 / 10 review |
| Final thesis title | TBD | pending | `final-audit.md` | Lock only after advisor/final evidence check |
| Title risk level | low/medium/high/TBD | pending | this file | Use high when a title phrase has no evidence path |

## Title Review Gates

| Gate | Stage | Review Question | Required Evidence | Decision | Status | Notes |
|---|---|---|---|---|---|---|
| title-intake | 1 | What does each title phrase require the thesis to prove? | `topic-intake.md`, `thesis-brief.md` | keep/narrow/rename/TBD | pending |  |
| literature-pressure | 2-3 | Does closest prior work make the title too broad or too strong? | `literature-matrix.md`, `section-citation-map.md` | keep/narrow/rename/TBD | pending |  |
| experiment-feasibility | 4 | Can the dataset, node definition, metrics, and baselines test the title? | `experiment-architecture.md` | keep/narrow/rename/TBD | pending |  |
| result-survival | 8 | Do results support the title's method and application phrases? | `experiment-reports/`, `claim-evidence-map.md` | keep/narrow/rename/TBD | pending |  |
| writing-lock | 10 | Is the title consistent with every chapter and evidence chain? | `writing-outline.md`, `nature-style-writing-checklist.md` | lock/revise/TBD | pending |  |

## Causal Availability Contract

Use this table for any prediction, forecasting, intervention, or event-driven task.

| Field / Signal | Observable Before Prediction Time? | Allowed As Input? | Allowed As Label / After-the-Fact Explanation? | Leakage Risk | Mitigation | Status |
|---|---|---|---|---|---|---|
| historical target values | yes/no/TBD | yes/no/TBD | yes/no/TBD | low/medium/high/TBD | fixed rolling window | pending |
| event counts up to time t | yes/no/TBD | yes/no/TBD | yes/no/TBD | low/medium/high/TBD | event timestamp cutoff | pending |
| future completion / departure / final outcome | yes/no/TBD | no | yes/no/TBD | high | never use before prediction time | pending |
| static metadata | yes/no/TBD | yes/no/TBD | yes/no/TBD | low/medium/high/TBD | split-aware preprocessing | pending |
| reconstructed or imputed signals | yes/no/TBD | yes/no/TBD | yes/no/TBD | medium/high/TBD | sensitivity analysis | pending |

## Graph / Structure Definition Gate

Use this table when the title or method claims graph, dynamic graph, network, topology, relation, event structure, or node-level modeling.

| Item | Decision | Status | Evidence / Test | Downgrade Route |
|---|---|---|---|---|
| Primary node definition | station/interface/user/item/time-window/TBD | pending | data fields and sample count | switch to segment/state features |
| Primary edge meaning | physical/topological/correlation/event/similarity/TBD | pending | construction rule and ablation | describe as feature relation, not graph |
| Dynamic update trigger | time/event/model-learned/TBD | pending | timestamped rule or learned update | static graph or feature fusion |
| Anti-leakage rule | TBD | pending | causal availability contract | remove risky fields |
| Minimum graph evidence | ablation/randomized graph/event-window gain/TBD | pending | `experiment-reports/` | weaken title phrase |

## Downgrade / Rename Policy

| Trigger | Required Response | Candidate Safer Wording | Status | Notes |
|---|---|---|---|---|
| graph ablation gives unstable or negligible gain | do not overclaim graph contribution | behavior/event feature modeling | pending |  |
| dynamic relation cannot be causally computed before prediction time | remove dynamic graph claim | time-varying feature or post-hoc event analysis | pending |  |
| interval prediction is weak but point prediction works | keep uncertainty as secondary result | point prediction with uncertainty analysis | pending |  |
| risk explanation lacks real operational labels | call it proxy risk, not full safety analysis | capacity-risk proxy or warning indicator | pending |  |
| closest prior work overlaps strongly | narrow title and contribution | application-specific framework or evaluation protocol | pending |  |

## Promotion Rule

A title phrase can be used in the final thesis title only if it connects to at least one verified evidence path:

| Title Phrase / Concept | Required Evidence Path | Current Linked IDs | Status | Notes |
|---|---|---|---|---|
| TBD | CLM-* + CIT-* + EXP-* / DATA-* / FIG-* | TBD | pending |  |

