"use client";

import { Download } from "lucide-react";
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
  const reportTimestamp = new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date());
  const dominantPath = analysis?.causalResult.dominantPaths[0];

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
          <img className="brandLogo" src="/assets/PSA_logo.jpeg" alt="PSA logo" />
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
          <header className="reportMasthead" data-pdf-block>
            <div className="reportIdentity">
              <img className="reportLogo" src="/assets/PSA_logo.jpeg" alt="PSA logo" />
              <div>
                <p className="reportKicker">Operational intelligence brief</p>
                <h1>Reasoning Report</h1>
                <p className="reportSubtitle">Causal analysis for port operations</p>
              </div>
            </div>
            <dl className="reportMetadata">
              <div>
                <dt>Analysis ID</dt>
                <dd>{analysis.analysisId}</dd>
              </div>
              <div>
                <dt>Generated</dt>
                <dd>{reportTimestamp}</dd>
              </div>
              <div>
                <dt>Analysis type</dt>
                <dd>{analysis.intent.replaceAll("_", " ")}</dd>
              </div>
            </dl>
          </header>
          <section className="reportMetricGrid" aria-label="Analysis summary" data-pdf-block>
            <div className="reportMetric">
              <span>Target KPI</span>
              <strong>{analysis.causalResult.targetNodeId.replaceAll("_", " ")}</strong>
            </div>
            <div className="reportMetric">
              <span>Primary path contribution</span>
              <strong>{dominantPath ? `${Math.round(dominantPath.contributionRatio * 100)}%` : "N/A"}</strong>
            </div>
            <div className="reportMetric">
              <span>Supporting evidence</span>
              <strong>{analysis.evidence.length} sources</strong>
            </div>
          </section>
          <section className="reportSection">
            <div className="reportSectionHeader" data-pdf-block>
              <p className="reportSectionLabel">Executive interpretation</p>
              <h2>AI analysis</h2>
            </div>
            <ReactMarkdown
              components={{
                h1: ({ children }) => <h1 data-pdf-block>{children}</h1>,
                h2: ({ children }) => <h2 data-pdf-block>{children}</h2>,
                h3: ({ children }) => <h3 data-pdf-block>{children}</h3>,
                p: ({ children }) => <p data-pdf-block>{children}</p>,
                ul: ({ children }) => <ul data-pdf-block>{children}</ul>,
                ol: ({ children }) => <ol data-pdf-block>{children}</ol>,
                pre: ({ children }) => <pre data-pdf-block>{children}</pre>
              }}
            >
              {analysis.answer}
            </ReactMarkdown>
          </section>
          <section className="reportSection" data-pdf-block>
            <p className="reportSectionLabel">Traceable model output</p>
            <h2>Reasoning trace</h2>
            <ol className="reportTraceList">
              {analysis.reasoningTrace.steps.map((step) => (
                <li key={step.id}>
                  <div>
                    <strong>{step.stepType === "dominant_path" ? "Dominant causal path" : "Feedback loop"}</strong>
                    <span>{step.summary}</span>
                  </div>
                  {step.confidence !== null && step.confidence !== undefined ? (
                    <small>Confidence {Math.round(step.confidence * 100)}%</small>
                  ) : null}
                </li>
              ))}
            </ol>
          </section>
          <section className="reportSection reportGraphSection" data-pdf-block>
            <p className="reportSectionLabel">Model view</p>
            <h2>Causal graph</h2>
            <p className="reportCaption">
              Highlighted nodes and edges show the dominant path and currently selected feedback loop.
            </p>
            <CausalMapCanvas
              nodes={causalNodes}
              edges={causalEdges}
              highlightedNodeIds={activeNodeIds}
              highlightedEdgeIds={activeEdgeIds}
            />
          </section>
          {analysis.evidence.length ? (
            <section className="reportSection" data-pdf-block>
              <p className="reportSectionLabel">Evidence register</p>
              <h2>Supporting sources</h2>
              <table className="reportEvidenceTable">
                <thead>
                  <tr>
                    <th>Source</th>
                    <th>Excerpt</th>
                    <th>Relevance</th>
                  </tr>
                </thead>
                <tbody>
                  {analysis.evidence.map((item) => (
                    <tr key={item.chunkId}>
                      <td>
                        {item.sourceUrl ? (
                          <a href={item.sourceUrl} target="_blank" rel="noreferrer">
                            {item.sourceTitle ?? item.documentId}
                          </a>
                        ) : (
                          item.sourceTitle ?? item.documentId
                        )}
                      </td>
                      <td>{item.text}</td>
                      <td>{Math.round(item.score * 100)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          ) : null}
          <footer className="reportFooter" data-pdf-block>
            <span>OptEWhy • Causal reasoning and scenario simulation</span>
            <span>Generated from the current analysis response</span>
          </footer>
        </div>
      ) : null}
    </main>
  );
}
