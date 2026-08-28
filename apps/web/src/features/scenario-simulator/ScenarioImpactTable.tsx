"use client";

import type { ImpactRow } from "@/lib/types";
import { useState } from "react";

type Props = {
  rows: ImpactRow[];
  onSimulate?: (nodeId: string, value: number) => void;
  isLoading?: boolean;
  statusMessage?: string;
};

const interventionOptions = [
  { id: "yard_density", label: "Yard Density" },
  { id: "truck_travel_time", label: "Truck Travel Time" },
  { id: "qc_waiting", label: "QC Waiting" },
  { id: "berth_occupancy", label: "Berth Occupancy" }
];

export function ScenarioImpactTable({ rows, onSimulate, isLoading = false, statusMessage }: Props) {
  const [nodeId, setNodeId] = useState("yard_density");
  const [percentage, setPercentage] = useState("15");

  function handleSubmit() {
    const value = Number(percentage) / 100;
    if (onSimulate && Number.isFinite(value) && value > 0 && value <= 1) {
      onSimulate(nodeId, value);
    }
  }

  return (
    <section className="impactTable">
      <div className="panelHeader">
        <h2>Scenario Impact</h2>
        <span>Baseline vs simulation</span>
      </div>
      <div className="scenarioControls">
        <label>
          Improve
          <select value={nodeId} onChange={(event) => setNodeId(event.target.value)} disabled={isLoading}>
            {interventionOptions.map((option) => (
              <option key={option.id} value={option.id}>{option.label}</option>
            ))}
          </select>
        </label>
        <label>
          By (%)
          <input
            aria-label="Scenario percentage"
            type="number"
            min="1"
            max="100"
            value={percentage}
            onChange={(event) => setPercentage(event.target.value)}
            disabled={isLoading}
          />
        </label>
        <button type="button" onClick={handleSubmit} disabled={isLoading || !onSimulate}>
          {isLoading ? "Simulating..." : "Run scenario"}
        </button>
      </div>
      {statusMessage ? <p className="scenarioStatus" role="status">{statusMessage}</p> : null}
      <table>
        <thead>
          <tr>
            <th>KPI</th>
            <th>Baseline</th>
            <th>Scenario</th>
            <th>Delta</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.kpi}>
              <td>{row.kpi}</td>
              <td>{row.baseline}</td>
              <td>{row.scenario}</td>
              <td>{row.delta}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
