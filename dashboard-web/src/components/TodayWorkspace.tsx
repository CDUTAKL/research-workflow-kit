import { Activity, AlertTriangle, BookOpen, CheckCircle2, ChevronRight, Download, ExternalLink, FileText, GitBranch, RefreshCw } from 'lucide-react';
import { postAction } from '../api/client';
import type { DashboardData, Health } from '../types';

const healthLabels: Record<Health, string> = {
  ok: '健康',
  warning: '需关注',
  blocked: '已阻塞',
};

function clean(value = '', fallback = '待填写') {
  const text = value.replace(/`/g, '').trim();
  return text && text.toLowerCase() !== 'tbd' ? text : fallback;
}

function translateStage(value = '') {
  return clean(value, '请先设置当前阶段');
}

export function CurrentWorkspace({ data, onReload }: { data: DashboardData; onReload: () => void }) {
  const summary = data.currentWorkspaceSummary;
  const currentStage = translateStage(summary?.stage ?? data.currentStatus['Current stage']);
  const currentFocus = clean(summary?.focus ?? data.currentStatus['Active focus'], '当前目标还未填写');
  const blocker = clean(summary?.blocker ?? data.currentStatus['Main blocker'], '暂无明确阻塞项');
  const nextAction = clean(summary?.nextAction ?? data.currentStatus['Next concrete action'], '运行快速健康检查，确认下一步');
  const auditTier = clean(summary?.auditTier ?? data.currentStatus['Current audit tier'], 'quick / advisor / final');
  const p0Count = data.issues.p0.length;
  const p1Count = data.issues.p1.length;
  const recentExperiment = data.recentExperiments[0];
  const evidenceGapCount = summary?.evidenceGapCount ?? p0Count + p1Count;
  const topRecommendation = data.nextRecommendations?.[0] ?? nextAction;
  const stageActions = data.activeStageWorkspace?.recommendedActions?.length
    ? data.activeStageWorkspace.recommendedActions
    : [topRecommendation, '补齐当前阶段关键文件记录', '运行快速健康检查'];
  const actionStatus = ['已完成', '进行中', '待开始', '待开始', '待开始'];

  async function run(endpoint: string, payload: object = {}) {
    await postAction(endpoint, payload);
    onReload();
  }

  return (
    <section className="today-workspace">
      <div className="today-primary">
        <div className="panel-title-row">
          <FileText size={20} />
          <h2>当前科研工作区</h2>
          <span className="orchestrator-chip">research-workflow-orchestrator · 12 阶段编排</span>
        </div>
        <p className="workspace-label">阶段目标</p>
        <p className="workspace-objective">{topRecommendation}</p>
        <p className="workspace-label">本阶段任务</p>
        <div className="task-checklist">
          {stageActions.slice(0, 5).map((action, index) => (
            <article className={index === 1 ? 'is-current' : ''} key={`${action}-${index}`}>
              <span className="task-dot">{index < 2 ? <CheckCircle2 size={15} /> : ''}</span>
              <strong>{clean(action)}</strong>
              <em>{actionStatus[index] ?? '待开始'}</em>
            </article>
          ))}
        </div>
        <div className="today-actions">
          <button type="button" onClick={() => run('/api/refresh-dashboard')}>
            <RefreshCw size={16} /> 刷新检查
          </button>
          <button type="button" onClick={() => postAction('/api/open-path', { key: 'dailyWorkflowEntry' })}>
            <Activity size={16} /> 记录进展
          </button>
          <button type="button" onClick={() => postAction('/api/open-path', { key: 'dashboard' })}>
            <ExternalLink size={16} /> 打开关键文件
          </button>
        </div>
      </div>
      <div className="today-side">
        <h3>快速入口</h3>
        <div className="quick-link-list">
          <button type="button" onClick={() => postAction('/api/open-path', { key: 'sectionCitationMap' })}>
            <BookOpen size={15} /> <span>打开章节引用</span> <ChevronRight size={15} />
          </button>
          <button type="button" onClick={() => postAction('/api/open-path', { key: 'claimMap' })}>
            <GitBranch size={15} /> <span>进入证据链</span> <ChevronRight size={15} />
          </button>
          <button type="button" onClick={() => postAction('/api/open-path', { key: 'experimentReports' })}>
            <Activity size={15} /> <span>实验报告</span> <ChevronRight size={15} />
          </button>
          <button type="button" onClick={() => postAction('/api/open-path', { key: 'weeklyReview' })}>
            <Download size={15} /> <span>导出阶段报告</span> <ChevronRight size={15} />
          </button>
        </div>
        <div className="today-status-row">
          <span className={`health-badge ${data.health}`}>
            {data.health === 'ok' ? <CheckCircle2 size={15} /> : <AlertTriangle size={15} />}
            {healthLabels[data.health]}
          </span>
          <span className="status-pill is-neutral">审计：{auditTier}</span>
        </div>
        <div className="today-brief-grid">
          <article><span>当前目标</span><strong>{currentFocus}</strong></article>
          <article><span>下一步动作</span><strong>{nextAction}</strong></article>
          <article><span>阻塞项</span><strong>{blocker}</strong></article>
          <article><span>待补证据</span><strong>{evidenceGapCount} 项，其中 {p0Count} 个 P0 / {p1Count} 个 P1</strong></article>
          <article><span>最近实验</span><strong>{summary?.recentExperiment || (recentExperiment ? `${recentExperiment.id} · ${clean(recentExperiment.status, '待处理')}` : '暂无实验记录')}</strong></article>
        </div>
      </div>
    </section>
  );
}
