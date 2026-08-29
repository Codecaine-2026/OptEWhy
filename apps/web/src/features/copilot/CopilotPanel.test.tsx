import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { submitCopilotQuery } from "@/lib/api";
import { CopilotPanel } from "./CopilotPanel";

vi.mock("@/lib/api", () => ({
  submitCopilotQuery: vi.fn()
}));

const submitCopilotQueryMock = vi.mocked(submitCopilotQuery);

beforeEach(() => {
  submitCopilotQueryMock.mockReset();
});

describe("CopilotPanel", () => {
  it("shows the answer returned by the backend", async () => {
    submitCopilotQueryMock.mockResolvedValue({
      answer: "## Root cause\n\n**QC waiting** is the strongest modeled driver.\n\n- Review yard density\n- Check truck flow",
      intent: "root_mechanism_analysis",
      analysisId: "analysis_demo_001",
      causalResult: {
        targetNodeId: "qc_productivity",
        observedDelta: -0.1,
        dominantPaths: [],
        feedbackLoops: []
      },
      evidence: [
        {
          documentId: "yard_report",
          chunkId: "yard_report_001",
          sourceTitle: "Yard operations report",
          text: "Yard congestion can increase QC waiting.",
          score: 0.8,
          relatedNodes: ["yard_density"],
          relatedEdges: []
        }
      ],
      reasoningTrace: {
        targetNodeId: "qc_productivity",
        steps: [
          {
            id: "path_1",
            stepType: "dominant_path",
            summary: "Ranked the strongest causal path.",
            usedNodeIds: ["yard_density", "qc_productivity"],
            usedEdgeIds: [],
            evidenceRefs: []
          }
        ]
      },
      visualization: {
        highlightedNodes: [],
        highlightedEdges: [],
        focusSubgraphId: "reasoning_qc_productivity",
        reasoningNodes: [],
        reasoningEdges: [],
        loops: []
      }
    });
    render(<CopilotPanel />);

    fireEvent.click(screen.getByRole("button", { name: "Send query" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Root cause" })).toBeTruthy();
      expect(screen.getByText("QC waiting").tagName).toBe("STRONG");
      expect(screen.getByText("Review yard density")).toBeTruthy();
    });
    expect(screen.getByText("Reasoning trace")).toBeTruthy();
    expect(screen.getAllByText("Yard operations report")).toHaveLength(2);
    expect(submitCopilotQueryMock).toHaveBeenCalledWith(
      "Why is Vessel A productivity low?"
    );
  });

  it("shows request errors instead of failing silently", async () => {
    submitCopilotQueryMock.mockRejectedValue(new Error("Copilot backend is unavailable"));
    render(<CopilotPanel />);

    fireEvent.click(screen.getByRole("button", { name: "Send query" }));

    await waitFor(() => {
      expect(screen.getByText("Copilot backend is unavailable")).toBeTruthy();
    });
    expect(screen.queryByText("Reasoning trace")).toBeNull();
  });

  it("shares the full analysis response with its parent", async () => {
    const response = {
      answer: "QC waiting is the strongest modeled driver.",
      intent: "root_mechanism_analysis",
      analysisId: "analysis_demo_001",
      causalResult: {
        targetNodeId: "qc_productivity",
        observedDelta: -0.1,
        dominantPaths: [],
        feedbackLoops: []
      },
      evidence: [],
      reasoningTrace: { targetNodeId: "qc_productivity", steps: [] },
      visualization: {
        highlightedNodes: ["qc_productivity"],
        highlightedEdges: ["edge_qc_waiting_to_qc_productivity"],
        focusSubgraphId: "reasoning_qc_productivity",
        reasoningNodes: [],
        reasoningEdges: [],
        loops: []
      }
    };
    submitCopilotQueryMock.mockResolvedValue(response);
    const onResponse = vi.fn();
    render(<CopilotPanel onResponse={onResponse} />);

    fireEvent.click(screen.getByRole("button", { name: "Send query" }));

    await waitFor(() => {
      expect(onResponse).toHaveBeenCalledWith(response);
    });
  });
});
