from pydantic import BaseModel, Field


class Kpi(BaseModel):
    id: str
    name: str
    unit: str
    subsystem: str
    higher_is_better: bool


class NormalizedNodeValue(BaseModel):
    node_id: str
    value: float = Field(ge=-1.0, le=1.0)
    baseline_value: float | None = None
    observed_value: float | None = None
    unit: str | None = None

