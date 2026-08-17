from api.schemas.base import ApiModel
from pydantic import Field


class DocumentIngestRequest(ApiModel):
    terminal_id: str
    document_id: str
    document_type: str
    text: str
    entity_id: str | None = None
    subsystem: str | None = None
    tags: list[str] = Field(default_factory=list)


class DocumentIngestResponse(ApiModel):
    document_id: str
    chunks_created: int


class EvidenceSearchResponse(ApiModel):
    results: list[dict[str, object]]
