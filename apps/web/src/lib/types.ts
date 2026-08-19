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
