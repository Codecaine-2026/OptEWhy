import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { submitCopilotQuery } from "@/lib/api";
import { OperationsWorkspace } from "./OperationsWorkspace";

vi.mock("@/lib/api", () => ({
  submitCopilotQuery: vi.fn()
}));

const submitCopilotQueryMock = vi.mocked(submitCopilotQuery);

beforeEach(() => {
  submitCopilotQueryMock.mockReset();
});

describe("OperationsWorkspace", () => {
  it("renders only the copilot, causal graph, and scenario impact", () => {
    render(<OperationsWorkspace />);

    expect(screen.getByText("AI Copilot")).toBeTruthy();
    expect(screen.getByText("Causal Graph")).toBeTruthy();
    expect(screen.getByLabelText("8-node causal system map")).toBeTruthy();
    expect(screen.getByText("Scenario Impact")).toBeTruthy();
    expect(screen.queryByText("Evidence")).toBeNull();
    expect(screen.queryByText("Scenario Composer")).toBeNull();
  });

  it("highlights causal path when diagnosis query is submitted", async () => {
    submitCopilotQueryMock.mockResolvedValue({
      answer: "Yard congestion is propagating to QC waiting.",
      intent: "root_mechanism_analysis",
      analysisId: "analysis_demo_001",
      causalResult: {
        targetNodeId: "qc_productivity",
        observedDelta: -0.1,
        dominantPaths: [
          {
            path: ["yard_density", "truck_travel_time", "qc_waiting", "qc_productivity"],
            contributionRatio: 0.46,
            signedImpact: -0.064,
            confidence: 0.8
          }
        ],
        feedbackLoops: []
      },
      evidence: [],
      reasoningTrace: {
        targetNodeId: "qc_productivity",
        steps: []
      },
      visualization: {
        highlightedNodes: ["yard_density", "truck_travel_time", "qc_waiting", "qc_productivity"],
        highlightedEdges: ["yard_to_truck", "truck_to_waiting", "waiting_to_productivity"],
        focusSubgraphId: "reasoning_qc_productivity",
        reasoningNodes: [],
        reasoningEdges: [],
        loops: []
      }
    });

    render(<OperationsWorkspace />);
    const diagnosisBtn = screen.getByRole("button", { name: /Diagnosis: Vessel A Delay/i });
    fireEvent.click(diagnosisBtn);

    await waitFor(() => {
      expect(screen.getByText("Yard congestion is propagating to QC waiting.")).toBeTruthy();
    });
  });

  it("transitions to simulated state when what-if scenario is triggered", async () => {
    submitCopilotQueryMock.mockResolvedValue({
      answer: "Intervention applied: Yard Block B load reduced.",
      intent: "scenario_simulation",
      analysisId: "scenario_demo_001",
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
        highlightedNodes: ["yard_density", "qc_productivity"],
        highlightedEdges: [],
        focusSubgraphId: null,
        reasoningNodes: [],
        reasoningEdges: [],
        loops: []
      }
    });

    render(<OperationsWorkspace />);
    const scenarioBtn = screen.getByRole("button", { name: /What-If: Move Block B to D/i });
    fireEvent.click(scenarioBtn);

    await waitFor(() => {
      expect(screen.getByText("⚡ Simulated State Active")).toBeTruthy();
      expect(screen.getByText("Simulated Intervention Active")).toBeTruthy();
      expect(screen.getByText("+3.7%")).toBeTruthy();
      expect(screen.getByText("-19 min")).toBeTruthy();
      expect(screen.getByText(/Tradeoff Notice:/i)).toBeTruthy();
    });
  });


  it("opens and closes the Evidence Drawer when clicking a citation pill", () => {
    render(<OperationsWorkspace />);

    const citationBtn = screen.getByRole("button", {
      name: /Shift Handover Log #402/i
    });
    expect(citationBtn).toBeTruthy();

    fireEvent.click(citationBtn);

    expect(screen.getByText("Operational Evidence Detail")).toBeTruthy();
    expect(screen.getByText(/RTG-02 mechanical fault led to 25min container retrieval backlog/i)).toBeTruthy();
    expect(screen.getByText("94% Relevance Match")).toBeTruthy();

    const doneButton = screen.getByRole("button", { name: "Done" });
    fireEvent.click(doneButton);

    expect(screen.queryByText("Operational Evidence Detail")).toBeNull();
  });
});



