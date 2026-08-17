import type { PathItem } from "@/lib/types";

type Props = {
  paths: PathItem[];
};

export function PathContributionPanel({ paths }: Props) {
  return (
    <section className="panel">
      <div className="panelHeader">
        <h2>Causal Paths</h2>
        <span>Ranked</span>
      </div>
      <div className="pathList">
        {paths.map((path) => (
          <article key={path.id} className="pathItem">
            <div>
              <strong>{path.label}</strong>
              <p>{path.nodes.join(" -> ")}</p>
            </div>
            <b>{Math.round(path.contribution * 100)}%</b>
          </article>
        ))}
      </div>
    </section>
  );
}

