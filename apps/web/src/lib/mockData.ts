import type { CausalEdge, CausalNode, ImpactRow } from "./types";

export const causalNodes: CausalNode[] = [
  { id: "weather_severity", label: "Weather Severity", subsystem: "External", abnormality: 0.2, x: 24, y: 30 },
  {
    id: "vessel_arrival_delay",
    label: "Vessel Arrival Delay",
    subsystem: "Vessel Ops",
    abnormality: 0.15,
    x: 246,
    y: 30
  },
  { id: "berth_occupancy", label: "Berth Occupancy", subsystem: "Berth", abnormality: 0.65, x: 24, y: 162 },
  { id: "yard_density", label: "Yard Density", subsystem: "Yard", abnormality: 0.55, x: 24, y: 294 },
  {
    id: "truck_travel_time",
    label: "Truck Travel Time",
    subsystem: "Transport",
    abnormality: 0.4,
    x: 24,
    y: 426
  },
  { id: "qc_waiting", label: "QC Waiting", subsystem: "Quay", abnormality: 0.35, x: 246, y: 294 },
  {
    id: "qc_productivity",
    label: "QC Productivity",
    subsystem: "Quay",
    abnormality: -0.1,
    x: 246,
    y: 426
  },
  {
    id: "vessel_turnaround_time",
    label: "Vessel Turnaround",
    subsystem: "Vessel Ops",
    abnormality: 0.3,
    x: 135,
    y: 558
  }
];

export const causalEdges: CausalEdge[] = [
  { id: "weather_to_truck", source: "weather_severity", target: "truck_travel_time", weight: 0.24, polarity: "positive" },
  { id: "weather_to_productivity", source: "weather_severity", target: "qc_productivity", weight: -0.18, polarity: "negative" },
  { id: "weather_to_turnaround", source: "weather_severity", target: "vessel_turnaround_time", weight: 0.22, polarity: "positive" },
  { id: "arrival_to_waiting", source: "vessel_arrival_delay", target: "qc_waiting", weight: 0.3, polarity: "positive" },
  { id: "berth_to_yard", source: "berth_occupancy", target: "yard_density", weight: 0.42, polarity: "positive" },
  { id: "berth_to_turnaround", source: "berth_occupancy", target: "vessel_turnaround_time", weight: 0.34, polarity: "positive" },
  { id: "yard_to_truck", source: "yard_density", target: "truck_travel_time", weight: 0.58, polarity: "positive" },
  { id: "truck_to_waiting", source: "truck_travel_time", target: "qc_waiting", weight: 0.55, polarity: "positive" },
  { id: "waiting_to_productivity", source: "qc_waiting", target: "qc_productivity", weight: -0.62, polarity: "negative" },
  { id: "waiting_to_berth", source: "qc_waiting", target: "berth_occupancy", weight: 0.28, polarity: "positive" },
  { id: "waiting_to_turnaround", source: "qc_waiting", target: "vessel_turnaround_time", weight: 0.36, polarity: "positive" },
  { id: "productivity_to_turnaround", source: "qc_productivity", target: "vessel_turnaround_time", weight: -0.52, polarity: "negative" }
];

export const impactRows: ImpactRow[] = [
  { kpi: "Yard Density", baseline: "85%", scenario: "72%", delta: "-13%", type: "improvement" },
  { kpi: "Truck Travel Time", baseline: "31 min", scenario: "29 min", delta: "-6%", type: "improvement" },
  { kpi: "QC Waiting", baseline: "18 min", scenario: "17 min", delta: "-4%", type: "improvement" },
  { kpi: "QC Productivity", baseline: "27.4 mph", scenario: "28.4 mph", delta: "+3.7%", type: "improvement" },
  { kpi: "Vessel Turnaround", baseline: "18h 20m", scenario: "18h 01m", delta: "-19 min", type: "improvement" },
  {
    kpi: "Gate Retrieval Delay",
    baseline: "12.0 min",
    scenario: "12.3 min",
    delta: "+2.0%",
    type: "warning",
    description: "Tradeoff: Block D container transfer load"
  }
];
