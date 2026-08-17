FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
COPY apps ./apps
COPY packages ./packages

RUN pip install --no-cache-dir -e ".[dev]"

ENV PYTHONPATH=/app/apps/api/src:/app/packages/causal-engine/src:/app/packages/rag-engine/src:/app/packages/llm-orchestrator/src:/app/packages/shared-domain/src:/app/packages/data-connectors/src

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "apps/api/src"]

