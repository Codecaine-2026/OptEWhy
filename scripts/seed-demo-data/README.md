# Seed Demo Data

This folder contains utilities for loading prototype terminal data and RAG seed
evidence.

Validate the structural-causality RAG seed file:

```bash
PYTHONPATH=packages/rag-engine/src python scripts/seed-demo-data/load_rag_seed.py
```

The loader reads `data/rag/port_structural_causality_seed.jsonl`, validates each line
as a `DocumentChunk`, and prints the number of loaded chunks.

The seed chunks are industry-reference evidence. They explain plausible mechanisms such
as chassis shortage, import dwell, yard density, gate exceptions, and berth-yard-quay
reinforcing loops. They should be combined with operational evidence before making a
terminal-specific causal claim.
