# Workflow Dashboard

## Purpose

This is the project homepage for the research workflow. Update it manually during weekly planning, or refresh the generated sections with:

```bash
python scripts/research_workflow_doctor.py --write-dashboard
```

## Current Status

| Field | Value |
|---|---|
| Current stage | 1-12/TBD |
| Active focus | planning/literature/experiment/writing/finalization/TBD |
| Current audit tier | quick/advisor/final/TBD |
| Main blocker | TBD |
| Next concrete action | TBD |
| Last dashboard refresh | TBD |

## Stage Snapshot

| Stage | Name | Status | Main Record | Notes |
|---|---|---|---|---|
| 1 | Paper planning | pending | `thesis-brief.md`, `idea-discovery.md` |  |
| 2 | Literature discovery and review | pending | `literature-matrix.md`, `section-citation-map.md` |  |
| 3 | Experiment question definition | pending | `claim-evidence-map.md` |  |
| 4 | Experiment architecture planning | pending | `experiment-architecture.md` |  |
| 5 | Research code implementation | pending | code repo, `git-version-log.md` |  |
| 6 | Experiment run and monitoring | pending | `experiment-runbook.md` |  |
| 7 | Experiment recording and result scan | pending | `experiment-registry.md` |  |
| 8 | Results analysis and claim mapping | pending | `claim-evidence-map.md`, `data-availability.md` |  |
| 9 | Figure and table production | pending | `figure-plan.md` |  |
| 10 | Paper writing and polishing | pending | `writing-outline.md` |  |
| 11 | Laptop DOCX / optional LaTeX / PDF | pending | final document artifacts |  |
| 12 | Laptop final audit and defense | pending | `final-audit.md`, `defense-prep.md` |  |

## Health Summary

<!-- workflow-doctor:start -->
Run `python scripts/research_workflow_doctor.py --write-dashboard` to refresh this section.
<!-- workflow-doctor:end -->

## Evidence Graph

Generate current evidence relationships with:

```bash
python scripts/export_evidence_graph.py --out docs/thesis/evidence-graph.json --mermaid docs/thesis/evidence-graph.mmd
```

| Graph Artifact | Status | Notes |
|---|---|---|
| `evidence-graph.json` | pending | machine-readable evidence relationship graph |
| `evidence-graph.mmd` | pending | Mermaid diagram for quick visual inspection |

## Quick Navigation

| Need | File |
|---|---|
| What should happen next? | `workflow-dashboard.md`, `task-board-sync.md` |
| What claims are safe? | `claim-evidence-map.md`, `evidence-promotion-policy.md` |
| What experiments support the thesis? | `experiment-registry.md`, `experiment-runbook.md` |
| What data backs the results? | `data-availability.md` |
| What citations support each section? | `section-citation-map.md`, `literature-matrix.md` |
| What figures are final? | `figure-plan.md`, `network-architecture-figures.md` |
| Is this ready for advisor or final review? | `final-audit.md` |
