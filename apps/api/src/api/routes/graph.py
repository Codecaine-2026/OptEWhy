from api.schemas.graph import GraphEdgeResponse, GraphNodeResponse, GraphResponse
from api.services.demo_data import build_demo_graph, build_demo_snapshot
from fastapi import APIRouter

router = APIRouter(tags=["graph"])


@router.get("/graph/current", response_model=GraphResponse)
def current_graph() -> GraphResponse:
    return _build_graph_response()


@router.get("/graph/subgraph", response_model=GraphResponse)
def subgraph() -> GraphResponse:
    return _build_graph_response()


def _build_graph_response() -> GraphResponse:
    graph = build_demo_graph()
    snapshot = build_demo_snapshot()
    return GraphResponse(
        graph_id=graph.id,
        terminal_id=graph.terminal_id,
        nodes=[
            GraphNodeResponse(
                id=node.id,
                label=node.label,
                subsystem=node.subsystem,
                abnormality=snapshot.node_values.get(node.id, 0.0),
            )
            for node in graph.nodes
        ],
        edges=[
            GraphEdgeResponse(
                id=edge.id,
                source_node_id=edge.source_node_id,
                target_node_id=edge.target_node_id,
                weight=edge.base_weight,
                polarity=edge.polarity.value,
            )
            for edge in graph.edges
        ],
    )

