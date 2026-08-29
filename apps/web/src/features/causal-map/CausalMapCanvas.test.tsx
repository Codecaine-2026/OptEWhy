import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CausalMapCanvas } from "./CausalMapCanvas";

const nodes = [
  { id: "source", label: "Source", subsystem: "Yard", abnormality: 0.2, x: 10, y: 10 },
  { id: "target", label: "Target", subsystem: "Quay", abnormality: -0.1, x: 220, y: 10 }
];

const edges = [
  { id: "source_to_target", source: "source", target: "target", weight: 0.5, polarity: "positive" as const }
];

describe("CausalMapCanvas", () => {
  it("marks only response-highlighted nodes in an analysis view", () => {
    const { container } = render(
      <CausalMapCanvas
        nodes={nodes}
        edges={edges}
        highlightedNodeIds={["target"]}
        highlightedEdgeIds={["edge_source_to_target"]}
      />
    );

    expect(screen.getByLabelText("2-node causal system map")).toBeTruthy();
    expect(container.querySelector('[data-highlighted="true"]')).toBeTruthy();
    expect(container.querySelectorAll('[data-highlighted="false"]')).toHaveLength(1);
    expect(container.querySelector('line[data-highlighted="true"]')?.getAttribute("marker-end")).toBe(
      "url(#positiveArrow)"
    );
  });
});
