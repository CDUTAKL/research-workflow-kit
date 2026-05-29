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
  ok: 'OK',
  warning: 'Warning',
  blocked: 'Blocked',
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
  const [message, setMessage] = useState('Control server actions use http://127.0.0.1:8765');
  const [busy, setBusy] = useState<string | null>(null);

  async function run(label: string, action: () => Promise<unknown>, reload = false) {
    setBusy(label);
    try {
      const result = await action();
      setMessage(typeof result === 'object' && result && 'output' in result ? String((result as { output?: string }).output || 'done') : 'done');
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
        <h2>Control Actions</h2>
      </div>
      <div className="action-grid">
        <button onClick={() => run('refresh', () => postAction('/api/refresh-dashboard'), true)} disabled={Boolean(busy)}>
          <RefreshCw size={16} /> Refresh Dashboard
        </button>
        <button onClick={() => run('graph', () => postAction('/api/export-evidence-graph'), true)} disabled={Boolean(busy)}>
          <GitBranch size={16} /> Export Evidence Graph
        </button>
        <button onClick={() => run('doctor', () => postAction('/api/run-doctor'))} disabled={Boolean(busy)}>
          <Activity size={16} /> Run Quick Health Check
        </button>
        <button onClick={() => run('open', () => postAction('/api/open-path', { key: 'dashboard' }))} disabled={Boolean(busy)}>
          <ExternalLink size={16} /> Open Dashboard Source
        </button>
        <button onClick={() => run('tasks', () => postAction('/api/open-path', { key: 'deepResearchTasks' }))} disabled={Boolean(busy)}>
          <BookOpen size={16} /> Open Research Tasks
        </button>
        <button onClick={() => run('zotero', () => postAction('/api/open-path', { key: 'zoteroScreeningLoop' }))} disabled={Boolean(busy)}>
          <BookOpen size={16} /> Open Zotero Screening
        </button>
        <button onClick={() => run('diagrams', () => postAction('/api/open-path', { key: 'diagramReplicaTasks' }))} disabled={Boolean(busy)}>
          <ExternalLink size={16} /> Open Diagram Tasks
        </button>
        <button onClick={() => run('reports', () => postAction('/api/open-path', { key: 'experimentReports' }))} disabled={Boolean(busy)}>
          <FlaskConical size={16} /> Open Reports Folder
        </button>
        <button onClick={() => navigator.clipboard.writeText(nextCommand).then(() => setMessage(`copied: ${nextCommand}`))} disabled={Boolean(busy)}>
          <FileText size={16} /> Copy Next Command
        </button>
      </div>
      <pre className="action-output">{busy ? `Running ${busy}...` : message}</pre>
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
        {items.length ? items.map((item) => <div className="issue-item" key={item}>{item}</div>) : <div className="empty-state">none</div>}
      </div>
    </section>
  );
}

