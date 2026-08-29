import type { ImpactRow, ReasoningNode, ReasoningTrace, ScenarioResponse } from "@/lib/types";

type Props = {
  rows: ImpactRow[];
  scenario: ScenarioResponse;
  reasoningTrace: ReasoningTrace;
  reasoningNodes: ReasoningNode[];
};

type Intervention = {
  nodeId: string;
  operation: "increase_relative" | "decrease_relative";
  value: number;
};

function displayNodeId(nodeId: string) {
  return nodeId.replaceAll("_", " ").replace(/\b\w/g, (character) => character.toUpperCase());
}

function extractIntervention(scenario: ScenarioResponse): Intervention | null {
  const interventions = scenario.structuredIntervention.interventions;
  if (!Array.isArray(interventions) || interventions.length === 0) {
    return null;
  }
  const firstIntervention = interventions[0];
  if (
    !firstIntervention ||
    typeof firstIntervention !== "object" ||
    !("node_id" in firstIntervention) ||
    !("operation" in firstIntervention) ||
    !("value" in firstIntervention) ||
    typeof firstIntervention.node_id !== "string" ||
    (firstIntervention.operation !== "increase_relative" &&
      firstIntervention.operation !== "decrease_relative") ||
    typeof firstIntervention.value !== "number"
  ) {
    return null;
  }
  return {
    nodeId: firstIntervention.node_id,
    operation: firstIntervention.operation,
    value: firstIntervention.value
  };
}

function trendSymbol(change: number | undefined) {
  if (change === undefined || Math.abs(change) < 0.0001) {
    return "\u2192";
  }
  return change > 0 ? "\u2191" : "\u2193";
}

export function ScenarioImpactTable({ rows, scenario, reasoningTrace, reasoningNodes }: Props) {
  const nodeLabels = new Map(reasoningNodes.map((node) => [node.id, node.label]));
  const dominantPath = reasoningTrace.steps.find((step) => step.stepType === "dominant_path");
  const intervention = extractIntervention(scenario);
  const pathNodeIds = dominantPath?.usedNodeIds ?? [];
  const interventionLabel = intervention
    ? nodeLabels.get(intervention.nodeId) ?? displayNodeId(intervention.nodeId)
    : "the selected operational factor";
  const interventionDirection = intervention?.operation === "increase_relative" ? "increase" : "decrease";

  return (
    <section className="impactTable">
      <div className="panelHeader">
        <h2>Scenario Impact</h2>
        <span>Chat-requested simulation</span>
      </div>
      <section className="scenarioReasoning" aria-label="Causal explanation of the simulation">
        <h3>Why these values change</h3>
        <p>
          The model applies a {intervention ? `${Math.round(intervention.value * 100)}% ` : ""}
          {interventionDirection} to {interventionLabel}, then propagates that change through the modeled causal links.
        </p>
        {pathNodeIds.length ? (
          <>
            <div className="scenarioChain" aria-label="Projected causal chain">
              {pathNodeIds.map((nodeId, index) => (
                <span key={nodeId} className="scenarioChainStep">
                  {index > 0 ? <span aria-hidden="true">{"\u2192"}</span> : null}
                  <strong>{nodeLabels.get(nodeId) ?? displayNodeId(nodeId)}</strong>
                  <b>{trendSymbol(scenario.predictedImpact[nodeId])}</b>
                </span>
              ))}
            </div>
            <p className="scenarioReasoningConclusion">
              Each arrow represents a modeled causal effect, so the table below shows the resulting value change rather than a separate chatbot answer.
            </p>
          </>
        ) : null}
      </section>
      <div className="impactTableScroll">
        <table>
          <thead>
            <tr>
              <th>KPI</th>
              <th>Baseline</th>
              <th>Scenario</th>
              <th>Delta</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                key={row.kpi}
                className={
                  Number(row.delta) < 0
                    ? "impactRow--decreased"
                    : Number(row.delta) > 0
                      ? "impactRow--increased"
                      : undefined
                }
              >
                <td>{row.kpi}</td>
                <td>{row.baseline}</td>
                <td>{row.scenario}</td>
                <td>{row.delta}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
