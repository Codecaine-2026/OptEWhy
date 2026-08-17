"use client";

import { Send } from "lucide-react";
import { useState } from "react";
import { submitCopilotQuery } from "@/lib/api";

export function CopilotPanel() {
  const [message, setMessage] = useState("Why is Vessel A productivity low?");
  const [answer, setAnswer] = useState(
    "Ask an operational question to inspect causal paths, evidence, and scenario impact."
  );

  async function handleSubmit() {
    const response = await submitCopilotQuery(message);
    setAnswer(response.answer);
  }

  return (
    <section className="panel copilotPanel">
      <div className="panelHeader">
        <h2>AI Copilot</h2>
        <span>Root mechanism</span>
      </div>
      <div className="answerBox">{answer}</div>
      <div className="chatInput">
        <input value={message} onChange={(event) => setMessage(event.target.value)} />
        <button aria-label="Send query" onClick={handleSubmit}>
          <Send size={17} />
        </button>
      </div>
    </section>
  );
}

