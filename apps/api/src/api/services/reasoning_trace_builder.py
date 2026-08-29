from api.schemas.common import EvidenceRefPayload, ReasoningStepPayload, ReasoningTracePayload
from causal_engine.models import CausalPath, FcmEdge, FcmGraph, FcmNode, FeedbackLoop


class ReasoningTraceBuilder:
    def build(
        self,
        *,
        graph: FcmGraph,
        target_node_id: str,
        paths: list[CausalPath],
        loops: list[FeedbackLoop],
        evidence: list[dict[str, object]],
    ) -> ReasoningTracePayload:
        edge_by_pair = {
            (edge.source_node_id, edge.target_node_id): edge for edge in graph.edges
        }
        node_by_id = {node.id: node for node in graph.nodes}
        evidence_refs = [_build_evidence_ref(item) for item in evidence]
        steps: list[ReasoningStepPayload] = []

        for path_index, path in enumerate(paths, start=1):
            edge_ids = _edge_ids_for_path(path.path, edge_by_pair)
            steps.append(
                ReasoningStepPayload(
                    id=f"path_{path_index}",
                    step_type="dominant_path",
                    summary=_path_reasoning_summary(path, edge_by_pair, node_by_id),
                    used_node_ids=path.path,
                    used_edge_ids=edge_ids,
                    evidence_refs=_matching_evidence_refs(evidence_refs, path.path, edge_ids),
                    contribution_ratio=path.contribution_ratio,
                    signed_impact=path.signed_impact,
                    confidence=path.confidence,
                )
            )

        path_node_ids = {
            node_id for step in steps for node_id in step.used_node_ids
        }
        scoped_loops = [
            loop for loop in loops if path_node_ids.intersection(loop.nodes)
        ]
        for loop_index, loop in enumerate(scoped_loops, start=1):
            edge_ids = _edge_ids_for_loop(loop.nodes, edge_by_pair)
            steps.append(
                ReasoningStepPayload(
                    id=f"loop_{loop_index}",
                    step_type="feedback_loop",
                    summary=_loop_reasoning_summary(loop, node_by_id),
                    used_node_ids=loop.nodes,
                    used_edge_ids=edge_ids,
                    evidence_refs=_matching_evidence_refs(evidence_refs, loop.nodes, edge_ids),
                    loop_type=loop.loop_type,
                    strength=loop.strength,
                    confidence=loop.confidence,
                )
            )

        return ReasoningTracePayload(target_node_id=target_node_id, steps=steps)


def _edge_ids_for_path(
    node_ids: list[str],
    edge_by_pair: dict[tuple[str, str], FcmEdge],
) -> list[str]:
    edge_ids: list[str] = []
    for source_node_id, target_node_id in zip(node_ids, node_ids[1:], strict=False):
        edge = edge_by_pair.get((source_node_id, target_node_id))
        if edge is not None:
            edge_ids.append(edge.id)
    return edge_ids


def _path_reasoning_summary(
    path: CausalPath,
    edge_by_pair: dict[tuple[str, str], FcmEdge],
    node_by_id: dict[str, FcmNode],
) -> str:
    transitions: list[str] = []
    for index, (source_id, target_id) in enumerate(
        zip(path.path, path.path[1:], strict=False), start=1
    ):
        edge = edge_by_pair.get((source_id, target_id))
        source = node_by_id.get(source_id)
        target = node_by_id.get(target_id)
        if edge is None or source is None or target is None:
            continue
        direction = "increases" if edge.polarity.value == "positive" else "reduces"
        transitions.append(
            f"{index}. {source.label} {direction} {target.label} "
            f"(weight {edge.base_weight:.2f}, confidence {edge.confidence:.0%})."
        )
    contribution = f"This path accounts for {path.contribution_ratio:.0%} of the estimated impact."
    return " ".join([*transitions, contribution])


def _loop_reasoning_summary(loop: FeedbackLoop, node_by_id: dict[str, FcmNode]) -> str:
    labels = [node_by_id[node_id].label for node_id in loop.nodes if node_id in node_by_id]
    loop_name = " → ".join(labels)
    return (
        f"{loop.loop_type.title()} feedback links {loop_name}. "
        f"Its strength is {loop.strength:.2f} with {loop.confidence:.0%} confidence, "
        "so it can amplify or dampen the path over time."
    )


def _edge_ids_for_loop(
    node_ids: list[str],
    edge_by_pair: dict[tuple[str, str], FcmEdge],
) -> list[str]:
    edge_ids: list[str] = []
    for source_node_id, target_node_id in zip(node_ids, node_ids[1:] + node_ids[:1], strict=True):
        edge = edge_by_pair.get((source_node_id, target_node_id))
        if edge is not None:
            edge_ids.append(edge.id)
    return edge_ids


def _build_evidence_ref(item: dict[str, object]) -> EvidenceRefPayload:
    return EvidenceRefPayload(
        document_id=_optional_string(item.get("documentId") or item.get("document_id")),
        chunk_id=_optional_string(item.get("chunkId") or item.get("chunk_id")),
        score=_optional_float(item.get("score")),
        related_node_ids=_string_list(item.get("relatedNodes") or item.get("related_nodes")),
        related_edge_ids=_string_list(item.get("relatedEdges") or item.get("related_edges")),
    )


def _matching_evidence_refs(
    evidence_refs: list[EvidenceRefPayload],
    node_ids: list[str],
    edge_ids: list[str],
) -> list[EvidenceRefPayload]:
    node_id_set = set(node_ids)
    edge_id_set = set(edge_ids)
    return [
        evidence_ref
        for evidence_ref in evidence_refs
        if node_id_set.intersection(evidence_ref.related_node_ids)
        or edge_id_set.intersection(evidence_ref.related_edge_ids)
    ]


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _optional_float(value: object) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    return None


def _string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []
