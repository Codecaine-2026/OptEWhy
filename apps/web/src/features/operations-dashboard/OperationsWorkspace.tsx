"use client";

import { Activity, Database, GitBranch, Ship, Wifi } from "lucide-react";
import { CausalMapCanvas } from "@/features/causal-map/CausalMapCanvas";
import { NodeInspector } from "@/features/causal-map/NodeInspector";
import { CopilotPanel } from "@/features/copilot/CopilotPanel";
import { EvidenceDrawer } from "@/features/copilot/EvidenceDrawer";
import { LoopInspector } from "@/features/scenario-simulator/LoopInspector";
import { PathContributionPanel } from "@/features/scenario-simulator/PathContributionPanel";
import { PropagationTimeline } from "@/features/scenario-simulator/PropagationTimeline";
import { ScenarioComposer } from "@/features/scenario-simulator/ScenarioComposer";
import { ScenarioImpactTable } from "@/features/scenario-simulator/ScenarioImpactTable";
import { causalEdges, causalNodes, evidence, impactRows, loops, paths } from "@/lib/mockData";

export function OperationsWorkspace() {
  return (
    <main className="workspace">
      <header className="topbar">
        <div className="brand">
          <Ship size={22} />
          <div>
            <strong>OptEWhy</strong>
            <span>Port Causal Intelligence</span>
          </div>
        </div>
        <div className="statusGroup">
          <span><Database size={15} /> Terminal Alpha</span>
          <span><Activity size={15} /> Current Shift</span>
          <span><GitBranch size={15} /> Scenario Mode</span>
          <span className="ok"><Wifi size={15} /> Live Mock</span>
        </div>
      </header>

      <section className="mainGrid">
        <aside className="leftPanel">
          <CopilotPanel />
          <EvidenceDrawer items={evidence} />
        </aside>

        <section className="mapPanel">
          <CausalMapCanvas nodes={causalNodes} edges={causalEdges} />
          <NodeInspector node={causalNodes[0]} />
        </section>

        <aside className="rightRail">
          <PathContributionPanel paths={paths} />
          <LoopInspector loops={loops} />
          <ScenarioComposer />
        </aside>
      </section>

      <section className="bottomPanel">
        <ScenarioImpactTable rows={impactRows} />
        <PropagationTimeline />
      </section>
    </main>
  );
}

