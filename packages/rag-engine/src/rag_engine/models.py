from datetime import datetime

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    document_id: str
    document_type: str
    terminal_id: str
    entity_type: str | None = None
    entity_id: str | None = None
    time_start: datetime | None = None
    time_end: datetime | None = None
    subsystem: str | None = None
    tags: list[str] = Field(default_factory=list)
    source_title: str | None = None
    source_url: str | None = None
    publisher: str | None = None
    published_date: str | None = None
    evidence_scope: str | None = None
    claim_type: str | None = None
    related_nodes: list[str] = Field(default_factory=list)
    related_edges: list[str] = Field(default_factory=list)
    scenario_ids: list[str] = Field(default_factory=list)


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    metadata: DocumentMetadata


class RetrievalQuery(BaseModel):
    question: str
    terminal_id: str
    entity_ids: list[str] = Field(default_factory=list)
    subsystem: str | None = None
    tags: list[str] = Field(default_factory=list)
    limit: int = Field(default=5, ge=1, le=25)


class Citation(BaseModel):
    document_id: str
    chunk_id: str
    title: str | None = None
    score: float = Field(ge=0.0, le=1.0)


class EvidenceResult(BaseModel):
    citation: Citation
    text: str
    metadata: DocumentMetadata
