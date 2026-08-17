import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OperationsWorkspace } from "./OperationsWorkspace";

describe("OperationsWorkspace", () => {
  it("renders the operational workspace", () => {
    render(<OperationsWorkspace />);

    expect(screen.getByText("Port Causal Intelligence")).toBeTruthy();
    expect(screen.getByText("AI Copilot")).toBeTruthy();
    expect(screen.getByText("Scenario Impact")).toBeTruthy();
  });
});
