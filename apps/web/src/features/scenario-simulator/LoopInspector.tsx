import type { LoopItem } from "@/lib/types";

type Props = {
  loops: LoopItem[];
};

export function LoopInspector({ loops }: Props) {
  return (
    <section className="panel">
      <div className="panelHeader">
        <h2>Feedback Loops</h2>
        <span>{loops.length} active</span>
      </div>
      {loops.map((loop) => (
        <article key={loop.id} className="loopItem">
          <strong>{loop.label}</strong>
          <span>{loop.type}</span>
          <meter value={loop.strength} max={1} />
        </article>
      ))}
    </section>
  );
}

