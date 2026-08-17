from causal_engine.models import EdgePolarity, FcmEdge, FcmGraph, FcmNode, FcmSnapshot, NodeType


def build_demo_graph() -> FcmGraph:
    return FcmGraph(
        id="graph_terminal_alpha_demo",
        terminal_id="terminal_alpha",
        nodes=[
            FcmNode(
                id="yard_density",
                label="Yard Density",
                node_type=NodeType.STATE_KPI,
                subsystem="yard",
            ),
            FcmNode(
                id="truck_travel_time",
                label="Internal Truck Travel Time",
                node_type=NodeType.DELAY_FACTOR,
                subsystem="internal_transport",
            ),
            FcmNode(
                id="qc_waiting",
                label="QC Waiting",
                node_type=NodeType.DELAY_FACTOR,
                subsystem="quay",
            ),
            FcmNode(
                id="qc_productivity",
                label="QC Productivity",
                node_type=NodeType.PERFORMANCE_KPI,
                subsystem="quay",
            ),
        ],
        edges=[
            FcmEdge(
                id="edge_yard_density_to_truck_travel_time",
                source_node_id="yard_density",
                target_node_id="truck_travel_time",
                base_weight=0.78,
                polarity=EdgePolarity.POSITIVE,
                confidence=0.82,
                subsystem="yard_to_transport",
            ),
            FcmEdge(
                id="edge_truck_travel_time_to_qc_waiting",
                source_node_id="truck_travel_time",
                target_node_id="qc_waiting",
                base_weight=0.66,
                polarity=EdgePolarity.POSITIVE,
                confidence=0.76,
                subsystem="transport_to_quay",
            ),
            FcmEdge(
                id="edge_qc_waiting_to_qc_productivity",
                source_node_id="qc_waiting",
                target_node_id="qc_productivity",
                base_weight=-0.71,
                polarity=EdgePolarity.NEGATIVE,
                confidence=0.79,
                subsystem="quay",
            ),
        ],
    )


def build_demo_snapshot() -> FcmSnapshot:
    return FcmSnapshot(
        snapshot_id="snap_current_shift_demo",
        terminal_id="terminal_alpha",
        node_values={
            "yard_density": 0.85,
            "truck_travel_time": 0.62,
            "qc_waiting": 0.58,
            "qc_productivity": -0.15,
        },
    )

