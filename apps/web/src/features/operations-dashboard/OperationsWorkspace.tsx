"use client";

import { Ship } from "lucide-react";
import { useState } from "react";
import { CausalMapCanvas } from "@/features/causal-map/CausalMapCanvas";
import { CopilotPanel } from "@/features/copilot/CopilotPanel";
import { EvidenceDrawer } from "@/features/evidence/EvidenceDrawer";
import { ScenarioImpactTable } from "@/features/scenario-simulator/ScenarioImpactTable";
import { causalEdges, causalNodes } from "@/lib/mockData";
import type { EvidenceItem, ScenarioResponse, VisualizationPayload } from "@/lib/types";

export function OperationsWorkspace() {
  const [visualization, setVisualization] = useState<VisualizationPayload | null>(null);
  const [scenario, setScenario] = useState<ScenarioResponse | null>(null);
  const [scenarioExplanation, setScenarioExplanation] = useState("");
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceItem | null>(null);
  const scenarioRows = scenario
    ? causalNodes.map((node) => {
        const baseline = scenario.baselineState[node.id] ?? 0;
        const simulated = scenario.scenarioState[node.id] ?? baseline;
        const delta = simulated - baseline;
        return {
          kpi: node.label,
          baseline: baseline.toFixed(2),
          scenario: simulated.toFixed(2),
          delta: `${delta >= 0 ? "+" : ""}${delta.toFixed(2)}`
        };
      })
    : [];

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
          <CopilotPanel
            onResponse={(response) => {
              setVisualization(response.visualization);
              setScenario(response.scenario ?? null);
              setScenarioExplanation(response.scenario ? response.answer : "");
            }}
            onSelectEvidence={setSelectedEvidence}
          />
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

      {scenario ? (
        <section className="bottomPanel">
          <ScenarioImpactTable rows={scenarioRows} scenarioExplanation={scenarioExplanation} />
        </section>
      ) : null}
      <EvidenceDrawer
        isOpen={selectedEvidence !== null}
        evidence={selectedEvidence}
        onClose={() => setSelectedEvidence(null)}
      />
    </main>
  );
}
