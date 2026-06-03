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

export interface SectionCitationCoverage {
  sectionId: string;
  segmentId: string;
  strong: string;
  partial: string;
  background: string;
  contradictory: string;
  zoteroChecked: string;
  readerChecked: string;
  status: string;
  candidateReferences?: string;
  identifiers?: string;
  zoteroStatus?: string;
  readerStatus?: string;
  nextAction?: string;
}

export interface PluginRecommendation {
  plugin: string;
  stage: string;
  reason: string;
  action: string;
  record: string;
  required: boolean;
  level: string;
  status: string;
}

export interface PluginGateHealth {
  missingPolicy?: boolean;
  missingReviewLog?: boolean;
  pendingRequiredGates?: number;
  optionalSuggestions?: number;
}

export interface ConsoleFileLayer {
  layer: string;
  when: string;
  files: string;
  rule: string;
}

export interface ExperimentComparison {
  id: string;
  baseline: string;
  metric: string;
  baselineValue: string;
  newValue: string;
  delta: string;
  verifyStatus: string;
  guardStatus: string;
  environmentSnapshot: string;
  status: string;
  nextAction: string;
  path: string;
}

export interface WeeklyReview {
  summary: Record<string, string>;
  recent: Array<{
    week: string;
    focus: string;
    completed: string;
    evidenceStronger: string;
    risk: string;
    bestExperiment: string;
    nextActions: string;
    filesToIgnore: string;
    notes: string;
  }>;
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
    pluginRecommendations?: number;
    experimentComparisons?: number;
  };
  currentStatus: Record<string, string>;
  activeStageWorkspace?: StageWorkspace;
  currentWorkspaceSummary?: {
    stage: string;
    focus: string;
    blocker: string;
    nextAction: string;
    auditTier: string;
    evidenceGapCount: number;
    recentExperiment: string;
  };
  nextRecommendations?: string[];
  citationCoverageSummary?: {
    missingStrong: number;
    candidate: number;
    verified: number;
    risk: number;
  };
  focusedEvidenceGraph?: {
    nodes: EvidenceNode[];
    edges: EvidenceEdge[];
  };
  stages: WorkflowStage[];
  issues: {
    p0: string[];
    p1: string[];
  };
  summary: string;
  recentExperiments: WorkflowRecord[];
  experimentReports?: WorkflowRecord[];
  experimentComparisons?: ExperimentComparison[];
  citationSuggestions?: CitationSuggestion[];
  sectionCitationCoverage?: SectionCitationCoverage[];
  consoleFileLayers?: ConsoleFileLayer[];
  weeklyReview?: WeeklyReview;
  pluginRecommendations?: PluginRecommendation[];
  pluginGateHealth?: PluginGateHealth;
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
