from api.services.query_orchestrator import QueryOrchestrator
from api.services.scenario_orchestrator import ScenarioOrchestrator


def get_query_orchestrator() -> QueryOrchestrator:
    return QueryOrchestrator()


def get_scenario_orchestrator() -> ScenarioOrchestrator:
    return ScenarioOrchestrator()

