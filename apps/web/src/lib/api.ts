import { impactRows } from "./mockData";
import type { EvidenceItem, PathItem } from "./types";

type ApiPath = {
  path: string[];
  contributionRatio: number;
};

type CopilotApiResponse = {
  answer: string;
  intent: string;
  causalResult: {
    dominantPaths: ApiPath[];
  };
  evidence: EvidenceItem[];
};

type ApiErrorResponse = {
  detail?: string;
};

const apiBaseUrl = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace(
  /\/$/,
  ""
);

function humanizeNodeId(nodeId: string) {
  return nodeId
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export async function submitCopilotQuery(message: string) {
  const response = await fetch(`${apiBaseUrl}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      terminalId: "terminal_alpha"
    })
  });

  if (!response.ok) {
    const error = (await response.json().catch(() => ({}))) as ApiErrorResponse;
    throw new Error(error.detail ?? `Copilot request failed with status ${response.status}`);
  }

  const payload = (await response.json()) as CopilotApiResponse;
  if (!payload.answer) {
    throw new Error("Copilot returned an empty answer");
  }

  const paths: PathItem[] = payload.causalResult.dominantPaths.map((path, index) => ({
    id: `path_${index + 1}`,
    label: path.path.map(humanizeNodeId).join(" → "),
    contribution: path.contributionRatio,
    nodes: path.path.map(humanizeNodeId)
  }));

  return {
    answer: payload.answer,
    intent: payload.intent,
    paths,
    evidence: payload.evidence
  };
}

export async function simulateScenario(_message: string) {
  return {
    impactRows,
    warning: "Block D may absorb additional load, so gate retrieval time should be monitored."
  };
}
