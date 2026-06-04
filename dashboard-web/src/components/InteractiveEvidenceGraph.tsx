import { ExternalLink, GitBranch, Search } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { postAction } from '../api/client';
import type { DashboardData, EvidenceEdge, EvidenceNode } from '../types';

const kindOrder = ['SEC', 'CLM', 'EXP', 'DATA', 'FIG', 'CIT'];
const kindColor: Record<string, string> = {
  SEC: '#2563eb',
  CLM: '#0f766e',
  EXP: '#7c3aed',
  DATA: '#b45309',
  FIG: '#be123c',
  CIT: '#475569',
};

const kindLabel: Record<string, string> = {
  SEC: '章节',
  CLM: '论点',
  EXP: '实验',
  DATA: '数据',
  FIG: '图表',
  CIT: '引用',
};

const laneLabels = [
  { key: 'SEC', title: '论文位置', subtitle: 'SEC / SEG' },
  { key: 'CLM', title: '核心论点', subtitle: 'CLM' },
  { key: 'EVIDENCE', title: '支撑证据', subtitle: 'EXP / DATA / FIG / CIT' },
];

const nodeWidth = 156;
const nodeHeight = 62;
const nodeRadius = 12;

function nodeStatus(node: EvidenceNode, edges: EvidenceEdge[], issues: DashboardData['issues']) {
  const issueText = [...issues.p0, ...issues.p1].join('\n');
  if (issues.p0.some((issue) => issue.includes(node.id))) return 'blocked';
  if (issues.p1.some((issue) => issue.includes(node.id))) return 'warning';
  if (!edges.some((edge) => edge.source === node.id || edge.target === node.id)) return 'warning';
  if (issueText.includes(node.id)) return 'warning';
  return 'ok';
}

function openKeyForKind(kind: string) {
  if (kind === 'SEC' || kind === 'CIT') return 'sectionCitationMap';
  if (kind === 'CLM') return 'claimMap';
  if (kind === 'EXP') return 'experimentRegistry';
  if (kind === 'DATA') return 'dataAvailability';
  if (kind === 'FIG') return 'figurePlan';
  return 'dashboard';
}

function laneRank(kind = '') {
  if (kind === 'SEC') return 0;
  if (kind === 'CLM') return 1;
  return 2;
}

