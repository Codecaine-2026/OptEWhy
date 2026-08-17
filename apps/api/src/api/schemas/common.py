from api.schemas.base import ApiModel
from pydantic import Field


class TimeWindow(ApiModel):
    mode: str = "current_shift"


class VisualizationPayload(ApiModel):
    highlighted_nodes: list[str] = Field(default_factory=list)
    highlighted_edges: list[str] = Field(default_factory=list)
    focus_subgraph_id: str | None = None
