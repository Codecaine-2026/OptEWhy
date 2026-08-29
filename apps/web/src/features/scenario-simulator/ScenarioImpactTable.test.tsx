import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ScenarioImpactTable } from "./ScenarioImpactTable";
import { impactRows } from "@/lib/mockData";

describe("ScenarioImpactTable", () => {
  it("renders baseline state by default with baseline labels", () => {
    render(<ScenarioImpactTable rows={impactRows} scenarioMode={false} />);

    expect(screen.getByText("Scenario Impact")).toBeTruthy();
    expect(screen.getByText(/Operational Baseline \(Awaiting Simulation\)/i)).toBeTruthy();
    expect(screen.getByText("Baseline State")).toBeTruthy();

    // Verify KPI rows are rendered
    expect(screen.getByText("Yard Density")).toBeTruthy();
    expect(screen.getByText("QC Productivity")).toBeTruthy();
    expect(screen.getByText("Vessel Turnaround")).toBeTruthy();

    // In baseline mode, delta badges show "Baseline"
    const baselineBadges = screen.getAllByText("Baseline");
    expect(baselineBadges.length).toBeGreaterThanOrEqual(1);

    // Tradeoff banner should not be displayed in baseline mode
    expect(screen.queryByText(/Tradeoff Notice/i)).toBeNull();
  });

  it("renders animated simulated delta badges and tradeoff warning when scenarioMode is active", () => {
    render(<ScenarioImpactTable rows={impactRows} scenarioMode={true} />);

    expect(screen.getByText(/Simulated Intervention vs Operational Baseline/i)).toBeTruthy();
    expect(screen.getByText(/Simulated Intervention Active/i)).toBeTruthy();

    // Verify improvement and warning delta values
    expect(screen.getByText("+3.7%")).toBeTruthy();
    expect(screen.getByText("-19 min")).toBeTruthy();
    expect(screen.getByText("-13%")).toBeTruthy();
    expect(screen.getAllByText("+2.0%").length).toBeGreaterThanOrEqual(1);

    // Verify simulated scenario values
    expect(screen.getByText("72%")).toBeTruthy();
    expect(screen.getByText("28.4 mph")).toBeTruthy();
    expect(screen.getByText("18h 01m")).toBeTruthy();

    // Verify tradeoff notice banner
    expect(screen.getByText(/Tradeoff Notice:/i)).toBeTruthy();
    expect(screen.getByText(/Block D density increase introduces a/i)).toBeTruthy();
  });
});
