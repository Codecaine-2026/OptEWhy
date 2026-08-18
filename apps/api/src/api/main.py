from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import get_cors_allowed_origins
from api.routes import analysis, documents, evidence, graph, health, query, scenarios

app = FastAPI(
    title="OptEWhy Port Causal Intelligence API",
    version="0.1.0",
    description="Causal reasoning and scenario simulation API for port operations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(health.router)
app.include_router(query.router, prefix="/api")
app.include_router(scenarios.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(evidence.router, prefix="/api")
