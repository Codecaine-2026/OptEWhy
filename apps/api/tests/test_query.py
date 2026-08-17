from api.main import app
from fastapi.testclient import TestClient


def test_query_endpoint_returns_contract() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/query",
        json={"message": "Why is Vessel A productivity low?", "terminal_id": "terminal_alpha"},
    )

    assert response.status_code == 200
    assert response.json()["analysisId"] == "analysis_demo_001"
