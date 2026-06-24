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

It starts a local-only control service on `127.0.0.1:8765` so the page can refresh dashboard data, export the evidence graph, run the quick health check, open whitelisted source files, copy recommended commands, update the current research workspace, generate local citation suggestions, package final artifacts for Windows compatibility review, verify the latest package, and use the flow editor to append standard records.

The web dashboard is organized as a current research workspace instead of a long report page. The first screen answers: current stage, current focus, blocker, next action, P0/P1 evidence gaps, audit tier, latest experiment, and the three most common actions. Lower-frequency views live in tabs: overview, current workspace, literature/citation, experiment loop, evidence graph, final artifact review, record editor, and system health.

`daily-workflow-entry.md` is retained as a legacy-compatible file name. In the web UI and operating language, treat it as the current research workspace record.

The Dashboard also shows plugin gate recommendations from `scripts/plugin_gate_advisor.py`. These recommendations route Codex Security, Build Web Apps, Data Analytics, Product Design, and CodeRabbit checks to the right stage. They are quality gates and review notes; confirmed evidence still lives in Markdown/TSV/JSON source records.

The evidence graph is rendered inside the page from `dashboard-data.json` as an **evidence chain inspector**, not as a full relationship map by default. The default reading path is `SEC/SEG -> CLM -> EXP/DATA/FIG/CIT`: it answers whether each thesis claim has a paper location and traceable supporting evidence. Duplicate relations are collapsed, reverse relations such as `FIG -> CLM` are displayed as `CLM -> FIG`, and evidence-internal links such as `EXP -> DATA` stay hidden in the default view to reduce visual noise. The full-project graph remains available as an advanced view and can still be exported as JSON/Mermaid for draw.io or static review. The section citation view is gap-first: missing strong support, Zotero checks, Reader/Scite checks, and risk rows appear before low-risk rows. It is a triage view only; confirmed citations still need `section-citation-map.md` and `citation-provenance.md` updates.

The Dashboard also includes three convergence aids:

- `console-file-index.md` groups source records into file layers so daily work opens fewer files.
- `project-scope-control.md` keeps a title-first thesis honest: title survival, causal availability, node/structure definition, and downgrade routes are reviewed before experiments and final writing.
- `experiment-reports/` and the experiment comparison panel show baseline -> new metric delta, verify gate, guard gate, and environment snapshot status.
- `weekly-review.md` records what became stronger or weaker, the current best experiment, and only 1-3 next actions.

Use Build Web Data Visualization principles when the dashboard becomes advisor-facing: keep charts simple, show uncertainty or missingness when relevant, make labels readable on desktop/mobile, and do not let visual polish hide unsupported claims.

## Current Status

| Field | Value |
|---|---|
| Current stage | 9 图表与表格生产 |
| Active focus | EXP-103 至 EXP-106 结果已冻结，进入论文图表生产与实验章节落稿 |
| Current audit tier | quick |
| Main blocker | 无 P0；剩余工作是图表风格 QA、论文图表生成、实验章节落稿和后续终稿兼容性检查。 |
| Next concrete action | 按 Stage 9 图表契约流程生成论文图表：先冻结每张图的结论、来源和图注口径，再用 Image Gen 生成方法图视觉母稿，经过内容准确性质检后用 draw.io 正式重绘；数据结果图由 Python/SVG/PDF 可复现生成。 |
| Last dashboard refresh | 2026-06-23T16:41:42 |

## Stage Snapshot

