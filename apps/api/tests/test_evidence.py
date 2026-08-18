from api.main import app
from fastapi.testclient import TestClient


def test_evidence_search_returns_qc_seed_chunks() -> None:
    response = TestClient(app).get(
        "/api/evidence/search",
        params={
            "terminal_id": "terminal_alpha",
            "node_id": "qc_productivity",
            "question": "Why is QC productivity down?",
        },
    )

    assert response.status_code == 200
    results = response.json()["results"]
    assert results
    assert any("qc_productivity" in result.get("relatedNodes", []) for result in results)


def test_evidence_search_returns_chassis_structural_evidence() -> None:
    response = TestClient(app).get(
        "/api/evidence/search",
        params={
            "terminal_id": "terminal_alpha",
            "node_id": "chassis_availability",
            "question": "Could chassis shortage cause yard congestion?",
        },
    )

    assert response.status_code == 200
    results = response.json()["results"]
    assert results[0]["documentId"] == "industry_chassis_dwell_yard_density"


def test_evidence_search_returns_yard_retrieval_evidence_for_truck_turn_time() -> None:
    response = TestClient(app).get(
        "/api/evidence/search",
        params={
            "terminal_id": "terminal_alpha",
            "node_id": "truck_turn_time",
            "question": "Why is truck turn time high if gate lanes are not the root cause?",
        },
    )

    assert response.status_code == 200
    results = response.json()["results"]
    assert any("yard retrieval" in result["text"].lower() for result in results)
