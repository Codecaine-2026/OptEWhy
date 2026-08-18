from causal_engine.models import FcmGraph, FcmSnapshot
from causal_engine.port_graph import build_reference_port_graph, build_reference_port_snapshot


def build_demo_graph() -> FcmGraph:
    return build_reference_port_graph()


def build_demo_snapshot() -> FcmSnapshot:
    return build_reference_port_snapshot()
