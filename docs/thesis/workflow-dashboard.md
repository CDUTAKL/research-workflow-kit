# Workflow Dashboard

## Purpose

This is the project homepage for the research workflow. Update it manually during weekly planning, or refresh the generated sections with:

```bash
python scripts/research_workflow_doctor.py --write-dashboard
```

The local web dashboard is the operational view of the same console. Start it with:

```bash
./scripts/open_dashboard.sh
```

It starts a local-only control service on `127.0.0.1:8765` so the page can refresh dashboard data, export the evidence graph, run the quick health check, open whitelisted source files, and copy recommended commands.

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

Open the local React/Vite dashboard with:

```bash
cd dashboard-web
pnpm run prepare:data
pnpm run dev
```

Simpler Mac launcher:

```bash
./scripts/open_dashboard.sh
```

Or double-click `open-dashboard.command` in Finder.

| Graph Artifact | Status | Notes |
|---|---|---|
| `evidence-graph.json` | pending | machine-readable evidence relationship graph |
| `evidence-graph.mmd` | pending | Mermaid diagram for quick visual inspection |

## Operational Actions

| Action | Script / Button | Output |
|---|---|---|
| Refresh dashboard data | `Refresh Dashboard` or `python scripts/research_workflow_doctor.py --write-dashboard --write-data` | `workflow-dashboard.md`, `dashboard-data.json` |
| Export evidence graph | `Export Evidence Graph` or `python scripts/export_evidence_graph.py` | `evidence-graph.json`, `evidence-graph.mmd` |
| Run quick health check | `Run Quick Health Check` or `python scripts/research_workflow_doctor.py --warn-only` | P0/P1 console report |
| Create deep research task | `python scripts/new_deep_research_task.py --section-id SEC-INTRO-001 --topic "..."` | `deep-research-tasks.md`, section packet |
| Create experiment report | `python scripts/new_experiment_report.py --experiment-id EXP-001 --baseline EXP-000` | `experiment-reports/EXP-001.md` |
| Audit skills | `python scripts/audit_skills.py --warn-only --write-report` | `skill-audit-report.md` |

## Quick Navigation

| Need | File |
|---|---|
| What should happen next? | `workflow-dashboard.md`, `task-board-sync.md` |
| What claims are safe? | `claim-evidence-map.md`, `evidence-promotion-policy.md` |
| What experiments support the thesis? | `experiment-registry.md`, `experiment-runbook.md` |
| What data backs the results? | `data-availability.md` |
| What citations support each section? | `section-citation-map.md`, `literature-matrix.md` |
| What citation search task should run next? | `deep-research-tasks.md`, `section-research-packets/` |
| What changed versus baseline? | `experiment-reports/` |
| What figures are final? | `figure-plan.md`, `network-architecture-figures.md` |
| Is this ready for advisor or final review? | `final-audit.md` |
