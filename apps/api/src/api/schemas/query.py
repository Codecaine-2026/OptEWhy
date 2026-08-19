from api.schemas.base import ApiModel
from api.schemas.common import ReasoningTracePayload, TimeWindow, VisualizationPayload
from pydantic import Field


class QueryContext(ApiModel):
    time_mode: str = "current_shift"
    preferred_language: str = "en"


class QueryRequest(ApiModel):
    message: str
    terminal_id: str
    context: QueryContext = Field(default_factory=QueryContext)


class QueryResponse(ApiModel):
    analysis_id: str
    intent: str
    answer: str
    causal_result: dict[str, object]
    evidence: list[dict[str, object]]
    reasoning_trace: ReasoningTracePayload
    visualization: VisualizationPayload


class AnalysisRecord(ApiModel):
    analysis_id: str
    terminal_id: str
    request: str
    snapshot_id: str
    fcm_model_version: str
    created_at: str


class ScenarioRequest(ApiModel):
    terminal_id: str
    message: str
    time_window: TimeWindow = Field(default_factory=TimeWindow)


class SideEffect(ApiModel):
    node_id: str
    impact: float
    description: str


class ScenarioResponse(ApiModel):
    scenario_id: str
    structured_intervention: dict[str, object]
    predicted_impact: dict[str, float]
    side_effects: list[SideEffect]
    propagation_frames: list[dict[str, float]]
