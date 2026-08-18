# RAG Ingestion

The RAG layer retrieves evidence for causal explanations. It should support two
evidence categories:

- Industry-reference evidence: public references that describe plausible mechanisms,
  such as chassis shortages increasing dwell or high yard utilization reducing berth
  and gate productivity.
- Operational evidence: terminal-specific reports, logs, incidents, maintenance events,
  shift notes, and historical observations.

Industry references help justify why a structural path is plausible. Operational
evidence is still required before claiming that the path caused a real event at a real
terminal.

Document metadata supports source citation and graph linkage:

- `source_title`, `source_url`, `publisher`, `published_date`
- `evidence_scope`, `claim_type`
- `subsystem`, `tags`
- `related_nodes`, `related_edges`, `scenario_ids`

The seed file at `data/rag/port_structural_causality_seed.jsonl` contains concise
industry-reference chunks tied to the structural graph and synthetic scenario labels.
The seed loader validates those chunks with the RAG models but does not build a
production vector database.

The RAG engine should provide citations and source metadata. It should not replace the
causal engine, and it should not convert synthetic data or generic industry references
into proof of terminal-specific causality.
