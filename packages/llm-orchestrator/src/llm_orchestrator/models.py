from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class IntentType(StrEnum):
    CASUAL_CONVERSATION = "casual_conversation"
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


class ScenarioIntervention(BaseModel):
    node_id: str
    operation: Literal["increase_relative", "decrease_relative"]
    value: float = Field(gt=0, le=1)


class StructuredQuery(BaseModel):
    intent: IntentType
    target: Target | None = None
    time_window: dict[str, str] = Field(default_factory=lambda: {"mode": "current_shift"})
    analysis_options: AnalysisOptions = Field(default_factory=AnalysisOptions)
    intervention: ScenarioIntervention | None = None
    raw_message: str
