from api.schemas.base import ApiModel
from pydantic import Field


class TimeWindow(ApiModel):
    mode: str = "current_shift"


class ReasoningNodePayload(ApiModel):
    id: str
    label: str
    subsystem: str
    node_type: str
    abnormality: float
    reasoning_step_ids: list[str] = Field(default_factory=list)


class ReasoningEdgePayload(ApiModel):
    id: str
    source_node_id: str
    target_node_id: str
    weight: float
    polarity: str
    confidence: float
    contribution_ratio: float | None = None
    signed_impact: float | None = None
    reasoning_step_ids: list[str] = Field(default_factory=list)


class ReasoningLoopPayload(ApiModel):
    id: str
    node_ids: list[str]
    edge_ids: list[str]
    loop_type: str
    strength: float
    confidence: float


class EvidenceRefPayload(ApiModel):
    document_id: str | None = None
    chunk_id: str | None = None
    score: float | None = None
    related_node_ids: list[str] = Field(default_factory=list)
    related_edge_ids: list[str] = Field(default_factory=list)


class ReasoningStepPayload(ApiModel):
    id: str
    step_type: str
    summary: str
    used_node_ids: list[str] = Field(default_factory=list)
    used_edge_ids: list[str] = Field(default_factory=list)
    evidence_refs: list[EvidenceRefPayload] = Field(default_factory=list)
    contribution_ratio: float | None = None
    signed_impact: float | None = None
    loop_type: str | None = None
    strength: float | None = None
    confidence: float | None = None


class ReasoningTracePayload(ApiModel):
    target_node_id: str
    steps: list[ReasoningStepPayload] = Field(default_factory=list)


class VisualizationPayload(ApiModel):
    highlighted_nodes: list[str] = Field(default_factory=list)
    highlighted_edges: list[str] = Field(default_factory=list)
    focus_subgraph_id: str | None = None
    reasoning_nodes: list[ReasoningNodePayload] = Field(default_factory=list)
    reasoning_edges: list[ReasoningEdgePayload] = Field(default_factory=list)
    loops: list[ReasoningLoopPayload] = Field(default_factory=list)
