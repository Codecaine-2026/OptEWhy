"use client";

import { FileText, Send } from "lucide-react";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { submitCopilotQuery } from "@/lib/api";
import type { EvidenceItem, QueryResponse } from "@/lib/types";
import { AnalysisDetails } from "./AnalysisDetails";

type Props = {
  onResponse?: (response: QueryResponse) => void;
  onClearResponse?: () => void;
  onSelectEvidence?: (evidence: EvidenceItem) => void;
};

const quickPrompts = [
  { label: "Diagnose Vessel A", query: "Why is Vessel A productivity low?" },
  { label: "Simulate yard improvement", query: "What if yard density improves by 15%?" }
];

export function CopilotPanel({ onResponse, onClearResponse, onSelectEvidence }: Props) {
  const [message, setMessage] = useState("Why is Vessel A productivity low?");
  const [answer, setAnswer] = useState(
    "Ask an operational question to inspect causal paths, evidence, and scenario impact."
  );
  const [isLoading, setIsLoading] = useState(false);
  const [analysis, setAnalysis] = useState<QueryResponse | null>(null);

  async function handleSubmit(query = message) {
    const trimmedMessage = query.trim();
    if (!trimmedMessage) {
      setAnswer("Enter an operational question first.");
      return;
    }

    setIsLoading(true);
    setAnalysis(null);
    onClearResponse?.();
    setAnswer("Analyzing the causal graph...");
    try {
      const response = await submitCopilotQuery(trimmedMessage);
      setAnswer(response.answer);
      setAnalysis(response);
      onResponse?.(response);
    } catch (error) {
      setAnswer(error instanceof Error ? error.message : "The Copilot request failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="panel copilotPanel">
      <div className="panelHeader">
        <h2>
          <img className="copilotLogo" src="/assets/optewhy-logo.png" alt="OptEWhy logo" />
        </h2>
        <span>Causal analysis</span>
      </div>
      <div className="answerBox" aria-live="polite">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{answer}</ReactMarkdown>
        {analysis?.evidence.length ? (
          <div className="citationPills" aria-label="Grounded evidence">
            {analysis.evidence.map((item) => (
              <button key={item.chunkId} type="button" onClick={() => onSelectEvidence?.(item)}>
                <FileText size={13} />
                {item.sourceTitle ?? item.documentId}
              </button>
            ))}
          </div>
        ) : null}
      </div>
      {analysis ? <AnalysisDetails evidence={analysis.evidence} reasoningTrace={analysis.reasoningTrace} /> : null}
      <div className="quickPromptArea" aria-label="Quick prompts">
        {quickPrompts.map((prompt) => (
          <button
            key={prompt.label}
            type="button"
            disabled={isLoading}
            onClick={() => {
              setMessage(prompt.query);
              void handleSubmit(prompt.query);
            }}
          >
            {prompt.label}
          </button>
        ))}
      </div>
      <div className="chatInput">
        <input
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !isLoading) void handleSubmit();
          }}
          disabled={isLoading}
        />
        <button
          aria-label={isLoading ? "Analyzing query" : "Send query"}
          onClick={() => void handleSubmit()}
          disabled={isLoading}
        >
          <Send size={17} />
        </button>
      </div>
    </section>
  );
}
