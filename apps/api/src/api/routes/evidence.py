from api.schemas.documents import EvidenceSearchResponse
from fastapi import APIRouter

router = APIRouter(tags=["evidence"])


@router.get("/evidence/search", response_model=EvidenceSearchResponse)
def search_evidence(
    terminal_id: str = "terminal_alpha", entity_id: str = "qc4"
) -> EvidenceSearchResponse:
    return EvidenceSearchResponse(
        results=[
            {
                "documentId": "maintenance_qc4_demo",
                "entityId": entity_id,
                "terminalId": terminal_id,
                "text": "QC4 had a mock availability event during the current shift.",
                "score": 0.82,
            }
        ]
    )

