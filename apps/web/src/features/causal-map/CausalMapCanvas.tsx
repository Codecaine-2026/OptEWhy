import type { CausalEdge, CausalNode } from "@/lib/types";

type Props = {
  nodes: CausalNode[];
  edges: CausalEdge[];
};

export function CausalMapCanvas({ nodes, edges }: Props) {
  const nodeById = new Map(nodes.map((node) => [node.id, node]));

  return (
    <section className="causalCanvas" aria-label="Dynamic causal system map">
      <svg viewBox="0 0 980 390" role="img">
        {edges.map((edge) => {
          const source = nodeById.get(edge.source);
          const target = nodeById.get(edge.target);
          if (!source || !target) {
            return null;
          }
          return (
            <line
              key={edge.id}
              x1={source.x + 78}
              y1={source.y + 28}
              x2={target.x + 4}
              y2={target.y + 28}
              stroke={edge.polarity === "positive" ? "#1f8a70" : "#b33a3a"}
              strokeWidth={Math.max(2, Math.abs(edge.weight) * 7)}
              strokeLinecap="round"
              opacity={0.76}
            />
          );
        })}
        {nodes.map((node) => (
          <g key={node.id} transform={`translate(${node.x}, ${node.y})`}>
            <rect
              width="168"
              height="58"
              rx="8"
              fill={node.abnormality >= 0 ? "#f8faf8" : "#fff7f7"}
              stroke={node.abnormality >= 0 ? "#1f8a70" : "#b33a3a"}
              strokeWidth={1.5 + Math.abs(node.abnormality) * 2}
            />
            <text x="14" y="24" className="svgLabel">
              {node.label}
            </text>
            <text x="14" y="43" className="svgMeta">
              {node.subsystem} | {Math.round(node.abnormality * 100)}%
            </text>
          </g>
        ))}
      </svg>
    </section>
  );
}

