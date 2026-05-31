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
  const rows = useMemo(() => coverage.slice(0, 30), [coverage]);

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
        <h2>章节引用覆盖</h2>
      </div>
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
