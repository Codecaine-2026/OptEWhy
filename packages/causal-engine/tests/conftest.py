import pytest
from causal_engine.models import EdgePolarity, FcmEdge, FcmGraph, FcmNode, FcmSnapshot, NodeType


@pytest.fixture
def sample_graph() -> FcmGraph:
    return FcmGraph(
        id="graph_demo",
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
                label="Truck Travel Time",
                node_type=NodeType.DELAY_FACTOR,
                subsystem="transport",
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
                id="e1",
                source_node_id="yard_density",
                target_node_id="truck_travel_time",
                base_weight=0.8,
                polarity=EdgePolarity.POSITIVE,
                subsystem="yard_to_transport",
            ),
            FcmEdge(
                id="e2",
                source_node_id="truck_travel_time",
                target_node_id="qc_waiting",
                base_weight=0.7,
                polarity=EdgePolarity.POSITIVE,
                subsystem="transport_to_quay",
            ),
            FcmEdge(
                id="e3",
                source_node_id="qc_waiting",
                target_node_id="qc_productivity",
                base_weight=-0.6,
                polarity=EdgePolarity.NEGATIVE,
                subsystem="quay",
            ),
            FcmEdge(
                id="e4",
                source_node_id="qc_waiting",
                target_node_id="yard_density",
                base_weight=0.2,
                polarity=EdgePolarity.POSITIVE,
                subsystem="quay_to_yard",
            ),
        ],
    )


@pytest.fixture
def sample_snapshot() -> FcmSnapshot:
    return FcmSnapshot(
        snapshot_id="snap_demo",
        terminal_id="terminal_alpha",
        node_values={
            "yard_density": 0.8,
            "truck_travel_time": 0.2,
            "qc_waiting": 0.1,
            "qc_productivity": -0.15,
        },
    )

