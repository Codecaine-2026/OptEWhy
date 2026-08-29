import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { ReasoningNode, ReasoningTrace, ScenarioResponse } from "@/lib/types";
import { ScenarioImpactTable } from "./ScenarioImpactTable";

const scenario: ScenarioResponse = {
  scenarioId: "scenario_demo_001",
  structuredIntervention: {
    interventions: [{ node_id: "yard_density", operation: "decrease_relative", value: 0.2 }]
  },
  predictedImpact: { yard_density: -0.15, truck_travel_time: -0.08, qc_productivity: 0.12 },
  baselineState: {},
  scenarioState: {},
  propagationFrames: []
};

const reasoningTrace: ReasoningTrace = {
  targetNodeId: "qc_productivity",
  steps: [
    {
      id: "path_1",
      stepType: "dominant_path",
      summary: "Yard density affects truck travel time and QC productivity.",
      usedNodeIds: ["yard_density", "truck_travel_time", "qc_productivity"],
      usedEdgeIds: [],
      evidenceRefs: []
    }
  ]
};

const reasoningNodes: ReasoningNode[] = [
  { id: "yard_density", label: "Yard Density", subsystem: "Yard", nodeType: "state", abnormality: 0, reasoningStepIds: [] },
  { id: "truck_travel_time", label: "Truck Travel Time", subsystem: "Transport", nodeType: "delay", abnormality: 0, reasoningStepIds: [] },
  { id: "qc_productivity", label: "QC Productivity", subsystem: "Quay", nodeType: "kpi", abnormality: 0, reasoningStepIds: [] }
];

describe("ScenarioImpactTable", () => {
  it("renders a causal explanation and a scrollable impact table", () => {
    const { container } = render(
      <ScenarioImpactTable
        rows={[{ kpi: "Yard Density", baseline: "0.55", scenario: "0.40", delta: "-0.15" }]}
        scenario={scenario}
        reasoningTrace={reasoningTrace}
        reasoningNodes={reasoningNodes}
      />
    );

    expect(screen.getByText("Chat-requested simulation")).toBeTruthy();
    expect(screen.getByText("Why these values change")).toBeTruthy();
    expect(screen.getByLabelText("Projected causal chain").textContent).toContain("Yard Density");
    expect(container.querySelector(".impactTableScroll")).toBeTruthy();
  });

  it("highlights decreased and increased KPI rows", () => {
    render(
      <ScenarioImpactTable
        rows={[
          { kpi: "Yard Density", baseline: "0.55", scenario: "0.40", delta: "-0.15" },
          { kpi: "QC Productivity", baseline: "0.40", scenario: "0.52", delta: "+0.12" },
          { kpi: "Berth Occupancy", baseline: "0.50", scenario: "0.50", delta: "0.00" }
        ]}
        scenario={scenario}
        reasoningTrace={reasoningTrace}
        reasoningNodes={reasoningNodes}
      />
    );

    expect(screen.getByRole("row", { name: /Yard Density/ }).className).toBe("impactRow--decreased");
    expect(screen.getByRole("row", { name: /QC Productivity/ }).className).toBe("impactRow--increased");
    expect(screen.getByRole("row", { name: /Berth Occupancy/ }).className).toBe("");
  });
});
