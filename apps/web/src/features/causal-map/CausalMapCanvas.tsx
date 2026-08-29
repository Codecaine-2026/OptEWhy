import type { CausalEdge, CausalNode } from "@/lib/types";

type Props = {
  nodes: CausalNode[];
  edges: CausalEdge[];
  highlightedNodeIds?: string[];
  highlightedEdgeIds?: string[];
};

const nodeWidth = 170;
const nodeHeight = 62;

function connectionPoints(source: CausalNode, target: CausalNode) {
  const sourceCenter = { x: source.x + nodeWidth / 2, y: source.y + nodeHeight / 2 };
  const targetCenter = { x: target.x + nodeWidth / 2, y: target.y + nodeHeight / 2 };
  const horizontal = Math.abs(targetCenter.x - sourceCenter.x) >= Math.abs(targetCenter.y - sourceCenter.y);

  if (horizontal) {
    const direction = Math.sign(targetCenter.x - sourceCenter.x) || 1;
    return {
      x1: sourceCenter.x + (nodeWidth / 2) * direction,
      y1: sourceCenter.y,
      x2: targetCenter.x - (nodeWidth / 2) * direction,
      y2: targetCenter.y
    };
  }

  const direction = Math.sign(targetCenter.y - sourceCenter.y) || 1;
  return {
    x1: sourceCenter.x,
    y1: sourceCenter.y + (nodeHeight / 2) * direction,
    x2: targetCenter.x,
    y2: targetCenter.y - (nodeHeight / 2) * direction
  };
}

export function CausalMapCanvas({
  nodes,
  edges,
  highlightedNodeIds = [],
  highlightedEdgeIds = []
}: Props) {
  const nodeById = new Map(nodes.map((node) => [node.id, node]));
  const highlightedNodes = new Set(highlightedNodeIds);
  const highlightedEdges = new Set(highlightedEdgeIds);
  const hasHighlights = highlightedNodes.size > 0 || highlightedEdges.size > 0;

  return (
    <section className="causalCanvas" aria-label={`${nodes.length}-node causal system map`}>
      <svg viewBox="0 0 440 650" role="img">
        <defs>
          <marker id="positiveArrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="#1c6f9b" />
          </marker>
          <marker id="positiveArrowMuted" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="#1c6f9b" opacity="0.16" />
          </marker>
          <marker id="negativeArrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="#dc2626" />
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
              stroke={isPositive ? "#1c6f9b" : "#dc2626"}
              strokeWidth={Math.max(2, Math.abs(edge.weight) * 7) + (isHighlighted ? 1.5 : 0)}
              strokeLinecap="round"
              opacity={hasHighlights && !isHighlighted ? 0.16 : 0.9}
              data-highlighted={isHighlighted}
              markerEnd={`url(#${isPositive ? "positiveArrow" : "negativeArrow"}${hasHighlights && !isHighlighted ? "Muted" : ""})`}
            />
          );
        })}
        {nodes.map((node) => {
          const isHighlighted = highlightedNodes.has(node.id);
          return (
            <g
              key={node.id}
              className={isHighlighted ? "causalNode causalNodeHighlighted" : "causalNode"}
              data-highlighted={isHighlighted}
              transform={`translate(${node.x}, ${node.y})`}
              opacity={hasHighlights && !isHighlighted ? 0.42 : 1}
            >
              <rect
                width={nodeWidth}
                height={nodeHeight}
                rx="8"
                fill={node.abnormality >= 0 ? "#eff9f7" : "#fff1f2"}
                stroke={node.abnormality >= 0 ? "#1c6f9b" : "#dc2626"}
                strokeWidth={1.5 + Math.abs(node.abnormality) * 2 + (isHighlighted ? 1.5 : 0)}
              />
              <text x="12" y="25" className="svgLabel">
                {node.label}
              </text>
              <text x="12" y="45" className="svgMeta">
                {node.subsystem} | {Math.round(node.abnormality * 100)}%
              </text>
            </g>
          );
        })}
      </svg>
    </section>
  );
}
