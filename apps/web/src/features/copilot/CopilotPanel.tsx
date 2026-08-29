"use client";

import { Send, FileText } from "lucide-react";
import { useState } from "react";
import { submitCopilotQuery } from "@/lib/api";

import type { EvidenceItem, QueryResponse } from "@/lib/types";

const DEMO_PROMPTS = [
  {
    label: "🔍 Diagnosis: Vessel A Delay",
    query: "Why is Vessel A productivity low?"
  },
  {
    label: "⚡ What-If: Move Block B to D",
    query: "What if we move 15% of Block B containers to Block D?"
  }
];

const DEFAULT_EVIDENCE: EvidenceItem[] = [
  {
    documentId: "shift_report_block_b_001",
    sourceTitle: "Shift Handover Log #402 (Yard Block B)",
    subsystem: "yard",
    text: "07:15 - RTG-02 mechanical fault led to 25min container retrieval backlog and internal truck queuing at Block B.",
    score: 0.94
  }
];

type Props = {
  onAnalysisComplete?: (response: QueryResponse) => void;
  onSelectEvidence?: (evidence: EvidenceItem) => void;
};

export function CopilotPanel({ onAnalysisComplete, onSelectEvidence }: Props) {
  const [message, setMessage] = useState("Why is Vessel A productivity low?");
  const [answer, setAnswer] = useState(
    "Ask an operational question to inspect causal paths, evidence, and scenario impact."
  );
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>(DEFAULT_EVIDENCE);
  const [isLoading, setIsLoading] = useState(false);

  async function handleQuery(queryText: string) {
    const trimmedMessage = queryText.trim();
    if (!trimmedMessage) {
      setAnswer("Enter an operational question first.");
      return;
    }

    setMessage(trimmedMessage);
    setIsLoading(true);
    setAnswer("Analyzing the causal graph...");
    try {
      const response = await submitCopilotQuery(trimmedMessage, { fallbackToMock: true });
      setAnswer(response.answer);
      if (response.evidence && response.evidence.length > 0) {
        setEvidenceList(response.evidence);
      }
      onAnalysisComplete?.(response);
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
      <div className="answerBox" aria-live="polite">
        <p>{answer}</p>
        {evidenceList.length > 0 && (
          <div className="citationsArea">
            <span className="citationsLabel">Grounded Evidence:</span>
            <div className="citationsList">
              {evidenceList.map((item, idx) => (
                <button
                  key={item.documentId || idx}
                  type="button"
                  className="citationPillButton"
                  onClick={() => onSelectEvidence?.(item)}
                >
                  <FileText size={13} />
                  <span>{item.sourceTitle || `Citation #${idx + 1}`}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="quickPromptArea">
        <span className="quickPromptLabel">Quick Scenarios:</span>
        <div className="quickPromptList">
          {DEMO_PROMPTS.map((prompt) => (
            <button
              key={prompt.label}
              type="button"
              className="quickPromptButton"
              disabled={isLoading}
              onClick={() => void handleQuery(prompt.query)}
            >
              {prompt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="chatInput">
        <input
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !isLoading) void handleQuery(message);
          }}
          disabled={isLoading}
        />
        <button
          aria-label={isLoading ? "Analyzing query" : "Send query"}
          onClick={() => void handleQuery(message)}
          disabled={isLoading}
        >
          <Send size={17} />
        </button>
      </div>
    </section>
  );
}


