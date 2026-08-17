from enum import StrEnum

from pydantic import BaseModel


class InterventionOperation(StrEnum):
    SET = "set"
    INCREASE_RELATIVE = "increase_relative"
    DECREASE_RELATIVE = "decrease_relative"


class ScenarioIntervention(BaseModel):
    node_id: str
    operation: InterventionOperation
    value: float

