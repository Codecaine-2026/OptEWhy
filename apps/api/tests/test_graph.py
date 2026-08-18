from api.main import app
from fastapi.testclient import TestClient


def test_current_graph_returns_expanded_reference_graph() -> None:
    client = TestClient(app)

    response = client.get("/api/graph/current")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["nodes"]) == 8
    assert len(payload["edges"]) == 12
    assert {node["id"] for node in payload["nodes"]} >= {
        "weather_severity",
        "berth_occupancy",
        "vessel_arrival_delay",
        "vessel_turnaround_time",
    }
