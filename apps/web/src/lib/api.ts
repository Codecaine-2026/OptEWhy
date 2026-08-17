import { evidence, impactRows, paths } from "./mockData";

export async function submitCopilotQuery(_message: string) {
  return {
    answer:
      "The strongest modeled causal path is Yard Density -> Truck Travel Time -> QC Waiting -> QC Productivity, explaining approximately 46% of the target KPI movement.",
    paths,
    evidence
  };
}

export async function simulateScenario(_message: string) {
  return {
    impactRows,
    warning: "Block D may absorb additional load, so gate retrieval time should be monitored."
  };
}

