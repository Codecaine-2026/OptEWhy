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


def test_explanation_summarizes_the_primary_path_and_loop() -> None:
    answer = BackendGroundedExplanationBuilder().build(
        {
            "dominantPaths": [
                {"path": ["qc_waiting", "qc_productivity"], "contributionRatio": 0.29},
                {"path": ["yard_density", "truck_travel_time", "qc_waiting"], "contributionRatio": 0.18},
            ],
            "feedbackLoops": [
                {"nodes": ["qc_waiting", "berth_occupancy", "yard_density"], "strength": 0.7},
                {"nodes": ["yard_density", "truck_travel_time", "qc_waiting"], "strength": 0.9},
            ],
        },
        [],
    )

    assert "yard_density -> truck_travel_time -> qc_waiting" in answer
    assert "qc_waiting -> berth_occupancy -> yard_density" not in answer
    assert "target KPI movement.\nMost important feedback loop:" in answer
