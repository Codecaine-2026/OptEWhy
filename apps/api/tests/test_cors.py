from api.main import app
from fastapi.testclient import TestClient


def test_local_frontend_origin_can_call_api() -> None:
    response = TestClient(app).options(
        "/api/query",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
