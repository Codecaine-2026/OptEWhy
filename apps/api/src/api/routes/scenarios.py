from typing import Annotated

from api.dependencies import get_scenario_orchestrator
from api.schemas.query import ScenarioRequest, ScenarioResponse
from api.services.scenario_orchestrator import ScenarioOrchestrator
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(tags=["scenarios"])


@router.post("/scenarios/simulate", response_model=ScenarioResponse)
def simulate_scenario(
    request: ScenarioRequest,
    orchestrator: Annotated[ScenarioOrchestrator, Depends(get_scenario_orchestrator)],
) -> ScenarioResponse:
    try:
        return orchestrator.handle(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
