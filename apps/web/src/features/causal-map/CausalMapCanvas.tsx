import type { CausalEdge, CausalNode } from "@/lib/types";

type Props = {
  nodes: CausalNode[];
  edges: CausalEdge[];
  fitToContent?: boolean;
  focusedNodeId?: string;
  highlightedNodeIds?: string[];
  highlightedEdgeIds?: string[];
};

const nodeRadius = 11;
const edgeStrokeScale = 0.4;
const labelOffset = 28;
const labelLineHeight = 12;
const labelHalfWidth = 72;
const fullViewBox = "-72 0 914 680";
const contentPadding = 24;
const crimson = [220, 38, 58];
const yellow = [250, 204, 21];
const lime = [163, 230, 53];

function interpolateColor(start: number[], end: number[], progress: number) {
  const channels = start.map((channel, index) =>
    Math.round(channel + (end[index] - channel) * progress)
  );
  return `rgb(${channels.join(", ")})`;
}

function nodeColor(delta: number) {
  const clampedDelta = Math.max(-1, Math.min(1, delta));
  return clampedDelta < 0
    ? interpolateColor(crimson, yellow, clampedDelta + 1)
    : interpolateColor(yellow, lime, clampedDelta);
}

function wrapLabel(label: string) {
  const words = label.split(/\s+/);
  const lines: string[] = [];
  let currentLine = "";

  for (const word of words) {
    const nextLine = currentLine ? `${currentLine} ${word}` : word;
    if (currentLine && nextLine.length > 20 && lines.length === 0) {
      lines.push(currentLine);
      currentLine = word;
    } else {
      currentLine = nextLine;
    }
  }

  if (currentLine) {
    lines.push(currentLine);
  }
  return lines.slice(0, 2);
}

function connectionPoints(source: CausalNode, target: CausalNode) {
  const sourceCenter = { x: source.x + nodeRadius, y: source.y + nodeRadius };
  const targetCenter = { x: target.x + nodeRadius, y: target.y + nodeRadius };
  const deltaX = targetCenter.x - sourceCenter.x;
  const deltaY = targetCenter.y - sourceCenter.y;
  const distance = Math.hypot(deltaX, deltaY) || 1;
  const unitX = deltaX / distance;
  const unitY = deltaY / distance;
  return {
    x1: sourceCenter.x + unitX * nodeRadius,
    y1: sourceCenter.y + unitY * nodeRadius,
    x2: targetCenter.x - unitX * nodeRadius,
    y2: targetCenter.y - unitY * nodeRadius
  };
}

export function CausalMapCanvas({
  nodes,
  edges,
  fitToContent = false,
  focusedNodeId,
  highlightedNodeIds = [],
  highlightedEdgeIds = []
}: Props) {
  const nodeById = new Map(nodes.map((node) => [node.id, node]));
  const highlightedNodes = new Set(highlightedNodeIds);
  const highlightedEdges = new Set(highlightedEdgeIds);
  const hasHighlights = highlightedNodes.size > 0 || highlightedEdges.size > 0;
  const contentMinX = nodes.length
    ? Math.min(...nodes.map((node) => node.x + nodeRadius)) - labelHalfWidth - contentPadding
    : 0;
  const contentMaxX = nodes.length
    ? Math.max(...nodes.map((node) => node.x + nodeRadius)) + labelHalfWidth + contentPadding
    : 320;
  const contentWidth = contentMaxX - contentMinX;
  const contentHeight = nodes.length
    ? Math.max(
        ...nodes.map(
          (node) => node.y + nodeRadius * 2 + labelOffset + labelLineHeight * (wrapLabel(node.label).length - 1)
        )
      ) + contentPadding
    : 180;
  const viewBox = fitToContent
    ? `${contentMinX} 0 ${Math.max(320, contentWidth)} ${Math.max(180, contentHeight)}`
    : fullViewBox;

  return (
    <section className="causalCanvas" aria-label={`${nodes.length}-node causal system map`}>
      <svg viewBox={viewBox} role="img">
        <defs>
          <marker id="positiveArrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="#1f8a70" opacity="0.72" />
          </marker>
          <marker id="positiveArrowMuted" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="#1c6f9b" opacity="0.16" />
          </marker>
          <marker id="negativeArrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="#b33a3a" opacity="0.72" />
          </marker>
          <marker id="negativeArrowMuted" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="#dc2626" opacity="0.16" />
          </marker>
        </defs>
        {edges.map((edge) => {
          const source = nodeById.get(edge.source);
          const target = nodeById.get(edge.target);
          if (!source || !target) {
            return null;
          }
          const points = connectionPoints(source, target);
          const isPositive = edge.polarity === "positive";
          const backendEdgeId = `edge_${edge.source}_to_${edge.target}`;
          const isHighlighted = highlightedEdges.has(edge.id) || highlightedEdges.has(backendEdgeId);
          return (
            <line
              key={edge.id}
              {...points}
              stroke={isPositive ? "#1f8a70" : "#b33a3a"}
              strokeWidth={
                (Math.max(2, Math.abs(edge.weight) * 7) + (isHighlighted ? 1.5 : 0)) *
                edgeStrokeScale
              }
              strokeLinecap="round"
              opacity={hasHighlights && !isHighlighted ? 0.16 : 0.9}
              data-highlighted={isHighlighted}
              markerEnd={`url(#${isPositive ? "positiveArrow" : "negativeArrow"}${hasHighlights && !isHighlighted ? "Muted" : ""})`}
            />
          );
        })}
        {nodes.map((node) => {
          const isHighlighted = highlightedNodes.has(node.id);
          const isFocused = node.id === focusedNodeId;
          const labelLines = wrapLabel(node.label);
          return (
            <g
              key={node.id}
              className={isHighlighted ? "causalNode causalNodeHighlighted" : "causalNode"}
              data-highlighted={isHighlighted}
              transform={`translate(${node.x}, ${node.y})`}
              opacity={hasHighlights && !isHighlighted ? 0.42 : 1}
            >
              <circle
                cx={nodeRadius}
                cy={nodeRadius}
                r={nodeRadius}
                fill={nodeColor(node.abnormality)}
                stroke={isFocused ? "#2563eb" : nodeColor(node.abnormality)}
                strokeWidth={1.5 + Math.abs(node.abnormality) * 2 + (isHighlighted ? 1.5 : 0)}
              />
              <text
                x={nodeRadius}
                y={nodeRadius + labelOffset}
                textAnchor="middle"
                className="svgLabel"
              >
                {labelLines.map((line, index) => (
                  <tspan key={`${node.id}-${index}`} x={nodeRadius} dy={index === 0 ? 0 : labelLineHeight}>
                    {line}
                  </tspan>
                ))}
              </text>
            </g>
          );
        })}
      </svg>
    </section>
  );
}
