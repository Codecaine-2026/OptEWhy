# OptEWhy

OptEWhy is an AI-driven causal reasoning and scenario simulation platform for port operations. It combines a Dynamic Fuzzy Cognitive Map engine, RAG-based operational evidence, and an LLM orchestration layer to help operators understand why KPIs changed and what could happen if they intervene.

## Repository Layout

- `apps/api`: FastAPI backend with API contracts and orchestration services.
- `apps/web`: Next.js operational workspace UI.
- `packages/causal-engine`: FCM models, propagation, path analysis, loop detection, and scenario simulation.
- `packages/rag-engine`: RAG models, interfaces, and in-memory retrieval mock.
- `packages/llm-orchestrator`: Structured query parsing and backend-grounded explanation interfaces.
- `packages/shared-domain`: Common terminal, vessel, equipment, KPI, and scenario domain models.
- `packages/data-connectors`: Connector interfaces and local mock connector.
- `infra`: Docker, migrations, and observability placeholders.
- `docs`: Domain, API, FCM, RAG, and evaluation notes.
- `scripts`: Placeholder folders for data seeding, calibration, and graph validation.

## Local Setup

```bash
make install
```

This installs Python development dependencies and frontend workspace dependencies.

## Run Locally

For the default Gemini parser, first copy `.env.example` to `.env` and set `GEMINI_API_KEY`.

Run the full local stack:

```bash
make dev
```

Run only the API:

```bash
make api
```

Run only the web app:

```bash
make web
```

The default Gemini structured-output parser is documented in
[`docs/gemini-intent-parser.md`](docs/gemini-intent-parser.md).

With `GRAPH_REPOSITORY_MODE=postgres` and `DATABASE_URL` configured, the graph, query, and
scenario endpoints read graph and snapshot data from PostgreSQL. Seed the reference data with the command documented in
[`scripts/seed-demo-data/README.md`](scripts/seed-demo-data/README.md).

Default local URLs:

- API: `http://localhost:8000`
- API health: `http://localhost:8000/api/health`
- Web: `http://localhost:3000`

## Test

```bash
make test
```

Python tests use `pytest`. Frontend tests use `vitest`.

## Development Notes

- Code, comments, documentation, and commit messages should be written in English.
- The LLM layer should not perform causal calculations.
- Every production answer should be backed by structured causal output, evidence metadata, and model version information.
- Local development uses mocks and does not require paid external services.
