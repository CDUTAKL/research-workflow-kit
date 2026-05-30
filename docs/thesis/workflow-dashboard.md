# Workflow Dashboard

## Purpose

This is the project homepage for the research workflow. Update it manually during weekly planning, or refresh the generated sections with:

```bash
python scripts/research_workflow_doctor.py --write-dashboard
```

The local web dashboard is the operational view of the same console. It is designed as a Chinese research cockpit for daily thesis management: current stage, blockers, next action, evidence health, and common actions are visible from the first screen. Start it with:

```bash
./scripts/open_dashboard.sh
```

It starts a local-only control service on `127.0.0.1:8765` so the page can refresh dashboard data, export the evidence graph, run the quick health check, open whitelisted source files, copy recommended commands, update the daily stage workspace, generate local citation suggestions, package final handoff artifacts, verify the latest handoff package, and use the flow editor to append standard records.

Use Build Web Data Visualization principles when the dashboard becomes advisor-facing: keep charts simple, show uncertainty or missingness when relevant, make labels readable on desktop/mobile, and do not let visual polish hide unsupported claims.

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
| 2 | Literature discovery and review | pending | `literature-matrix.md`, `zotero-screening-loop.md`, `section-citation-map.md` |  |
| 3 | Experiment question definition | pending | `claim-evidence-map.md` |  |
| 4 | Experiment architecture planning | pending | `experiment-architecture.md` |  |
| 5 | Research code implementation | pending | code repo, `git-version-log.md` |  |
| 6 | Experiment run and monitoring | pending | `experiment-runbook.md` |  |
| 7 | Experiment recording and result scan | pending | `experiment-registry.md` |  |
| 8 | Results analysis and claim mapping | pending | `claim-evidence-map.md`, `data-availability.md` |  |
| 9 | Figure and table production | pending | `figure-plan.md`, `diagram-replica-tasks.md` |  |
| 10 | Paper writing and polishing | pending | `writing-outline.md` |  |
| 11 | Laptop DOCX / optional LaTeX / PDF | pending | `final-artifact-manifest.md`, final document artifacts |  |
| 12 | Laptop final audit and defense | pending | `final-audit.md`, `defense-prep.md`, `final-artifact-manifest.md` |  |

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

Recommended Mac route: install a fixed local URL service once:

```bash
./scripts/install_dashboard_fixed_url_macos.sh
```

Then open this fixed page from a browser bookmark or pinned tab:

```text
http://127.0.0.1:5173/
```

This uses a macOS user LaunchAgent to start the dashboard service at login and check it every 5 minutes. It does not require a desktop shortcut.

Manual launchers remain available:

```bash
./scripts/open_dashboard.sh
./scripts/install_dashboard_app_macos.sh
```

`open_dashboard.sh` shows terminal logs. `install_dashboard_app_macos.sh` creates an optional app under `~/Applications/`.

| Graph Artifact | Status | Notes |
|---|---|---|
| `evidence-graph.json` | pending | machine-readable evidence relationship graph |
| `evidence-graph.mmd` | pending | Mermaid diagram for quick visual inspection |
| Visual QA | pending | check graph/chart readability, contrast, labels, and missing-evidence visibility before advisor/final review |

## Operational Actions

