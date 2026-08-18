from math import tanh

import pytest
from causal_engine.training import EdgeTrainingSpec, fit_static_weights


def test_recovers_known_static_weights() -> None:
    true_weights = {
        ("yard_density", "truck_travel_time"): 0.78,
        ("truck_travel_time", "qc_waiting"): 0.66,
        ("qc_waiting", "qc_productivity"): -0.71,
    }
    states = [
        (-0.8, 0.1, -0.2, 0.3),
        (-0.5, -0.3, 0.4, -0.1),
        (-0.2, 0.6, -0.5, 0.2),
        (0.1, -0.7, 0.3, -0.4),
        (0.3, 0.2, 0.7, 0.1),
        (0.5, -0.4, -0.6, 0.4),
        (0.7, 0.5, 0.1, -0.3),
        (0.9, -0.1, 0.5, 0.0),
    ]
    rows = []
    for yard_density, truck_travel_time, qc_waiting, qc_productivity in states:
        rows.append(
            {
                "yard_density_t": yard_density,
                "truck_travel_time_t": truck_travel_time,
                "truck_travel_time_next": tanh(
                    truck_travel_time + 0.78 * yard_density
                ),
                "qc_waiting_t": qc_waiting,
                "qc_waiting_next": tanh(qc_waiting + 0.66 * truck_travel_time),
                "qc_productivity_t": qc_productivity,
                "qc_productivity_next": tanh(qc_productivity - 0.71 * qc_waiting),
            }
        )

    specs = [EdgeTrainingSpec(source, target) for source, target in true_weights]
    result = fit_static_weights(rows, specs, ridge_alpha=1e-12)
    learned = {
        (edge.source_node_id, edge.target_node_id): edge.weight for edge in result.edges
    }

    assert result.training_rows == len(rows)
    assert result.overall_rmse < 1e-10
    for edge, true_weight in true_weights.items():
        assert learned[edge] == pytest.approx(true_weight, abs=1e-9)
        assert -1.0 <= learned[edge] <= 1.0


def test_clips_weights_to_fcm_bounds() -> None:
    rows = [
        {
            "source_t": source,
            "target_t": 0.0,
            "target_next": tanh(1.5 * source),
        }
        for source in (-0.8, -0.4, 0.4, 0.8)
    ]

    result = fit_static_weights(
        rows,
        [EdgeTrainingSpec("source", "target")],
        ridge_alpha=1e-12,
    )

    assert result.edges[0].weight == 1.0


def test_requires_training_rows() -> None:
    with pytest.raises(ValueError, match="At least one training row"):
        fit_static_weights([], [EdgeTrainingSpec("source", "target")])
