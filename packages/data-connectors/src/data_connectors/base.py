from abc import ABC, abstractmethod
from enum import StrEnum

from pydantic import BaseModel


class ConnectorHealth(StrEnum):
    OK = "ok"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class DataConnector(ABC):
    @abstractmethod
    def health(self) -> ConnectorHealth:
        raise NotImplementedError

    @abstractmethod
    def fetch_current_state(self, terminal_id: str) -> dict[str, object]:
        raise NotImplementedError


class ConnectorRecord(BaseModel):
    source: str
    terminal_id: str
    payload: dict[str, object]

