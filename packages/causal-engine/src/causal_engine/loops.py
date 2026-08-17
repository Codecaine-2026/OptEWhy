from math import prod

from causal_engine.graph import to_networkx
from causal_engine.models import FcmGraph, FcmSnapshot, FeedbackLoop


def detect_feedback_loops(
    graph: FcmGraph, snapshot: FcmSnapshot, max_loops: int = 5
) -> list[FeedbackLoop]:
    directed = to_networkx(graph)
    loops: list[FeedbackLoop] = []

    for cycle in list(__import__("networkx").simple_cycles(directed))[: max_loops * 4]:
        cycle_edges = list(zip(cycle, cycle[1:] + cycle[:1], strict=True))
        weights = [float(directed[source][target]["weight"]) for source, target in cycle_edges]
        confidences = [
            float(directed[source][target]["confidence"]) for source, target in cycle_edges
        ]
        abnormality = (
            sum(abs(snapshot.node_values.get(node_id, 0.0)) for node_id in cycle) / len(cycle)
        )
        signed_weight = prod(weights)
        strength = abs(signed_weight) * abnormality
        loops.append(
            FeedbackLoop(
                nodes=cycle,
                loop_type="reinforcing" if signed_weight > 0 else "balancing",
                strength=strength,
                confidence=prod(confidences),
            )
        )

    return sorted(loops, key=lambda item: item.strength, reverse=True)[:max_loops]
