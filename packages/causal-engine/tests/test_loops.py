from causal_engine.loops import detect_feedback_loops
from causal_engine.models import FcmGraph, FcmSnapshot


def test_detects_feedback_loop(sample_graph: FcmGraph, sample_snapshot: FcmSnapshot) -> None:
    loops = detect_feedback_loops(sample_graph, sample_snapshot)

    assert loops
    assert loops[0].loop_type in {"reinforcing", "balancing"}

