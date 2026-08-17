from causal_engine.models import FcmGraph, FcmSnapshot, ScenarioIntervention
from causal_engine.simulation import simulate_scenario


def test_simulates_scenario(sample_graph: FcmGraph, sample_snapshot: FcmSnapshot) -> None:
    result = simulate_scenario(
        sample_graph,
        sample_snapshot,
        [ScenarioIntervention(node_id="yard_density", operation="decrease_relative", value=0.2)],
    )

    assert result.baseline["yard_density"] == 0.8
    assert result.propagation_frames

