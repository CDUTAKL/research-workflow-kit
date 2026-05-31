import { CheckCircle2 } from 'lucide-react';
import type { DashboardData } from '../types';

export function SystemHealthPanel({ data }: { data: DashboardData }) {
  return (
    <section className="panel system-health-panel">
      <div className="panel-title-row">
        <CheckCircle2 size={18} />
        <h2>系统健康</h2>
      </div>
      <div className="skill-health">
        <div><strong>{data.skillHealth?.totalSkills ?? 0}</strong><span>Skill 总数</span></div>
        <div><strong>{data.skillHealth?.metadataIssues ?? 0}</strong><span>元数据问题</span></div>
        <div><strong>{data.skillHealth?.metadataWarnings ?? 0}</strong><span>元数据提醒</span></div>
        <div><strong>{data.skillHealth?.brokenReferences ?? 0}</strong><span>断裂引用</span></div>
        <div><strong>{data.skillHealth?.missingScripts ?? 0}</strong><span>缺失脚本</span></div>
        <div><strong>{data.skillHealth?.outdatedAssumptions ?? 0}</strong><span>旧工具假设</span></div>
      </div>
      <p className="panel-note">系统健康来自本地 skill audit 和 workflow doctor。它只检查结构一致性，不替代论文终审。</p>
    </section>
  );
}
