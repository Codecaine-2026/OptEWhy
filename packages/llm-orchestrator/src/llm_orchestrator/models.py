from enum import StrEnum

from pydantic import BaseModel, Field


class IntentType(StrEnum):
    ANOMALY_EXPLANATION = "anomaly_explanation"
    ROOT_MECHANISM_ANALYSIS = "root_mechanism_analysis"
    SCENARIO_SIMULATION = "scenario_simulation"
    COUNTERFACTUAL = "counterfactual"
    RECOMMENDATION = "recommendation"
    EVIDENCE_LOOKUP = "evidence_lookup"


class Target(BaseModel):
    node_id: str
    entity_type: str | None = None
    entity_id: str | None = None


class AnalysisOptions(BaseModel):
    include_paths: bool = True
    include_loops: bool = True
    include_evidence: bool = True
    include_recommendations: bool = False


class StructuredQuery(BaseModel):
    intent: IntentType
    target: Target | None = None
    time_window: dict[str, str] = Field(default_factory=lambda: {"mode": "current_shift"})
    analysis_options: AnalysisOptions = Field(default_factory=AnalysisOptions)
    raw_message: str

