from typing import Annotated

from api.dependencies import get_graph_repository
from api.schemas.graph import GraphEdgeResponse, GraphNodeResponse, GraphResponse
from api.services.graph_repository import GraphRepository
from fastapi import APIRouter, Depends

router = APIRouter(tags=["graph"])


@router.get("/graph/current", response_model=GraphResponse)
def current_graph(
    repository: Annotated[GraphRepository, Depends(get_graph_repository)],
) -> GraphResponse:
    return _build_graph_response(repository)


@router.get("/graph/subgraph", response_model=GraphResponse)
def subgraph(
    repository: Annotated[GraphRepository, Depends(get_graph_repository)],
) -> GraphResponse:
    return _build_graph_response(repository)


def _build_graph_response(repository: GraphRepository) -> GraphResponse:
    graph = repository.get_graph("terminal_alpha")
    snapshot = repository.get_current_snapshot("terminal_alpha")
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
