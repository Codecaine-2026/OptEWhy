from api.main import app
from fastapi.testclient import TestClient


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
