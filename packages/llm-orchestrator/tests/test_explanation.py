from llm_orchestrator.explanation import BackendGroundedExplanationBuilder


def test_explanation_uses_backend_result() -> None:
    answer = BackendGroundedExplanationBuilder().build(
        {
            "dominantPaths": [
                {
                    "path": ["yard_density", "truck_travel_time", "qc_waiting"],
                    "contributionRatio": 0.43,
                }
            ]
        },
        [],
    )

    assert "43%" in answer

