from enum import StrEnum

from pydantic import BaseModel, Field


class NodeType(StrEnum):
    STATE_KPI = "state_kpi"
    PERFORMANCE_KPI = "performance_kpi"
    RESOURCE_AVAILABILITY = "resource_availability"
    DELAY_FACTOR = "delay_factor"
    EXTERNAL_CONTEXT = "external_context"
    INTERVENTION_VARIABLE = "intervention_variable"


class EdgePolarity(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


class FcmNode(BaseModel):
    id: str
    label: str
    node_type: NodeType
    subsystem: str
    entity_id: str | None = None


class FcmEdge(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    base_weight: float = Field(ge=-1.0, le=1.0)
    polarity: EdgePolarity
    lag_minutes: int = Field(default=0, ge=0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence_level: str = "expert"
    subsystem: str
    dynamic_weight_model_id: str | None = None


class FcmGraph(BaseModel):
    id: str
    terminal_id: str
    nodes: list[FcmNode]
    edges: list[FcmEdge]


class FcmSnapshot(BaseModel):
    snapshot_id: str
    terminal_id: str
    node_values: dict[str, float]


class CausalPath(BaseModel):
    path: list[str]
    contribution_ratio: float
    signed_impact: float
    confidence: float


class FeedbackLoop(BaseModel):
    nodes: list[str]
    loop_type: str
    strength: float
    confidence: float


class ScenarioIntervention(BaseModel):
    node_id: str
    operation: str
    value: float


class ScenarioResult(BaseModel):
    baseline: dict[str, float]
    final_state: dict[str, float]
    propagation_frames: list[dict[str, float]]

