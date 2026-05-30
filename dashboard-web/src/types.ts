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

export interface StageWorkspace {
  stage: string;
  name: string;
  fileKeys: string[];
  commands: string[];
  recommendedActions: string[];
  issues: {
    p0: string[];
    p1: string[];
  };
}

export interface CitationSuggestion {
  rank: string;
  score: string;
  sectionId: string;
  segmentId: string;
  candidateReference: string;
  identifier: string;
  source: string;
  status: string;
  suggestedUse: string;
  reasons: string;
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
    finalArtifacts?: number;
    idLifecycleRecords?: number;
    skillIssues?: number;
    citationSuggestions?: number;
  };
  currentStatus: Record<string, string>;
  activeStageWorkspace?: StageWorkspace;
  stages: WorkflowStage[];
  issues: {
    p0: string[];
    p1: string[];
  };
  summary: string;
  recentExperiments: WorkflowRecord[];
  experimentReports?: WorkflowRecord[];
  citationSuggestions?: CitationSuggestion[];
  finalArtifacts?: WorkflowRecord[];
  handoffPackage?: {
    exists: string;
    latestZip: string;
    latestDir: string;
    verifyReport: string;
  };
  skillHealth?: {
    totalSkills: number;
    metadataIssues?: number;
    metadataWarnings?: number;
    brokenReferences: number;
    missingScripts: number;
    outdatedAssumptions: number;
    reportPath?: string;
  };
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
