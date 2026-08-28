"use client";

import { Send } from "lucide-react";
import { useState } from "react";
import { submitCopilotQuery } from "@/lib/api";
import type { QueryResponse } from "@/lib/types";
import { AnalysisDetails } from "./AnalysisDetails";

type Props = {
  onResponse?: (response: QueryResponse) => void;
};

export function CopilotPanel({ onResponse }: Props) {
  const [message, setMessage] = useState("Why is Vessel A productivity low?");
  const [answer, setAnswer] = useState(
    "Ask an operational question to inspect causal paths, evidence, and scenario impact."
  );
  const [isLoading, setIsLoading] = useState(false);
  const [analysis, setAnalysis] = useState<QueryResponse | null>(null);

  async function handleSubmit() {
    const trimmedMessage = message.trim();
    if (!trimmedMessage) {
      setAnswer("Enter an operational question first.");
      return;
    }

    setIsLoading(true);
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
        <h2>AI Copilot</h2>
        <span>Causal analysis</span>
      </div>
      <div className="answerBox" aria-live="polite">{answer}</div>
      {analysis ? <AnalysisDetails evidence={analysis.evidence} reasoningTrace={analysis.reasoningTrace} /> : null}
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
          onClick={handleSubmit}
          disabled={isLoading}
        >
          <Send size={17} />
        </button>
      </div>
    </section>
  );
}
