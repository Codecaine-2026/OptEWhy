import { afterEach, describe, expect, it, vi } from "vitest";
import { getCurrentGraph, simulateScenario, submitCopilotQuery } from "./api";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("submitCopilotQuery", () => {
  it("posts the user's message to the FastAPI query endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        answer: "Yard density is the strongest modeled driver.",
        intent: "root_mechanism_analysis",
        analysisId: "analysis_demo_001",
        causalResult: {
          targetNodeId: "qc_productivity",
          observedDelta: -0.1,
          dominantPaths: [],
          feedbackLoops: []
        },
        evidence: [],
        reasoningTrace: {
          targetNodeId: "qc_productivity",
          steps: []
        },
        visualization: {
          highlightedNodes: [],
          highlightedEdges: [],
          focusSubgraphId: "reasoning_qc_productivity",
          reasoningNodes: [],
          reasoningEdges: [],
          loops: []
        }
      })
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await submitCopilotQuery("What is driving productivity?");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/query",
      expect.objectContaining({ method: "POST" })
    );
    const request = fetchMock.mock.calls[0][1] as RequestInit;
    expect(JSON.parse(String(request.body))).toEqual({
      message: "What is driving productivity?",
      terminalId: "terminal_alpha"
    });
    expect(result.answer).toContain("Yard density");
    expect(result.intent).toBe("root_mechanism_analysis");
  });

  it("surfaces an API error to the Copilot UI", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        json: async () => ({ detail: "Intent parsing service is temporarily unavailable" })
      })
    );

    await expect(submitCopilotQuery("Explain the delay")).rejects.toThrow(
      "Intent parsing service is temporarily unavailable"
    );
  });

  it("posts a selected intervention to the scenario endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        scenarioId: "scenario_demo_001",
        structuredIntervention: {},
        predictedImpact: {},
        baselineState: { yard_density: 0.55 },
        scenarioState: { yard_density: 0.4 },
        propagationFrames: []
      })
    });
    vi.stubGlobal("fetch", fetchMock);

    await simulateScenario("Improve yard density by 15%", {
      nodeId: "yard_density",
      operation: "decrease_relative",
      value: 0.15
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/scenarios/simulate",
      expect.objectContaining({ method: "POST" })
    );
    const request = fetchMock.mock.calls[0][1] as RequestInit;
    expect(JSON.parse(String(request.body))).toEqual({
      message: "Improve yard density by 15%",
      terminalId: "terminal_alpha",
      intervention: {
        nodeId: "yard_density",
        operation: "decrease_relative",
        value: 0.15
      }
    });
  });
});

describe("getCurrentGraph", () => {
  it("loads the complete graph from the FastAPI graph endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        graphId: "graph_terminal_alpha_reference",
        terminalId: "terminal_alpha",
        nodes: Array.from({ length: 26 }, (_, index) => ({
          id: `node_${index}`,
          label: `Node ${index}`,
          subsystem: "test",
          abnormality: 0
        })),
        edges: []
      })
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await getCurrentGraph();

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/graph/current",
      { cache: "no-store" }
    );
    expect(result.nodes).toHaveLength(26);
  });
});
