from causal_engine.loops import detect_feedback_loops
from causal_engine.port_graph import build_reference_port_graph, build_reference_port_snapshot


def test_reference_port_graph_has_expected_nodes_and_edges() -> None:
    graph = build_reference_port_graph()
    snapshot = build_reference_port_snapshot()
    node_ids = {node.id for node in graph.nodes}

    assert node_ids >= {
        "import_volume_pressure",
        "vessel_bunching",
        "weather_severity",
        "vessel_arrival_delay",
        "gate_throughput",
        "gate_queue_length",
        "truck_arrival_peaking",
        "truck_appointment_compliance",
        "document_error_rate",
        "gate_exception_rate",
        "chassis_availability",
        "warehouse_capacity_pressure",
        "import_dwell_time",
        "berth_occupancy",
        "yard_density",
        "yard_rehandle_rate",
        "yard_crane_availability",
        "empty_container_imbalance",
        "truck_travel_time",
        "truck_turn_time",
        "qc_waiting",
        "qc_productivity",
        "crane_equipment_availability",
        "labor_availability",
        "berth_productivity",
        "vessel_turnaround_time",
    }
    assert set(snapshot.node_values) == node_ids
    assert all(edge.source_node_id in node_ids for edge in graph.edges)
    assert all(edge.target_node_id in node_ids for edge in graph.edges)
    assert {
        (edge.source_node_id, edge.target_node_id, edge.polarity.value) for edge in graph.edges
    } >= {
        ("chassis_availability", "gate_throughput", "positive"),
        ("gate_throughput", "import_dwell_time", "negative"),
        ("import_dwell_time", "yard_density", "positive"),
        ("yard_density", "yard_rehandle_rate", "positive"),
        ("truck_travel_time", "qc_waiting", "positive"),
        ("qc_waiting", "qc_productivity", "negative"),
        ("truck_turn_time", "gate_throughput", "negative"),
    }


def test_reference_port_graph_contains_reinforcing_congestion_loop() -> None:
    graph = build_reference_port_graph()
    snapshot = build_reference_port_snapshot()

    loops = detect_feedback_loops(graph, snapshot)

    assert any(
        set(loop.nodes) == {"qc_waiting", "berth_occupancy", "yard_density", "truck_travel_time"}
        and loop.loop_type == "reinforcing"
        for loop in loops
    )
