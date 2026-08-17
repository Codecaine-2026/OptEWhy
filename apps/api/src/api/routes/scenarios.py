from typing import Annotated

from api.dependencies import get_scenario_orchestrator
from api.schemas.query import ScenarioRequest, ScenarioResponse
from api.services.scenario_orchestrator import ScenarioOrchestrator
from fastapi import APIRouter, Depends

router = APIRouter(tags=["scenarios"])


@router.post("/scenarios/simulate", response_model=ScenarioResponse)
def simulate_scenario(
    request: ScenarioRequest,
    orchestrator: Annotated[ScenarioOrchestrator, Depends(get_scenario_orchestrator)],
) -> ScenarioResponse:
    return orchestrator.handle(request)
