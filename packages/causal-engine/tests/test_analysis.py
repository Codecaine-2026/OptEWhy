from causal_engine.analysis import find_dominant_paths
from causal_engine.models import FcmGraph, FcmSnapshot


def test_finds_dominant_path(sample_graph: FcmGraph, sample_snapshot: FcmSnapshot) -> None:
    paths = find_dominant_paths(sample_graph, sample_snapshot, "qc_productivity")

    assert paths
    assert paths[0].path[-1] == "qc_productivity"

