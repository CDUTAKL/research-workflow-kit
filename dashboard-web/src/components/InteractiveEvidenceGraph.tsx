import { AlertTriangle, CheckCircle2, ExternalLink, GitBranch, Search } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import type { CSSProperties } from 'react';
import { postAction } from '../api/client';
import type { DashboardData, EvidenceEdge, EvidenceNode } from '../types';

const kindOrder = ['SEC', 'CLM', 'EXP', 'DATA', 'FIG', 'CIT'];
const evidenceKinds = ['EXP', 'DATA', 'FIG', 'CIT'];

const kindColor: Record<string, string> = {
  SEC: '#2563eb',
  SEG: '#2563eb',
  CLM: '#0f766e',
  EXP: '#7c3aed',
  DATA: '#b45309',
  FIG: '#be123c',
  CIT: '#475569',
};

const kindLabel: Record<string, string> = {
  SEC: '章节',
  SEG: '段落',
  CLM: '论点',
  EXP: '实验',
  DATA: '数据',
  FIG: '图表',
  CIT: '引用',
};

const laneLabels = [
  { key: 'position', title: '论文位置', subtitle: 'SEC / SEG', className: 'is-position' },
  { key: 'claim', title: '核心论点', subtitle: 'CLM', className: 'is-claim' },
  { key: 'evidence', title: '支撑证据', subtitle: 'EXP / DATA / FIG / CIT', className: 'is-evidence' },
];

const nodeWidth = 172;
const nodeHeight = 72;
const canvasWidth = 1040;
const canvasHeight = 610;
const laneWidth = 286;
const laneTop = 34;
const laneHeight = 538;
const laneX = [36, 364, 692];
const anchorX = [laneX[0] + laneWidth / 2, laneX[1] + laneWidth / 2, laneX[2] + laneWidth / 2];

type GraphStatus = 'ok' | 'warning' | 'blocked';
type NormalizedEdge = EvidenceEdge & {
  originalRelations: string[];
  inferred?: boolean;
};

function rankForKind(kind = '') {
  if (kind === 'SEC' || kind === 'SEG') return 0;
  if (kind === 'CLM') return 1;
  return 2;
}

function nodeStatus(node: EvidenceNode, edges: EvidenceEdge[], issues: DashboardData['issues']): GraphStatus {
  const p0Hit = issues.p0.some((issue) => issue.includes(node.id));
  const p1Hit = issues.p1.some((issue) => issue.includes(node.id));
  if (p0Hit) return 'blocked';
  if (p1Hit) return 'warning';
  if (!edges.some((edge) => edge.source === node.id || edge.target === node.id)) return 'warning';
  return 'ok';
}

function openKeyForKind(kind: string) {
  if (kind === 'SEC' || kind === 'SEG' || kind === 'CIT') return 'sectionCitationMap';
  if (kind === 'CLM') return 'claimMap';
  if (kind === 'EXP') return 'experimentRegistry';
  if (kind === 'DATA') return 'dataAvailability';
  if (kind === 'FIG') return 'figurePlan';
  return 'dashboard';
}

function cleanLabel(value = '', fallback = '待填写') {
  const text = value.trim();
  if (!text || text.toLowerCase() === 'tbd') return fallback;
  return text;
}