| Action | Script / Button | Output |
|---|---|---|
| 更新今日工作区 | Dashboard `今日工作区` or `python scripts/update_daily_workflow.py --stage "2 文献发现与综述" --next-action "..."` | `daily-workflow-entry.md`, `workflow-dashboard.md`, `workflow-edit-log.md` |
| 刷新控制台数据 | `刷新控制台` or `python scripts/research_workflow_doctor.py --write-dashboard --write-data` | `workflow-dashboard.md`, `dashboard-data.json` |
| 导出证据图谱 | `导出证据图谱` or `python scripts/export_evidence_graph.py` | `evidence-graph.json`, `evidence-graph.mmd` |
| 快速健康检查 | `快速健康检查` or `python scripts/research_workflow_doctor.py --warn-only` | P0/P1 console report |
| 创建深研任务 | `python scripts/new_deep_research_task.py --section-id SEC-INTRO-001 --topic "..."` | `deep-research-tasks.md`, section packet |
| 生成本地引用推荐 | Dashboard `引用推荐` or `python scripts/suggest_section_citations.py --section-id SEC-INTRO-001` | `section-citation-suggestions.md`, optional dashboard JSON |
| 创建实验报告 | `python scripts/new_experiment_report.py --experiment-id EXP-001 --baseline EXP-000` | `experiment-reports/EXP-001.md` |
| 检查材料护照 | `打开材料护照` | `material-passport.md` |
| 检查引用溯源 | `打开引用溯源` | `citation-provenance.md` |
| 检查 Zotero 覆盖 | `打开文献覆盖` | `zotero-collection-coverage.md` |
| 检查 benchmark 规范 | `打开 Benchmark` | `benchmark-report-schema.md` |
| 审计 skills | `python scripts/audit_skills.py --warn-only --write-report` | `skill-audit-report.md` |
| 可视化质量检查 | Build Web Data Visualization checklist | readable charts, visible uncertainty, accessible contrast, no hidden evidence gaps |
| 使用流程编辑器新增记录 | Dashboard `流程编辑器` | `claim-evidence-map.md`, `experiment-registry.md`, `material-passport.md`, `citation-provenance.md`, `final-artifact-manifest.md` |
| 审计最终交付物 | `python scripts/audit_final_artifacts.py --tier quick --warn-only` | stage 11-12 handoff risk list |
| 打包最终交接 | Dashboard `最终交接` or `python scripts/package_final_handoff.py --update-manifest-checksums` | `handoff-packages/final-handoff-*/` zip, manifest, checksum, summary |
| 校验最终交接 | Dashboard `校验最新包` or `python scripts/verify_final_handoff.py --latest --write-report docs/thesis/final-handoff-verify-report.md` | `final-handoff-verify-report.md` |
| 审计 ID 生命周期 | `python scripts/audit_id_lifecycle.py --warn-only` | orphan, unknown, deprecated, or weakly linked ID warnings |

## Quick Navigation

| Need | File |
|---|---|
| What should happen next? | `workflow-dashboard.md`, `task-board-sync.md` |
| What claims are safe? | `claim-evidence-map.md`, `evidence-promotion-policy.md`, `id-lifecycle-policy.md` |
| What materials identify the evidence chain? | `material-passport.md`, `research-materials-index.md` |
| What experiments support the thesis? | `experiment-registry.md`, `experiment-runbook.md` |
| What benchmark comparison is defensible? | `benchmark-report-schema.md`, `experiment-reports/` |
| What data backs the results? | `data-availability.md` |
| What citations support each section? | `section-citation-map.md`, `citation-provenance.md`, `literature-matrix.md` |
| What citation candidates can be confirmed locally? | `section-citation-suggestions.md` |
| What literature candidates need screening? | `zotero-screening-loop.md`, `zotero-collection-coverage.md` |
| What citation search task should run next? | `deep-research-tasks.md`, `section-research-packets/` |
| What changed versus baseline? | `experiment-reports/` |
| What figures are final? | `figure-plan.md`, `diagram-replica-tasks.md`, `network-architecture-figures.md` |
| What must move to the laptop? | `final-artifact-manifest.md` |
| What final handoff package was verified? | `final-handoff-verify-report.md`, `handoff-packages/` |
| What did the dashboard edit? | `workflow-edit-log.md` |
| Is this ready for advisor or final review? | `final-audit.md` |

## Flow Editor

The Dashboard flow editor is a convenience layer over Markdown source files. It can:

- update the current stage, blocker, next action, and audit tier in this file;
- add `CLM-*` rows to `claim-evidence-map.md`;
- add `EXP-*` rows to `experiment-registry.md`;
- add `MAT-*` rows to `material-passport.md`;
- add `CIT-*` rows to `citation-provenance.md`;
- add final artifact rows to `final-artifact-manifest.md`;
- update important ID lifecycle rows in `id-lifecycle-policy.md`.

Every write creates a backup under `tmp/dashboard-edits/backups/` and appends `workflow-edit-log.md`.
