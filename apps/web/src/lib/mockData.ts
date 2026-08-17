import type { CausalEdge, CausalNode, EvidenceItem, ImpactRow, LoopItem, PathItem } from "./types";

export const causalNodes: CausalNode[] = [
  { id: "yard_density", label: "Yard Density", subsystem: "Yard", abnormality: 0.85, x: 70, y: 110 },
  {
    id: "truck_travel_time",
    label: "Truck Travel Time",
    subsystem: "Transport",
    abnormality: 0.62,
    x: 320,
    y: 110
  },
  { id: "qc_waiting", label: "QC Waiting", subsystem: "Quay", abnormality: 0.58, x: 560, y: 110 },
  {
    id: "qc_productivity",
    label: "QC Productivity",
    subsystem: "Quay",
    abnormality: -0.15,
    x: 800,
    y: 110
  },
  { id: "qc4_availability", label: "QC4 Availability", subsystem: "Equipment", abnormality: -0.31, x: 560, y: 270 }
];

export const causalEdges: CausalEdge[] = [
  { id: "e1", source: "yard_density", target: "truck_travel_time", weight: 0.78, polarity: "positive" },
  { id: "e2", source: "truck_travel_time", target: "qc_waiting", weight: 0.66, polarity: "positive" },
  { id: "e3", source: "qc_waiting", target: "qc_productivity", weight: -0.71, polarity: "negative" },
  { id: "e4", source: "qc4_availability", target: "qc_productivity", weight: 0.48, polarity: "positive" }
];

export const paths: PathItem[] = [
  {
    id: "path_1",
    label: "Yard congestion to QC productivity",
    contribution: 0.46,
    nodes: ["Yard Density", "Truck Travel Time", "QC Waiting", "QC Productivity"]
  },
  {
    id: "path_2",
    label: "QC4 availability to QC productivity",
    contribution: 0.27,
    nodes: ["QC4 Availability", "QC Productivity"]
  }
];

export const loops: LoopItem[] = [
  {
    id: "loop_1",
    label: "Yard congestion reinforcing loop",
    type: "reinforcing",
    strength: 0.37
  }
];

export const impactRows: ImpactRow[] = [
  { kpi: "Block B Density", baseline: "85%", scenario: "72%", delta: "-13%" },
  { kpi: "Truck Travel Time", baseline: "31 min", scenario: "29 min", delta: "-6%" },
  { kpi: "QC Waiting", baseline: "18 min", scenario: "17 min", delta: "-4%" },
  { kpi: "QC Productivity", baseline: "27.4 mph", scenario: "28.4 mph", delta: "+3.7%" },
  { kpi: "Vessel Turnaround", baseline: "18h 20m", scenario: "18h 01m", delta: "-19 min" }
];

export const evidence: EvidenceItem[] = [
  {
    id: "ev_1",
    title: "Shift report",
    text: "Block B and Block C operated above planned density during the current shift.",
    score: 0.84
  },
  {
    id: "ev_2",
    title: "Maintenance note",
    text: "QC4 availability was reduced by a mock equipment event in the demo dataset.",
    score: 0.79
  }
];

