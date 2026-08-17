# RAG Ingestion

The RAG layer retrieves operational evidence for causal explanations.

Target sources:

- Terminal operating procedures.
- Equipment maintenance reports.
- Incident reports.
- Historical operational reports.
- Shift reports.
- Vessel operation reports.
- Yard planning guidelines.
- Equipment manuals.

Document chunks should include metadata for terminal, entity, subsystem, time window, document type, and tags. Retrieval should support filtering by entity, subsystem, and terminal before ranking evidence.

The RAG engine should provide citations and source metadata. It should not replace the causal engine or invent causal claims.

