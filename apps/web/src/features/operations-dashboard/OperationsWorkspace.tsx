"use client";

import { Download } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CausalMapCanvas } from "@/features/causal-map/CausalMapCanvas";
import { AnalysisDetails } from "@/features/copilot/AnalysisDetails";
import { CopilotPanel } from "@/features/copilot/CopilotPanel";
import { EvidenceDrawer } from "@/features/evidence/EvidenceDrawer";
import { ScenarioImpactTable } from "@/features/scenario-simulator/ScenarioImpactTable";
import { getCurrentGraph } from "@/lib/api";
import { downloadElementAsPdf } from "@/lib/exportPdf";
import { feedbackLoopLabel } from "@/lib/loopLabel";
import type {
  CausalEdge,
  CausalNode,
  EvidenceItem,
  GraphResponse,
  QueryResponse,
  ScenarioResponse,
  VisualizationPayload
} from "@/lib/types";

const graphColumns = 4;
const graphColumnWidth = 190;
const graphRowHeight = 82;

function layoutGraph(
  graph: GraphResponse,
  visibleNodeIds?: Set<string>,
  visibleEdgeIds?: Set<string>
) {
  const visibleNodes = visibleNodeIds
    ? graph.nodes.filter((node) => visibleNodeIds.has(node.id))
    : graph.nodes;
  const columns = visibleNodeIds
    ? Math.min(3, Math.max(1, Math.ceil(Math.sqrt(visibleNodes.length))))
    : graphColumns;
  const nodes: CausalNode[] = visibleNodes.map((node, index) => ({
    ...node,
    x: 14 + (index % columns) * graphColumnWidth,
    y: 12 + Math.floor(index / columns) * graphRowHeight
  }));
  const edges: CausalEdge[] = graph.edges
    .filter(
      (edge) =>
        (!visibleNodeIds ||
          (visibleNodeIds.has(edge.sourceNodeId) && visibleNodeIds.has(edge.targetNodeId))) &&
        (!visibleEdgeIds || visibleEdgeIds.has(edge.id))
    )
    .map((edge) => ({
      id: edge.id,
      source: edge.sourceNodeId,
      target: edge.targetNodeId,
      weight: edge.weight,
      polarity: edge.polarity
    }));
  return { nodes, edges };
}

function getScenarioInterventionNodeIds(scenario: ScenarioResponse) {
  const interventions = scenario.structuredIntervention.interventions;
  if (!Array.isArray(interventions)) {
    return new Set<string>();
  }
  return new Set(
    interventions.flatMap((intervention) => {
      if (typeof intervention !== "object" || intervention === null) {
        return [];
      }
      const interventionRecord = intervention as Record<string, unknown>;
      const nodeId = interventionRecord.nodeId ?? interventionRecord.node_id;
      return typeof nodeId === "string" ? [nodeId] : [];
    })
  );
}

function getScenarioTargetNodeId(scenario: ScenarioResponse) {
  const targetNodeId = scenario.structuredIntervention.targetNodeId;
  return typeof targetNodeId === "string" ? targetNodeId : null;
}

function getScenarioPathNodeIds(
  graph: GraphResponse,
  interventionNodeIds: Set<string>,
  targetNodeId: string
) {
  const incomingNodeIds = new Map<string, string[]>();
  const outgoingNodeIds = new Map<string, string[]>();
  for (const edge of graph.edges) {
    incomingNodeIds.set(edge.targetNodeId, [
      ...(incomingNodeIds.get(edge.targetNodeId) ?? []),
      edge.sourceNodeId
    ]);
    outgoingNodeIds.set(edge.sourceNodeId, [
      ...(outgoingNodeIds.get(edge.sourceNodeId) ?? []),
      edge.targetNodeId
    ]);
  }

  const ancestors = new Set([targetNodeId]);
  const ancestorQueue = [targetNodeId];
  while (ancestorQueue.length) {
    const currentNodeId = ancestorQueue.shift();
    if (!currentNodeId) {
      continue;
    }
    for (const sourceNodeId of incomingNodeIds.get(currentNodeId) ?? []) {
      if (!ancestors.has(sourceNodeId)) {
        ancestors.add(sourceNodeId);
        ancestorQueue.push(sourceNodeId);
      }
    }
  }

  if (!interventionNodeIds.size) {
    return ancestors;
  }

  const interventionDescendants = new Set(interventionNodeIds);
  const descendantQueue = [...interventionNodeIds];
  while (descendantQueue.length) {
    const currentNodeId = descendantQueue.shift();
    if (!currentNodeId) {
      continue;
    }
    for (const targetId of outgoingNodeIds.get(currentNodeId) ?? []) {
      if (!interventionDescendants.has(targetId)) {
        interventionDescendants.add(targetId);
        descendantQueue.push(targetId);
      }
    }
  }

  const pathNodeIds = new Set(
    [...ancestors].filter((nodeId) => interventionDescendants.has(nodeId))
  );
  return pathNodeIds.size ? pathNodeIds : ancestors;
}

