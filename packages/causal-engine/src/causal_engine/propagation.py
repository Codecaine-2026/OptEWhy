import numpy as np

from causal_engine.models import FcmGraph, FcmSnapshot


def propagate(graph: FcmGraph, snapshot: FcmSnapshot, steps: int = 1) -> list[dict[str, float]]:
    node_ids = [node.id for node in graph.nodes]
    index = {node_id: offset for offset, node_id in enumerate(node_ids)}
    state = np.array([snapshot.node_values.get(node_id, 0.0) for node_id in node_ids], dtype=float)
    weights = np.zeros((len(node_ids), len(node_ids)), dtype=float)

    for edge in graph.edges:
        if edge.source_node_id in index and edge.target_node_id in index:
            weights[index[edge.source_node_id], index[edge.target_node_id]] = edge.base_weight

    frames: list[dict[str, float]] = []
    for _ in range(steps):
        propagated = state @ weights
        state = np.tanh(state + propagated)
        frames.append({node_id: float(state[index[node_id]]) for node_id in node_ids})

    return frames

