import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ScenarioImpactTable } from "./ScenarioImpactTable";

describe("ScenarioImpactTable", () => {
  it("renders the context for a chat-requested simulation", () => {
    render(
      <ScenarioImpactTable
        rows={[{ kpi: "Yard Density", baseline: "0.55", scenario: "0.40", delta: "-0.15" }]}
        scenarioExplanation="Reducing yard density by 20% was simulated."
      />
    );

    expect(screen.getByText("Chat-requested simulation")).toBeTruthy();
    expect(screen.getByText("Reducing yard density by 20% was simulated.")).toBeTruthy();
  });
});