function getScenarioCausalPath(
  graph: GraphResponse,
  interventionNodeIds: Set<string>,
  targetNodeId: string
) {
  const outgoingEdges = new Map<string, GraphResponse["edges"]>();
  for (const edge of graph.edges) {
    outgoingEdges.set(edge.sourceNodeId, [...(outgoingEdges.get(edge.sourceNodeId) ?? []), edge]);
  }

  const nodeIds = new Set<string>();
  const edgeIds = new Set<string>();
  const maxPaths = 50;
  let foundPathCount = 0;

  function visit(currentNodeId: string, pathNodeIds: string[], pathEdgeIds: string[], visited: Set<string>) {
    if (foundPathCount >= maxPaths) {
      return;
    }
    if (currentNodeId === targetNodeId) {
      foundPathCount += 1;
      pathNodeIds.forEach((nodeId) => nodeIds.add(nodeId));
      pathEdgeIds.forEach((edgeId) => edgeIds.add(edgeId));
      return;
    }

    for (const edge of outgoingEdges.get(currentNodeId) ?? []) {
      if (visited.has(edge.targetNodeId)) {
        continue;
      }
      const nextVisited = new Set(visited);
      nextVisited.add(edge.targetNodeId);
      visit(
        edge.targetNodeId,
        [...pathNodeIds, edge.targetNodeId],
        [...pathEdgeIds, edge.id],
        nextVisited
      );
    }
  }

  for (const interventionNodeId of interventionNodeIds) {
    visit(interventionNodeId, [interventionNodeId], [], new Set([interventionNodeId]));
  }

  return { nodeIds, edgeIds };
}