| Stage | Name | Status | Main Record | Notes |
|---|---|---|---|---|
| 1 | Paper planning | done | `topic-intake.md`, `thesis-brief.md`, `project-scope-control.md`, `writing-outline.md` | DOCX mother plan imported; fixed title is a draft hypothesis |
| 2 | Literature discovery and review | done_for_stage_gate | `academic-search-policy.md`, `literature-matrix.md`, `zotero-literature-hub.md`, `section-citation-map.md`, `citation-provenance.md`, `core-literature-shortlist-and-review-structure.md` | 100-paper pool and 34-paper core shortlist complete; full source readers continue in parallel |
| 3 | Experiment question definition | done_for_stage_gate | `experiment-question-definition.md`, `claim-evidence-map.md`, `experiment-registry.md`, `data-availability.md`, `metric-diagnostics.md` | Q1-Q5, H1-H5, CLM-101..CLM-106, EXP-101..EXP-106, DATA-101..DATA-104 defined |
| 4 | Experiment architecture planning | done_for_stage_gate | `experiment-architecture.md`, `experiment-runbook.md`, `benchmark-report-schema.md`, `reproducibility-checklist.md`, `project-scope-control.md` | Data route, causal field audit, node definition, `A_event,t` construction, DTW/adaptive/destroyed graph baselines, metrics, outputs, and downgrade rules are specified |
| 5 | Research code implementation | done_for_stage_gate | `src/`, `configs/`, `tests/`, `experiment-registry.md` | EXP-101..EXP-106 scripts/configs implemented; V6 event-triggered correction, interval calibration, capacity-risk proxy, and robustness guard scripts are available |
| 6 | Experiment run and monitoring | done_for_stage_gate | `experiment-runbook.md`, `outputs/`, remote AutoDL archives | Formal EXP-103..EXP-106 runs completed on AutoDL clones with logs, manifests, and copied lightweight outputs |
| 7 | Experiment recording and result scan | done_for_stage_gate | `experiment-registry.md`, `metric-diagnostics.md`, `benchmark-report-schema.md`, `experiment-reports/` | EXP-103 V6, EXP-104 interval calibration, EXP-105 capacity-risk proxy, and EXP-106 robustness decisions recorded |
| 8 | Results analysis and claim mapping | done_for_stage_gate | `claim-evidence-map.md`, `project-scope-control.md`, `data-availability.md`, `experiment-reports/frozen-experiment-result-tables.md` | Main claim reframed as event-triggered forecast correction; frozen result tables and caveat wording are established |
| 9 | Figure and table production | in_progress | `figure-plan.md`, `figure-style-qa.md`, `diagram-replica-tasks.md`, `experiment-reports/frozen-experiment-result-tables.md` | Current focus: use figure contracts, Image Gen visual mother drafts, draw.io formal redraw, Python result plots, and figure QA to turn frozen EXP-103..EXP-106 tables into manuscript-ready figures, tables, captions, and experiment-section text |
| 10 | Paper writing and polishing | pending | `writing-outline.md`, `project-scope-control.md` | Lock title only when chapters and evidence support it |
| 11 | Mac DOCX / PDF / PPTX main production | pending | `final-artifact-manifest.md`, DOCX/PDF/PPTX artifacts | Mac produces the main thesis document, PDF candidate, and PPTX candidate |
| 12 | Windows compatibility review and final submission preparation | pending | `final-audit.md`, `defense-prep.md`, `final-artifact-manifest.md` | Windows laptop verifies Word/WPS/PowerPoint compatibility and final submission readiness |

## Health Summary

<!-- workflow-doctor:start -->
Generated: 2026-06-23T16:45:33

**Workflow Health:** `warning`

### Counts

- claims=7 experiments=7 datasets=5 figures=4 sections=4

### P0 Blockers

- none

### P1 Issues

- figure style QA checklist still has pending checklist items
- Nature-style writing checklist still has pending checklist items
- thesis-docx is still pending Windows compatibility review
- thesis-docx is missing checksum
- final-pdf is still pending Windows compatibility review
- final-pdf is missing checksum
- defense-pptx is still pending Windows compatibility review
- defense-pptx is missing checksum
- unknown ID prefix or unmanaged ID: TBL-101
- unknown ID prefix or unmanaged ID: TBL-103
- unknown ID prefix or unmanaged ID: TBL-103-
- unknown ID prefix or unmanaged ID: TBL-106
- unknown ID prefix or unmanaged ID: TBL-106-
- project scope control still has pending title, causal, node, or downgrade decisions
- plugin gate pending: Product Design for stage 9 -> docs/thesis/visual-design-review.md

### Recent Experiment Candidates

