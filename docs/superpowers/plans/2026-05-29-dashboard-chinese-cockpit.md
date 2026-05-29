# Dashboard Chinese Cockpit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert `dashboard-web` into a Chinese research cockpit that foregrounds current stage, blockers, next action, and common operations.

**Architecture:** Keep the existing React + Vite frontend, generated JSON data contract, and local control server. Implement Chinese label maps and targeted layout/CSS improvements without adding a heavy UI framework or backend.

**Tech Stack:** React, TypeScript, Vite, lucide-react, CSS, existing Python dashboard scripts.

---

## File Structure

- Modify `dashboard-web/src/App.tsx`: Chinese UI labels, localized status helpers, reordered first-screen cockpit blocks, action button labels, table headings, graph labels.
- Modify `dashboard-web/src/mockData.ts`: Chinese fallback data so the page is understandable before data generation.
- Modify `dashboard-web/src/styles.css`: improve readability, action layout, first-screen hierarchy, responsive behavior.
- Modify `docs/thesis/workflow-dashboard.md`: note that the web dashboard is a Chinese cockpit.
- Modify `.gitignore`: ignore `.superpowers/` visual brainstorming artifacts.
- Add `docs/superpowers/specs/2026-05-29-dashboard-chinese-cockpit-design.md`: design record.

### Task 1: Localized UI Labels

**Files:**
- Modify: `dashboard-web/src/App.tsx`
- Modify: `dashboard-web/src/mockData.ts`

- [ ] **Step 1: Add Chinese label maps**

Add maps near the top of `App.tsx`:

```ts
const healthLabels: Record<Health, string> = {
  ok: '健康',
  warning: '需关注',
  blocked: '已阻塞',
};

const statusLabels: Record<string, string> = {
  done: '已完成',
  reviewed: '已复核',
  final: '已定稿',
  supported: '证据支持',
  ok: '正常',
  availability_ready: '数据说明就绪',
  restricted_ready: '受限数据说明就绪',
  blocked: '阻塞',
  invalid: '无效',
  unsupported: '证据不足',
  not_reproducible: '不可复现',
  missing: '缺失',
  pending: '待处理',
  weak: '较弱',
  candidate: '候选',
  completed_unreviewed: '已完成待复核',
  planned: '计划中',
};
```

- [ ] **Step 2: Add a display helper**

Add:

```ts
function displayStatus(value = '', fallback = '待处理') {
  const raw = compact(value, fallback);
  return statusLabels[raw.toLowerCase()] ?? raw;
}
```

- [ ] **Step 3: Update fallback mock data**

Translate `mockData.currentStatus`, stage names, issue text, and fallback summary into Chinese while keeping IDs and file paths unchanged.

- [ ] **Step 4: Build**

Run:

```bash
PATH=/opt/homebrew/bin:$PATH pnpm run build
```

Expected: TypeScript and Vite build pass.

### Task 2: Cockpit First Screen

**Files:**
- Modify: `dashboard-web/src/App.tsx`
- Modify: `dashboard-web/src/styles.css`

- [ ] **Step 1: Update header and status band**

Use Chinese headings:

```tsx
<p className="eyebrow">Research Workflow Kit</p>
<h1>科研工作流总控台</h1>
```

Status band labels:

```tsx
<p className="eyebrow">当前阶段</p>
<span>审计等级</span>
<span>更新时间</span>
```

- [ ] **Step 2: Move action panel immediately after the status band**

Render `<ActionPanel onReload={reloadData} />` before metric cards so operations are visible in the first viewport.

- [ ] **Step 3: Translate metric cards**

Use labels:

```tsx
论点
实验
数据
图表
证据关系
```

- [ ] **Step 4: Update CSS spacing**

Make `.action-panel` part of the first-screen flow and ensure `.action-grid` uses `repeat(3, minmax(0, 1fr))` on desktop, `repeat(2, minmax(0, 1fr))` on medium screens, and one column on mobile.

### Task 3: Actions, Tables, And Graph Labels

**Files:**
- Modify: `dashboard-web/src/App.tsx`
- Modify: `dashboard-web/src/styles.css`

- [ ] **Step 1: Translate action panel**

Use:

```tsx
<h2>一键操作</h2>
刷新控制台
导出证据图谱
快速健康检查
打开控制台源文件
打开深研任务
打开 Zotero 筛选
打开图表任务
打开实验报告
复制启动命令
```

- [ ] **Step 2: Translate issue panels and empty states**

Use:

```tsx
P0 阻塞项
P1 待补项
暂无
```

- [ ] **Step 3: Translate graph title and relation labels**

Add:

```ts
const relationLabels: Record<string, string> = {
  contains_claim: '包含论点',
  supported_by: '由实验支持',
  traces_to: '追溯到数据',
  visualizes: '图表呈现',
  cites: '引用支持',
};
```

Use Chinese labels in SVG edge text while preserving raw IDs in nodes.

- [ ] **Step 4: Translate tables**

Use table titles:

```tsx
论点与证据
数据可用性
```

Column labels:

```tsx
ID, 状态, 实验, 图表, 文献, Hash, 访问条件
```

### Task 4: Verification And Integration

**Files:**
- Modify: `docs/thesis/workflow-dashboard.md`

- [ ] **Step 1: Update dashboard docs**

Add one sentence that the web dashboard is a Chinese local cockpit for daily thesis management.

- [ ] **Step 2: Run frontend data preparation**

Run:

```bash
PATH=/opt/homebrew/bin:$PATH pnpm run prepare:data
```

Expected: `dashboard-data.json`, `evidence-graph.json`, and `evidence-graph.mmd` are generated under ignored paths.

- [ ] **Step 3: Run Python unit tests**

Run:

```bash
.venv/bin/python -m unittest tests.test_research_workflow_scripts -v
```

Expected: all tests pass.

- [ ] **Step 4: Run final frontend build**

Run:

```bash
PATH=/opt/homebrew/bin:$PATH pnpm run build
```

Expected: build passes.

- [ ] **Step 5: Commit and merge**

Run:

```bash
git add .gitignore docs/superpowers docs/thesis/workflow-dashboard.md dashboard-web/src/App.tsx dashboard-web/src/mockData.ts dashboard-web/src/styles.css
git commit -m "feat: localize dashboard cockpit"
git switch main
git merge --ff-only codex/chinese-dashboard-cockpit
git push origin main
```
