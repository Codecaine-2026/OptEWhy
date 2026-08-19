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
    });
    render(<CopilotPanel />);

    fireEvent.click(screen.getByRole("button", { name: "Send query" }));

    await waitFor(() => {
      expect(screen.getByText("QC waiting is the strongest modeled driver.")).toBeTruthy();
    });
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
  });
});
