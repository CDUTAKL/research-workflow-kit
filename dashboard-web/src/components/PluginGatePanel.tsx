import { ExternalLink, PlugZap } from 'lucide-react';
import { postAction } from '../api/client';
import type { DashboardData, PluginRecommendation } from '../types';

const levelLabels: Record<string, string> = {
  required: '必须处理',
  recommended: '建议使用',
  optional: '可选增强',
};

const statusLabels: Record<string, string> = {
  recorded: '已记录',
  pending_required: '待补门禁',
  required: '必须处理',
  recommended: '建议使用',
  optional: '可选增强',
};

const recordOpenKeys: Array<[string, string]> = [
  ['plugin-review-log.md', 'pluginReviewLog'],
  ['plugin-gate-policy.md', 'pluginGatePolicy'],
  ['dashboard-ux-qa.md', 'dashboardUxQa'],
  ['data-quality-report.md', 'dataQualityReport'],
  ['metric-diagnostics.md', 'metricDiagnostics'],
  ['visual-design-review.md', 'visualDesignReview'],
];

function statusClass(item: PluginRecommendation) {
  if (item.status === 'recorded') return 'is-ok';
  if (item.status === 'pending_required') return 'is-blocked';
  if (item.level === 'recommended') return 'is-warning';
  return 'is-neutral';
}

function openKeyForRecord(record: string) {
  return recordOpenKeys.find(([needle]) => record.includes(needle))?.[1] ?? 'pluginReviewLog';
}

export function PluginGatePanel({ data }: { data: DashboardData }) {
  const recommendations = data.pluginRecommendations ?? [];
  const health = data.pluginGateHealth ?? {};
  return (
    <section className="panel plugin-gate-panel">
      <div className="panel-title-row">
        <PlugZap size={18} />
        <h2>插件建议</h2>
        <span className={`count-badge ${(health.pendingRequiredGates ?? 0) > 0 ? 'p0' : 'p1'}`}>
          {health.pendingRequiredGates ?? 0} 个必补
        </span>
      </div>
      <p className="panel-note">
        根据当前阶段和可能的改动类型推荐插件门禁；插件只做质量增强，不替代 Markdown/TSV/JSON 源记录。
      </p>
      <div className="plugin-health-row">
        <span>策略文件：{health.missingPolicy ? '缺失' : '存在'}</span>
        <span>审查日志：{health.missingReviewLog ? '缺失' : '存在'}</span>
        <span>可选建议：{health.optionalSuggestions ?? 0}</span>
      </div>
      <div className="plugin-list">
        {recommendations.length ? recommendations.map((item) => (
          <article className="plugin-row" key={`${item.plugin}-${item.stage}-${item.record}`}>
            <div>
              <strong>{item.plugin}</strong>
              <span>阶段 {item.stage} · {item.reason}</span>
            </div>
            <div className="plugin-actions">
              <span className={`status-pill ${statusClass(item)}`}>
                {statusLabels[item.status] ?? levelLabels[item.level] ?? item.status}
              </span>
              <button type="button" onClick={() => postAction('/api/open-path', { key: openKeyForRecord(item.record) })}>
                <ExternalLink size={15} /> 打开记录
              </button>
            </div>
            <p>{item.action}</p>
          </article>
        )) : <div className="empty-state">当前阶段没有必须处理的插件门禁</div>}
      </div>
      <div className="detail-actions">
        <button type="button" onClick={() => postAction('/api/open-path', { key: 'pluginGatePolicy' })}>
          <ExternalLink size={15} /> 打开插件策略
        </button>
        <button type="button" onClick={() => postAction('/api/open-path', { key: 'pluginReviewLog' })}>
          <ExternalLink size={15} /> 打开审查日志
        </button>
      </div>
    </section>
  );
}
