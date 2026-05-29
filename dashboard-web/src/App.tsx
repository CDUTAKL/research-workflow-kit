import { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BarChart3,
  BookOpen,
  CheckCircle2,
  CircleAlert,
  Database,
  ExternalLink,
  FileText,
  FlaskConical,
  GitBranch,
  Layers3,
  RefreshCw,
  Terminal,
} from 'lucide-react';
import { mockData } from './mockData';
import type { DashboardData, EvidenceEdge, EvidenceNode, Health, WorkflowRecord } from './types';

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
  'Laptop final audit and defense': '笔记本终审与答辩准备',
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

async function postAction(endpoint: string, payload: object = {}) {
  const response = await fetch(`http://127.0.0.1:8765${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok || !data.ok) {
    throw new Error(data.error || data.output || 'dashboard action failed');
  }
  return data as { ok: boolean; output?: string };
}

function ActionPanel({ onReload }: { onReload: () => void }) {
  const [message, setMessage] = useState('本地控制服务使用 http://127.0.0.1:8765，只在本机访问');
  const [busy, setBusy] = useState<string | null>(null);

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
        <h2>一键操作</h2>
      </div>
      <div className="action-grid">
        <button onClick={() => run('refresh', () => postAction('/api/refresh-dashboard'), true)} disabled={Boolean(busy)}>
          <RefreshCw size={16} /> 刷新控制台
        </button>
        <button onClick={() => run('graph', () => postAction('/api/export-evidence-graph'), true)} disabled={Boolean(busy)}>
          <GitBranch size={16} /> 导出证据图谱
        </button>
        <button onClick={() => run('doctor', () => postAction('/api/run-doctor'))} disabled={Boolean(busy)}>
          <Activity size={16} /> 快速健康检查
        </button>
        <button onClick={() => run('open', () => postAction('/api/open-path', { key: 'dashboard' }))} disabled={Boolean(busy)}>
          <ExternalLink size={16} /> 打开控制台源文件
        </button>
        <button onClick={() => run('tasks', () => postAction('/api/open-path', { key: 'deepResearchTasks' }))} disabled={Boolean(busy)}>
          <BookOpen size={16} /> 打开深研任务
        </button>
        <button onClick={() => run('zotero', () => postAction('/api/open-path', { key: 'zoteroScreeningLoop' }))} disabled={Boolean(busy)}>
          <BookOpen size={16} /> 打开 Zotero 筛选
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
      </div>
      <pre className="action-output">{busy ? `正在执行 ${busy}...` : message}</pre>
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
  const [data, setData] = useState<DashboardData>(mockData);
  const [loadedFromFile, setLoadedFromFile] = useState(false);

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
        setData(mockData);
        setLoadedFromFile(false);
      });
  }

  useEffect(() => {
    reloadData();
  }, []);

  const auditTier = displayAuditTier(data.currentStatus['Current audit tier'] ?? 'quick/advisor/final/TBD');
  const currentStage = displayText(data.currentStatus['Current stage'] ?? '1-12/TBD');
  const nextAction = displayText(data.currentStatus['Next concrete action'] ?? '请运行健康检查或刷新控制台');

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Research Workflow Kit</p>
          <h1>科研工作流总控台</h1>
        </div>
        <div className="top-actions">
          <span className={`health-badge ${data.health}`}>
            {data.health === 'ok' ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
            {healthLabels[data.health]}
          </span>
          <span className="data-source">
            <RefreshCw size={15} />
            {loadedFromFile ? '实时数据' : '示例数据'}
          </span>
        </div>
      </header>

      <section className="status-band">
        <div className="status-copy">
          <p className="eyebrow">当前阶段</p>
          <div className="stage-headline">{currentStage}</div>
          <p>{nextAction}</p>
        </div>
        <div className="audit-chip">
          <span>审计等级</span>
          <strong>{auditTier}</strong>
        </div>
        <div className="generated">
          <span>更新时间</span>
          <strong>{data.generatedAt}</strong>
        </div>
      </section>

      <ActionPanel onReload={reloadData} />

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

      <section className="content-grid wide-left">
        <EvidenceGraph nodes={data.graph.nodes} edges={data.graph.edges} />
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
      </section>

      <section className="content-grid">
        <section className="panel">
          <div className="panel-title-row">
            <FlaskConical size={18} />
            <h2>实验闭环</h2>
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
        <section className="panel">
          <div className="panel-title-row">
            <CheckCircle2 size={18} />
            <h2>Skill 健康度</h2>
          </div>
          <div className="skill-health">
            <div><strong>{data.skillHealth?.totalSkills ?? 0}</strong><span>Skill 总数</span></div>
            <div><strong>{data.skillHealth?.brokenReferences ?? 0}</strong><span>断裂引用</span></div>
            <div><strong>{data.skillHealth?.missingScripts ?? 0}</strong><span>缺失脚本</span></div>
            <div><strong>{data.skillHealth?.outdatedAssumptions ?? 0}</strong><span>旧工具假设</span></div>
          </div>
        </section>
      </section>

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

      <footer>
        <span>打开 Markdown 源文件</span>
        <ArrowRight size={15} />
        <code>{data.links.dashboard ?? 'docs/thesis/workflow-dashboard.md'}</code>
      </footer>
    </main>
  );
}
