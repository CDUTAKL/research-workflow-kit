export type Health = 'ok' | 'warning' | 'blocked';

export interface EvidenceNode {
  id: string;
  kind: string;
  label: string;
}

export interface EvidenceEdge {
  source: string;
  target: string;
  relation: string;
}

export interface WorkflowStage {
  stage: string;
  name: string;
  status: string;
  record: string;
  notes: string;
}

export interface WorkflowRecord {
  id: string;
  status?: string;
  row?: string;
  output?: string;
  claim?: string;
  coverage?: string;
  hash?: string;
  access?: string;
  experiments?: string;
  figures?: string;
  literature?: string;
}

export interface DashboardData {
  generatedAt: string;
  health: Health;
  counts: {
    claims: number;
    experiments: number;
    datasets: number;
    figures: number;
    sections: number;
    graphNodes: number;
    graphEdges: number;
  };
  currentStatus: Record<string, string>;
  stages: WorkflowStage[];
  issues: {
    p0: string[];
    p1: string[];
  };
  summary: string;
  recentExperiments: WorkflowRecord[];
  records: {
    claims?: WorkflowRecord[];
    experiments?: WorkflowRecord[];
    datasets?: WorkflowRecord[];
    figures?: WorkflowRecord[];
    sections?: WorkflowRecord[];
  };
  graph: {
    nodes: EvidenceNode[];
    edges: EvidenceEdge[];
  };
  links: Record<string, string>;
}
