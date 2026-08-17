import type { CausalNode } from "@/lib/types";

type Props = {
  node: CausalNode;
};

export function NodeInspector({ node }: Props) {
  return (
    <section className="panel inspectorPanel">
      <div className="panelHeader">
        <h2>Node Inspector</h2>
        <span>{node.subsystem}</span>
      </div>
      <dl className="metricGrid">
        <div>
          <dt>Selected node</dt>
          <dd>{node.label}</dd>
        </div>
        <div>
          <dt>Abnormality</dt>
          <dd>{Math.round(node.abnormality * 100)}%</dd>
        </div>
        <div>
          <dt>Model confidence</dt>
          <dd>82%</dd>
        </div>
      </dl>
    </section>
  );
}

