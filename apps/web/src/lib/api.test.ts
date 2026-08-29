import { afterEach, describe, expect, it, vi } from "vitest";
import { submitCopilotQuery } from "./api";

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

  it("surfaces an API error to the Copilot UI when fallbackToMock is disabled", async () => {
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

  it("returns instant deterministic mock payload when fallbackToMock is enabled and network fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("Failed to fetch"))
    );

    const result = await submitCopilotQuery("What if we move 15% of Block B containers to Block D?", {
      fallbackToMock: true
    });

    expect(result.intent).toBe("scenario_simulation");
    expect(result.answer).toContain("Simulated Intervention");
    expect(result.answer).toContain("Tradeoff Notice");
    expect(result.visualization?.highlightedNodes).toContain("yard_density");
  });

  it("handles feedback loop queries in mock mode", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("Network offline"))
    );

    const result = await submitCopilotQuery("Explain the feedback loop causing congestion", {
      fallbackToMock: true
    });

    expect(result.intent).toBe("root_mechanism_analysis");
    expect(result.answer).toContain("Root Mechanism Analysis");
  });
});
