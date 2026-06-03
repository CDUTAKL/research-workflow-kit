import { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Bell,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  CircleAlert,
  Database,
  ExternalLink,
  FileText,
  FlaskConical,
  Folder,
  GitBranch,
  Layers3,
  ListChecks,
  RefreshCw,
  Save,
  Search,
  Terminal,
  User,
} from 'lucide-react';
import { postAction } from './api/client';
import { DashboardTabs, type DashboardTab } from './components/DashboardTabs';
import { InteractiveEvidenceGraph } from './components/InteractiveEvidenceGraph';
import { PluginGatePanel } from './components/PluginGatePanel';
import { SectionCitationHeatmap } from './components/SectionCitationHeatmap';
import { SystemHealthPanel } from './components/SystemHealthPanel';
import { CurrentWorkspace } from './components/TodayWorkspace';
import { demoFallbackData } from './mockData';
import type { CitationSuggestion, DashboardData, EvidenceEdge, EvidenceNode, ExperimentComparison, Health, StageWorkspace, WorkflowRecord } from './types';

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

const stageNameLabels: Record<string, string> = {
  'Paper planning': '论文规划',
  'Literature discovery and review': '文献发现与综述',
  'Experiment question definition': '实验问题定义',
  'Experiment architecture planning': '实验架构规划',
  'Research code implementation': '科研代码实现',
  'Experiment run and monitoring': '实验运行与监控',
  'Experiment recording and result scan': '实验记录与结果扫描',
  'Results analysis and claim mapping': '结果分析与论点映射',
  'Figure and table production': '图表与模型结构图制作',
  'Paper writing and polishing': '论文写作与润色',
  'Laptop DOCX / optional LaTeX / PDF': '笔记本 DOCX / 可选 LaTeX / PDF',
  'Laptop DOCX / PDF production': '笔记本 DOCX / PDF 生产',
  'Laptop final audit and defense': '笔记本终审与答辩准备',
  'Final audit and defense': '终审与答辩准备',
  'Select a stage': '选择阶段',
};

const relationLabels: Record<string, string> = {
  contains_claim: '包含论点',
  supported_by: '由实验支持',
  traces_to: '追溯到数据',
  visualizes: '图表呈现',
  cites: '引用支持',
};

const auditTierLabels: Record<string, string> = {
  quick: '快速审计',
  advisor: '导师审计',
  final: '终审',
  TBD: '待填写',
};

const kindOrder = ['SEC', 'CLM', 'EXP', 'DATA', 'FIG'];
const kindColor: Record<string, string> = {
  SEC: '#2563eb',
  CLM: '#0f766e',
  EXP: '#7c3aed',
  DATA: '#b45309',
  FIG: '#be123c',
};

function statusClass(value = '') {
  const normalized = value.toLowerCase();
  if (['done', 'reviewed', 'final', 'supported', 'ok', 'availability_ready', 'restricted_ready'].includes(normalized)) {
    return 'is-ok';
  }
  if (['blocked', 'invalid', 'unsupported', 'not_reproducible'].includes(normalized)) {
    return 'is-blocked';
  }
  if (['missing', 'pending', 'weak', 'candidate', 'completed_unreviewed'].includes(normalized)) {
    return 'is-warning';
  }
  return 'is-neutral';
}

