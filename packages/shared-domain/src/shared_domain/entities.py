from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class EntityType(StrEnum):
    TERMINAL = "terminal"
    VESSEL = "vessel"
    BERTH = "berth"
    QUAY_CRANE = "quay_crane"
    YARD_BLOCK = "yard_block"
    INTERNAL_TRUCK = "internal_truck"
    GATE = "gate"
    EQUIPMENT = "equipment"
    SHIFT = "shift"


class Terminal(BaseModel):
    id: str
    name: str
    timezone: str = "Asia/Seoul"


class Vessel(BaseModel):
    id: str
    name: str
    voyage_number: str | None = None


class Berth(BaseModel):
    id: str
    terminal_id: str
    name: str


class QuayCrane(BaseModel):
    id: str
    terminal_id: str
    name: str
    berth_id: str | None = None


class YardBlock(BaseModel):
    id: str
    terminal_id: str
    name: str
    capacity_teu: int = Field(ge=0)


class InternalTruck(BaseModel):
    id: str
    terminal_id: str
    name: str
    active: bool = True


class Gate(BaseModel):
    id: str
    terminal_id: str
    name: str
    lane_count: int = Field(ge=0)


class Equipment(BaseModel):
    id: str
    terminal_id: str
    equipment_type: str
    name: str
    available: bool = True


class Shift(BaseModel):
    id: str
    terminal_id: str
    name: str
    starts_at: datetime
    ends_at: datetime

