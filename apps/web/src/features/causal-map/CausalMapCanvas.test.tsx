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

  it("fits a focused graph to its visible nodes", () => {
    const { container } = render(<CausalMapCanvas nodes={nodes} edges={edges} fitToContent />);

    const viewBox = container.querySelector("svg")?.getAttribute("viewBox");
    expect(viewBox).toBeTruthy();
    expect(Number(viewBox?.split(" ")[2])).toBeLessThan(770);
  });

  it("fits all nodes and keeps long labels inside their boxes", () => {
    const { container } = render(
      <CausalMapCanvas
        nodes={[{ ...nodes[0], label: "Internal Truck Travel Time", y: 558 }]}
        edges={[]}
        fitToContent
      />
    );

    const viewBox = container.querySelector("svg")?.getAttribute("viewBox");
    expect(Number(viewBox?.split(" ")[3])).toBe(646);
    expect(container.querySelectorAll(".svgLabel tspan")).toHaveLength(2);
    expect(container.querySelector(".svgLabel")?.getAttribute("text-anchor")).toBe("middle");
  });

  it("renders non-highlighted causal edges with slight transparency", () => {
    const { container } = render(<CausalMapCanvas nodes={nodes} edges={edges} />);

    expect(container.querySelector("line")?.getAttribute("opacity")).toBe("0.72");
  });

  it("renders causal edges at 40% of their original thickness", () => {
    const { container } = render(<CausalMapCanvas nodes={nodes} edges={edges} />);

    expect(Number(container.querySelector("line")?.getAttribute("stroke-width"))).toBeCloseTo(1.4);
  });

  it("colors the focused node blue", () => {
    const { container } = render(
      <CausalMapCanvas nodes={nodes} edges={edges} focusedNodeId="target" />
    );

    const targetCircle = container.querySelector('g[transform="translate(220, 10)"] circle');
    expect(targetCircle?.getAttribute("fill")).toBe("rgb(247, 187, 25)");
    expect(targetCircle?.getAttribute("stroke")).toBe("#2563eb");
  });

  it("colors zero deltas yellow and omits subsystem metadata", () => {
    const { container } = render(
      <CausalMapCanvas
        nodes={[{ ...nodes[0], abnormality: 0 }]}
        edges={[]}
      />
    );

    expect(container.querySelector("rect")?.getAttribute("fill")).toBe("rgb(250, 204, 21)");
    expect(container.querySelector(".svgMeta")).toBeNull();
  });

  it("moves positive deltas toward lime", () => {
    const { container } = render(
      <CausalMapCanvas
        nodes={[{ ...nodes[0], abnormality: 0.2 }]}
        edges={[]}
      />
    );

    expect(container.querySelector("rect")?.getAttribute("fill")).toBe("rgb(233, 209, 27)");
  });
});
