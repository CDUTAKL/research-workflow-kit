# Dashboard Chinese Cockpit Design

## Goal

Turn `dashboard-web` from an English status board into a Chinese research cockpit for daily thesis management.

The first screen should answer three questions within a few seconds:

- 当前推进到哪一步？
- 现在有什么阻塞或待补证据？
- 下一步应该点哪里或打开哪个文件？

## Selected Direction

Use option B: 中文任务驾驶舱.

This keeps the current lightweight architecture while improving readability and operation flow. It does not introduce a backend database, account system, heavy UI framework, or cloud dependency.

## Product Principles

- Put current status, blockers, next action, and common actions in the first viewport.
- Use Chinese interface text for everyday reading.
- Keep technical IDs in English, such as `SEC-*`, `CLM-*`, `EXP-*`, `DATA-*`, and `FIG-*`, because they are search and audit keys.
- Keep operation buttons close to the state they affect.
- Use restrained, work-focused styling: dense but readable, card radius at 8px or less, clear spacing, no decorative landing-page layout.
- Use color only for status and category signals.

## Information Architecture

The dashboard will keep one page, ordered as:

1. Header: 科研工作流总控台, health badge, data source badge.
2. Hero status band: 当前阶段, 下一步行动, 审计等级, 更新时间.
3. Quick action panel: 刷新控制台, 导出证据图谱, 快速健康检查, open source files, copy command.
4. Metric cards: 论点, 实验, 数据, 图表, 证据关系.
5. Blockers: P0 阻塞项 and P1 待补项.
6. 12-stage progress: Chinese stage names with record file paths.
7. Evidence and experiments: evidence graph, recent experiments, experiment loop, skill health.
8. Record tables: claim/evidence and data availability tables.

## Chinese Terminology

- Claim -> 论点
- Evidence -> 证据
- Experiment -> 实验
- Data Availability -> 数据可用性
- Figure -> 图表
- Evidence Graph -> 证据图谱
- Health Check -> 健康检查
- Audit Tier -> 审计等级
- Blocker -> 阻塞项
- Issue -> 待补项

The UI can show both Chinese and ID terms when useful, for example `论点 CLM-*`.

## Architecture

Keep the current structure:

- React + Vite frontend in `dashboard-web/`.
- Static generated JSON from `dashboard-web/public/data/dashboard-data.json`.
- Local-only control server in `scripts/dashboard_control_server.py`.
- Markdown source files remain the source of truth under `docs/thesis/`.

Targeted frontend changes:

- Add small label maps for health, status, current-status keys, stage names, table headings, action names, graph relation names, and fallback messages.
- Keep the existing `DashboardData` shape so scripts do not need a data migration.
- Improve layout using the existing CSS file rather than adding a large component library.

## Safety And Compatibility

- Preserve all API endpoints.
- Preserve dashboard generated data schema.
- Do not commit generated `dist/` or `public/data/`.
- Keep localhost control actions restricted to whitelisted paths.
- `.superpowers/` visual brainstorming artifacts are ignored by git.

## Verification

- `pnpm run build`
- `pnpm run prepare:data`
- Python unit tests for dashboard control server and workflow scripts
- Visual check in browser on desktop and narrow widths
