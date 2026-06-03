import { Activity, BookOpen, Database, FileText, GitBranch, ListChecks, Save, Settings } from 'lucide-react';

export type DashboardTab =
  | 'overview'
  | 'today'
  | 'citation'
  | 'experiments'
  | 'graph'
  | 'handoff'
  | 'editor'
  | 'health';

const tabs: Array<{ id: DashboardTab; label: string; icon: JSX.Element }> = [
  { id: 'overview', label: '总览', icon: <Activity size={16} /> },
  { id: 'today', label: '当前工作区', icon: <ListChecks size={16} /> },
  { id: 'citation', label: '文献引用', icon: <BookOpen size={16} /> },
  { id: 'experiments', label: '实验闭环', icon: <Database size={16} /> },
  { id: 'graph', label: '证据图谱', icon: <GitBranch size={16} /> },
  { id: 'handoff', label: '最终交接', icon: <Save size={16} /> },
  { id: 'editor', label: '记录编辑', icon: <FileText size={16} /> },
  { id: 'health', label: '系统健康', icon: <Settings size={16} /> },
];

export function DashboardTabs({
  activeTab,
  onChange,
}: {
  activeTab: DashboardTab;
  onChange: (tab: DashboardTab) => void;
}) {
  return (
    <nav className="dashboard-tabs" aria-label="Dashboard sections">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          className={activeTab === tab.id ? 'is-active' : ''}
          onClick={() => onChange(tab.id)}
          type="button"
        >
          {tab.icon}
          {tab.label}
        </button>
      ))}
    </nav>
  );
}
