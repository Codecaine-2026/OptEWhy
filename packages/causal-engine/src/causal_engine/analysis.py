from collections.abc import Iterable
from math import prod

import networkx as nx

from causal_engine.graph import to_networkx
from causal_engine.models import CausalPath, FcmGraph, FcmSnapshot


def find_dominant_paths(
    graph: FcmGraph,
    snapshot: FcmSnapshot,
    target_node_id: str,
    max_paths: int = 5,
    cutoff: int = 4,
) -> list[CausalPath]:
    directed = to_networkx(graph)
    candidates: list[CausalPath] = []

    for source_node_id, value in snapshot.node_values.items():
        if source_node_id == target_node_id or abs(value) < 0.01:
            continue
        if source_node_id not in directed or target_node_id not in directed:
            continue
        for path in _safe_paths(directed, source_node_id, target_node_id, cutoff):
            weights = [
                float(directed[path[idx]][path[idx + 1]]["weight"]) for idx in range(len(path) - 1)
            ]
            confidence = prod(
                float(directed[path[idx]][path[idx + 1]]["confidence"])
                for idx in range(len(path) - 1)
            )
            signed_impact = float(value * prod(weights))
            candidates.append(
                CausalPath(
                    path=list(path),
                    contribution_ratio=abs(signed_impact),
                    signed_impact=signed_impact,
                    confidence=confidence,
                )
            )

    total = sum(path.contribution_ratio for path in candidates) or 1.0
    normalized = [
        path.model_copy(update={"contribution_ratio": path.contribution_ratio / total})
        for path in candidates
    ]
    return sorted(normalized, key=lambda item: item.contribution_ratio, reverse=True)[:max_paths]


def _safe_paths(
    graph: nx.DiGraph, source_node_id: str, target_node_id: str, cutoff: int
) -> Iterable[list[str]]:
    try:
        return nx.all_simple_paths(graph, source_node_id, target_node_id, cutoff=cutoff)
    except nx.NetworkXNoPath:
        return []

