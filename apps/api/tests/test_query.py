from api.dependencies import get_query_orchestrator
from api.main import app
from api.services.query_orchestrator import QueryOrchestrator
from fastapi.testclient import TestClient
from llm_orchestrator.models import IntentType, StructuredQuery
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

    reasoning_trace = body["reasoningTrace"]
    assert reasoning_trace["targetNodeId"] == body["causalResult"]["targetNodeId"]
    assert reasoning_trace["steps"]
    trace_step_ids = {step["id"] for step in reasoning_trace["steps"]}
    dominant_path_steps = [
        step for step in reasoning_trace["steps"] if step["stepType"] == "dominant_path"
    ]
    feedback_loop_steps = [
        step for step in reasoning_trace["steps"] if step["stepType"] == "feedback_loop"
    ]
    assert dominant_path_steps
    assert feedback_loop_steps
    assert dominant_path_steps[0]["usedNodeIds"] == body["causalResult"]["dominantPaths"][0][
        "path"
    ]
    assert dominant_path_steps[0]["usedEdgeIds"]
    assert dominant_path_steps[0]["contributionRatio"] > 0
    assert dominant_path_steps[0]["confidence"] > 0

    visualization = body["visualization"]
    assert visualization["highlightedNodes"]
    assert visualization["highlightedEdges"]
    assert visualization["focusSubgraphId"] == (
        f"reasoning_{body['causalResult']['targetNodeId']}"
    )

    reasoning_nodes = visualization["reasoningNodes"]
    reasoning_edges = visualization["reasoningEdges"]
    loops = visualization["loops"]
    assert reasoning_nodes
    assert reasoning_edges
    assert loops
    assert {node["id"] for node in reasoning_nodes} >= set(
        body["causalResult"]["dominantPaths"][0]["path"]
    )

    first_edge = reasoning_edges[0]
    assert first_edge["id"] in visualization["highlightedEdges"]
    assert first_edge["sourceNodeId"]
    assert first_edge["targetNodeId"]
    assert isinstance(first_edge["weight"], float)
    assert first_edge["polarity"] in {"positive", "negative"}
    assert first_edge["confidence"] > 0
    assert first_edge["reasoningStepIds"]
    assert set(first_edge["reasoningStepIds"]) <= trace_step_ids

    first_loop = loops[0]
    assert first_loop["id"]
    assert first_loop["id"] in trace_step_ids
    assert first_loop["nodeIds"]
    assert first_loop["edgeIds"]
    assert first_loop["loopType"] in {"reinforcing", "balancing"}
    assert first_loop["strength"] >= 0
    assert first_loop["confidence"] > 0


class FailingParser:
    def __init__(self, error: Exception) -> None:
        self._error = error

    def parse(self, message: str) -> StructuredQuery:
        raise self._error


class GreetingResponder:
    def respond(self, message: str) -> str:
        assert message == "hi"
        return "Hi! How can I help?"


class GreetingParser:
    def parse(self, message: str) -> StructuredQuery:
        return StructuredQuery(intent=IntentType.CASUAL_CONVERSATION, raw_message=message)


def test_query_endpoint_uses_chat_responder_for_greetings() -> None:
    app.dependency_overrides[get_query_orchestrator] = lambda: QueryOrchestrator(
        parser=GreetingParser(),
        chat_responder=GreetingResponder(),
    )
    try:
        response = TestClient(app).post(
            "/api/query",
            json={"message": "hi", "terminal_id": "terminal_alpha"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["intent"] == "casual_conversation"
    assert response.json()["answer"] == "Hi! How can I help?"
    assert response.json()["causalResult"] == {}


def test_query_endpoint_returns_503_when_gemini_parser_is_unavailable() -> None:
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
