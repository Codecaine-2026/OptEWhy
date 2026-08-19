import type { CausalEdge, CausalNode } from "@/lib/types";

type Props = {
  nodes: CausalNode[];
  edges: CausalEdge[];
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

export function CausalMapCanvas({ nodes, edges }: Props) {
  const nodeById = new Map(nodes.map((node) => [node.id, node]));

  return (
    <section className="causalCanvas" aria-label={`${nodes.length}-node causal system map`}>
      <svg viewBox="0 0 440 650" role="img">
        <defs>
          <marker id="positiveArrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="#1f8a70" />
          </marker>
          <marker id="negativeArrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="#b33a3a" />
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
          return (
            <line
              key={edge.id}
              {...points}
              stroke={isPositive ? "#1f8a70" : "#b33a3a"}
              strokeWidth={Math.max(2, Math.abs(edge.weight) * 7)}
              strokeLinecap="round"
              opacity={0.76}
              markerEnd={`url(#${isPositive ? "positiveArrow" : "negativeArrow"})`}
            />
          );
        })}
        {nodes.map((node) => (
          <g key={node.id} transform={`translate(${node.x}, ${node.y})`}>
            <rect
              width={nodeWidth}
              height={nodeHeight}
              rx="8"
              fill={node.abnormality >= 0 ? "#f8faf8" : "#fff7f7"}
              stroke={node.abnormality >= 0 ? "#1f8a70" : "#b33a3a"}
              strokeWidth={1.5 + Math.abs(node.abnormality) * 2}
            />
            <text x="12" y="25" className="svgLabel">
              {node.label}
            </text>
            <text x="12" y="45" className="svgMeta">
              {node.subsystem} | {Math.round(node.abnormality * 100)}%
            </text>
          </g>
        ))}
      </svg>
    </section>
  );
}