export function InteractiveEvidenceGraph({
  nodes,
  edges,
  issues,
  focusedGraph,
}: {
  nodes: EvidenceNode[];
  edges: EvidenceEdge[];
  issues: DashboardData['issues'];
  focusedGraph?: DashboardData['focusedEvidenceGraph'];
}) {
  const [selectedId, setSelectedId] = useState(nodes[0]?.id ?? '');
  const [query, setQuery] = useState('');
  const [showAll, setShowAll] = useState(false);
  const [enabledKinds, setEnabledKinds] = useState<Record<string, boolean>>(() => Object.fromEntries(kindOrder.map((kind) => [kind, true])));
  const seedNodes = focusedGraph?.nodes?.length && !showAll ? focusedGraph.nodes : nodes;
  const seedEdges = focusedGraph?.edges?.length && !showAll ? focusedGraph.edges : edges;
  const selected = nodes.find((node) => node.id === selectedId) ?? seedNodes[0] ?? nodes[0];
  const connectedIds = useMemo(() => {
    const ids = new Set<string>();
    edges.forEach((edge) => {
      if (edge.source === selected?.id || edge.target === selected?.id) {
        ids.add(edge.source);
        ids.add(edge.target);
      }
    });
    return ids;
  }, [edges, selected?.id]);

  const localGraph = useMemo(() => {
    if (showAll || focusedGraph?.nodes?.length) {
      return { nodes: seedNodes, edges: seedEdges };
    }
    if (!selected) return { nodes: seedNodes, edges: seedEdges };
    const ids = new Set<string>([selected.id]);
    edges.forEach((edge) => {
      if (edge.source === selected.id || edge.target === selected.id) {
        ids.add(edge.source);
        ids.add(edge.target);
      }
    });
    return {
      nodes: nodes.filter((node) => ids.has(node.id)),
      edges: edges.filter((edge) => ids.has(edge.source) && ids.has(edge.target)),
    };
  }, [edges, focusedGraph?.nodes?.length, nodes, seedEdges, seedNodes, selected, showAll]);

  useEffect(() => {
    if (!selectedId && seedNodes[0]) setSelectedId(seedNodes[0].id);
  }, [seedNodes, selectedId]);

  const visibleNodes = useMemo(() => {
    const cleanQuery = query.trim().toLowerCase();
    return localGraph.nodes.filter((node) => {
      if (!enabledKinds[node.kind]) return false;
      if (!cleanQuery) return true;
      return `${node.id} ${node.label} ${node.kind}`.toLowerCase().includes(cleanQuery);
    });
  }, [enabledKinds, localGraph.nodes, query]);
  const visibleIds = new Set(visibleNodes.map((node) => node.id));
  const visibleNodeById = useMemo(() => new Map(visibleNodes.map((node) => [node.id, node])), [visibleNodes]);
  const visibleEdges = useMemo(() => {
    const grouped = new Map<string, EvidenceEdge & { count: number }>();
    localGraph.edges
      .filter((edge) => visibleIds.has(edge.source) && visibleIds.has(edge.target))
      .forEach((edge) => {
        const sourceNode = visibleNodeById.get(edge.source);
        const targetNode = visibleNodeById.get(edge.target);
        if (!sourceNode || !targetNode) return;

        const sourceRank = laneRank(sourceNode.kind);
        const targetRank = laneRank(targetNode.kind);
        if (!showAll && sourceRank === 2 && targetRank === 2) return;

        let source = edge.source;
        let target = edge.target;
        if (sourceRank > targetRank) {
          source = edge.target;
          target = edge.source;
        }

        const key = `${source}→${target}`;
        const current = grouped.get(key);
        if (current) {
          grouped.set(key, { ...current, count: current.count + 1 });
        } else {
          grouped.set(key, { ...edge, source, target, count: 1 });
        }
      });
    return Array.from(grouped.values());
  }, [localGraph.edges, showAll, visibleIds, visibleNodeById]);
  const layout = useMemo(() => {
    const positions = new Map<string, { x: number; y: number }>();
    const columns = [
      visibleNodes.filter((node) => node.kind === 'SEC'),
      visibleNodes.filter((node) => node.kind === 'CLM'),
      visibleNodes.filter((node) => !['SEC', 'CLM'].includes(node.kind)),
    ];
    columns.forEach((group, columnIndex) => {
      const x = 148 + columnIndex * 330;
      const gap = Math.max(96, 392 / Math.max(group.length, 1));
      group.forEach((node, rowIndex) => positions.set(node.id, { x, y: 132 + rowIndex * gap }));
    });
    return positions;
  }, [visibleNodes]);

  return (
    <section className="panel interactive-graph-panel">
      <div className="panel-title-row">
        <GitBranch size={18} />
        <h2>局部证据链</h2>
        <span className="status-pill is-neutral">{showAll ? '全项目视图' : '当前局部视图'}</span>
      </div>
      <div className="graph-toolbar">
        <label>
          <Search size={15} />
          <input value={query} placeholder="搜索 ID / 标签" onChange={(event) => setQuery(event.target.value)} />
        </label>
        <div className="kind-filters">
          {kindOrder.map((kind) => (
            <button
              type="button"
              key={kind}
              className={enabledKinds[kind] ? 'is-active' : ''}
              onClick={() => setEnabledKinds((current) => ({ ...current, [kind]: !current[kind] }))}
              style={{ '--kind-color': kindColor[kind] } as React.CSSProperties}
            >
              {kind}
            </button>
          ))}
        </div>
        <button className="subtle-toggle inline-toggle" type="button" onClick={() => setShowAll((value) => !value)}>
          {showAll ? '显示局部证据链' : '显示全项目图谱'}
        </button>
      </div>
      <p className="panel-note">默认只显示当前阶段或当前节点附近的证据链，避免全项目关系过载；需要全局检查时再展开全项目图谱。</p>
      <div className="interactive-graph-layout">
        <div className="graph-canvas-wrap">
          <svg viewBox="0 0 920 560" role="img" aria-label="可交互证据图谱">
            <defs>
              <marker id="graph-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5.8" markerHeight="5.8" orient="auto">
                <path d="M 0 1.4 L 9 5 L 0 8.6 z" className="graph-arrow-head" />
              </marker>
              <filter id="node-shadow" x="-20%" y="-20%" width="140%" height="150%">
                <feDropShadow dx="0" dy="5" stdDeviation="5" floodColor="#1d2939" floodOpacity="0.11" />
              </filter>
            </defs>
            {laneLabels.map((lane, index) => (
              <g className="graph-lane" key={lane.key} transform={`translate(${36 + index * 302} 24)`}>
                <rect width="260" height="500" rx="14" />
                <text className="graph-lane-title" x="18" y="30">{lane.title}</text>
                <text className="graph-lane-subtitle" x="18" y="51">{lane.subtitle}</text>
              </g>
            ))}
            {visibleEdges.map((edge) => {
              const source = layout.get(edge.source);
              const target = layout.get(edge.target);
              if (!source || !target) return null;
              const highlighted = connectedIds.has(edge.source) && connectedIds.has(edge.target);
              const midX = (source.x + target.x) / 2;
              const direction = target.x >= source.x ? 1 : -1;
              const startX = source.x + direction * (nodeWidth / 2 + 8);
              const endX = target.x - direction * (nodeWidth / 2 + 18);
              const startY = source.y;
              const endY = target.y;
              return (
                <g key={`${edge.source}-${edge.target}`}>
                  <path
                    className={`graph-edge ${highlighted ? 'is-highlighted' : ''}`}
                    markerEnd="url(#graph-arrow)"
                    d={`M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}`}
                  />
                </g>
              );
            })}
            {visibleNodes.map((node) => {
              const point = layout.get(node.id);
              if (!point) return null;
              const selectedNode = selected?.id === node.id;
              const related = connectedIds.has(node.id);
              const status = nodeStatus(node, edges, issues);
              return (
                <g
                  key={node.id}
                  transform={`translate(${point.x - nodeWidth / 2} ${point.y - nodeHeight / 2})`}
                  className={`graph-node-group ${selectedNode ? 'is-selected' : ''} ${related ? 'is-related' : ''}`}
                  onClick={() => setSelectedId(node.id)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault();
                      setSelectedId(node.id);
                    }
                  }}
                  role="button"
                  tabIndex={0}
                >
                  <rect
                    className={`graph-node graph-status-${status}`}
                    width={nodeWidth}
                    height={nodeHeight}
                    rx={nodeRadius}
                    style={{ '--node-color': kindColor[node.kind] ?? '#475569' } as React.CSSProperties}
                  />
                  <circle className={`node-status-dot node-status-${status}`} cx="135" cy="18" r="5" />
                  <text className="node-kind" x="14" y="20">{kindLabel[node.kind] ?? node.kind}</text>
                  <text className="node-id" x="14" y="39">{node.id}</text>
                  <text className="node-hint" x="14" y="53">{node.label && node.label !== 'TBD' ? node.label : status === 'ok' ? '证据链已连接' : '需要补充证据'}</text>
                </g>
              );
            })}
          </svg>
        </div>
        <aside className="graph-detail">
          <p className="eyebrow">节点详情</p>
          <h3>{selected?.id ?? '未选择'}</h3>
          <dl>
            <dt>类型</dt>
            <dd>{selected?.kind ?? 'TBD'}</dd>
            <dt>标签</dt>
            <dd>{selected?.label ?? 'TBD'}</dd>
            <dt>状态</dt>
            <dd>{selected ? nodeStatus(selected, edges, issues) : 'TBD'}</dd>
            <dt>连接数</dt>
            <dd>{selected ? edges.filter((edge) => edge.source === selected.id || edge.target === selected.id).length : 0}</dd>
            <dt>下一步</dt>
            <dd>{selected && nodeStatus(selected, edges, issues) !== 'ok' ? '补齐该节点的证据链接或状态说明' : '保持当前证据链，可进入下一步审查'}</dd>
          </dl>
          <button type="button" onClick={() => selected && postAction('/api/open-path', { key: openKeyForKind(selected.kind) })}>
            <ExternalLink size={15} /> 打开相关源文件
          </button>
        </aside>
      </div>
    </section>
  );
}
