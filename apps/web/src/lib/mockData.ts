import type { CausalEdge, CausalNode } from "./types";

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
    label: "Internal Truck Travel Time",
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
    id: "berth_productivity",
    label: "Berth Productivity",
    subsystem: "Berth",
    abnormality: 0.1,
    x: 24,
    y: 558
  },
  {
    id: "vessel_turnaround_time",
    label: "Vessel Turnaround",
    subsystem: "Vessel Ops",
    abnormality: 0.3,
    x: 246,
    y: 558
  }
];
export const causalEdges: CausalEdge[] = [
  { id: "edge_weather_to_truck_travel_time", source: "weather_severity", target: "truck_travel_time", weight: 0.24, polarity: "positive" },
  { id: "edge_weather_to_qc_productivity", source: "weather_severity", target: "qc_productivity", weight: -0.18, polarity: "negative" },
  { id: "edge_weather_to_vessel_turnaround_time", source: "weather_severity", target: "vessel_turnaround_time", weight: 0.22, polarity: "positive" },
  { id: "edge_weather_to_yard_density", source: "weather_severity", target: "yard_density", weight: 0.18, polarity: "positive" },
  { id: "edge_arrival_delay_to_qc_waiting", source: "vessel_arrival_delay", target: "qc_waiting", weight: 0.3, polarity: "positive" },
  { id: "edge_berth_occupancy_to_yard_density", source: "berth_occupancy", target: "yard_density", weight: 0.42, polarity: "positive" },
  { id: "edge_berth_occupancy_to_vessel_turnaround_time", source: "berth_occupancy", target: "vessel_turnaround_time", weight: 0.34, polarity: "positive" },
  { id: "edge_yard_density_to_truck_travel_time", source: "yard_density", target: "truck_travel_time", weight: 0.58, polarity: "positive" },
  { id: "edge_truck_travel_time_to_qc_waiting", source: "truck_travel_time", target: "qc_waiting", weight: 0.55, polarity: "positive" },
  { id: "edge_qc_waiting_to_qc_productivity", source: "qc_waiting", target: "qc_productivity", weight: -0.62, polarity: "negative" },
  { id: "edge_qc_waiting_to_berth_occupancy", source: "qc_waiting", target: "berth_occupancy", weight: 0.28, polarity: "positive" },
  { id: "edge_qc_waiting_to_vessel_turnaround_time", source: "qc_waiting", target: "vessel_turnaround_time", weight: 0.36, polarity: "positive" },
  { id: "edge_qc_productivity_to_berth_productivity", source: "qc_productivity", target: "berth_productivity", weight: 0.58, polarity: "positive" },
  { id: "edge_qc_productivity_to_vessel_turnaround_time", source: "qc_productivity", target: "vessel_turnaround_time", weight: -0.52, polarity: "negative" }
];

