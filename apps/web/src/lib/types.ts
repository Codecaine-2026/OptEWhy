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

export type PathItem = {
  id: string;
  label: string;
  contribution: number;
  nodes: string[];
};

export type LoopItem = {
  id: string;
  label: string;
  type: "reinforcing" | "balancing";
  strength: number;
};

export type ImpactRow = {
  kpi: string;
  baseline: string;
  scenario: string;
  delta: string;
};

export type EvidenceItem = {
  id: string;
  title: string;
  text: string;
  score: number;
};

