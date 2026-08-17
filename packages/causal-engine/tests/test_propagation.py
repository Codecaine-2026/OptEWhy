from causal_engine.models import FcmGraph, FcmSnapshot
from causal_engine.propagation import propagate


def test_propagation_returns_frames(sample_graph: FcmGraph, sample_snapshot: FcmSnapshot) -> None:
    frames = propagate(sample_graph, sample_snapshot, steps=2)

    assert len(frames) == 2
    assert "qc_productivity" in frames[-1]

