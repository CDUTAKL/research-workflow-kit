import { BookOpen, ExternalLink, RefreshCw } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { postAction } from '../api/client';
import type { SectionCitationCoverage } from '../types';

const columns: Array<{ key: keyof SectionCitationCoverage; label: string }> = [
  { key: 'strong', label: '强支持' },
  { key: 'partial', label: '部分支持' },
  { key: 'background', label: '背景引用' },
  { key: 'contradictory', label: '限制/反例' },
  { key: 'zoteroChecked', label: 'Zotero' },
  { key: 'readerChecked', label: 'Reader/Scite' },
];

const statusLabels: Record<string, string> = {
  missing: '缺失',
  candidate: '候选',
  verified: '已验证',
  risk: '有风险',
};

function riskScore(row: SectionCitationCoverage) {
  let score = 0;
  if (cellClass(row.strong) === 'coverage-missing') score += 8;
  if (cellClass(row.zoteroChecked) === 'coverage-missing') score += 4;
  if (cellClass(row.readerChecked) === 'coverage-missing') score += 4;
  if (cellClass(row.strong) === 'coverage-candidate') score += 3;
  if (cellClass(row.partial) === 'coverage-candidate') score += 2;
  if (cellClass(row.contradictory) === 'coverage-risk' || cellClass(row.status) === 'coverage-risk') score += 6;
  if (cellClass(row.background) === 'coverage-verified' && cellClass(row.strong) !== 'coverage-verified') score += 2;
  return score;
}

function cellClass(value = '') {
  const normalized = value.toLowerCase();
  if (normalized === 'verified') return 'coverage-verified';
  if (normalized === 'candidate') return 'coverage-candidate';
  if (normalized === 'risk') return 'coverage-risk';
  return 'coverage-missing';
}

function display(value = '', fallback = '待补') {
  const normalized = value.trim().toLowerCase();
  return statusLabels[normalized] ?? (value.trim() || fallback);
}

export function SectionCitationHeatmap({
  coverage,
  onReload,
}: {
  coverage: SectionCitationCoverage[];
  onReload: () => void;
}) {
  const [selected, setSelected] = useState<SectionCitationCoverage | null>(coverage[0] ?? null);
  const rows = useMemo(() => [...coverage].sort((a, b) => riskScore(b) - riskScore(a)).slice(0, 30), [coverage]);
  const summary = useMemo(() => {
    return coverage.reduce(
      (acc, row) => {
        if (cellClass(row.strong) === 'coverage-missing') acc.missingStrong += 1;
        if (Object.values(row).some((value) => cellClass(String(value ?? '')) === 'coverage-candidate')) acc.candidate += 1;
        if (cellClass(row.status) === 'coverage-verified' || cellClass(row.strong) === 'coverage-verified') acc.verified += 1;
        if (cellClass(row.status) === 'coverage-risk' || cellClass(row.contradictory) === 'coverage-risk') acc.risk += 1;
        return acc;
      },
      { missingStrong: 0, candidate: 0, verified: 0, risk: 0 },
    );
  }, [coverage]);

  useEffect(() => {
    if (!selected && coverage.length) setSelected(coverage[0]);
  }, [coverage, selected]);

  async function refreshSuggestions() {
    const sectionId = selected?.sectionId ?? '';
    await postAction('/api/suggest-section-citations', sectionId ? { section_id: sectionId } : {});
    onReload();
  }

  return (
    <section className="panel citation-heatmap-panel">
      <div className="panel-title-row">
        <BookOpen size={18} />
        <h2>章节引用缺口</h2>
      </div>
      <div className="coverage-summary">
        <article><strong>{summary.missingStrong}</strong><span>缺强支持</span></article>
        <article><strong>{summary.candidate}</strong><span>有候选待确认</span></article>
        <article><strong>{summary.verified}</strong><span>已验证</span></article>
        <article><strong>{summary.risk}</strong><span>有风险</span></article>
      </div>
      <p className="panel-note">默认按缺口风险排序：缺强支持、缺 Zotero、缺 Reader/Scite 和限制/反例会排在前面。</p>
      <div className="heatmap-layout">
        <div className="heatmap-table-wrap">
          {rows.length ? (
            <table className="heatmap-table">
              <thead>
                <tr>
                  <th>章节 / 段落</th>
                  {columns.map((column) => <th key={String(column.key)}>{column.label}</th>)}
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={`${row.sectionId}-${row.segmentId || 'section'}`}>
                    <th>
                      <button type="button" className="link-button" onClick={() => setSelected(row)}>
                        {row.segmentId || row.sectionId}
                      </button>
                    </th>
                    {columns.map((column) => (
                      <td key={String(column.key)}>
                        <button
                          type="button"
                          className={`coverage-cell ${cellClass(String(row[column.key] ?? ''))}`}
                          onClick={() => setSelected(row)}
                          aria-label={`${row.segmentId || row.sectionId} ${column.label}: ${display(String(row[column.key] ?? ''))}`}
                        >
                          {display(String(row[column.key] ?? ''))}
                        </button>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="empty-state">暂无覆盖数据，请先补充 section-citation-map.md</div>
          )}
        </div>
        <aside className="heatmap-detail">
          <p className="eyebrow">当前单元详情</p>
          <h3>{selected ? `${selected.sectionId}${selected.segmentId ? ` / ${selected.segmentId}` : ''}` : '未选择'}</h3>
          <dl>
            <dt>整体状态</dt>
            <dd>{display(selected?.status ?? '')}</dd>
            <dt>候选论文</dt>
            <dd>{selected?.candidateReferences || '暂无'}</dd>
            <dt>标识符</dt>
            <dd>{selected?.identifiers || '暂无'}</dd>
            <dt>Zotero</dt>
            <dd>{selected?.zoteroStatus || display(selected?.zoteroChecked ?? '')}</dd>
            <dt>Reader / Scite</dt>
            <dd>{selected?.readerStatus || display(selected?.readerChecked ?? '')}</dd>
            <dt>推荐下一步</dt>
            <dd>{selected?.nextAction || '确认候选文献后写入正式引用表'}</dd>
          </dl>
          <div className="detail-actions">
            <button type="button" onClick={refreshSuggestions}><RefreshCw size={15} /> 刷新推荐</button>
            <button type="button" onClick={() => postAction('/api/open-path', { key: 'sectionCitationMap' })}><ExternalLink size={15} /> 打开章节表</button>
            <button type="button" onClick={() => postAction('/api/open-path', { key: 'citationProvenance' })}><ExternalLink size={15} /> 打开引用溯源</button>
          </div>
        </aside>
      </div>
    </section>
  );
}
