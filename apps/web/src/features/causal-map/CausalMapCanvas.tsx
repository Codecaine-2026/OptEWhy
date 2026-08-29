import type { CausalEdge, CausalNode } from "@/lib/types";

type Props = {
  nodes: CausalNode[];
  edges: CausalEdge[];
  highlightedNodeIds?: string[];
  highlightedEdgeIds?: string[];
  scenarioMode?: boolean;
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
  highlightedEdgeIds = [],
  scenarioMode = false
}: Props) {
  const nodeById = new Map(nodes.map((node) => [node.id, node]));
  const hasHighlights = highlightedNodeIds.length > 0 || highlightedEdgeIds.length > 0;

  return (
    <section className="causalCanvas" aria-label={`${nodes.length}-node causal system map`}>
      <svg viewBox="0 0 440 650" role="img">
        <defs>
          <filter id="activeGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          <marker id="positiveArrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="#1f8a70" />
          </marker>
          <marker id="negativeArrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="#b33a3a" />
          </marker>
          <marker id="activePositiveArrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
            <path d="M0,0 L9,4.5 L0,9 Z" fill="#15803d" />
          </marker>
          <marker id="activeNegativeArrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
            <path d="M0,0 L9,4.5 L0,9 Z" fill="#b91c1c" />
          </marker>
          <marker id="activeScenarioArrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
            <path d="M0,0 L9,4.5 L0,9 Z" fill="#0284c7" />
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
          const isEdgeHighlighted =
            highlightedEdgeIds.includes(edge.id) ||
            (highlightedNodeIds.includes(edge.source) && highlightedNodeIds.includes(edge.target));

          let strokeColor = isPositive ? "#1f8a70" : "#b33a3a";
          let strokeOpacity = 0.76;
          let strokeWidth = Math.max(2, Math.abs(edge.weight) * 7);
          let markerId = isPositive ? "positiveArrow" : "negativeArrow";

          if (hasHighlights) {
            if (isEdgeHighlighted) {
              strokeColor = scenarioMode ? "#0284c7" : isPositive ? "#15803d" : "#b91c1c";
              strokeOpacity = 1.0;
              strokeWidth = Math.max(4, Math.abs(edge.weight) * 9);
              markerId = scenarioMode ? "activeScenarioArrow" : isPositive ? "activePositiveArrow" : "activeNegativeArrow";
            } else {
              strokeOpacity = 0.15;
              strokeColor = "#94a3b8";
            }
          }

          return (
            <line
              key={edge.id}
              {...points}
              className="causalEdgeLine"
              stroke={strokeColor}
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              opacity={strokeOpacity}
              markerEnd={`url(#${markerId})`}
            />
          );
        })}

        {nodes.map((node) => {
          const isNodeHighlighted = highlightedNodeIds.includes(node.id);
          let nodeOpacity = 1.0;
          let rectFill = node.abnormality >= 0 ? "#f8faf8" : "#fff7f7";
          let rectStroke = node.abnormality >= 0 ? "#1f8a70" : "#b33a3a";
          let strokeWidth = 1.5 + Math.abs(node.abnormality) * 2;

          if (hasHighlights) {
            if (isNodeHighlighted) {
              nodeOpacity = 1.0;
              rectFill = scenarioMode
                ? "#f0fdf4"
                : node.abnormality >= 0
                ? "#fffbeb"
                : "#fef2f2";
              rectStroke = scenarioMode
                ? "#16a34a"
                : node.abnormality >= 0
                ? "#d97706"
                : "#dc2626";
              strokeWidth = 3.2;
            } else {
              nodeOpacity = 0.32;
            }
          }

          const sign = node.abnormality > 0 ? "+" : "";
          const percentageText = `${sign}${Math.round(node.abnormality * 100)}%`;

          return (
            <g
              key={node.id}
              className="causalNodeGroup"
              transform={`translate(${node.x}, ${node.y})`}
              opacity={nodeOpacity}
            >
              <rect
                width={nodeWidth}
                height={nodeHeight}
                rx="8"
                fill={rectFill}
                stroke={rectStroke}
                strokeWidth={strokeWidth}
                filter={isNodeHighlighted ? "url(#activeGlow)" : undefined}
                className="causalNodeRect"
              />
              <text x="12" y="25" className="svgLabel">
                {node.label}
              </text>
              <text x="12" y="45" className="svgMeta">
                {node.subsystem} | {percentageText}
              </text>
            </g>
          );
        })}
      </svg>
    </section>
  );
}

