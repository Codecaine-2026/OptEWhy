import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ScenarioImpactTable } from "./ScenarioImpactTable";

describe("ScenarioImpactTable", () => {
  it("submits the selected intervention as a normalized relative decrease", () => {
    const onSimulate = vi.fn();
    render(
      <ScenarioImpactTable
        rows={[{ kpi: "Yard Density", baseline: "0.55", scenario: "0.40", delta: "-0.15" }]}
        onSimulate={onSimulate}
      />
    );

    fireEvent.change(screen.getByLabelText("Improve"), { target: { value: "qc_waiting" } });
    fireEvent.change(screen.getByLabelText("Scenario percentage"), { target: { value: "20" } });
    fireEvent.click(screen.getByRole("button", { name: "Run scenario" }));

    expect(onSimulate).toHaveBeenCalledWith("qc_waiting", 0.2);
  });
});
