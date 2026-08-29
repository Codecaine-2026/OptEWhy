"use client";

import { useState } from "react";
import { Ship } from "lucide-react";
import { CausalMapCanvas } from "@/features/causal-map/CausalMapCanvas";
import { CopilotPanel } from "@/features/copilot/CopilotPanel";
import { EvidenceDrawer } from "@/features/evidence/EvidenceDrawer";
import { ScenarioImpactTable } from "@/features/scenario-simulator/ScenarioImpactTable";
import { causalEdges, causalNodes, impactRows } from "@/lib/mockData";
import type { CausalNode, EvidenceItem, QueryResponse } from "@/lib/types";

export function OperationsWorkspace() {
  const [nodes, setNodes] = useState<CausalNode[]>(causalNodes);
  const [highlightedNodeIds, setHighlightedNodeIds] = useState<string[]>([]);
  const [highlightedEdgeIds, setHighlightedEdgeIds] = useState<string[]>([]);
  const [scenarioMode, setScenarioMode] = useState(false);
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceItem | null>(null);
  const [isEvidenceOpen, setIsEvidenceOpen] = useState(false);

  function handleSelectEvidence(evidence: EvidenceItem) {
    setSelectedEvidence(evidence);
    setIsEvidenceOpen(true);
  }

  function handleAnalysisComplete(response: QueryResponse) {
    const isScenario =
      response.intent === "scenario_simulation" ||
      response.analysisId.includes("scenario") ||
      response.answer.toLowerCase().includes("scenario") ||
      response.answer.toLowerCase().includes("transfer") ||
      response.answer.toLowerCase().includes("move");

    if (isScenario) {
      setScenarioMode(true);
      // Simulate post-intervention improved port states:
      setNodes((prevNodes) =>
        prevNodes.map((node) => {
          if (node.id === "yard_density") return { ...node, abnormality: 0.12 };
          if (node.id === "truck_travel_time") return { ...node, abnormality: 0.15 };
          if (node.id === "qc_waiting") return { ...node, abnormality: 0.1 };
          if (node.id === "qc_productivity") return { ...node, abnormality: 0.04 };
          if (node.id === "vessel_turnaround_time") return { ...node, abnormality: 0.08 };
          return node;
        })
      );
      setHighlightedNodeIds([
        "yard_density",
        "truck_travel_time",
        "qc_waiting",
        "qc_productivity",
        "vessel_turnaround_time"
      ]);
      setHighlightedEdgeIds([
        "yard_to_truck",
        "truck_to_waiting",
        "waiting_to_productivity",
        "productivity_to_turnaround"
      ]);
    } else {
      setScenarioMode(false);
      // Reset nodes to current operational baseline anomaly state:
      setNodes(causalNodes);

      const resNodes = response.visualization?.highlightedNodes?.length
        ? response.visualization.highlightedNodes
        : response.causalResult?.dominantPaths?.[0]?.path || [
            "yard_density",
            "truck_travel_time",
            "qc_waiting",
            "qc_productivity"
          ];
      const resEdges = response.visualization?.highlightedEdges || [
        "yard_to_truck",
        "truck_to_waiting",
        "waiting_to_productivity"
      ];
      setHighlightedNodeIds(resNodes);
      setHighlightedEdgeIds(resEdges);
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
          <CopilotPanel
            onAnalysisComplete={handleAnalysisComplete}
            onSelectEvidence={handleSelectEvidence}
          />
        </section>

        <section className="mapPanel">
          <div className="mapHeader">
            <h2>Causal Graph</h2>
            <span>
              {scenarioMode ? "⚡ Simulated State Active" : `${nodes.length} modeled nodes`}
            </span>
          </div>
          <CausalMapCanvas
            nodes={nodes}
            edges={causalEdges}
            highlightedNodeIds={highlightedNodeIds}
            highlightedEdgeIds={highlightedEdgeIds}
            scenarioMode={scenarioMode}
          />
        </section>
      </section>

      <section className="bottomPanel">
        <ScenarioImpactTable rows={impactRows} scenarioMode={scenarioMode} />
      </section>

      <EvidenceDrawer
        isOpen={isEvidenceOpen}
        evidence={selectedEvidence}
        onClose={() => setIsEvidenceOpen(false)}
      />
    </main>
  );
}


