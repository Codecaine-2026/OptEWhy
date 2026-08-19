from api.dependencies import get_query_orchestrator
from api.main import app
from api.services.query_orchestrator import QueryOrchestrator
from fastapi.testclient import TestClient
from llm_orchestrator.models import StructuredQuery
from llm_orchestrator.parsers import (
    IntentParserUnavailableError,
    InvalidIntentTargetError,
    MockIntentParser,
)


def test_query_endpoint_returns_contract() -> None:
    app.dependency_overrides[get_query_orchestrator] = lambda: QueryOrchestrator(
        parser=MockIntentParser()
    )
    try:
        response = TestClient(app).post(
            "/api/query",
            json={"message": "Why is Vessel A productivity low?", "terminal_id": "terminal_alpha"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["analysisId"] == "analysis_demo_001"
    assert body["causalResult"]["dominantPaths"][0]["contributionRatio"] > 0
    assert "approximately 0%" not in body["answer"]


class FailingParser:
    def __init__(self, error: Exception) -> None:
        self._error = error

    def parse(self, message: str) -> StructuredQuery:
        raise self._error


def test_query_endpoint_returns_503_when_openai_parser_is_unavailable() -> None:
    app.dependency_overrides[get_query_orchestrator] = lambda: QueryOrchestrator(
        parser=FailingParser(IntentParserUnavailableError("offline"))
    )
    try:
        response = TestClient(app).post(
            "/api/query",
            json={"message": "Why is productivity low?", "terminal_id": "terminal_alpha"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503


def test_query_endpoint_returns_422_for_unsupported_target() -> None:
    app.dependency_overrides[get_query_orchestrator] = lambda: QueryOrchestrator(
        parser=FailingParser(InvalidIntentTargetError("unsupported node"))
    )
    try:
        response = TestClient(app).post(
            "/api/query",
            json={"message": "Explain that metric", "terminal_id": "terminal_alpha"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["detail"] == "unsupported node"
