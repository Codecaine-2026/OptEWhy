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

## PostgreSQL graph seed

After the database migrations are applied, seed the reference graph and current-shift snapshot:

```bash
DATABASE_URL=postgresql://optewhy:optewhy@localhost:5432/optewhy \
PYTHONPATH=apps/api/src:packages/causal-engine/src \
python scripts/seed-demo-data/seed_graph.py
```

Set `GRAPH_REPOSITORY_MODE=postgres` with `DATABASE_URL` to make the graph, query, and scenario
APIs read their graph and snapshot data from PostgreSQL. The default `demo` mode uses the
in-memory reference repository for local development and tests.
