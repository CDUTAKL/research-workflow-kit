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
  const visibleEdges = localGraph.edges.filter((edge) => visibleIds.has(edge.source) && visibleIds.has(edge.target));
  const layout = useMemo(() => {
    const positions = new Map<string, { x: number; y: number }>();
    const columns = [
      visibleNodes.filter((node) => node.kind === 'SEC'),
      visibleNodes.filter((node) => node.kind === 'CLM'),
      visibleNodes.filter((node) => !['SEC', 'CLM'].includes(node.kind)),
    ];
    columns.forEach((group, columnIndex) => {
      const x = 110 + columnIndex * 265;
      const gap = Math.max(76, 430 / Math.max(group.length, 1));
      group.forEach((node, rowIndex) => positions.set(node.id, { x, y: 76 + rowIndex * gap }));
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
          <svg viewBox="0 0 720 520" role="img" aria-label="可交互证据图谱">
            {visibleEdges.map((edge) => {
              const source = layout.get(edge.source);
              const target = layout.get(edge.target);
              if (!source || !target) return null;
              const highlighted = connectedIds.has(edge.source) && connectedIds.has(edge.target);
              const midX = (source.x + target.x) / 2;
              return (
                <path
                  key={`${edge.source}-${edge.target}-${edge.relation}`}
                  className={`graph-edge ${highlighted ? 'is-highlighted' : ''}`}
                  d={`M ${source.x + 64} ${source.y} C ${midX} ${source.y}, ${midX} ${target.y}, ${target.x - 64} ${target.y}`}
                />
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
                  transform={`translate(${point.x - 64} ${point.y - 24})`}
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
                    width="128"
                    height="48"
                    rx="8"
                    style={{ '--node-color': kindColor[node.kind] ?? '#475569' } as React.CSSProperties}
                  />
                  <text className="node-kind" x="12" y="18">{node.kind}</text>
                  <text className="node-id" x="12" y="35">{node.id}</text>
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
