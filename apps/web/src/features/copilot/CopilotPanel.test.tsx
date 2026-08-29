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
      "Why is Vessel A productivity low?",
      { fallbackToMock: true }
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

  it("submits the selected scenario when clicking a quick prompt button", async () => {
    submitCopilotQueryMock.mockResolvedValue({
      answer: "Block D transfer simulated successfully.",
      intent: "scenario_simulation",
      analysisId: "analysis_demo_002",
      causalResult: {
        targetNodeId: "qc_productivity",
        observedDelta: 0.037,
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

    const scenarioButton = screen.getByRole("button", { name: /What-If: Move Block B to D/i });
    fireEvent.click(scenarioButton);

    await waitFor(() => {
      expect(screen.getByText("Block D transfer simulated successfully.")).toBeTruthy();
    });
    expect(submitCopilotQueryMock).toHaveBeenCalledWith(
      "What if we move 15% of Block B containers to Block D?",
      { fallbackToMock: true }
    );
  });

  it("triggers onSelectEvidence when clicking an evidence citation pill", () => {
    const onSelectEvidence = vi.fn();
    render(<CopilotPanel onSelectEvidence={onSelectEvidence} />);

    const citationBtn = screen.getByRole("button", {
      name: /Shift Handover Log #402/i
    });
    expect(citationBtn).toBeTruthy();

    fireEvent.click(citationBtn);
    expect(onSelectEvidence).toHaveBeenCalledTimes(1);
    expect(onSelectEvidence).toHaveBeenCalledWith(
      expect.objectContaining({
        documentId: "shift_report_block_b_001",
        sourceTitle: "Shift Handover Log #402 (Yard Block B)"
      })
    );
  });
});