- EXP-102
- EXP-103
- EXP-104
- EXP-105
- EXP-106
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
| 更新当前科研工作区 | Dashboard `当前工作区` or `python scripts/update_daily_workflow.py --stage "2 文献发现与综述" --next-action "..."` | `daily-workflow-entry.md`, `workflow-dashboard.md`, `workflow-edit-log.md` |
| 查看文件分层 | Dashboard `文件分层` or `console-file-index.md` | lower-noise source-file map |
| 更新每周复盘 | Dashboard `每周复盘` or `python scripts/update_weekly_review.py --focus "..." --next-actions "..."` | `weekly-review.md`, `workflow-edit-log.md` |
| 刷新控制台数据 | `刷新控制台` or `python scripts/research_workflow_doctor.py --write-dashboard --write-data` | `workflow-dashboard.md`, `dashboard-data.json` |
| 检查证据链 | Dashboard `证据图谱` / `#graph` | default `SEC/SEG -> CLM -> EXP/DATA/FIG/CIT` evidence chain inspector |
| 导出完整证据图谱 | `导出证据图谱` or `python scripts/export_evidence_graph.py` | `evidence-graph.json`, `evidence-graph.mmd` |
| 快速健康检查 | `快速健康检查` or `python scripts/research_workflow_doctor.py --warn-only` | P0/P1 console report |
| 创建深研任务 | `python scripts/new_deep_research_task.py --section-id SEC-INTRO-001 --topic "..."` | `deep-research-tasks.md`, section packet |
| 生成本地引用推荐 | Dashboard `引用推荐` or `python scripts/suggest_section_citations.py --section-id SEC-INTRO-001` | `section-citation-suggestions.md`, optional dashboard JSON |
| 查看章节引用覆盖 | Dashboard `文献引用` tab | `section-citation-map.md`, `citation-provenance.md`, `section-citation-suggestions.md` |
| 生成 Zotero inventory 快照 | Dashboard `Zotero 文献中枢` or `python scripts/sync_zotero_inventory.py` | `zotero-literature-hub.md` |
| 审计 Zotero 覆盖 | Dashboard `Zotero 文献中枢` or `python scripts/audit_zotero_coverage.py --warn-only` | section-level Zotero coverage warning list |
| 导出 BibTeX 草稿 | Dashboard `Zotero 文献中枢` or `python scripts/export_zotero_bibliography.py --allow-stub --out references.bib` | `references.bib` review stub or Zotero helper export |
| 查看局部证据链 / 全项目图谱 | Dashboard `证据图谱` tab | `dashboard-data.json`, `evidence-graph.json`, `evidence-graph.mmd` |
| 创建实验报告 | `python scripts/new_experiment_report.py --experiment-id EXP-001 --baseline EXP-000` | `experiment-reports/EXP-001.md` |
| 检查材料护照 | `打开材料护照` | `material-passport.md` |
| 检查引用溯源 | `打开引用溯源` | `citation-provenance.md` |
| 检查 Zotero 覆盖 | `打开文献覆盖` | `zotero-collection-coverage.md` |
| 检查 benchmark 规范 | `打开 Benchmark` | `benchmark-report-schema.md` |
| 审计 skills | `python scripts/audit_skills.py --warn-only --write-report` | `skill-audit-report.md` |
| 可视化质量检查 | Build Web Data Visualization checklist | readable charts, visible uncertainty, accessible contrast, no hidden evidence gaps |
| 使用流程编辑器新增记录 | Dashboard `流程编辑器` | `claim-evidence-map.md`, `experiment-registry.md`, `material-passport.md`, `citation-provenance.md`, `final-artifact-manifest.md` |
| 审计最终交付物 | `python scripts/audit_final_artifacts.py --tier quick --warn-only` | stage 11-12 handoff risk list |
| 打包终稿验收文件 | Dashboard `终稿验收` or `python scripts/package_final_handoff.py --update-manifest-checksums` | `handoff-packages/final-handoff-*/` zip, manifest, checksum, summary |
| 校验终稿验收文件 | Dashboard `校验最新包` or `python scripts/verify_final_handoff.py --latest --write-report docs/thesis/final-handoff-verify-report.md` | `final-handoff-verify-report.md` |
| 审计 ID 生命周期 | `python scripts/audit_id_lifecycle.py --warn-only` | orphan, unknown, deprecated, or weakly linked ID warnings |
| 查看插件门禁建议 | Dashboard `插件建议` or `python scripts/plugin_gate_advisor.py` | recommended / required plugin checks |
| 审计插件门禁配置 | `python scripts/plugin_gate_advisor.py --audit-only` | policy/log presence and current recommendations |

## Quick Navigation

| Need | File |
|---|---|
| What should happen next? | `workflow-dashboard.md`, `task-board-sync.md` |
| Which files should I open now? | `console-file-index.md` |
| What changed this week? | `weekly-review.md` |
| What claims are safe? | `claim-evidence-map.md`, `evidence-promotion-policy.md`, `id-lifecycle-policy.md` |
| What materials identify the evidence chain? | `material-passport.md`, `research-materials-index.md` |
| What experiments support the thesis? | `experiment-architecture.md`, `experiment-registry.md`, `experiment-runbook.md` |
| Where are full experiment artifacts stored? | `experiment-registry.md` remote artifact fields, `outputs/EXP-*/manifest.json` |
| What benchmark comparison is defensible? | `benchmark-report-schema.md`, `experiment-reports/` |
| What data backs the results? | `data-availability.md` |
| What citations support each section? | `section-citation-map.md`, `citation-provenance.md`, `literature-matrix.md` |
| What citation candidates can be confirmed locally? | `section-citation-suggestions.md` |
| What literature candidates need screening? | `zotero-literature-hub.md`, `zotero-screening-loop.md`, `zotero-collection-coverage.md` |
| What citation search task should run next? | `deep-research-tasks.md`, `section-research-packets/` |
| What changed versus baseline? | `experiment-reports/` |
| What figures are final? | `figure-plan.md`, `diagram-replica-tasks.md`, `network-architecture-figures.md` |
| What Mac-produced final candidates need Windows compatibility review? | `final-artifact-manifest.md` |
| What final artifact package was verified? | `final-handoff-verify-report.md`, `handoff-packages/` |
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