function compact(value = '', fallback = 'TBD') {
  const text = value.replace(/`/g, '').trim();
  return text || fallback;
}

function displayStatus(value = '', fallback = '待处理') {
  const raw = compact(value, fallback);
  return statusLabels[raw.toLowerCase()] ?? raw.replace(/TBD/g, '待填写');
}

function displayText(value = '', fallback = '待填写') {
  return compact(value, fallback).replace(/TBD/g, '待填写');
}

function displayStageName(value = '') {
  return stageNameLabels[value] ?? displayText(value);
}

function displayAuditTier(value = '') {
  return compact(value, 'TBD')
    .split('/')
    .map((part) => auditTierLabels[part] ?? part.replace(/TBD/g, '待填写'))
    .join(' / ');
}

function displayRelation(value = '') {
  return relationLabels[value] ?? value;
}

function displayIssue(value = '') {
  const text = displayText(value);
  const replacements: Array<[RegExp, string]> = [
    [/^missing console file: (.+)$/i, '缺少控制台文件：$1'],
    [/^(.+) is marked supported but has no structured evidence ID$/i, '$1 标记为已支持，但缺少结构化证据 ID'],
    [/^(.+) has no experiment, figure, data, section, or literature evidence$/i, '$1 缺少实验、图表、数据、章节或文献证据'],
    [/^(.+) is (done|reviewed) but has no output path$/i, '$1 已完成或已复核，但缺少输出路径'],
    [/^(.+) is a formal 4060 run but missing (.+)$/i, '$1 是正式 4060 实验，但缺少 $2'],
    [/^(.+) is reviewed but missing hash\/manifest$/i, '$1 已复核，但缺少 hash 或 manifest'],
    [/^(.+) is reviewed but missing access level$/i, '$1 已复核，但缺少访问条件说明'],
    [/^(.+) is final but has no linked claim\/data\/experiment ID$/i, '$1 已定稿，但没有关联论点、数据或实验 ID'],
    [/^(.+) has missing section citation coverage$/i, '$1 章节引用覆盖不足'],
  ];
  for (const [pattern, replacement] of replacements) {
    if (pattern.test(text)) return text.replace(pattern, replacement);
  }
  return text;
}

function MetricCard({
  label,
  value,
  icon,
  accent,
}: {
  label: string;
  value: number | string;
  icon: JSX.Element;
  accent: string;
}) {
  return (
    <section className="metric-card" style={{ '--accent': accent } as React.CSSProperties}>
      <div className="metric-icon">{icon}</div>
      <div>
        <div className="metric-value">{value}</div>
        <div className="metric-label">{label}</div>
      </div>
    </section>
  );
}

function CockpitTopBar({ loadedFromFile }: { loadedFromFile: boolean }) {
  return (
    <header className="cockpit-topbar">
      <div className="traffic-dots" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
      <strong>医学研究工作流 · 本地研究驾驶舱</strong>
      <label className="top-search">
        <Search size={15} />
        <input value="" readOnly placeholder="搜索（⌘F）" aria-label="搜索" />
      </label>
      <button type="button" className="icon-button" aria-label="通知">
        <Bell size={17} />
      </button>
      <div className="avatar-chip" aria-label="当前用户">
        <User size={16} />
      </div>
      <span className={`data-source ${loadedFromFile ? 'is-ok' : 'is-warning'}`}>
        {loadedFromFile ? '实时数据' : '示例数据'}
      </span>
    </header>
  );
}

function KpiStrip({ data }: { data: DashboardData }) {
  const citationSummary = data.citationCoverageSummary;
  const totalCitationSections = (citationSummary?.missingStrong ?? 0) + (citationSummary?.candidate ?? 0) + (citationSummary?.verified ?? 0) + (citationSummary?.risk ?? 0);
  const citationRate = totalCitationSections > 0 ? `${Math.round(((citationSummary?.verified ?? 0) / totalCitationSections) * 100)}%` : '待填写';
  const items = [
    { label: '论点总数', value: data.counts.claims, sub: 'CLM 记录', icon: <FileText size={26} />, accent: '#2563eb' },
    { label: '实验记录', value: data.counts.experiments, sub: 'EXP 运行', icon: <FlaskConical size={26} />, accent: '#0ea5e9' },
    { label: '数据条目', value: data.counts.datasets, sub: 'DATA 可追踪', icon: <Database size={26} />, accent: '#14b8a6' },
    { label: '图表产物', value: data.counts.figures, sub: 'FIG / PPTX / SVG', icon: <BarChart3 size={26} />, accent: '#7c3aed' },
    { label: '引用覆盖率', value: citationRate, sub: `${data.citationCoverageSummary?.verified ?? 0} 个已验证`, icon: <BookOpen size={26} />, accent: '#06b6d4' },
    { label: '待补证据', value: data.issues.p0.length + data.issues.p1.length, sub: `${data.issues.p0.length} P0 / ${data.issues.p1.length} P1`, icon: <AlertTriangle size={26} />, accent: '#f59e0b' },
  ];

  return (
    <section className="kpi-strip" aria-label="科研项目指标总览">
      {items.map((item) => (
        <article className="kpi-item" style={{ '--accent': item.accent } as React.CSSProperties} key={item.label}>
          <div className="kpi-icon">{item.icon}</div>
          <div>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
            <p>{item.sub}</p>
          </div>
        </article>
      ))}
    </section>
  );
}

function ProjectHero({ data, loadedFromFile, onReload }: { data: DashboardData; loadedFromFile: boolean; onReload: () => void }) {
  const focus = displayText(data.currentWorkspaceSummary?.focus ?? data.currentStatus['Active focus'], '请先填写当前研究项目');
  return (
    <section className="project-hero">
      <div>
        <h1>上午好，AI小A</h1>
        <p>当前研究项目：{focus}</p>
      </div>
      <div className="hero-actions">
        <button type="button" className="hero-primary" onClick={() => postAction('/api/open-path', { key: 'dashboard' })}>
          新建项目 <ArrowRight size={15} />
        </button>
        <button type="button" onClick={() => postAction('/api/open-path', { key: 'sectionCitationMap' })}>
          导入文献
        </button>
        <span>最后更新：{loadedFromFile ? displayText(data.generatedAt) : '示例数据'}</span>
        <button type="button" className="icon-button" onClick={onReload} aria-label="刷新数据">
          <RefreshCw size={17} />
        </button>
      </div>
      <KpiStrip data={data} />
    </section>
  );
}

function ActionPanel({ onReload }: { onReload: () => void }) {
  const [message, setMessage] = useState('本地控制服务使用 http://127.0.0.1:8765，只在本机访问');
  const [busy, setBusy] = useState<string | null>(null);
  const [showMore, setShowMore] = useState(false);

  async function run(label: string, action: () => Promise<unknown>, reload = false) {
    setBusy(label);
    try {
      const result = await action();
      setMessage(typeof result === 'object' && result && 'output' in result ? String((result as { output?: string }).output || '已完成') : '已完成');
      if (reload) onReload();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(null);
    }
  }

  const nextCommand = './scripts/open_dashboard.sh';

  return (
    <section className="panel action-panel">
      <div className="panel-title-row">
        <Terminal size={18} />
        <h2>常用操作</h2>
      </div>
      <div className="action-grid">
        <button onClick={() => run('refresh', () => postAction('/api/refresh-dashboard'), true)} disabled={Boolean(busy)}>
          <RefreshCw size={16} /> 刷新检查
        </button>
        <button onClick={() => run('doctor', () => postAction('/api/run-doctor'))} disabled={Boolean(busy)}>
          <Activity size={16} /> 快速健康检查
        </button>
        <button onClick={() => run('open', () => postAction('/api/open-path', { key: 'dashboard' }))} disabled={Boolean(busy)}>
          <ExternalLink size={16} /> 打开控制台源文件
        </button>
      </div>
      <button className="subtle-toggle" type="button" onClick={() => setShowMore((value) => !value)}>
        {showMore ? '收起更多文件' : '展开更多文件与命令'}
      </button>
      {showMore ? <div className="action-grid secondary-action-grid">
        <button onClick={() => run('graph', () => postAction('/api/export-evidence-graph'), true)} disabled={Boolean(busy)}>
          <GitBranch size={16} /> 导出证据图谱
        </button>
        <button onClick={() => run('tasks', () => postAction('/api/open-path', { key: 'deepResearchTasks' }))} disabled={Boolean(busy)}>
          <BookOpen size={16} /> 打开深研任务
        </button>
        <button onClick={() => run('zotero', () => postAction('/api/open-path', { key: 'zoteroScreeningLoop' }))} disabled={Boolean(busy)}>
          <BookOpen size={16} /> 打开 Zotero 筛选
        </button>
        <button onClick={() => run('coverage', () => postAction('/api/open-path', { key: 'zoteroCollectionCoverage' }))} disabled={Boolean(busy)}>
          <BookOpen size={16} /> 打开文献覆盖
        </button>
        <button onClick={() => run('citation', () => postAction('/api/open-path', { key: 'citationProvenance' }))} disabled={Boolean(busy)}>
          <BookOpen size={16} /> 打开引用溯源
        </button>
        <button onClick={() => run('material', () => postAction('/api/open-path', { key: 'materialPassport' }))} disabled={Boolean(busy)}>
          <Database size={16} /> 打开材料护照
        </button>
        <button onClick={() => run('artifacts', () => postAction('/api/open-path', { key: 'finalArtifactManifest' }))} disabled={Boolean(busy)}>
          <FileText size={16} /> 打开交付清单
        </button>
        <button onClick={() => run('ids', () => postAction('/api/open-path', { key: 'idLifecyclePolicy' }))} disabled={Boolean(busy)}>
          <ListChecks size={16} /> 打开 ID 规则
        </button>
        <button onClick={() => run('editlog', () => postAction('/api/open-path', { key: 'workflowEditLog' }))} disabled={Boolean(busy)}>
          <FileText size={16} /> 打开写入日志
        </button>
        <button onClick={() => run('benchmark', () => postAction('/api/open-path', { key: 'benchmarkReportSchema' }))} disabled={Boolean(busy)}>
          <FlaskConical size={16} /> 打开 Benchmark
        </button>
        <button onClick={() => run('diagrams', () => postAction('/api/open-path', { key: 'diagramReplicaTasks' }))} disabled={Boolean(busy)}>
          <ExternalLink size={16} /> 打开图表任务
        </button>
        <button onClick={() => run('reports', () => postAction('/api/open-path', { key: 'experimentReports' }))} disabled={Boolean(busy)}>
          <FlaskConical size={16} /> 打开实验报告
        </button>
        <button onClick={() => navigator.clipboard.writeText(nextCommand).then(() => setMessage(`已复制：${nextCommand}`))} disabled={Boolean(busy)}>
          <FileText size={16} /> 复制启动命令
        </button>
      </div> : null}
      <pre className="action-output">{busy ? `正在执行 ${busy}...` : message}</pre>
    </section>
  );
}

function StageWorkspacePanel({ workspace, links, onReload }: { workspace?: StageWorkspace; links: Record<string, string>; onReload: () => void }) {
  const [message, setMessage] = useState('记录当前目标、阻塞项和下一步，会写入兼容文件 daily-workflow-entry.md');
  const [busy, setBusy] = useState(false);
  const [fields, setFields] = useState<Record<string, string>>({
    stage: workspace?.stage ? `${workspace.stage} ${workspace.name}` : '',
    focus: '',
    blocker: '',
    next_action: '',
    done_note: '',
  });

  async function saveDaily() {
    setBusy(true);
    try {
      const result = await postAction('/api/daily-workflow/update', { fields });
      setMessage(result.output ?? '当前科研工作区已更新');
      onReload();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  const active = workspace ?? {
    stage: '',
    name: '选择阶段',
    fileKeys: ['dashboard', 'dailyWorkflowEntry'],
    commands: ['python scripts/research_workflow_doctor.py --warn-only'],
    recommendedActions: ['设置当前阶段后，这里会显示本阶段推荐动作。'],
    issues: { p0: [], p1: [] },
  };

  return (
    <section className="panel workspace-panel">
      <div className="panel-title-row">
        <ListChecks size={18} />
        <h2>当前科研工作区</h2>
      </div>
      <div className="workspace-grid">
        <div className="workspace-main">
          <p className="eyebrow">当前阶段</p>
          <h3>{active.stage ? `${active.stage}. ${displayStageName(active.name)}` : displayStageName(active.name)}</h3>
          <div className="workspace-actions">
            {active.recommendedActions.map((action) => <div className="issue-item" key={action}>{displayText(action)}</div>)}
          </div>
          <div className="workspace-files">
            {active.fileKeys.map((key) => (
              <button key={key} onClick={() => postAction('/api/open-path', { key }).catch((error) => setMessage(error instanceof Error ? error.message : String(error)))}>
                <ExternalLink size={15} /> {links[key] ?? key}
              </button>
            ))}
          </div>
        </div>
        <div className="workspace-side">
          <label className="form-field">
            <span>当前阶段</span>
            <input value={fields.stage} placeholder="例如：2 文献发现与综述" onChange={(event) => setFields((current) => ({ ...current, stage: event.target.value }))} />
          </label>
          <label className="form-field">
            <span>当前目标</span>
            <input value={fields.focus} placeholder="当前主要推进什么" onChange={(event) => setFields((current) => ({ ...current, focus: event.target.value }))} />
          </label>
          <label className="form-field">
            <span>阻塞项</span>
            <input value={fields.blocker} placeholder="没有就留空" onChange={(event) => setFields((current) => ({ ...current, blocker: event.target.value }))} />
          </label>
          <label className="form-field">
            <span>下一步动作</span>
            <textarea value={fields.next_action} placeholder="下一步具体做什么" onChange={(event) => setFields((current) => ({ ...current, next_action: event.target.value }))} />
          </label>
          <label className="form-field">
            <span>完成记录</span>
            <input value={fields.done_note} placeholder="刚完成了什么" onChange={(event) => setFields((current) => ({ ...current, done_note: event.target.value }))} />
          </label>
          <button className="primary-button" onClick={saveDaily} disabled={busy}><Save size={16} /> 保存当前记录</button>
          <pre className="action-output compact-output">{busy ? '正在写入...' : message}</pre>
        </div>
      </div>
      <div className="workspace-command-row">
        {active.commands.map((command) => (
          <button key={command} onClick={() => navigator.clipboard.writeText(command).then(() => setMessage(`已复制：${command}`))}>
            <Terminal size={15} /> {command}
          </button>
        ))}
      </div>
    </section>
  );
}

function CitationSuggestionPanel({ suggestions, onReload }: { suggestions: CitationSuggestion[]; onReload: () => void }) {
  const [sectionId, setSectionId] = useState('');
  const [message, setMessage] = useState('基于已有文献、Zotero、章节表和深研任务包做离线排序，不自动写入正式引用。');
  const [busy, setBusy] = useState(false);

  async function runSuggestions() {
    setBusy(true);
    try {
      const result = await postAction('/api/suggest-section-citations', { section_id: sectionId });
      setMessage(result.output ?? '引用推荐已生成');
      onReload();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel citation-panel">
      <div className="panel-title-row">
        <BookOpen size={18} />
        <h2>引用推荐</h2>
      </div>
      <div className="inline-form">
        <input value={sectionId} placeholder="SEC-INTRO-001，可留空生成全部" onChange={(event) => setSectionId(event.target.value)} />
        <button onClick={runSuggestions} disabled={busy}><RefreshCw size={16} /> 生成推荐</button>
        <button onClick={() => postAction('/api/open-path', { key: 'sectionCitationSuggestions' }).catch((error) => setMessage(error instanceof Error ? error.message : String(error)))} disabled={busy}>
          <ExternalLink size={16} /> 打开推荐表
        </button>
      </div>
      <pre className="action-output compact-output">{busy ? '正在生成...' : message}</pre>
      <div className="suggestion-list">
        {suggestions.length ? suggestions.slice(0, 5).map((item) => (
          <article className="suggestion-row" key={`${item.rank}-${item.sectionId}-${item.candidateReference}`}>
            <div>
              <strong>{item.candidateReference}</strong>
              <span>{displayText(item.sectionId)} / {displayText(item.segmentId)} / {displayText(item.identifier)}</span>
            </div>
            <div className="suggestion-meta">
              <span className="status-pill is-ok">分数 {item.score}</span>
              <span>{displayText(item.suggestedUse)}</span>
            </div>
          </article>
        )) : <div className="empty-state">暂无推荐，请先生成或补充本地文献记录</div>}
      </div>
    </section>
  );
}

function HandoffPanel({ data, onReload }: { data: DashboardData; onReload: () => void }) {
  const [message, setMessage] = useState('只打包 final-artifact-manifest.md 中登记且未 blocked 的文件。');
  const [busy, setBusy] = useState<string | null>(null);
  async function run(label: string, endpoint: string) {
    setBusy(label);
    try {
      const result = await postAction(endpoint);
      setMessage(result.output ?? '已完成');
      onReload();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(null);
    }
  }
  const artifacts = data.finalArtifacts ?? [];
  const counts = artifacts.reduce<Record<string, number>>((acc, item) => {
    const status = (item.status ?? 'pending').toLowerCase();
    acc[status] = (acc[status] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <section className="panel handoff-panel">
      <div className="panel-title-row">
        <FileText size={18} />
        <h2>最终交接</h2>
      </div>
      <div className="handoff-counts">
        {['pending', 'copied', 'verified', 'blocked'].map((key) => (
          <div key={key}><strong>{counts[key] ?? 0}</strong><span>{displayStatus(key)}</span></div>
        ))}
      </div>
      <div className="handoff-actions">
        <button onClick={() => run('package', '/api/package-final-handoff')} disabled={Boolean(busy)}><Save size={16} /> 打包交接包</button>
        <button onClick={() => run('verify', '/api/verify-final-handoff')} disabled={Boolean(busy)}><CheckCircle2 size={16} /> 校验最新包</button>
        <button onClick={() => postAction('/api/open-path', { key: 'finalArtifactManifest' }).catch((error) => setMessage(error instanceof Error ? error.message : String(error)))} disabled={Boolean(busy)}>
          <ExternalLink size={16} /> 打开交接清单
        </button>
      </div>
      <pre className="action-output compact-output">{busy ? `正在执行 ${busy}...` : message}</pre>
      <div className="handoff-latest">
        <span>最新包</span>
        <code>{displayText(data.handoffPackage?.latestZip ?? '', '尚未打包')}</code>
      </div>
    </section>
  );
}

function ConsoleFileLayerPanel({ data }: { data: DashboardData }) {
  const layers = data.consoleFileLayers ?? [];
  return (
    <section className="panel console-layer-panel">
      <div className="panel-title-row">
        <ListChecks size={18} />
        <h2>文件分层</h2>
      </div>
      <p className="panel-note">只打开当前任务需要的文件，避免控制台文件太多带来的认知负担。</p>
      <div className="console-layer-list">
        {layers.length ? layers.map((item) => (
          <article className="console-layer-row" key={item.layer}>
            <strong>{item.layer}</strong>
            <span>{item.when}</span>
            <p>{item.rule}</p>
            <code>{item.files}</code>
          </article>
        )) : <div className="empty-state">暂无文件分层数据</div>}
      </div>
      <div className="detail-actions">
        <button type="button" onClick={() => postAction('/api/open-path', { key: 'consoleFileIndex' })}>
          <ExternalLink size={15} /> 打开文件索引
        </button>
      </div>
    </section>
  );
}

function WeeklyReviewPanel({ data, onReload }: { data: DashboardData; onReload: () => void }) {
  const [message, setMessage] = useState('每周只保留 1-3 个下一步动作，防止研究任务发散。');
  const [busy, setBusy] = useState(false);
  const [fields, setFields] = useState<Record<string, string>>({
    focus: '',
    completed: '',
    evidence_stronger: '',
    evidence_risk: '',
    best_experiment: '',
    next_actions: '',
    files_to_ignore: '',
  });
  const summary = data.weeklyReview?.summary ?? {};
  const recent = data.weeklyReview?.recent ?? [];

  function setField(key: string, value: string) {
    setFields((current) => ({ ...current, [key]: value }));
  }

  async function saveWeekly() {
    setBusy(true);
    try {
      const result = await postAction('/api/weekly-review/update', { fields });
      setMessage(result.output ?? '每周复盘已更新');
      onReload();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel weekly-review-panel">
      <div className="panel-title-row">
        <ListChecks size={18} />
        <h2>每周复盘</h2>
      </div>
      <div className="weekly-summary">
        <article><span>本周重点</span><strong>{displayText(summary['Main focus'] ?? '')}</strong></article>
        <article><span>最佳实验</span><strong>{displayText(summary['Current best experiment'] ?? '')}</strong></article>
        <article><span>最大风险</span><strong>{displayText(summary['Biggest risk'] ?? '')}</strong></article>
        <article><span>下一步</span><strong>{displayText(summary['Next action 1'] ?? summary['Next action 2'] ?? '')}</strong></article>
      </div>
      <details className="weekly-editor">
        <summary>填写本周复盘</summary>
        <div className="weekly-form">
          <Field label="本周重点" value={fields.focus} onChange={(value) => setField('focus', value)} />
          <Field label="已完成" value={fields.completed} onChange={(value) => setField('completed', value)} />
          <Field label="变强的证据" value={fields.evidence_stronger} onChange={(value) => setField('evidence_stronger', value)} />
          <Field label="风险 / 变弱证据" value={fields.evidence_risk} onChange={(value) => setField('evidence_risk', value)} />
          <Field label="当前最佳实验" value={fields.best_experiment} onChange={(value) => setField('best_experiment', value)} />
          <Field label="下周 1-3 个动作" value={fields.next_actions} onChange={(value) => setField('next_actions', value)} multiline />
          <Field label="下周暂时不看的文件" value={fields.files_to_ignore} onChange={(value) => setField('files_to_ignore', value)} />
          <button className="primary-button" type="button" onClick={saveWeekly} disabled={busy}><Save size={16} /> 保存复盘</button>
        </div>
      </details>
      <div className="weekly-recent">
        {recent.length ? recent.map((item) => (
          <article key={item.week}>
            <strong>{item.week}</strong>
            <span>{displayText(item.focus)} · {displayText(item.nextActions)}</span>
          </article>
        )) : <div className="empty-state">暂无周复盘记录</div>}
      </div>
      <div className="detail-actions">
        <button type="button" onClick={() => postAction('/api/open-path', { key: 'weeklyReview' })}>
          <ExternalLink size={15} /> 打开周复盘
        </button>
      </div>
      <pre className="action-output compact-output">{busy ? '正在写入...' : message}</pre>
    </section>
  );
}

function ExperimentComparisonPanel({ comparisons }: { comparisons: ExperimentComparison[] }) {
  return (
    <section className="panel experiment-comparison-panel">
      <div className="panel-title-row">
        <FlaskConical size={18} />
        <h2>Baseline 对比</h2>
      </div>
      <p className="panel-note">先看 baseline、delta、verify gate、guard gate，再决定实验能否升级为论文论点证据。</p>
      <div className="comparison-list">
        {comparisons.length ? comparisons.map((item) => (
          <article className="comparison-row" key={item.id}>
            <div>
              <strong>{item.id}</strong>
              <span>{displayText(item.metric)}：{displayText(item.baselineValue)} 到 {displayText(item.newValue)}，delta {displayText(item.delta)}</span>
            </div>
            <div className="comparison-pills">
              <span className={`status-pill ${statusClass(item.verifyStatus)}`}>verify {displayStatus(item.verifyStatus)}</span>
              <span className={`status-pill ${statusClass(item.guardStatus)}`}>guard {displayStatus(item.guardStatus)}</span>
              <span className={`status-pill ${item.environmentSnapshot === 'present' ? 'is-ok' : 'is-warning'}`}>env {displayText(item.environmentSnapshot)}</span>
            </div>
            <p>{displayText(item.nextAction)}</p>
          </article>
        )) : <div className="empty-state">暂无实验对比。先生成 experiment report。</div>}
      </div>
    </section>
  );
}

type RecordType = 'claim' | 'experiment' | 'material' | 'citation';
type QuickMode = 'status' | 'claim' | 'experiment' | 'citation' | 'blocker';

const recordTypeLabels: Record<RecordType, string> = {
  claim: '新增论点 CLM-*',
  experiment: '新增实验 EXP-*',
  material: '新增材料 MAT-*',
  citation: '新增引用 CIT-*',
};

const recordFields: Record<RecordType, Array<{ key: string; label: string; multiline?: boolean }>> = {
  claim: [
    { key: 'claim_draft', label: '论点内容', multiline: true },
    { key: 'status', label: '状态' },
    { key: 'experiment_evidence', label: '实验证据' },
    { key: 'figure_table', label: '图表' },
    { key: 'literature_evidence', label: '文献证据' },
    { key: 'caveat', label: '限定条件' },
    { key: 'next_action', label: '下一步' },
  ],
  experiment: [
    { key: 'claim', label: '关联论点' },
    { key: 'method_config', label: '方法 / 配置' },
    { key: 'dataset_split', label: '数据 / 切分' },
    { key: 'command', label: '命令 / Notebook' },
    { key: 'output_path', label: '输出路径' },
    { key: 'key_metrics', label: '关键指标' },
    { key: 'status', label: '状态' },
    { key: 'notes', label: '备注', multiline: true },
  ],
  material: [
    { key: 'type', label: '材料类型' },
    { key: 'title', label: '标题 / 描述', multiline: true },
    { key: 'source_path', label: '来源路径 / URL' },
    { key: 'owner', label: '负责人' },
    { key: 'related_ids', label: '关联 ID' },
    { key: 'access_level', label: '访问级别' },
    { key: 'integrity_check', label: '完整性检查' },
    { key: 'status', label: '状态' },
  ],
  citation: [
    { key: 'section_id', label: '章节 ID' },
    { key: 'segment_id', label: '段落 ID' },
    { key: 'claim_id', label: '论点 ID' },
    { key: 'title', label: '论文题名', multiline: true },
    { key: 'identifier', label: 'DOI / arXiv / S2 / PMID' },
    { key: 'candidate_source', label: '候选来源' },
    { key: 'metadata_status', label: '元数据状态' },
    { key: 'support_status', label: '支持状态' },
    { key: 'zotero_status', label: 'Zotero 状态' },
  ],
};

function Field({
  label,
  value,
  onChange,
  multiline = false,
  placeholder = '待填写',
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  multiline?: boolean;
  placeholder?: string;
}) {
  return (
    <label className="form-field">
      <span>{label}</span>
      {multiline ? (
        <textarea value={value} placeholder={placeholder} onChange={(event) => onChange(event.target.value)} />
      ) : (
        <input value={value} placeholder={placeholder} onChange={(event) => onChange(event.target.value)} />
      )}
    </label>
  );
}

function FlowEditorPanel({ onReload }: { onReload: () => void }) {
  const [message, setMessage] = useState('表单会写入 docs/thesis/ 的标准 Markdown 文件，并自动记录 workflow-edit-log.md');
  const [busy, setBusy] = useState(false);
  const [recordType, setRecordType] = useState<RecordType>('claim');
  const [quickMode, setQuickMode] = useState<QuickMode>('status');
  const [quickFields, setQuickFields] = useState<Record<string, string>>({
    current_stage: '',
    active_focus: '',
    main_blocker: '',
    next_action: '',
    claim_draft: '',
    experiment_id: '',
    citation_title: '',
  });
  const [statusFields, setStatusFields] = useState<Record<string, string>>({
    current_stage: '',
    active_focus: '',
    audit_tier: 'quick',
    main_blocker: '',
    next_action: '',
  });
  const [recordValues, setRecordValues] = useState<Record<string, string>>({});
  const [artifactFields, setArtifactFields] = useState<Record<string, string>>({
    artifact_key: '',
    stage: '11-doc-production',
    source_ids: '',
    mac_source_path: '',
    laptop_target_path: '',
    format: 'docx',
    checksum: '',
    produced_by: 'Documents',
    transfer_status: 'pending',
    laptop_verification: 'pending',
    notes: '',
  });
  const [lifecycleFields, setLifecycleFields] = useState<Record<string, string>>({
    id: '',
    type: '',
    status: 'candidate',
    primary_file: '',
    related_ids: '',
    replacement_id: '',
    owner: 'user/Codex',
    notes: '',
  });

  async function submit(endpoint: string, payload: object) {
    setBusy(true);
    try {
      const result = await postAction(endpoint, payload);
      setMessage(`已写入：${result.id ?? 'record'} -> ${result.target ?? result.output ?? 'workflow console'}`);
      onReload();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  const updateRecordValue = (key: string, value: string) => setRecordValues((current) => ({ ...current, [key]: value }));
  const updateStatusValue = (key: string, value: string) => setStatusFields((current) => ({ ...current, [key]: value }));
  const updateArtifactValue = (key: string, value: string) => setArtifactFields((current) => ({ ...current, [key]: value }));
  const updateLifecycleValue = (key: string, value: string) => setLifecycleFields((current) => ({ ...current, [key]: value }));
  const updateQuickValue = (key: string, value: string) => setQuickFields((current) => ({ ...current, [key]: value }));

  function submitQuick() {
    if (quickMode === 'status') {
      submit('/api/flow-editor/update-status', {
        fields: {
          current_stage: quickFields.current_stage,
          active_focus: quickFields.active_focus,
          main_blocker: quickFields.main_blocker,
          next_action: quickFields.next_action,
          audit_tier: 'quick',
        },
      });
      return;
    }
    if (quickMode === 'blocker') {
      submit('/api/flow-editor/update-status', {
        fields: {
          current_stage: quickFields.current_stage,
          active_focus: quickFields.active_focus,
          main_blocker: quickFields.main_blocker,
          next_action: quickFields.next_action,
          audit_tier: 'quick',
        },
      });
      return;
    }
    if (quickMode === 'claim') {
      submit('/api/flow-editor/create-record', {
        record_type: 'claim',
        fields: {
          claim_draft: quickFields.claim_draft,
          status: 'candidate',
          next_action: quickFields.next_action,
        },
      });
      return;
    }
    if (quickMode === 'experiment') {
      submit('/api/flow-editor/create-record', {
        record_type: 'experiment',
        fields: {
          claim: quickFields.claim_draft,
          output_path: quickFields.experiment_id ? `outputs/${quickFields.experiment_id}` : '',
          status: 'planned',
          notes: quickFields.next_action,
        },
      });
      return;
    }
    submit('/api/flow-editor/create-record', {
      record_type: 'citation',
      fields: {
        title: quickFields.citation_title,
        support_status: 'candidate',
        candidate_source: 'dashboard quick entry',
        claim_id: quickFields.claim_draft,
      },
    });
  }

  return (
    <section className="panel flow-editor">
      <div className="panel-title-row">
        <ListChecks size={18} />
        <h2>流程编辑器</h2>
      </div>
      <p className="editor-note">默认只做轻量登记。复杂内容可以展开高级表单，或打开 Markdown 源文件细修。</p>
      <div className="quick-editor-grid">
        {[
          ['status', '更新当前状态'],
          ['claim', '新增论点'],
          ['experiment', '新增实验'],
          ['citation', '新增引用'],
          ['blocker', '记录/解除阻塞'],
        ].map(([mode, label]) => (
          <button type="button" key={mode} className={quickMode === mode ? 'is-active' : ''} onClick={() => setQuickMode(mode as QuickMode)}>
            {label}
          </button>
        ))}
      </div>
      <form
        className="quick-editor-form"
        onSubmit={(event) => {
          event.preventDefault();
          submitQuick();
        }}
      >
        {(quickMode === 'status' || quickMode === 'blocker') ? (
          <>
            <Field label="当前阶段" value={quickFields.current_stage} onChange={(value) => updateQuickValue('current_stage', value)} placeholder="例如：6 实验运行与监控" />
            <Field label="当前目标" value={quickFields.active_focus} onChange={(value) => updateQuickValue('active_focus', value)} placeholder="当前主要推进什么" />
            <Field label="阻塞项" value={quickFields.main_blocker} onChange={(value) => updateQuickValue('main_blocker', value)} placeholder={quickMode === 'blocker' ? '写下阻塞项；若已解除可写“已解除：...”' : '没有就留空'} />
            <Field label="下一步动作" value={quickFields.next_action} onChange={(value) => updateQuickValue('next_action', value)} multiline />
          </>
        ) : null}
        {quickMode === 'claim' ? (
          <>
            <Field label="论点内容" value={quickFields.claim_draft} onChange={(value) => updateQuickValue('claim_draft', value)} multiline />
            <Field label="下一步动作" value={quickFields.next_action} onChange={(value) => updateQuickValue('next_action', value)} placeholder="需要补哪个实验/引用/图表" />
          </>
        ) : null}
        {quickMode === 'experiment' ? (
          <>
            <Field label="关联论点" value={quickFields.claim_draft} onChange={(value) => updateQuickValue('claim_draft', value)} placeholder="CLM-001 或简要说明" />
            <Field label="实验 ID 提示" value={quickFields.experiment_id} onChange={(value) => updateQuickValue('experiment_id', value)} placeholder="EXP-001，可留空自动生成" />
            <Field label="下一步动作 / 备注" value={quickFields.next_action} onChange={(value) => updateQuickValue('next_action', value)} multiline />
          </>
        ) : null}
        {quickMode === 'citation' ? (
          <>
            <Field label="论文题名" value={quickFields.citation_title} onChange={(value) => updateQuickValue('citation_title', value)} multiline />
            <Field label="关联论点 / 章节" value={quickFields.claim_draft} onChange={(value) => updateQuickValue('claim_draft', value)} placeholder="CLM-001 / SEC-INTRO-001" />
          </>
        ) : null}
        <button type="submit" disabled={busy}><Save size={16} /> 快速写入</button>
      </form>
      <details className="advanced-editor">
        <summary>高级表单</summary>
        <div className="editor-grid">
        <form
          className="editor-form"
          onSubmit={(event) => {
            event.preventDefault();
            submit('/api/flow-editor/update-status', { fields: statusFields });
          }}
        >
          <h3>更新当前状态</h3>
          <Field label="当前阶段" value={statusFields.current_stage} onChange={(value) => updateStatusValue('current_stage', value)} placeholder="例如：6 实验运行与监控" />
          <Field label="当前重点" value={statusFields.active_focus} onChange={(value) => updateStatusValue('active_focus', value)} placeholder="literature / experiment / writing" />
          <Field label="审计等级" value={statusFields.audit_tier} onChange={(value) => updateStatusValue('audit_tier', value)} placeholder="quick / advisor / final" />
          <Field label="主要阻塞" value={statusFields.main_blocker} onChange={(value) => updateStatusValue('main_blocker', value)} />
          <Field label="下一步动作" value={statusFields.next_action} onChange={(value) => updateStatusValue('next_action', value)} multiline />
          <button type="submit" disabled={busy}><Save size={16} /> 保存当前状态</button>
        </form>

        <form
          className="editor-form"
          onSubmit={(event) => {
            event.preventDefault();
            submit('/api/flow-editor/create-record', { record_type: recordType, fields: recordValues });
          }}
        >
          <h3>新增标准记录</h3>
          <label className="form-field">
            <span>记录类型</span>
            <select value={recordType} onChange={(event) => {
              setRecordType(event.target.value as RecordType);
              setRecordValues({});
            }}>
              {(Object.keys(recordTypeLabels) as RecordType[]).map((type) => (
                <option value={type} key={type}>{recordTypeLabels[type]}</option>
              ))}
            </select>
          </label>
          {recordFields[recordType].map((field) => (
            <Field
              key={`${recordType}-${field.key}`}
              label={field.label}
              value={recordValues[field.key] ?? ''}
              onChange={(value) => updateRecordValue(field.key, value)}
              multiline={field.multiline}
            />
          ))}
          <button type="submit" disabled={busy}><Save size={16} /> 新增记录</button>
        </form>

        <form
          className="editor-form"
          onSubmit={(event) => {
            event.preventDefault();
            submit('/api/flow-editor/create-final-artifact', { fields: artifactFields });
          }}
        >
          <h3>登记最终交付物</h3>
          <Field label="Artifact Key" value={artifactFields.artifact_key} onChange={(value) => updateArtifactValue('artifact_key', value)} placeholder="thesis-docx / final-pdf / defense-pptx" />
          <Field label="阶段" value={artifactFields.stage} onChange={(value) => updateArtifactValue('stage', value)} />
          <Field label="关联 Source IDs" value={artifactFields.source_ids} onChange={(value) => updateArtifactValue('source_ids', value)} />
          <Field label="Mac 源路径" value={artifactFields.mac_source_path} onChange={(value) => updateArtifactValue('mac_source_path', value)} />
          <Field label="笔记本目标路径" value={artifactFields.laptop_target_path} onChange={(value) => updateArtifactValue('laptop_target_path', value)} />
          <Field label="格式" value={artifactFields.format} onChange={(value) => updateArtifactValue('format', value)} />
          <Field label="Checksum" value={artifactFields.checksum} onChange={(value) => updateArtifactValue('checksum', value)} />
          <Field label="生成工具" value={artifactFields.produced_by} onChange={(value) => updateArtifactValue('produced_by', value)} />
          <Field label="交接状态" value={artifactFields.transfer_status} onChange={(value) => updateArtifactValue('transfer_status', value)} />
          <Field label="笔记本验证" value={artifactFields.laptop_verification} onChange={(value) => updateArtifactValue('laptop_verification', value)} />
          <Field label="备注" value={artifactFields.notes} onChange={(value) => updateArtifactValue('notes', value)} multiline />
          <button type="submit" disabled={busy}><Save size={16} /> 登记交付物</button>
        </form>

        <form
          className="editor-form"
          onSubmit={(event) => {
            event.preventDefault();
            submit('/api/flow-editor/update-id-lifecycle', { fields: lifecycleFields });
          }}
        >
          <h3>更新 ID 生命周期</h3>
          <Field label="ID" value={lifecycleFields.id} onChange={(value) => updateLifecycleValue('id', value)} placeholder="CLM-001 / EXP-001 / FIG-001" />
          <Field label="类型" value={lifecycleFields.type} onChange={(value) => updateLifecycleValue('type', value)} placeholder="claim / experiment / figure" />
          <Field label="生命周期状态" value={lifecycleFields.status} onChange={(value) => updateLifecycleValue('status', value)} placeholder="draft / candidate / verified / promoted" />
          <Field label="主文件" value={lifecycleFields.primary_file} onChange={(value) => updateLifecycleValue('primary_file', value)} placeholder="docs/thesis/claim-evidence-map.md" />
          <Field label="关联 ID" value={lifecycleFields.related_ids} onChange={(value) => updateLifecycleValue('related_ids', value)} />
          <Field label="替代 ID" value={lifecycleFields.replacement_id} onChange={(value) => updateLifecycleValue('replacement_id', value)} />
          <Field label="负责人" value={lifecycleFields.owner} onChange={(value) => updateLifecycleValue('owner', value)} />
          <Field label="备注" value={lifecycleFields.notes} onChange={(value) => updateLifecycleValue('notes', value)} multiline />
          <button type="submit" disabled={busy}><Save size={16} /> 更新生命周期</button>
        </form>
        </div>
      </details>
      <pre className="action-output">{busy ? '正在写入...' : message}</pre>
    </section>
  );
}

function IssueList({ title, items, tone }: { title: string; items: string[]; tone: 'p0' | 'p1' }) {
  return (
    <section className="panel">
      <div className="panel-title-row">
        {tone === 'p0' ? <CircleAlert size={18} /> : <AlertTriangle size={18} />}
        <h2>{title}</h2>
        <span className={`count-badge ${tone}`}>{items.length}</span>
      </div>
      <div className="issue-list">
        {items.length ? items.map((item) => <div className="issue-item" key={item}>{displayIssue(item)}</div>) : <div className="empty-state">暂无</div>}
      </div>
    </section>
  );
}

function StageRail({ data }: { data: DashboardData }) {
  return (
    <section className="panel stage-panel">
      <div className="panel-title-row">
        <Layers3 size={18} />
        <h2>12 步流程进度</h2>
      </div>
      <div className="stage-grid">
        {data.stages.map((stage) => (
          <article className={`stage-item ${statusClass(stage.status)}`} key={stage.stage}>
            <div className="stage-number">{stage.stage}</div>
            <div className="stage-body">
              <div className="stage-name">{displayStageName(stage.name)}</div>
              <div className="stage-record">{displayText(stage.record)}</div>
            </div>
            <span className="status-pill">{displayStatus(stage.status)}</span>
          </article>
        ))}
      </div>
    </section>
  );
}

function CompactStageNav({ data }: { data: DashboardData }) {
  const activeStage = compact(data.activeStageWorkspace?.stage ?? data.currentStatus['Current stage'] ?? '', '');
  return (
    <section className="compact-stage-nav" aria-label="12 步阶段导航">
      {data.stages.map((stage) => {
        const active = activeStage.includes(stage.stage);
        return (
          <article className={`compact-stage-item ${statusClass(stage.status)} ${active ? 'is-current' : ''}`} key={stage.stage}>
            <strong>{stage.stage}</strong>
            <span>{displayStageName(stage.name)}</span>
          </article>
        );
      })}
    </section>
  );
}

function AppSidebar({
  data,
  activeTab,
  onTabChange,
}: {
  data: DashboardData;
  activeTab: DashboardTab;
  onTabChange: (tab: DashboardTab) => void;
}) {
  const currentStage = compact(data.activeStageWorkspace?.stage ?? '', 'TBD');
  const navItems: Array<{ id: DashboardTab; label: string; icon: JSX.Element }> = [
    { id: 'today', label: '工作台', icon: <ListChecks size={17} /> },
    { id: 'citation', label: '文献库', icon: <BookOpen size={17} /> },
    { id: 'graph', label: '证据链', icon: <GitBranch size={17} /> },
    { id: 'experiments', label: '实验闭环', icon: <FlaskConical size={17} /> },
    { id: 'editor', label: '写作与笔记', icon: <FileText size={17} /> },
    { id: 'handoff', label: '周报与交接', icon: <Save size={17} /> },
    { id: 'overview', label: '总览', icon: <Activity size={17} /> },
    { id: 'health', label: '配置中心', icon: <CheckCircle2 size={17} /> },
  ];
  const stagePreview = data.stages.slice(0, 4);
  return (
    <aside className="app-sidebar">
      <div className="stage-rail-title">阶段流程 <span>Stage Rail</span></div>
      <div className="stage-rail-list">
        {stagePreview.map((stage, index) => {
          const isCurrent = currentStage.includes(stage.stage);
          const isDone = ['done', 'reviewed', 'final', 'completed'].includes(stage.status.toLowerCase()) || index === 0 && !isCurrent;
          return (
            <button type="button" className={`stage-rail-row ${isCurrent ? 'is-current' : ''} ${isDone ? 'is-done' : ''}`} key={stage.stage}>
              <span className="stage-rail-dot">{isDone ? <CheckCircle2 size={17} /> : stage.stage}</span>
              <span>
                <strong>Stage {stage.stage}</strong>
                <em>{displayStageName(stage.name)}</em>
                <small>{isCurrent ? '进行中' : isDone ? '已完成' : '待开始'}</small>
              </span>
            </button>
          );
        })}
      </div>
      <nav className="sidebar-nav" aria-label="Dashboard navigation">
        {navItems.map((item) => (
          <button type="button" key={item.id} className={activeTab === item.id ? 'is-active' : ''} onClick={() => onTabChange(item.id)}>
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
      <div className="storage-card">
        <div>
          <span>本地存储</span>
          <strong>{Math.min(100, Math.max(8, data.counts.graphNodes + data.counts.graphEdges))}%</strong>
        </div>
        <div className="storage-track"><span style={{ width: `${Math.min(100, Math.max(8, data.counts.graphNodes + data.counts.graphEdges))}%` }} /></div>
        <p><span className="sync-dot" /> 数据已同步 <small>刚刚</small></p>
      </div>
    </aside>
  );
}

function RecordTable({ title, icon, rows, columns }: {
  title: string;
  icon: JSX.Element;
  rows: WorkflowRecord[];
  columns: Array<{ key: keyof WorkflowRecord; label: string }>;
}) {
  return (
    <section className="panel table-panel">
      <div className="panel-title-row">
        {icon}
        <h2>{title}</h2>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {columns.map((column) => <th key={String(column.key)}>{column.label}</th>)}
            </tr>
          </thead>
          <tbody>
            {rows.length ? rows.map((row) => (
              <tr key={row.id}>
                {columns.map((column) => (
                  <td key={String(column.key)}>
                    {column.key === 'status' || column.key === 'coverage'
                      ? <span className={`status-pill ${statusClass(String(row[column.key] ?? ''))}`}>{displayStatus(String(row[column.key] ?? ''))}</span>
                      : displayText(String(row[column.key] ?? ''))}
                  </td>
                ))}
              </tr>
            )) : (
              <tr>
                <td colSpan={columns.length}>暂无记录</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function EvidenceGraph({ nodes, edges }: { nodes: EvidenceNode[]; edges: EvidenceEdge[] }) {
  const layout = useMemo(() => {
    const grouped = kindOrder.map((kind) => nodes.filter((node) => node.kind === kind));
    const positions = new Map<string, { x: number; y: number }>();
    grouped.forEach((group, columnIndex) => {
      const x = 96 + columnIndex * 190;
      const gap = Math.max(72, 430 / Math.max(group.length, 1));
      group.forEach((node, rowIndex) => {
        positions.set(node.id, { x, y: 72 + rowIndex * gap });
      });
    });
    return positions;
  }, [nodes]);

  return (
    <section className="panel graph-panel">
      <div className="panel-title-row">
        <GitBranch size={18} />
        <h2>证据图谱</h2>
      </div>
      <svg viewBox="0 0 920 520" role="img" aria-label="证据关系图谱">
        {edges.map((edge) => {
          const source = layout.get(edge.source);
          const target = layout.get(edge.target);
          if (!source || !target) return null;
          const midX = (source.x + target.x) / 2;
          return (
            <g key={`${edge.source}-${edge.target}-${edge.relation}`}>
              <path
                className="graph-edge"
                d={`M ${source.x + 58} ${source.y} C ${midX} ${source.y}, ${midX} ${target.y}, ${target.x - 58} ${target.y}`}
              />
              <text className="edge-label" x={midX - 28} y={(source.y + target.y) / 2 - 4}>{displayRelation(edge.relation)}</text>
            </g>
          );
        })}
        {nodes.map((node) => {
          const point = layout.get(node.id);
          if (!point) return null;
          return (
            <g key={node.id} transform={`translate(${point.x - 58} ${point.y - 20})`}>
              <rect className="graph-node" width="116" height="40" rx="8" style={{ '--node-color': kindColor[node.kind] ?? '#475569' } as React.CSSProperties} />
              <text className="node-kind" x="12" y="16">{node.kind}</text>
              <text className="node-id" x="12" y="31">{node.id}</text>
            </g>
          );
        })}
      </svg>
    </section>
  );
}

export function App() {
  const [data, setData] = useState<DashboardData>(demoFallbackData);
  const [loadedFromFile, setLoadedFromFile] = useState(false);
  const [activeTab, setActiveTab] = useState<DashboardTab>('today');

  function reloadData() {
    fetch('/data/dashboard-data.json', { cache: 'no-store' })
      .then((response) => {
        if (!response.ok) throw new Error('dashboard-data.json not found');
        return response.json() as Promise<DashboardData>;
      })
      .then((payload) => {
        setData(payload);
        setLoadedFromFile(true);
      })
      .catch(() => {
        setData(demoFallbackData);
        setLoadedFromFile(false);
      });
  }

  useEffect(() => {
    reloadData();
  }, []);

  const overviewPanel = (
    <>
      <section className="metric-grid">
        <MetricCard label="论点" value={data.counts.claims} icon={<FileText size={18} />} accent="#0f766e" />
        <MetricCard label="实验" value={data.counts.experiments} icon={<FlaskConical size={18} />} accent="#7c3aed" />
        <MetricCard label="数据" value={data.counts.datasets} icon={<Database size={18} />} accent="#b45309" />
        <MetricCard label="图表" value={data.counts.figures} icon={<BarChart3 size={18} />} accent="#be123c" />
        <MetricCard label="证据关系" value={data.counts.graphEdges} icon={<GitBranch size={18} />} accent="#2563eb" />
      </section>
      <section className="content-grid">
        <IssueList title="P0 阻塞项" items={data.issues.p0} tone="p0" />
        <IssueList title="P1 待补项" items={data.issues.p1} tone="p1" />
      </section>
      <StageRail data={data} />
      <section className="table-grid">
        <RecordTable
          title="论点与证据"
          icon={<BookOpen size={18} />}
          rows={data.records.claims ?? []}
          columns={[
            { key: 'id', label: 'ID' },
            { key: 'status', label: '状态' },
            { key: 'experiments', label: '实验' },
            { key: 'figures', label: '图表' },
            { key: 'literature', label: '文献' },
          ]}
        />
        <RecordTable
          title="数据可用性"
          icon={<Database size={18} />}
          rows={data.records.datasets ?? []}
          columns={[
            { key: 'id', label: 'ID' },
            { key: 'status', label: '状态' },
            { key: 'hash', label: 'Hash' },
            { key: 'access', label: '访问条件' },
            { key: 'experiments', label: '实验' },
          ]}
        />
      </section>
    </>
  );

  const experimentsPanel = (
    <>
      <ExperimentComparisonPanel comparisons={data.experimentComparisons ?? []} />
      <section className="content-grid">
        <section className="panel">
          <div className="panel-title-row">
            <Activity size={18} />
            <h2>最近实验</h2>
          </div>
          <div className="experiment-list">
            {data.recentExperiments.length ? data.recentExperiments.map((experiment) => (
              <article className="experiment-row" key={experiment.id}>
                <div>
                  <strong>{experiment.id}</strong>
                  <span>{displayText(experiment.output)}</span>
                </div>
                <span className={`status-pill ${statusClass(experiment.status)}`}>{displayStatus(experiment.status)}</span>
              </article>
            )) : <div className="empty-state">暂无</div>}
          </div>
        </section>
        <section className="panel">
          <div className="panel-title-row">
            <FlaskConical size={18} />
            <h2>实验报告</h2>
          </div>
          <div className="experiment-list">
            {(data.experimentReports ?? []).length ? data.experimentReports!.map((report) => (
              <article className="experiment-row" key={report.id}>
                <div>
                  <strong>{report.id}</strong>
                  <span>{displayText(report.row)}</span>
                </div>
                <span className={`status-pill ${statusClass(report.status)}`}>{displayStatus(report.status)}</span>
              </article>
            )) : <div className="empty-state">暂无实验报告</div>}
          </div>
        </section>
      </section>
    </>
  );

  const handoffPanel = (
    <section className="content-grid">
      <HandoffPanel data={data} onReload={reloadData} />
      <section className="panel">
        <div className="panel-title-row">
          <FileText size={18} />
          <h2>最终交付物</h2>
        </div>
        <div className="experiment-list">
          {(data.finalArtifacts ?? []).length ? data.finalArtifacts!.map((artifact) => (
            <article className="experiment-row" key={artifact.id}>
              <div>
                <strong>{artifact.id}</strong>
                <span>{displayText(artifact.row)}</span>
              </div>
              <span className={`status-pill ${statusClass(artifact.status)}`}>{displayStatus(artifact.status)}</span>
            </article>
          )) : <div className="empty-state">暂无最终交付物记录</div>}
        </div>
      </section>
    </section>
  );

  const tabContent: Record<DashboardTab, JSX.Element> = {
    overview: overviewPanel,
    today: (
      <>
        <section className="home-cockpit-grid">
          <CurrentWorkspace data={data} onReload={reloadData} />
          <ConsoleFileLayerPanel data={data} />
          <WeeklyReviewPanel data={data} onReload={reloadData} />
          <PluginGatePanel data={data} />
        </section>
        <section className="content-grid">
          <ActionPanel onReload={reloadData} />
          <StageWorkspacePanel workspace={data.activeStageWorkspace} links={data.links} onReload={reloadData} />
        </section>
      </>
    ),
    citation: (
      <section className="content-grid citation-grid">
        <SectionCitationHeatmap coverage={data.sectionCitationCoverage ?? []} onReload={reloadData} />
        <CitationSuggestionPanel suggestions={data.citationSuggestions ?? []} onReload={reloadData} />
      </section>
    ),
    experiments: experimentsPanel,
    graph: <InteractiveEvidenceGraph nodes={data.graph.nodes} edges={data.graph.edges} issues={data.issues} focusedGraph={data.focusedEvidenceGraph} />,
    handoff: handoffPanel,
    editor: <FlowEditorPanel onReload={reloadData} />,
    health: <SystemHealthPanel data={data} />,
  };

  return (
    <main className="app-frame">
      <AppSidebar data={data} activeTab={activeTab} onTabChange={setActiveTab} />
      <section className="app-shell">
        <CockpitTopBar loadedFromFile={loadedFromFile} />
        <ProjectHero data={data} loadedFromFile={loadedFromFile} onReload={reloadData} />
        <DashboardTabs activeTab={activeTab} onChange={setActiveTab} />
        <section className="tab-content">{tabContent[activeTab]}</section>

        <footer>
          <span>打开 Markdown 源文件</span>
          <ArrowRight size={15} />
          <code>{data.links.dashboard ?? 'docs/thesis/workflow-dashboard.md'}</code>
        </footer>
      </section>
    </main>
  );
}
