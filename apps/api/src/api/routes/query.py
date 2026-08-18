from typing import Annotated

from api.dependencies import get_query_orchestrator
from api.schemas.query import QueryRequest, QueryResponse
from api.services.query_orchestrator import QueryOrchestrator
from fastapi import APIRouter, Depends, HTTPException, status
from llm_orchestrator.parsers import (
    IntentParserUnavailableError,
    InvalidIntentTargetError,
)

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query(
    request: QueryRequest,
    orchestrator: Annotated[QueryOrchestrator, Depends(get_query_orchestrator)],
) -> QueryResponse:
    try:
        return orchestrator.handle(request)
    except InvalidIntentTargetError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except IntentParserUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Intent parsing service is temporarily unavailable",
        ) from exc