function StageRail({ data }: { data: DashboardData }) {
  return (
    <section className="panel stage-panel">
      <div className="panel-title-row">
        <Layers3 size={18} />
        <h2>12-Stage Progress</h2>
      </div>
      <div className="stage-grid">
        {data.stages.map((stage) => (
          <article className={`stage-item ${statusClass(stage.status)}`} key={stage.stage}>
            <div className="stage-number">{stage.stage}</div>
            <div className="stage-body">
              <div className="stage-name">{stage.name}</div>
              <div className="stage-record">{compact(stage.record)}</div>
            </div>
            <span className="status-pill">{compact(stage.status, 'pending')}</span>
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
                      ? <span className={`status-pill ${statusClass(String(row[column.key] ?? ''))}`}>{compact(String(row[column.key] ?? ''))}</span>
                      : compact(String(row[column.key] ?? ''))}
                  </td>
                ))}
              </tr>
            )) : (
              <tr>
                <td colSpan={columns.length}>No records yet</td>
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
        <h2>Evidence Graph</h2>
      </div>
      <svg viewBox="0 0 920 520" role="img" aria-label="Evidence relationship graph">
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
              <text className="edge-label" x={midX - 28} y={(source.y + target.y) / 2 - 4}>{edge.relation}</text>
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

  const p0Count = data.issues.p0.length;
  const p1Count = data.issues.p1.length;
  const auditTier = data.currentStatus['Current audit tier'] ?? 'quick/advisor/final/TBD';
  const currentStage = data.currentStatus['Current stage'] ?? '1-12/TBD';
  const nextAction = data.currentStatus['Next concrete action'] ?? 'TBD';

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Research Workflow Kit</p>
          <h1>Workflow Dashboard</h1>
        </div>
        <div className="top-actions">
          <span className={`health-badge ${data.health}`}>
            {data.health === 'ok' ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
            {healthLabels[data.health]}
          </span>
          <span className="data-source">
            <RefreshCw size={15} />
            {loadedFromFile ? 'live data' : 'fallback data'}
          </span>
        </div>
      </header>

      <section className="status-band">
        <div className="status-copy">
          <p className="eyebrow">Current Stage</p>
          <div className="stage-headline">{currentStage}</div>
          <p>{nextAction}</p>
        </div>
        <div className="audit-chip">
          <span>Audit Tier</span>
          <strong>{auditTier}</strong>
        </div>
        <div className="generated">
          <span>Generated</span>
          <strong>{data.generatedAt}</strong>
        </div>
      </section>

      <section className="metric-grid">
        <MetricCard label="Claims" value={data.counts.claims} icon={<FileText size={18} />} accent="#0f766e" />
        <MetricCard label="Experiments" value={data.counts.experiments} icon={<FlaskConical size={18} />} accent="#7c3aed" />
        <MetricCard label="Data" value={data.counts.datasets} icon={<Database size={18} />} accent="#b45309" />
        <MetricCard label="Figures" value={data.counts.figures} icon={<BarChart3 size={18} />} accent="#be123c" />
        <MetricCard label="Graph Links" value={data.counts.graphEdges} icon={<GitBranch size={18} />} accent="#2563eb" />
      </section>

      <section className="content-grid">
        <IssueList title="P0 Blockers" items={data.issues.p0} tone="p0" />
        <IssueList title="P1 Issues" items={data.issues.p1} tone="p1" />
      </section>

      <ActionPanel onReload={reloadData} />

      <StageRail data={data} />

      <section className="content-grid wide-left">
        <EvidenceGraph nodes={data.graph.nodes} edges={data.graph.edges} />
        <section className="panel">
          <div className="panel-title-row">
            <Activity size={18} />
            <h2>Recent Experiments</h2>
          </div>
          <div className="experiment-list">
            {data.recentExperiments.length ? data.recentExperiments.map((experiment) => (
              <article className="experiment-row" key={experiment.id}>
                <div>
                  <strong>{experiment.id}</strong>
                  <span>{compact(experiment.output)}</span>
                </div>
                <span className={`status-pill ${statusClass(experiment.status)}`}>{compact(experiment.status)}</span>
              </article>
            )) : <div className="empty-state">none</div>}
          </div>
        </section>
      </section>

      <section className="content-grid">
        <section className="panel">
          <div className="panel-title-row">
            <FlaskConical size={18} />
            <h2>Experiment Loop</h2>
          </div>
          <div className="experiment-list">
            {(data.experimentReports ?? []).length ? data.experimentReports!.map((report) => (
              <article className="experiment-row" key={report.id}>
                <div>
                  <strong>{report.id}</strong>
                  <span>{compact(report.row)}</span>
                </div>
                <span className={`status-pill ${statusClass(report.status)}`}>{compact(report.status)}</span>
              </article>
            )) : <div className="empty-state">No experiment reports yet</div>}
          </div>
        </section>
        <section className="panel">
          <div className="panel-title-row">
            <CheckCircle2 size={18} />
            <h2>Skill Health</h2>
          </div>
          <div className="skill-health">
            <div><strong>{data.skillHealth?.totalSkills ?? 0}</strong><span>Total skills</span></div>
            <div><strong>{data.skillHealth?.brokenReferences ?? 0}</strong><span>Broken references</span></div>
            <div><strong>{data.skillHealth?.missingScripts ?? 0}</strong><span>Missing scripts</span></div>
            <div><strong>{data.skillHealth?.outdatedAssumptions ?? 0}</strong><span>Outdated assumptions</span></div>
          </div>
        </section>
      </section>

      <section className="table-grid">
        <RecordTable
          title="Claims"
          icon={<BookOpen size={18} />}
          rows={data.records.claims ?? []}
          columns={[
            { key: 'id', label: 'ID' },
            { key: 'status', label: 'Status' },
            { key: 'experiments', label: 'Experiments' },
            { key: 'figures', label: 'Figures' },
            { key: 'literature', label: 'Literature' },
          ]}
        />
        <RecordTable
          title="Data Availability"
          icon={<Database size={18} />}
          rows={data.records.datasets ?? []}
          columns={[
            { key: 'id', label: 'ID' },
            { key: 'status', label: 'Status' },
            { key: 'hash', label: 'Hash' },
            { key: 'access', label: 'Access' },
            { key: 'experiments', label: 'Experiments' },
          ]}
        />
      </section>

      <footer>
        <span>Open Markdown source</span>
        <ArrowRight size={15} />
        <code>{data.links.dashboard ?? 'docs/thesis/workflow-dashboard.md'}</code>
      </footer>
    </main>
  );
}
