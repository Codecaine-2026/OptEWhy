import networkx as nx

from causal_engine.models import FcmGraph


def to_networkx(graph: FcmGraph) -> nx.DiGraph:
    directed = nx.DiGraph()
    for node in graph.nodes:
        directed.add_node(node.id, label=node.label, subsystem=node.subsystem)
    for edge in graph.edges:
        directed.add_edge(
            edge.source_node_id,
            edge.target_node_id,
            id=edge.id,
            weight=edge.base_weight,
            confidence=edge.confidence,
        )
    return directed

