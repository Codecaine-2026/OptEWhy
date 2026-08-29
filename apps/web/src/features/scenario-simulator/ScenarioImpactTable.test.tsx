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

  it("highlights decreased and increased KPI rows", () => {
    render(
      <ScenarioImpactTable
        rows={[
          { kpi: "Yard Density", baseline: "0.55", scenario: "0.40", delta: "-0.15" },
          { kpi: "QC Productivity", baseline: "0.40", scenario: "0.52", delta: "+0.12" },
          { kpi: "Berth Occupancy", baseline: "0.50", scenario: "0.50", delta: "0.00" }
        ]}
        scenarioExplanation="Scenario completed."
      />
    );

    expect(screen.getByRole("row", { name: /Yard Density/ }).className).toBe("impactRow--decreased");
    expect(screen.getByRole("row", { name: /QC Productivity/ }).className).toBe("impactRow--increased");
    expect(screen.getByRole("row", { name: /Berth Occupancy/ }).className).toBe("");
  });
});
