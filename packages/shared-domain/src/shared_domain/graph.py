from pydantic import BaseModel, Field


class GraphNodeRef(BaseModel):
    id: str
    label: str
    subsystem: str
    entity_id: str | None = None


class GraphEdgeRef(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    weight: float = Field(ge=-1.0, le=1.0)

