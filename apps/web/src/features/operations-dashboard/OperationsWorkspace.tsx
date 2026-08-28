"use client";

import { Ship } from "lucide-react";
import { useState } from "react";
import { CausalMapCanvas } from "@/features/causal-map/CausalMapCanvas";
import { CopilotPanel } from "@/features/copilot/CopilotPanel";
import { ScenarioImpactTable } from "@/features/scenario-simulator/ScenarioImpactTable";
import { simulateScenario } from "@/lib/api";
import { causalEdges, causalNodes, impactRows } from "@/lib/mockData";
import type { VisualizationPayload } from "@/lib/types";

export function OperationsWorkspace() {
  const [visualization, setVisualization] = useState<VisualizationPayload | null>(null);
  const [scenarioRows, setScenarioRows] = useState(impactRows);
  const [isScenarioLoading, setIsScenarioLoading] = useState(false);
  const [scenarioStatus, setScenarioStatus] = useState("");

  async function handleScenario(nodeId: string, value: number) {
    setIsScenarioLoading(true);
    setScenarioStatus("");
    try {
      const response = await simulateScenario(`Improve ${nodeId} by ${Math.round(value * 100)}%`, {
        nodeId,
        operation: "decrease_relative",
        value
      });
      setScenarioRows(
        causalNodes.map((node) => {
          const baseline = response.baselineState[node.id] ?? 0;
          const scenario = response.scenarioState[node.id] ?? baseline;
          const delta = scenario - baseline;
          return {
            kpi: node.label,
            baseline: baseline.toFixed(2),
            scenario: scenario.toFixed(2),
            delta: `${delta >= 0 ? "+" : ""}${delta.toFixed(2)}`
          };
        })
      );
      setScenarioStatus("Scenario results are shown as normalized causal-state values.");
    } catch (error) {
      setScenarioStatus(error instanceof Error ? error.message : "The scenario request failed.");
    } finally {
      setIsScenarioLoading(false);
    }
  }

  return (
    <main className="workspace">
      <header className="topbar">
        <div className="brand">
          <Ship size={22} />
          <div>
            <strong>OptEWhy</strong>
            <span>Port operations copilot</span>
          </div>
        </div>
      </header>

      <section className="mainGrid">
        <section className="copilotArea">
          <CopilotPanel onResponse={(response) => setVisualization(response.visualization)} />
        </section>

        <section className="mapPanel">
          <div className="mapHeader">
            <h2>Causal Graph</h2>
            <span>{visualization ? "Analysis highlights" : "8 modeled nodes"}</span>
          </div>
          <CausalMapCanvas
            nodes={causalNodes}
            edges={causalEdges}
            highlightedNodeIds={visualization?.highlightedNodes}
            highlightedEdgeIds={visualization?.highlightedEdges}
          />
        </section>
      </section>

      <section className="bottomPanel">
        <ScenarioImpactTable
          rows={scenarioRows}
          onSimulate={handleScenario}
          isLoading={isScenarioLoading}
          statusMessage={scenarioStatus}
        />
      </section>
    </main>
  );
}
