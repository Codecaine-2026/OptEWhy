import pytest
from api.services.graph_repository import DemoGraphRepository


def test_demo_repository_returns_reference_graph_and_snapshot() -> None:
    repository = DemoGraphRepository()

    graph = repository.get_graph("terminal_alpha")
    snapshot = repository.get_current_snapshot("terminal_alpha")

    assert graph.nodes
    assert graph.edges
    assert snapshot.node_values["qc_productivity"] == -0.1


def test_demo_repository_rejects_unknown_terminal() -> None:
    repository = DemoGraphRepository()

    with pytest.raises(ValueError, match="Unknown terminal"):
        repository.get_graph("unknown_terminal")
