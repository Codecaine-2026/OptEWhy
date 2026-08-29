"use client";

import { Download, Ship } from "lucide-react";
import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { CausalMapCanvas } from "@/features/causal-map/CausalMapCanvas";
import { AnalysisDetails } from "@/features/copilot/AnalysisDetails";
import { CopilotPanel } from "@/features/copilot/CopilotPanel";
import { EvidenceDrawer } from "@/features/evidence/EvidenceDrawer";
import { ScenarioImpactTable } from "@/features/scenario-simulator/ScenarioImpactTable";
import { causalEdges, causalNodes } from "@/lib/mockData";
import { downloadElementAsPdf } from "@/lib/exportPdf";
import type { EvidenceItem, QueryResponse, ScenarioResponse, VisualizationPayload } from "@/lib/types";

export function OperationsWorkspace() {
  const [visualization, setVisualization] = useState<VisualizationPayload | null>(null);
  const [scenario, setScenario] = useState<ScenarioResponse | null>(null);
  const [scenarioExplanation, setScenarioExplanation] = useState("");
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceItem | null>(null);
  const [loopIndex, setLoopIndex] = useState(0);
  const [analysis, setAnalysis] = useState<QueryResponse | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const exportReportRef = useRef<HTMLDivElement>(null);
  const activeLoop = visualization?.loops[loopIndex] ?? null;
  const strongestPathNodeIds = visualization?.reasoningNodes
    .filter((node) => node.reasoningStepIds.includes("path_1"))
    .map((node) => node.id) ?? [];
  const strongestPathEdgeIds = visualization?.reasoningEdges
    .filter((edge) => edge.reasoningStepIds.includes("path_1"))
    .map((edge) => edge.id) ?? [];
  const activeNodeIds = activeLoop
    ? [...new Set([...strongestPathNodeIds, ...activeLoop.nodeIds])]
    : visualization?.highlightedNodes;
  const activeEdgeIds = activeLoop
    ? [...new Set([...strongestPathEdgeIds, ...activeLoop.edgeIds])]
    : visualization?.highlightedEdges;
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

  async function handleExport() {
    if (!exportReportRef.current || !analysis) {
      return;
    }
    setIsExporting(true);
    try {
      await downloadElementAsPdf(exportReportRef.current, "optewhy-reasoning-report.pdf");
    } finally {
      setIsExporting(false);
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
        {analysis ? (
          <button type="button" className="exportButton" onClick={() => void handleExport()} disabled={isExporting}>
            <Download size={15} />
            {isExporting ? "Preparing PDF..." : "Export PDF"}
          </button>
        ) : null}
      </header>

      <section className="mainGrid">
        <section className="copilotArea">
          <CopilotPanel
            onClearResponse={() => {
              setAnalysis(null);
              setVisualization(null);
              setScenario(null);
              setScenarioExplanation("");
              setSelectedEvidence(null);
            }}
            onResponse={(response) => {
              setAnalysis(response);
              setVisualization(response.visualization);
              setLoopIndex(0);
              setScenario(response.scenario ?? null);
              setScenarioExplanation(response.scenario ? response.answer : "");
            }}
            onSelectEvidence={setSelectedEvidence}
          />
        </section>

        <section className="mapPanel">
          <div className="mapHeader">
            <h2>Causal Graph</h2>
            {visualization?.loops.length ? (
              <div className="loopPager" aria-label="Feedback loop pages">
                <button
                  type="button"
                  onClick={() => setLoopIndex((current) => Math.max(0, current - 1))}
                  disabled={loopIndex === 0}
                >
                  Previous
                </button>
                <span>Causal path + feedback loop {loopIndex + 1} / {visualization.loops.length}</span>
                <button
                  type="button"
                  onClick={() =>
                    setLoopIndex((current) => Math.min(visualization.loops.length - 1, current + 1))
                  }
                  disabled={loopIndex === visualization.loops.length - 1}
                >
                  Next
                </button>
              </div>
            ) : (
              <span>{visualization ? "Analysis highlights" : `${causalNodes.length} modeled nodes`}</span>
            )}
          </div>
          <CausalMapCanvas
            nodes={causalNodes}
            edges={causalEdges}
            highlightedNodeIds={activeNodeIds}
            highlightedEdgeIds={activeEdgeIds}
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
      {analysis ? (
        <div className="pdfExportReport" ref={exportReportRef} aria-hidden="true">
          <header>
            <h1>OptEWhy Reasoning Report</h1>
            <p>{analysis.intent.replaceAll("_", " ")}</p>
          </header>
          <section>
            <h2>AI analysis</h2>
            <ReactMarkdown>{analysis.answer}</ReactMarkdown>
          </section>
          <section>
            <h2>Reasoning trace</h2>
            <AnalysisDetails evidence={analysis.evidence} reasoningTrace={analysis.reasoningTrace} />
          </section>
          <section>
            <h2>Causal graph</h2>
            <CausalMapCanvas
              nodes={causalNodes}
              edges={causalEdges}
              highlightedNodeIds={activeNodeIds}
              highlightedEdgeIds={activeEdgeIds}
            />
          </section>
        </div>
      ) : null}
    </main>
  );
}
