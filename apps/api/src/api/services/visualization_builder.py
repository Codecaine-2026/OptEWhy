from api.schemas.common import (
    ReasoningEdgePayload,
    ReasoningLoopPayload,
    ReasoningNodePayload,
    ReasoningStepPayload,
    ReasoningTracePayload,
    VisualizationPayload,
)
from causal_engine.models import FcmEdge, FcmGraph, FcmSnapshot


class VisualizationBuilder:
    def build_for_trace(
        self,
        *,
        graph: FcmGraph,
        snapshot: FcmSnapshot,
        trace: ReasoningTracePayload,
    ) -> VisualizationPayload:
        node_by_id = {node.id: node for node in graph.nodes}
        edge_by_id = {edge.id: edge for edge in graph.edges}

        node_step_ids = _step_ids_by_used_id(trace.steps, "node")
        edge_step_ids = _step_ids_by_used_id(trace.steps, "edge")
        unique_node_ids = list(node_step_ids)
        unique_edge_ids = list(edge_step_ids)

        reasoning_nodes = [
            ReasoningNodePayload(
                id=node.id,
                label=node.label,
                subsystem=node.subsystem,
                node_type=node.node_type.value,
                abnormality=snapshot.node_values.get(node.id, 0.0),
                reasoning_step_ids=node_step_ids[node_id],
            )
            for node_id in unique_node_ids
            if (node := node_by_id.get(node_id)) is not None
        ]
        reasoning_edges = [
            _build_reasoning_edge(
                edge=edge,
                step_ids=edge_step_ids[edge_id],
                path_steps=_steps_using_edge(trace.steps, edge_id),
            )
            for edge_id in unique_edge_ids
            if (edge := edge_by_id.get(edge_id)) is not None
        ]
        reasoning_loops = [
            _build_reasoning_loop(step=step)
            for step in trace.steps
            if step.step_type == "feedback_loop"
        ]

        return VisualizationPayload(
            highlighted_nodes=unique_node_ids,
            highlighted_edges=unique_edge_ids,
            focus_subgraph_id=f"reasoning_{trace.target_node_id}",
            reasoning_nodes=reasoning_nodes,
            reasoning_edges=reasoning_edges,
            loops=reasoning_loops,
        )


def _step_ids_by_used_id(
    steps: list[ReasoningStepPayload],
    used_id_type: str,
) -> dict[str, list[str]]:
    ids_by_used_id: dict[str, list[str]] = {}
    for step in steps:
        used_ids = step.used_node_ids if used_id_type == "node" else step.used_edge_ids
        for used_id in used_ids:
            ids_by_used_id.setdefault(used_id, []).append(step.id)
    return ids_by_used_id


def _steps_using_edge(
    steps: list[ReasoningStepPayload],
    edge_id: str,
) -> list[ReasoningStepPayload]:
    return [
        step
        for step in steps
        if step.step_type == "dominant_path" and edge_id in step.used_edge_ids
    ]


def _build_reasoning_edge(
    edge: FcmEdge,
    step_ids: list[str],
    path_steps: list[ReasoningStepPayload],
) -> ReasoningEdgePayload:
    contribution_ratio = None
    signed_impact = None
    for step in path_steps:
        if step.contribution_ratio is not None:
            contribution_ratio = max(contribution_ratio or 0.0, step.contribution_ratio)
        if step.signed_impact is not None and (
            signed_impact is None or abs(step.signed_impact) > abs(signed_impact)
        ):
            signed_impact = step.signed_impact

    return ReasoningEdgePayload(
        id=edge.id,
        source_node_id=edge.source_node_id,
        target_node_id=edge.target_node_id,
        weight=edge.base_weight,
        polarity=edge.polarity.value,
        confidence=edge.confidence,
        contribution_ratio=contribution_ratio,
        signed_impact=signed_impact,
        reasoning_step_ids=step_ids,
    )


def _build_reasoning_loop(step: ReasoningStepPayload) -> ReasoningLoopPayload:
    return ReasoningLoopPayload(
        id=step.id,
        node_ids=step.used_node_ids,
        edge_ids=step.used_edge_ids,
        loop_type=step.loop_type or "unknown",
        strength=step.strength or 0.0,
        confidence=step.confidence or 0.0,
    )
