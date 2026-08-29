import pytest
from api.dependencies import get_scenario_orchestrator
from api.main import app
from api.services.graph_repository import DemoGraphRepository
from api.services.scenario_orchestrator import ScenarioOrchestrator
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def use_test_graph_repository() -> None:
    app.dependency_overrides[get_scenario_orchestrator] = lambda: ScenarioOrchestrator(
        graph_repository=DemoGraphRepository()
    )
    yield
    app.dependency_overrides.pop(get_scenario_orchestrator, None)


def test_scenario_endpoint_uses_requested_intervention() -> None:
    response = TestClient(app).post(
        "/api/scenarios/simulate",
        json={
            "terminal_id": "terminal_alpha",
            "message": "Improve yard density by 20%",
            "intervention": {
                "node_id": "yard_density",
                "operation": "decrease_relative",
                "value": 0.2,
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["structuredIntervention"]["interventions"] == [
        {"node_id": "yard_density", "operation": "decrease_relative", "value": 0.2}
    ]
    assert body["baselineState"]["yard_density"] != body["scenarioState"]["yard_density"]


def test_scenario_endpoint_rejects_unknown_intervention_node() -> None:
    response = TestClient(app).post(
        "/api/scenarios/simulate",
        json={
            "terminal_id": "terminal_alpha",
            "message": "Improve an unknown node",
            "intervention": {
                "node_id": "unknown_node",
                "operation": "decrease_relative",
                "value": 0.2,
            },
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Unsupported intervention node: unknown_node"
