from typing import Annotated

from api.schemas.documents import EvidenceSearchResponse
from api.services.evidence_seed import load_rag_seed_chunks
from fastapi import APIRouter, Query
from rag_engine.mock import InMemoryRetriever
from rag_engine.models import RetrievalQuery

router = APIRouter(tags=["evidence"])


@router.get("/evidence/search", response_model=EvidenceSearchResponse)
def search_evidence(
    terminal_id: str = "terminal_alpha",
    entity_id: str | None = None,
    node_id: str | None = None,
    subsystem: str | None = None,
    tags: Annotated[list[str] | None, Query()] = None,
    question: str = "Why is QC productivity down?",
) -> EvidenceSearchResponse:
    entity_ids = [value for value in (entity_id, node_id) if value]
    retriever = InMemoryRetriever(list(load_rag_seed_chunks()))
    results = retriever.retrieve(
        RetrievalQuery(
            question=question,
            terminal_id=terminal_id,
            entity_ids=entity_ids,
            subsystem=subsystem,
            tags=tags or [],
        )
    )
    return EvidenceSearchResponse(
        results=[
            {
                "documentId": result.citation.document_id,
                "chunkId": result.citation.chunk_id,
                "entityId": entity_id or node_id,
                "terminalId": result.metadata.terminal_id,
                "sourceTitle": result.metadata.source_title,
                "sourceUrl": result.metadata.source_url,
                "publisher": result.metadata.publisher,
                "evidenceScope": result.metadata.evidence_scope,
                "subsystem": result.metadata.subsystem,
                "tags": result.metadata.tags,
                "relatedNodes": result.metadata.related_nodes,
                "relatedEdges": result.metadata.related_edges,
                "scenarioIds": result.metadata.scenario_ids,
                "text": result.text,
                "score": result.citation.score,
            }
            for result in results
        ]
        or [
            {
                "documentId": "maintenance_qc4_demo",
                "entityId": entity_id or node_id or "qc4",
                "terminalId": terminal_id,
                "text": "QC4 had a mock availability event during the current shift.",
                "score": 0.82,
            }
        ]
    )
