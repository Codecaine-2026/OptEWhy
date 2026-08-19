export type CausalNode = {
  id: string;
  label: string;
  subsystem: string;
  abnormality: number;
  x: number;
  y: number;
};

export type CausalEdge = {
  id: string;
  source: string;
  target: string;
  weight: number;
  polarity: "positive" | "negative";
};

export type ImpactRow = {
  kpi: string;
  baseline: string;
  scenario: string;
  delta: string;
};

export type DominantPath = {
  path: string[];
  contributionRatio: number;
  signedImpact: number;
  confidence: number;
};

export type FeedbackLoop = {
  nodes: string[];
  loopType: "reinforcing" | "balancing" | string;
  strength: number;
  confidence: number;
};

export type CausalResult = {
  targetNodeId: string;
  observedDelta: number;
  dominantPaths: DominantPath[];
  feedbackLoops: FeedbackLoop[];
};

export type EvidenceRef = {
  documentId?: string | null;
  chunkId?: string | null;
  score?: number | null;
  relatedNodeIds: string[];
  relatedEdgeIds: string[];
};

export type ReasoningStep = {
  id: string;
  stepType: "dominant_path" | "feedback_loop" | string;
  summary: string;
  usedNodeIds: string[];
  usedEdgeIds: string[];
  evidenceRefs: EvidenceRef[];
  contributionRatio?: number | null;
  signedImpact?: number | null;
  loopType?: string | null;
  strength?: number | null;
  confidence?: number | null;
};

export type ReasoningTrace = {
  targetNodeId: string;
  steps: ReasoningStep[];
};

export type ReasoningNode = {
  id: string;
  label: string;
  subsystem: string;
  nodeType: string;
  abnormality: number;
  reasoningStepIds: string[];
};

export type ReasoningEdge = {
  id: string;
  sourceNodeId: string;
  targetNodeId: string;
  weight: number;
  polarity: "positive" | "negative" | string;
  confidence: number;
  contributionRatio?: number | null;
  signedImpact?: number | null;
  reasoningStepIds: string[];
};

export type ReasoningLoop = {
  id: string;
  nodeIds: string[];
  edgeIds: string[];
  loopType: "reinforcing" | "balancing" | string;
  strength: number;
  confidence: number;
};

export type VisualizationPayload = {
  highlightedNodes: string[];
  highlightedEdges: string[];
  focusSubgraphId: string | null;
  reasoningNodes: ReasoningNode[];
  reasoningEdges: ReasoningEdge[];
  loops: ReasoningLoop[];
};

export type QueryResponse = {
  analysisId: string;
  intent: string;
  answer: string;
  causalResult: CausalResult;
  evidence: Record<string, unknown>[];
  reasoningTrace: ReasoningTrace;
  visualization: VisualizationPayload;
};
