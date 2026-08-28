import type { QueryResponse, ScenarioIntervention, ScenarioResponse } from "./types";

type ApiErrorResponse = {
  detail?: string;
};

const apiBaseUrl = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace(
  /\/$/,
  ""
);

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

  const payload = (await response.json()) as QueryResponse;
  if (!payload.answer) {
    throw new Error("Copilot returned an empty answer");
  }

  return payload;
}

export async function simulateScenario(message: string, intervention: ScenarioIntervention) {
  const response = await fetch(`${apiBaseUrl}/api/scenarios/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, terminalId: "terminal_alpha", intervention })
  });

  if (!response.ok) {
    const error = (await response.json().catch(() => ({}))) as ApiErrorResponse;
    throw new Error(error.detail ?? `Scenario request failed with status ${response.status}`);
  }

  return (await response.json()) as ScenarioResponse;
}
