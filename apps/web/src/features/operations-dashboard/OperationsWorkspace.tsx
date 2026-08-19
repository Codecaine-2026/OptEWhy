"use client";

import { Ship } from "lucide-react";
import { CausalMapCanvas } from "@/features/causal-map/CausalMapCanvas";
import { CopilotPanel } from "@/features/copilot/CopilotPanel";
import { ScenarioImpactTable } from "@/features/scenario-simulator/ScenarioImpactTable";
import { causalEdges, causalNodes, impactRows } from "@/lib/mockData";

export function OperationsWorkspace() {
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
          <CopilotPanel />
        </section>

        <section className="mapPanel">
          <div className="mapHeader">
            <h2>Causal Graph</h2>
            <span>8 modeled nodes</span>
          </div>
          <CausalMapCanvas nodes={causalNodes} edges={causalEdges} />
        </section>
      </section>

      <section className="bottomPanel">
        <ScenarioImpactTable rows={impactRows} />
      </section>
    </main>
  );
}
