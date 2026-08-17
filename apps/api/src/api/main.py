from fastapi import FastAPI

from api.routes import analysis, documents, evidence, graph, health, query, scenarios

app = FastAPI(
    title="OptEWhy Port Causal Intelligence API",
    version="0.1.0",
    description="Causal reasoning and scenario simulation API for port operations.",
)

app.include_router(health.router)
app.include_router(query.router, prefix="/api")
app.include_router(scenarios.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(evidence.router, prefix="/api")