export function OperationsWorkspace() {
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [graphError, setGraphError] = useState("");
  const [visualization, setVisualization] = useState<VisualizationPayload | null>(null);
  const [scenario, setScenario] = useState<ScenarioResponse | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceItem | null>(null);
  const [loopIndex, setLoopIndex] = useState(0);
  const [analysis, setAnalysis] = useState<QueryResponse | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState("");
  const exportReportRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    let isActive = true;
    void getCurrentGraph()
      .then((response) => {
        if (isActive) {
          setGraph(response);
        }
      })
      .catch((error) => {
        if (isActive) {
          setGraphError(error instanceof Error ? error.message : "The causal graph could not be loaded.");
        }
      });
    return () => {
      isActive = false;
    };
  }, []);

  const graphView = graph ? layoutGraph(graph) : { nodes: [], edges: [] };
  const scenarioInterventionNodeIds = scenario
    ? getScenarioInterventionNodeIds(scenario)
    : new Set<string>();
  const requestedScenarioTargetNodeId = scenario ? getScenarioTargetNodeId(scenario) : null;
  const scenarioTargetNode = scenario
    ? graphView.nodes.find((node) => node.id === requestedScenarioTargetNodeId) ??
      graphView.nodes
        .filter((node) => !scenarioInterventionNodeIds.has(node.id))
        .map((node) => {
          const baseline = scenario.baselineState[node.id] ?? 0;
          const simulated = scenario.scenarioState[node.id] ?? baseline;
          return { node, absoluteDelta: Math.abs(simulated - baseline) };
        })
        .sort((left, right) => right.absoluteDelta - left.absoluteDelta)[0]?.node ?? null
    : null;
  const exactScenarioPath = scenario && graph && scenarioTargetNode && scenarioInterventionNodeIds.size
    ? getScenarioCausalPath(graph, scenarioInterventionNodeIds, scenarioTargetNode.id)
    : null;
  const hasExactScenarioPath = Boolean(exactScenarioPath?.nodeIds.size);
  const hasRequestedScenarioTarget = Boolean(requestedScenarioTargetNodeId && scenarioTargetNode);
  const noModeledScenarioPath = Boolean(
    scenario &&
      hasRequestedScenarioTarget &&
      scenarioInterventionNodeIds.size &&
      !hasExactScenarioPath
  );
  const scenarioPathNodeIds = exactScenarioPath?.nodeIds.size
    ? exactScenarioPath.nodeIds
    : scenario && graph && scenarioTargetNode
      ? getScenarioPathNodeIds(graph, scenarioInterventionNodeIds, scenarioTargetNode.id)
      : null;
  const scenarioFeedbackLoops = exactScenarioPath?.nodeIds.size
    ? visualization?.loops.filter((loop) =>
        loop.nodeIds.some((nodeId) => exactScenarioPath.nodeIds.has(nodeId))
      ) ?? []
    : [];
  const activeScenarioLoop = scenarioFeedbackLoops[loopIndex] ?? null;
  const displayedScenarioNodeIds = noModeledScenarioPath && scenarioTargetNode
    ? new Set([...scenarioInterventionNodeIds, scenarioTargetNode.id])
    : exactScenarioPath?.nodeIds.size
    ? new Set([...exactScenarioPath.nodeIds, ...(activeScenarioLoop?.nodeIds ?? [])])
    : scenarioPathNodeIds;
  const scenarioPathEdgeIds = exactScenarioPath?.edgeIds.size
    ? new Set([...exactScenarioPath.edgeIds, ...(activeScenarioLoop?.edgeIds ?? [])])
    : noModeledScenarioPath
      ? new Set<string>()
      : undefined;
  const displayedGraphView = graph
    ? scenario
      ? layoutGraph(graph, displayedScenarioNodeIds ?? new Set<string>(), scenarioPathEdgeIds)
      : graphView
    : { nodes: [], edges: [] };
  const activeLoop = visualization?.loops[loopIndex] ?? null;
  const strongestPathNodeIds = visualization?.reasoningNodes
    .filter((node) => node.reasoningStepIds.includes("path_1"))
    .map((node) => node.id) ?? [];
  const strongestPathEdgeIds = visualization?.reasoningEdges
    .filter((edge) => edge.reasoningStepIds.includes("path_1"))
    .map((edge) => edge.id) ?? [];
  const activeNodeIds = noModeledScenarioPath
    ? [...(displayedScenarioNodeIds ?? [])]
    : exactScenarioPath?.nodeIds.size
    ? [...new Set([...exactScenarioPath.nodeIds, ...(activeScenarioLoop?.nodeIds ?? [])])]
    : activeLoop
    ? [...new Set([...strongestPathNodeIds, ...activeLoop.nodeIds])]
    : visualization?.highlightedNodes;
  const activeEdgeIds = noModeledScenarioPath
    ? []
    : exactScenarioPath?.edgeIds.size
    ? [...new Set([...exactScenarioPath.edgeIds, ...(activeScenarioLoop?.edgeIds ?? [])])]
    : activeLoop
    ? [...new Set([...strongestPathEdgeIds, ...activeLoop.edgeIds])]
    : visualization?.highlightedEdges;
  const scenarioRows = scenario
    ? graphView.nodes.map((node) => {
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
  const isScenarioReport = analysis?.intent === "scenario_simulation" && scenario !== null;
  const reportTitle = isScenarioReport ? "Scenario Simulation Report" : "Reasoning Analysis Report";
  const reportKicker = isScenarioReport ? "Operational scenario assessment" : "Operational intelligence brief";
  const reportSubtitle = isScenarioReport
    ? "Projected impact of the proposed operational intervention"
    : "Causal analysis for port operations";
  const exportFileName = isScenarioReport
    ? "optewhy-scenario-simulation-report.pdf"
    : "optewhy-reasoning-analysis-report.pdf";
  const targetScenarioImpact =
    isScenarioReport && analysis && scenario
      ? scenario.predictedImpact[analysis.causalResult.targetNodeId]
      : null;

  async function handleExport() {
    if (!exportReportRef.current || !analysis) {
      return;
    }
    setIsExporting(true);
    setExportError("");
    try {
      await downloadElementAsPdf(exportReportRef.current, exportFileName);
    } catch (error) {
      setExportError(error instanceof Error ? error.message : "The PDF could not be generated.");
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
        {exportError ? <span className="exportError" role="alert">PDF export failed: {exportError}</span> : null}
      </header>

      <section className="mainGrid">
        <section className="copilotArea">
          <CopilotPanel
            onClearResponse={() => {
              setAnalysis(null);
              setVisualization(null);
              setScenario(null);
              setSelectedEvidence(null);
            }}
            onResponse={(response) => {
              setAnalysis(response);
              setVisualization(response.visualization);
              setLoopIndex(0);
              setScenario(response.scenario ?? null);
            }}
            onSelectEvidence={setSelectedEvidence}
          />
        </section>

        <section className="mapPanel">
          <div className="mapHeader">
            <h2>Causal Graph</h2>
            {scenario ? (
              noModeledScenarioPath ? (
                <span>
                  No modeled causal path from {graphView.nodes.find((node) => scenarioInterventionNodeIds.has(node.id))?.label ?? "intervention"} to {scenarioTargetNode?.label ?? "target"}
                </span>
              ) : scenarioFeedbackLoops.length ? (
                <div className="loopPager" aria-label="Scenario feedback loop pages">
                  <button
                    type="button"
                    onClick={() => setLoopIndex((current) => Math.max(0, current - 1))}
                    disabled={loopIndex === 0}
                  >
                    Previous
                  </button>
                  <span>
                    Path to {scenarioTargetNode?.label ?? "target"} + {feedbackLoopLabel(activeScenarioLoop?.loopType).toLowerCase()} {loopIndex + 1} / {scenarioFeedbackLoops.length}
                  </span>
                  <button
                    type="button"
                    onClick={() =>
                      setLoopIndex((current) => Math.min(scenarioFeedbackLoops.length - 1, current + 1))
                    }
                    disabled={loopIndex === scenarioFeedbackLoops.length - 1}
                  >
                    Next
                  </button>
                </div>
              ) : (
                <span>
                  {scenarioTargetNode
                    ? `Path to ${scenarioTargetNode.label}`
                    : "No eligible affected node"}
                </span>
              )
            ) : visualization?.loops.length ? (
              <div className="loopPager" aria-label="Feedback loop pages">
                <button
                  type="button"
                  onClick={() => setLoopIndex((current) => Math.max(0, current - 1))}
                  disabled={loopIndex === 0}
                >
                  Previous
                </button>
                <span>Causal path + {feedbackLoopLabel(activeLoop?.loopType).toLowerCase()} {loopIndex + 1} / {visualization.loops.length}</span>
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
              <span>
                {visualization
                  ? "Analysis highlights"
                  : graph
                    ? `${graph.nodes.length} modeled nodes`
                    : "Loading graph..."}
              </span>
            )}
          </div>
          {graph ? (
            <CausalMapCanvas
              nodes={displayedGraphView.nodes}
              edges={displayedGraphView.edges}
              fitToContent
              focusedNodeId={scenarioTargetNode?.id}
              highlightedNodeIds={activeNodeIds}
              highlightedEdgeIds={activeEdgeIds}
            />
          ) : (
            <div className="graphLoading" role="status">
              {graphError || "Loading the causal graph from the backend..."}
            </div>
          )}
        </section>
      </section>

      {scenario ? (
        <section className="bottomPanel">
          <ScenarioImpactTable
            rows={scenarioRows}
            scenario={scenario}
            reasoningTrace={analysis?.reasoningTrace ?? { targetNodeId: "", steps: [] }}
            reasoningNodes={visualization?.reasoningNodes ?? []}
          />
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
                <p className="reportKicker">{reportKicker}</p>
                <h1>{reportTitle}</h1>
                <p className="reportSubtitle">{reportSubtitle}</p>
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
              <span>{isScenarioReport ? "Scenario ID" : "Target KPI"}</span>
              <strong>
                {isScenarioReport ? scenario?.scenarioId.replaceAll("_", " ") : analysis.causalResult.targetNodeId.replaceAll("_", " ")}
              </strong>
            </div>
            <div className="reportMetric">
              <span>{isScenarioReport ? "Target KPI" : "Primary path contribution"}</span>
              <strong>
                {isScenarioReport
                  ? analysis.causalResult.targetNodeId.replaceAll("_", " ")
                  : dominantPath
                    ? `${Math.round(dominantPath.contributionRatio * 100)}%`
                    : "N/A"}
              </strong>
            </div>
            <div className="reportMetric">
              <span>{isScenarioReport ? "Predicted target change" : "Supporting evidence"}</span>
              <strong>
                {isScenarioReport
                  ? targetScenarioImpact === null || targetScenarioImpact === undefined
                    ? "N/A"
                    : `${targetScenarioImpact >= 0 ? "+" : ""}${(targetScenarioImpact * 100).toFixed(1)}%`
                  : `${analysis.evidence.length} sources`}
              </strong>
            </div>
          </section>
          <section className="reportSection">
            <div className="reportSectionHeader" data-pdf-block>
              <p className="reportSectionLabel">{isScenarioReport ? "Projected outcome" : "Executive interpretation"}</p>
              <h2>{isScenarioReport ? "AI simulation interpretation" : "AI reasoning analysis"}</h2>
            </div>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({ children }) => <h1 data-pdf-block>{children}</h1>,
                h2: ({ children }) => <h2 data-pdf-block>{children}</h2>,
                h3: ({ children }) => <h3 data-pdf-block>{children}</h3>,
                p: ({ children }) => <p data-pdf-block>{children}</p>,
                ul: ({ children }) => <ul data-pdf-block>{children}</ul>,
                ol: ({ children }) => <ol data-pdf-block>{children}</ol>,
                pre: ({ children }) => <pre data-pdf-block>{children}</pre>,
                table: ({ children }) => (
                  <table className="reportMarkdownTable" data-pdf-block>
                    {children}
                  </table>
                )
              }}
            >
              {analysis.answer}
            </ReactMarkdown>
          </section>
          {isScenarioReport ? (
            <section className="reportSection" data-pdf-block>
              <p className="reportSectionLabel">Simulation output</p>
              <h2>Projected KPI impact</h2>
              <table className="reportScenarioTable">
                <thead>
                  <tr>
                    <th>KPI</th>
                    <th>Baseline</th>
                    <th>Scenario</th>
                    <th>Delta</th>
                  </tr>
                </thead>
                <tbody>
                  {scenarioRows.map((row) => (
                    <tr key={row.kpi} className={Number(row.delta) < 0 ? "impactRow--decreased" : "impactRow--increased"}>
                      <td>{row.kpi}</td>
                      <td>{row.baseline}</td>
                      <td>{row.scenario}</td>
                      <td>{row.delta}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          ) : (
            <section className="reportSection" data-pdf-block>
              <p className="reportSectionLabel">Traceable model output</p>
              <h2>Reasoning trace</h2>
              <ol className="reportTraceList">
                {analysis.reasoningTrace.steps.map((step) => (
                  <li key={step.id}>
                    <div>
                      <strong>{step.stepType === "dominant_path" ? "Dominant causal path" : feedbackLoopLabel(step.loopType)}</strong>
                      <span>{step.summary}</span>
                    </div>
                    {step.confidence !== null && step.confidence !== undefined ? (
                      <small>Confidence {Math.round(step.confidence * 100)}%</small>
                    ) : null}
                  </li>
                ))}
              </ol>
            </section>
          )}
          <section className="reportSection reportGraphSection" data-pdf-block>
            <p className="reportSectionLabel">Model view</p>
            <h2>Causal graph</h2>
            <p className="reportCaption">
              Highlighted nodes and edges show the dominant path and currently selected feedback loop.
            </p>
            <CausalMapCanvas
              nodes={displayedGraphView.nodes}
              edges={displayedGraphView.edges}
              fitToContent
              focusedNodeId={scenarioTargetNode?.id}
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
            <span>Generated from the current {isScenarioReport ? "simulation" : "analysis"} response</span>
          </footer>
        </div>
      ) : null}
    </main>
  );
}
