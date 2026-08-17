from api.schemas.documents import DocumentIngestRequest, DocumentIngestResponse
from fastapi import APIRouter

router = APIRouter(tags=["documents"])


@router.post("/documents/ingest", response_model=DocumentIngestResponse)
def ingest_document(request: DocumentIngestRequest) -> DocumentIngestResponse:
    chunks_created = max(1, len(request.text) // 800)
    return DocumentIngestResponse(document_id=request.document_id, chunks_created=chunks_created)

