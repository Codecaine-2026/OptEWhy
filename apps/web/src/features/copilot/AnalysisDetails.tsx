import type { EvidenceItem, ReasoningTrace } from "@/lib/types";

type Props = {
  evidence: EvidenceItem[];
  reasoningTrace: ReasoningTrace;
};

export function AnalysisDetails({ evidence, reasoningTrace }: Props) {
  if (evidence.length === 0 && reasoningTrace.steps.length === 0) {
    return null;
  }

  return (
    <section className="analysisDetails" aria-label="Analysis details">
      <div className="analysisDetailSection">
        <h3>Reasoning trace</h3>
        <ol>
          {reasoningTrace.steps.map((step) => (
            <li key={step.id}>
              <strong>{step.stepType === "dominant_path" ? "Causal path" : "Feedback loop"}</strong>
              <span>{step.summary}</span>
            </li>
          ))}
        </ol>
      </div>
      <div className="analysisDetailSection">
        <h3>Evidence</h3>
        <ul>
          {evidence.map((item) => (
            <li key={item.chunkId}>
              {item.sourceUrl ? (
                <a href={item.sourceUrl} target="_blank" rel="noreferrer">
                  {item.sourceTitle ?? item.documentId}
                </a>
              ) : (
                <strong>{item.sourceTitle ?? item.documentId}</strong>
              )}
              <span>{item.text}</span>
              <small>Relevance {Math.round(item.score * 100)}%</small>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
