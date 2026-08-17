import type { EvidenceItem } from "@/lib/types";

type Props = {
  items: EvidenceItem[];
};

export function EvidenceDrawer({ items }: Props) {
  return (
    <section className="panel evidencePanel">
      <div className="panelHeader">
        <h2>Evidence</h2>
        <span>{items.length} sources</span>
      </div>
      <div className="evidenceList">
        {items.map((item) => (
          <article key={item.id} className="evidenceItem">
            <strong>{item.title}</strong>
            <p>{item.text}</p>
            <span>{Math.round(item.score * 100)}% relevance</span>
          </article>
        ))}
      </div>
    </section>
  );
}

