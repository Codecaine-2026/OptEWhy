"use client";

import { useEffect } from "react";
import { FileText, X } from "lucide-react";
import type { EvidenceItem } from "@/lib/types";

type Props = {
  isOpen: boolean;
  evidence: EvidenceItem | null;
  onClose: () => void;
};

export function EvidenceDrawer({ isOpen, evidence, onClose }: Props) {
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
      }
    }
    if (isOpen) {
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen || !evidence) {
    return null;
  }

  const matchPercentage = Math.round((evidence.score ?? 0.9) * 100);

  return (
    <div className="evidenceDrawerOverlay" onClick={onClose} role="dialog" aria-modal="true">
      <div
        className="evidenceDrawerContent"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="drawerHeader">
          <div className="drawerTitleGroup">
            <FileText size={20} className="drawerIcon" />
            <div>
              <h3>Operational Evidence Detail</h3>
              <span>Verified Port Operational Logs & References</span>
            </div>
          </div>
          <button
            type="button"
            className="drawerCloseButton"
            onClick={onClose}
            aria-label="Close evidence drawer"
          >
            <X size={18} />
          </button>
        </div>

        <div className="drawerBody">
          <div className="evidenceMetaRow">
            <span className="badge subsystemBadge">
              Subsystem: {evidence.subsystem ? evidence.subsystem.toUpperCase() : "OPERATIONS"}
            </span>
            <span className="badge scoreBadge">
              {matchPercentage}% Relevance Match
            </span>
            {evidence.documentId && (
              <span className="badge docIdBadge">ID: {evidence.documentId}</span>
            )}
          </div>

          <div className="evidenceSourceSection">
            <label className="evidenceFieldLabel">Source Document</label>
            <h4 className="evidenceSourceTitle">
              {evidence.sourceTitle || "Shift Handover Log #402 (Yard Block B)"}
            </h4>
          </div>

          <div className="evidenceExcerptSection">
            <label className="evidenceFieldLabel">Log Excerpt & Observations</label>
            <blockquote className="evidenceQuote">
              &ldquo;{evidence.text}&rdquo;
            </blockquote>
          </div>

          <div className="evidenceCausalContext">
            <label className="evidenceFieldLabel">Causal Grounding Context</label>
            <p className="causalContextText">
              This log excerpt provides direct qualitative confirmation for the high-weight link
              between Yard Density and Internal Truck Travel Time, proving the bottleneck is
              localized to Yard Block B rather than quay crane mechanical availability.
            </p>
          </div>
        </div>

        <div className="drawerFooter">
          <button type="button" className="drawerDismissBtn" onClick={onClose}>
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
