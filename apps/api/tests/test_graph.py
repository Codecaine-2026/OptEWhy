import pytest
from api.dependencies import get_graph_repository
from api.main import app
from api.services.graph_repository import DemoGraphRepository
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def use_test_graph_repository() -> None:
    app.dependency_overrides[get_graph_repository] = DemoGraphRepository
    yield
    app.dependency_overrides.pop(get_graph_repository, None)


def test_current_graph_returns_expanded_reference_graph() -> None:
    client = TestClient(app)

    response = client.get("/api/graph/current")

    assert response.status_code == 200
    payload = response.json()
    assert {node["id"] for node in payload["nodes"]} >= {
        "weather_severity",
        "berth_occupancy",
        "import_dwell_time",
        "gate_throughput",
        "chassis_availability",
        "qc_productivity",
        "truck_turn_time",
        "vessel_turnaround_time",
    }
    assert len(payload["edges"]) >= 30
