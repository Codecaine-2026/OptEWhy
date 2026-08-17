from typing import Annotated

from api.dependencies import get_query_orchestrator
from api.schemas.query import QueryRequest, QueryResponse
from api.services.query_orchestrator import QueryOrchestrator
from fastapi import APIRouter, Depends

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query(
    request: QueryRequest,
    orchestrator: Annotated[QueryOrchestrator, Depends(get_query_orchestrator)],
) -> QueryResponse:
    return orchestrator.handle(request)
