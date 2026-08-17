"use client";

import { Play } from "lucide-react";
import { useState } from "react";
import { simulateScenario } from "@/lib/api";

export function ScenarioComposer() {
  const [scenario, setScenario] = useState("Move 15% of Block B containers to Block D");
  const [status, setStatus] = useState("Ready");

  async function handleSimulate() {
    await simulateScenario(scenario);
    setStatus("Simulation complete");
  }

  return (
    <section className="panel">
      <div className="panelHeader">
        <h2>Scenario</h2>
        <span>{status}</span>
      </div>
      <textarea value={scenario} onChange={(event) => setScenario(event.target.value)} />
      <button className="primaryButton" onClick={handleSimulate}>
        <Play size={16} />
        Simulate
      </button>
    </section>
  );
}

