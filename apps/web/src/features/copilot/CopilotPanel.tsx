"use client";

import { Send } from "lucide-react";
import { useState } from "react";
import { submitCopilotQuery } from "@/lib/api";

export function CopilotPanel() {
  const [message, setMessage] = useState("Why is Vessel A productivity low?");
  const [answer, setAnswer] = useState(
    "Ask an operational question to inspect causal paths, evidence, and scenario impact."
  );
  const [isLoading, setIsLoading] = useState(false);

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
        <span>Root mechanism</span>
      </div>
      <div className="answerBox" aria-live="polite">{answer}</div>
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
