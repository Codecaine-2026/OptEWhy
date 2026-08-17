from api.schemas.base import ApiModel


class GraphNodeResponse(ApiModel):
    id: str
    label: str
    subsystem: str
    abnormality: float = 0.0


class GraphEdgeResponse(ApiModel):
    id: str
    source_node_id: str
    target_node_id: str
    weight: float
    polarity: str


class GraphResponse(ApiModel):
    graph_id: str
    terminal_id: str
    nodes: list[GraphNodeResponse]
    edges: list[GraphEdgeResponse]
