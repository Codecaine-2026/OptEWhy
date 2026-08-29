import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { OperationsWorkspace } from "./OperationsWorkspace";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("OperationsWorkspace", () => {
  it("shows a scenario panel only after a chat-requested simulation", () => {
    const nodes = Array.from({ length: 26 }, (_, index) => ({
      id: `node_${index}`,
      label: `Node ${index}`,
      subsystem: "test",
      abnormality: 0
    }));
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ graphId: "graph_test", terminalId: "terminal_alpha", nodes, edges: [] })
      })
    );

    render(<OperationsWorkspace />);

    expect(screen.getByText("AI Copilot")).toBeTruthy();
    expect(screen.getByText("Causal Graph")).toBeTruthy();
    return waitFor(() => expect(screen.getByLabelText("26-node causal system map")).toBeTruthy());
  });

  it("shows a graph loading error when the backend graph cannot be loaded", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("Graph request failed")));

    render(<OperationsWorkspace />);

    expect(await screen.findByText("Graph request failed")).toBeTruthy();
    expect(screen.queryByText("Scenario Impact")).toBeNull();
    expect(screen.queryByText("Evidence")).toBeNull();
    expect(screen.queryByText("Scenario Composer")).toBeNull();
  });

  it("shows the causal path to the most affected non-intervention node", async () => {
    const nodes = Array.from({ length: 8 }, (_, index) => ({
      id: `node_${index}`,
      label: `Node ${index}`,
      subsystem: "test",
      abnormality: 0
    }));
    const baselineState = Object.fromEntries(nodes.map((node) => [node.id, 0]));
    const scenarioState = Object.fromEntries(
      nodes.map((node, index) => [
        node.id,
        index === 0 ? 0.9 : index === 1 ? 0.2 : index === 2 ? 0.7 : index === 3 ? 0.6 : 0
      ])
    );
    const graphResponse = {
      graphId: "graph_test",
      terminalId: "terminal_alpha",
      nodes,
      edges: [
        {
          id: "edge_0_to_1",
          sourceNodeId: "node_0",
          targetNodeId: "node_1",
          weight: 0.5,
          polarity: "positive" as const
        },
        {
          id: "edge_1_to_2",
          sourceNodeId: "node_1",
          targetNodeId: "node_2",
          weight: 0.5,
          polarity: "positive" as const
        }
      ]
    };
    const queryResponse = {
      answer: "Scenario completed.",
      intent: "scenario_simulation",
      analysisId: "analysis_test",
      causalResult: { targetNodeId: "node_7", observedDelta: 0, dominantPaths: [], feedbackLoops: [] },
      evidence: [],
      reasoningTrace: { targetNodeId: "node_7", steps: [] },
      visualization: {
        highlightedNodes: [],
        highlightedEdges: [],
        focusSubgraphId: null,
        reasoningNodes: [],
        reasoningEdges: [],
        loops: []
      },
      scenario: {
        scenarioId: "scenario_test",
        structuredIntervention: { targetNodeId: "node_2", interventions: [{ nodeId: "node_0" }] },
        predictedImpact: scenarioState,
        baselineState,
        scenarioState,
        propagationFrames: []
      }
    };
    vi.stubGlobal(
      "fetch",
      vi.fn()
        .mockResolvedValueOnce({ ok: true, json: async () => graphResponse })
        .mockResolvedValueOnce({ ok: true, json: async () => queryResponse })
    );

    render(<OperationsWorkspace />);
    await waitFor(() => expect(screen.getByLabelText("8-node causal system map")).toBeTruthy());

    fireEvent.click(screen.getByRole("button", { name: "Send query" }));

    const [pathGraph] = await screen.findAllByLabelText("3-node causal system map");
    expect(pathGraph).toBeTruthy();
    expect(screen.getByText("Path to Node 2")).toBeTruthy();
    expect(Array.from(pathGraph.querySelectorAll(".svgLabel")).map((label) => label.textContent)).toEqual([
      "Node 0",
      "Node 1",
      "Node 2",
    ]);
    expect(Array.from(pathGraph.querySelectorAll("line"))).toHaveLength(2);
    expect(
      Array.from(pathGraph.querySelectorAll("line")).every(
        (edge) => edge.getAttribute("data-highlighted") === "true"
      )
    ).toBe(true);
    expect(pathGraph.querySelector("text")?.textContent).not.toBe("Node 3");
  });
});
