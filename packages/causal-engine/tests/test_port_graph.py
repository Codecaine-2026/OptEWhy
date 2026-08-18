from causal_engine.loops import detect_feedback_loops
from causal_engine.port_graph import build_reference_port_graph, build_reference_port_snapshot


def test_reference_port_graph_has_expected_nodes_and_edges() -> None:
    graph = build_reference_port_graph()
    snapshot = build_reference_port_snapshot()
    node_ids = {node.id for node in graph.nodes}

    assert node_ids == {
        "weather_severity",
        "vessel_arrival_delay",
        "berth_occupancy",
        "yard_density",
        "truck_travel_time",
        "qc_waiting",
        "qc_productivity",
        "vessel_turnaround_time",
    }
    assert len(graph.edges) == 12
    assert set(snapshot.node_values) == node_ids
    assert all(edge.source_node_id in node_ids for edge in graph.edges)
    assert all(edge.target_node_id in node_ids for edge in graph.edges)


def test_reference_port_graph_contains_reinforcing_congestion_loop() -> None:
    graph = build_reference_port_graph()
    snapshot = build_reference_port_snapshot()

    loops = detect_feedback_loops(graph, snapshot)

    assert any(
        set(loop.nodes) == {"qc_waiting", "berth_occupancy", "yard_density", "truck_travel_time"}
        and loop.loop_type == "reinforcing"
        for loop in loops
    )
