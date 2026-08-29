import type { QueryResponse } from "./types";

type ApiErrorResponse = {
  detail?: string;
};

type SubmitOptions = {
  fallbackToMock?: boolean;
};

const apiBaseUrl = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace(
  /\/$/,
  ""
);

export function getDeterministicMockQueryResponse(message: string): QueryResponse {
  const lowered = message.toLowerCase();

  if (
    lowered.includes("what if") ||
    lowered.includes("move") ||
    lowered.includes("block") ||
    lowered.includes("simulate") ||
    lowered.includes("transfer")
  ) {
    return {
      analysisId: "scenario_demo_001",
      intent: "scenario_simulation",
      answer:
        "Simulated Intervention: Reallocating 15% container load from Yard Block B to Block D reduces Yard Density from 85% to 72% (-13%). This alleviates Internal Truck Travel Time (-6%) and QC Waiting (-4%), yielding a +3.7% boost in QC Productivity (+1.0 mph) and saving 19 minutes on Vessel Turnaround.\n\n⚠️ Tradeoff Notice: Block D density increase introduces a +2.0% Gate Retrieval Delay during peak hours.",
      causalResult: {
        targetNodeId: "qc_productivity",
        observedDelta: 0.037,
        dominantPaths: [
          {
            path: ["yard_density", "truck_travel_time", "qc_waiting", "qc_productivity"],
            contributionRatio: 0.58,
            signedImpact: 0.037,
            confidence: 0.89
          }
        ],
        feedbackLoops: []
      },
      evidence: [
        {
          documentId: "shift_report_block_b_001",
          sourceTitle: "Shift Handover Log #402 (Yard Block B)",
          subsystem: "yard",
          text: "07:15 - RTG-02 mechanical fault led to 25min container retrieval backlog and internal truck queuing at Block B.",
          score: 0.94
        }
      ],
      reasoningTrace: {
        targetNodeId: "qc_productivity",
        steps: []
      },
      visualization: {
        highlightedNodes: [
          "yard_density",
          "truck_travel_time",
          "qc_waiting",
          "qc_productivity",
          "vessel_turnaround_time"
        ],
        highlightedEdges: [
          "yard_to_truck",
          "truck_to_waiting",
          "waiting_to_productivity",
          "productivity_to_turnaround"
        ],
        focusSubgraphId: "reasoning_qc_productivity",
        reasoningNodes: [],
        reasoningEdges: [],
        loops: []
      }
    };
  }

  if (
    lowered.includes("loop") ||
    lowered.includes("feedback") ||
    lowered.includes("congestion") ||
    lowered.includes("mechanism")
  ) {
    return {
      analysisId: "mechanism_demo_001",
      intent: "root_mechanism_analysis",
      answer:
        "Root Mechanism Analysis: High Yard Density (85%) triggers a reinforcing feedback loop with Yard Rehandle Rate and Internal Truck Travel Time. Internal transport delays starve Quay Cranes of container flow, causing 18 min average QC waiting.",
      causalResult: {
        targetNodeId: "yard_density",
        observedDelta: 0.55,
        dominantPaths: [
          {
            path: ["yard_density", "truck_travel_time", "qc_waiting"],
            contributionRatio: 0.62,
            signedImpact: 0.4,
            confidence: 0.84
          }
        ],
        feedbackLoops: [
          {
            nodes: ["yard_density", "truck_travel_time"],
            loopType: "reinforcing",
            strength: 0.68,
            confidence: 0.82
          }
        ]
      },
      evidence: [
        {
          documentId: "shift_report_block_b_001",
          sourceTitle: "Shift Handover Log #402 (Yard Block B)",
          subsystem: "yard",
          text: "07:15 - RTG-02 mechanical fault led to 25min container retrieval backlog and internal truck queuing at Block B.",
          score: 0.94
        }
      ],
      reasoningTrace: {
        targetNodeId: "yard_density",
        steps: []
      },
      visualization: {
        highlightedNodes: ["yard_density", "truck_travel_time", "qc_waiting"],
        highlightedEdges: ["yard_to_truck", "truck_to_waiting"],
        focusSubgraphId: "reasoning_yard_density",
        reasoningNodes: [],
        reasoningEdges: [],
        loops: []
      }
    };
  }

  if (
    lowered.includes("report") ||
    lowered.includes("evidence") ||
    lowered.includes("crane 4") ||
    lowered.includes("qc4") ||
    lowered.includes("citation")
  ) {
    return {
      analysisId: "evidence_demo_001",
      intent: "evidence_lookup",
      answer:
        "Evidence Records: Verified Shift Handover Log #402 and QC Maintenance Notice #118. Quay Crane 4 was mechanically operational; productivity slowdown was downstream from yard transport arrival delays.",
      causalResult: {
        targetNodeId: "qc_productivity",
        observedDelta: -0.1,
        dominantPaths: [],
        feedbackLoops: []
      },
      evidence: [
        {
          documentId: "maintenance_qc4_demo",
          sourceTitle: "Quay Crane Maintenance Notice #118",
          subsystem: "quay",
          text: "QC4 operating at normal capacity; delays observed were downstream from internal transport arrivals rather than crane mechanics.",
          score: 0.88
        },
        {
          documentId: "shift_report_block_b_001",
          sourceTitle: "Shift Handover Log #402 (Yard Block B)",
          subsystem: "yard",
          text: "07:15 - RTG-02 mechanical fault led to 25min container retrieval backlog and internal truck queuing at Block B.",
          score: 0.94
        }
      ],
      reasoningTrace: {
        targetNodeId: "qc_productivity",
        steps: []
      },
      visualization: {
        highlightedNodes: ["qc_productivity", "qc_waiting"],
        highlightedEdges: ["waiting_to_productivity"],
        focusSubgraphId: "reasoning_qc_productivity",
        reasoningNodes: [],
        reasoningEdges: [],
        loops: []
      }
    };
  }

  if (
    lowered === "hi" ||
    lowered === "hello" ||
    lowered === "hey" ||
    lowered === "hey there" ||
    lowered.startsWith("good morning") ||
    lowered.startsWith("good afternoon")
  ) {
    return {
      analysisId: "chat_demo_001",
      intent: "casual_conversation",
      answer:
        "Hi! I’m the OptEWhy Copilot. Ask me about port operations, causal bottlenecks, or run a what-if scenario simulation.",
      causalResult: {
        targetNodeId: "",
        observedDelta: 0,
        dominantPaths: [],
        feedbackLoops: []
      },
      evidence: [],
      reasoningTrace: {
        targetNodeId: "",
        steps: []
      },
      visualization: {
        highlightedNodes: [],
        highlightedEdges: [],
        focusSubgraphId: null,
        reasoningNodes: [],
        reasoningEdges: [],
        loops: []
      }
    };
  }

  // Default: Anomaly Explanation (e.g. "Why is Vessel A productivity low?")
  return {
    analysisId: "analysis_demo_001",
    intent: "anomaly_explanation",
    answer:
      "The strongest modeled causal path is Yard Density (0.55) ➔ Internal Truck Travel Time (0.40) ➔ QC Waiting (0.35) ➔ QC Productivity (-0.10) ➔ Vessel Turnaround (+0.30), explaining approximately 58% of the target KPI slowdown. Supporting evidence from Shift Handover Log #402 confirms an RTG mechanical fault at Block B as the primary trigger.",
    causalResult: {
      targetNodeId: "qc_productivity",
      observedDelta: -0.1,
      dominantPaths: [
        {
          path: ["yard_density", "truck_travel_time", "qc_waiting", "qc_productivity"],
          contributionRatio: 0.58,
          signedImpact: -0.1,
          confidence: 0.89
        }
      ],
      feedbackLoops: []
    },
    evidence: [
      {
        documentId: "shift_report_block_b_001",
        sourceTitle: "Shift Handover Log #402 (Yard Block B)",
        subsystem: "yard",
        text: "07:15 - RTG-02 mechanical fault led to 25min container retrieval backlog and internal truck queuing at Block B.",
        score: 0.94
      },
      {
        documentId: "maintenance_qc4_demo",
        sourceTitle: "Quay Crane Maintenance Notice #118",
        subsystem: "quay",
        text: "QC4 operating at normal capacity; delays observed were downstream from internal transport arrivals rather than crane mechanics.",
        score: 0.88
      }
    ],
    reasoningTrace: {
      targetNodeId: "qc_productivity",
      steps: []
    },
    visualization: {
      highlightedNodes: [
        "yard_density",
        "truck_travel_time",
        "qc_waiting",
        "qc_productivity",
        "vessel_turnaround_time"
      ],
      highlightedEdges: [
        "yard_to_truck",
        "truck_to_waiting",
        "waiting_to_productivity",
        "productivity_to_turnaround"
      ],
      focusSubgraphId: "reasoning_qc_productivity",
      reasoningNodes: [],
      reasoningEdges: [],
      loops: []
    }
  };
}

export async function submitCopilotQuery(
  message: string,
  options?: SubmitOptions
): Promise<QueryResponse> {
  const fallbackToMock = options?.fallbackToMock ?? false;
  const trimmedMessage = message.trim();

  try {
    const response = await fetch(`${apiBaseUrl}/api/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: trimmedMessage,
        terminalId: "terminal_alpha"
      })
    });

    if (!response.ok) {
      if (fallbackToMock) {
        return getDeterministicMockQueryResponse(trimmedMessage);
      }
      const error = (await response.json().catch(() => ({}))) as ApiErrorResponse;
      throw new Error(error.detail ?? `Copilot request failed with status ${response.status}`);
    }

    const payload = (await response.json()) as QueryResponse;
    if (!payload.answer) {
      if (fallbackToMock) {
        return getDeterministicMockQueryResponse(trimmedMessage);
      }
      throw new Error("Copilot returned an empty answer");
    }

    return payload;
  } catch (error) {
    if (fallbackToMock) {
      return getDeterministicMockQueryResponse(trimmedMessage);
    }
    throw error;
  }
}
