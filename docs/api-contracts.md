# API Contracts

The API exposes causal analysis, scenario simulation, graph retrieval, document ingestion, and evidence search.

Main endpoints:

- `GET /api/health`
- `POST /api/query`
- `POST /api/scenarios/simulate`
- `GET /api/graph/current`
- `GET /api/graph/subgraph`
- `GET /api/analysis/{analysisId}`
- `POST /api/documents/ingest`
- `GET /api/evidence/search`

Responses use camelCase JSON fields. Python code uses snake_case internally and Pydantic aliases at the API boundary.

The query endpoint returns:

- `analysisId`.
- `intent`.
- `answer`.
- `causalResult`.
- `evidence`.
- `visualization`.

Every production analysis should be traceable to a data snapshot, FCM model version, dynamic weight model version, and retrieved evidence identifiers.

