import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OperationsWorkspace } from "./OperationsWorkspace";

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
});