function clampText(value = '', max = 28) {
  const text = cleanLabel(value, '证据链已连接');
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

function semanticKey(source: string, target: string) {
  return `${source}__${target}`;
}

function normalizeEdges(rawEdges: EvidenceEdge[], nodeById: Map<string, EvidenceNode>, showAll: boolean) {
  const grouped = new Map<string, NormalizedEdge>();

  rawEdges.forEach((edge) => {
    const sourceNode = nodeById.get(edge.source);
    const targetNode = nodeById.get(edge.target);
    if (!sourceNode || !targetNode) return;

    const sourceRank = rankForKind(sourceNode.kind);
    const targetRank = rankForKind(targetNode.kind);

    if (!showAll) {
      if (sourceRank === 2 && targetRank === 2) return;
      if (sourceRank === 0 && targetRank === 2) return;
      if (sourceRank === targetRank) return;
    }

    let source = edge.source;
    let target = edge.target;
    if (sourceRank > targetRank) {
      source = edge.target;
      target = edge.source;
    }

    const key = semanticKey(source, target);
    const current = grouped.get(key);
    if (current) {
      const relations = new Set([...current.originalRelations, edge.relation]);
      grouped.set(key, {
        ...current,
        relation: current.relation || edge.relation,
        originalRelations: Array.from(relations),
      });
      return;
    }

    grouped.set(key, {
      source,
      target,
      relation: edge.relation,
      originalRelations: [edge.relation],
    });
  });

  if (!showAll) {
    const positionNodes = Array.from(nodeById.values()).filter((node) => rankForKind(node.kind) === 0);
    const claimNodes = Array.from(nodeById.values()).filter((node) => node.kind === 'CLM');
    claimNodes.forEach((claim) => {
      const hasPositionLink = Array.from(grouped.values()).some((edge) => edge.target === claim.id && rankForKind(nodeById.get(edge.source)?.kind) === 0);
      if (!hasPositionLink && positionNodes[0]) {
        grouped.set(semanticKey(positionNodes[0].id, claim.id), {
          source: positionNodes[0].id,
          target: claim.id,
          relation: 'section_supports_claim',
          originalRelations: ['inferred_section_supports_claim'],
          inferred: true,
        });
      }
    });
  }

  return Array.from(grouped.values());
}

function makePath(source: { x: number; y: number }, target: { x: number; y: number }, edgeIndex: number) {
  const startX = source.x + nodeWidth / 2;
  const endX = target.x - nodeWidth / 2 - 10;
  const startY = source.y - 12 + edgeIndex * 10;
  const endY = target.y;
  const controlA = startX + Math.max(72, (endX - startX) * 0.42);
  const controlB = endX - Math.max(72, (endX - startX) * 0.26);
  return {
    d: `M ${startX} ${startY} C ${controlA} ${startY}, ${controlB} ${endY}, ${endX} ${endY}`,
    arrow: `${endX},${endY} ${endX - 9},${endY - 5} ${endX - 9},${endY + 5}`,
  };
}

function summarizeRelated(selected: EvidenceNode | undefined, nodes: EvidenceNode[], edges: NormalizedEdge[], kind: string) {
  if (!selected) return [];
  return edges
    .filter((edge) => edge.source === selected.id || edge.target === selected.id)
    .map((edge) => (edge.source === selected.id ? edge.target : edge.source))
    .map((id) => nodes.find((node) => node.id === id))
    .filter((node): node is EvidenceNode => Boolean(node && node.kind === kind));
}

function EvidenceNodeDetail({
  selected,
  nodes,
  edges,
  issues,
}: {
  selected?: EvidenceNode;
  nodes: EvidenceNode[];
  edges: NormalizedEdge[];
  issues: DashboardData['issues'];
}) {
  const status = selected ? nodeStatus(selected, edges, issues) : 'warning';
  const linkedClaims = summarizeRelated(selected, nodes, edges, 'CLM');
  const linkedSections = summarizeRelated(selected, nodes, edges, 'SEC');
  const support = evidenceKinds.map((kind) => ({
    kind,
    items: summarizeRelated(selected, nodes, edges, kind),
  }));
  const hasAnyEvidence = support.some((group) => group.items.length);

  return (
    <aside className="evidence-detail-panel">
      <p className="eyebrow">证据检查面板</p>
      <h3>{selected?.id ?? '未选择节点'}</h3>
      <div className={`evidence-status-card is-${status}`}>
        {status === 'ok' ? <CheckCircle2 size={17} /> : <AlertTriangle size={17} />}
        <span>{status === 'ok' ? '当前主证据链已连接' : '该节点仍有待补记录'}</span>
      </div>

      {selected?.kind === 'CLM' ? (
        <>
          <div className="detail-section">
            <span>论点内容</span>
            <strong>{cleanLabel(selected.label, '尚未填写论点正文')}</strong>
          </div>
          <div className="detail-section">
            <span>所属章节</span>
            <div className="detail-chip-row">
              {linkedSections.length ? linkedSections.map((node) => <b key={node.id}>{node.id}</b>) : <em>暂无章节链接</em>}
            </div>
          </div>
          <div className="detail-evidence-grid">
            {support.map((group) => (
              <article key={group.kind} className={group.items.length ? 'is-filled' : 'is-missing'}>
                <span>{kindLabel[group.kind]}</span>
                <strong>{group.items.length}</strong>
                <small>{group.items.map((node) => node.id).join(', ') || '待补'}</small>
              </article>
            ))}
          </div>
          <div className={hasAnyEvidence ? 'detail-next is-ok' : 'detail-next is-warning'}>
            <span>下一步</span>
            <strong>{hasAnyEvidence ? '检查证据质量后，可进入写作或终审。' : '先补实验、数据、图表或引用，再提升为正文论点。'}</strong>
          </div>
        </>
      ) : (
        <>
          <dl className="detail-list">
            <dt>类型</dt>
            <dd>{selected ? kindLabel[selected.kind] ?? selected.kind : '暂无'}</dd>
            <dt>说明</dt>
            <dd>{selected ? cleanLabel(selected.label) : '暂无'}</dd>
            <dt>关联论点</dt>
            <dd>{linkedClaims.map((node) => node.id).join(', ') || '暂无'}</dd>
            <dt>来源记录</dt>
            <dd>{selected ? openKeyForKind(selected.kind) : 'dashboard'}</dd>
            <dt>证据状态</dt>
            <dd>{status === 'ok' ? '可作为候选论文证据' : '需要补来源、状态或链接'}</dd>
          </dl>
          <div className={status === 'ok' ? 'detail-next is-ok' : 'detail-next is-warning'}>
            <span>下一步</span>
            <strong>{status === 'ok' ? '回到论点表检查是否可提升为正式证据。' : '打开源文件补齐可追踪记录。'}</strong>
          </div>
        </>
      )}

      <button type="button" onClick={() => selected && postAction('/api/open-path', { key: openKeyForKind(selected.kind) })}>
        <ExternalLink size={15} /> 打开相关源文件
      </button>
    </aside>
  );
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
  const [query, setQuery] = useState('');
  const [showAll, setShowAll] = useState(false);
  const [enabledKinds, setEnabledKinds] = useState<Record<string, boolean>>(() => Object.fromEntries(kindOrder.map((kind) => [kind, true])));
  const [selectedId, setSelectedId] = useState(nodes.find((node) => node.kind === 'CLM')?.id ?? nodes[0]?.id ?? '');

  const seedNodes = !showAll && focusedGraph?.nodes?.length ? focusedGraph.nodes : nodes;
  const seedEdges = !showAll && focusedGraph?.edges?.length ? focusedGraph.edges : edges;

  const filteredNodes = useMemo(() => {
    const cleanQuery = query.trim().toLowerCase();
    return seedNodes.filter((node) => {
      if (!enabledKinds[node.kind]) return false;
      if (!cleanQuery) return true;
      return `${node.id} ${node.label} ${node.kind}`.toLowerCase().includes(cleanQuery);
    });
  }, [enabledKinds, query, seedNodes]);

  const nodeById = useMemo(() => new Map(filteredNodes.map((node) => [node.id, node])), [filteredNodes]);
  const semanticEdges = useMemo(() => normalizeEdges(seedEdges, nodeById, showAll), [nodeById, seedEdges, showAll]);

  const selected = useMemo(() => {
    return filteredNodes.find((node) => node.id === selectedId) ?? filteredNodes.find((node) => node.kind === 'CLM') ?? filteredNodes[0];
  }, [filteredNodes, selectedId]);

  useEffect(() => {
    if (selected && selected.id !== selectedId) setSelectedId(selected.id);
  }, [selected, selectedId]);

  const connectedIds = useMemo(() => {
    const ids = new Set<string>();
    semanticEdges.forEach((edge) => {
      if (edge.source === selected?.id || edge.target === selected?.id) {
        ids.add(edge.source);
        ids.add(edge.target);
      }
    });
    return ids;
  }, [selected?.id, semanticEdges]);

  const layout = useMemo(() => {
    const positions = new Map<string, { x: number; y: number; edgeIndex: number }>();
    const columns = [
      filteredNodes.filter((node) => rankForKind(node.kind) === 0),
      filteredNodes.filter((node) => node.kind === 'CLM'),
      filteredNodes.filter((node) => evidenceKinds.includes(node.kind)),
    ];
    columns.forEach((column, columnIndex) => {
      const startY = column.length <= 1 ? 294 : 156;
      const gap = column.length <= 1 ? 0 : Math.min(118, 332 / Math.max(column.length - 1, 1));
      column.forEach((node, rowIndex) => {
        positions.set(node.id, {
          x: anchorX[columnIndex],
          y: startY + rowIndex * gap,
          edgeIndex: rowIndex,
        });
      });
    });
    return positions;
  }, [filteredNodes]);

  const edgeIndexBySource = useMemo(() => {
    const counters = new Map<string, number>();
    const indexes = new Map<string, number>();
    semanticEdges.forEach((edge) => {
      const index = counters.get(edge.source) ?? 0;
      counters.set(edge.source, index + 1);
      indexes.set(semanticKey(edge.source, edge.target), index);
    });
    return indexes;
  }, [semanticEdges]);

  return (
    <section className="panel interactive-graph-panel evidence-chain-inspector">
      <div className="panel-title-row">
        <GitBranch size={18} />
        <h2>证据链检查器</h2>
        <span className="status-pill is-neutral">{showAll ? '高级全项目视图' : '主证据链视图'}</span>
      </div>
      <div className="graph-toolbar evidence-toolbar">
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
              style={{ '--kind-color': kindColor[kind] } as CSSProperties}
            >
              {kind}
            </button>
          ))}
        </div>
        <button className="subtle-toggle inline-toggle" type="button" onClick={() => setShowAll((value) => !value)}>
          {showAll ? '回到主证据链' : '高级全项目图谱'}
        </button>
      </div>
      <p className="panel-note">默认只检查“论点由什么证据支撑”：SEC/SEG 到 CLM，再到 EXP、DATA、FIG、CIT。重复关系、反向关系和证据内部关系会被收敛，避免线条误导。</p>

      <div className="evidence-inspector-layout">
        <div className="evidence-canvas-wrap">
          <svg viewBox={`0 0 ${canvasWidth} ${canvasHeight}`} role="img" aria-label="可交互证据链检查器">
            <defs>
              <filter id="evidence-card-shadow" x="-18%" y="-18%" width="136%" height="150%">
                <feDropShadow dx="0" dy="8" stdDeviation="8" floodColor="#101828" floodOpacity="0.10" />
              </filter>
            </defs>

            {laneLabels.map((lane, index) => (
              <g className={`evidence-lane ${lane.className}`} key={lane.key} transform={`translate(${laneX[index]} ${laneTop})`}>
                <rect width={laneWidth} height={laneHeight} rx="18" />
                <text className="evidence-lane-title" x="20" y="34">{lane.title}</text>
                <text className="evidence-lane-subtitle" x="20" y="56">{lane.subtitle}</text>
              </g>
            ))}

            {semanticEdges.map((edge) => {
              const source = layout.get(edge.source);
              const target = layout.get(edge.target);
              if (!source || !target || target.x <= source.x) return null;
              const edgeOffset = edgeIndexBySource.get(semanticKey(edge.source, edge.target)) ?? 0;
              const { d, arrow } = makePath(source, target, edgeOffset);
              const highlighted = connectedIds.has(edge.source) && connectedIds.has(edge.target);
              const dimmed = selected && !highlighted;
              return (
                <g key={semanticKey(edge.source, edge.target)} className={`evidence-flow-edge ${highlighted ? 'is-highlighted' : ''} ${dimmed ? 'is-muted' : ''}`}>
                  <path d={d} />
                  <polygon points={arrow} />
                </g>
              );
            })}

            {filteredNodes.map((node) => {
              const point = layout.get(node.id);
              if (!point) return null;
              const selectedNode = selected?.id === node.id;
              const related = connectedIds.has(node.id);
              const dimmed = selected && !selectedNode && !related;
              const status = nodeStatus(node, semanticEdges, issues);
              return (
                <g
                  key={node.id}
                  transform={`translate(${point.x - nodeWidth / 2} ${point.y - nodeHeight / 2})`}
                  className={`evidence-node-card ${selectedNode ? 'is-selected' : ''} ${related ? 'is-related' : ''} ${dimmed ? 'is-muted' : ''}`}
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
                    width={nodeWidth}
                    height={nodeHeight}
                    rx="13"
                    style={{ '--node-color': kindColor[node.kind] ?? '#475569' } as CSSProperties}
                    className={`evidence-node-shell is-${status}`}
                  />
                  <circle className={`evidence-node-dot is-${status}`} cx={nodeWidth - 20} cy="20" r="5.5" />
                  <text className="evidence-node-kind" x="16" y="22">{kindLabel[node.kind] ?? node.kind}</text>
                  <text className="evidence-node-id" x="16" y="43">{node.id}</text>
                  <text className="evidence-node-caption" x="16" y="60">{clampText(node.label, 22)}</text>
                </g>
              );
            })}
          </svg>
        </div>
        <EvidenceNodeDetail selected={selected} nodes={filteredNodes} edges={semanticEdges} issues={issues} />
      </div>
    </section>
  );
}
