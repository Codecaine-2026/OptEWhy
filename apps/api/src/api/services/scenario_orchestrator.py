from api.schemas.query import ScenarioRequest, ScenarioResponse
from api.services.graph_repository import DemoGraphRepository, GraphRepository
from causal_engine.models import ScenarioIntervention
from causal_engine.simulation import simulate_scenario


class ScenarioOrchestrator:
    def __init__(self, graph_repository: GraphRepository | None = None) -> None:
        self._graph_repository = graph_repository or DemoGraphRepository()

    def handle(self, request: ScenarioRequest) -> ScenarioResponse:
        graph = self._graph_repository.get_graph(request.terminal_id)
        snapshot = self._graph_repository.get_current_snapshot(request.terminal_id)
        requested_intervention = request.intervention
        intervention = ScenarioIntervention(
            node_id=(requested_intervention.node_id if requested_intervention else "yard_density"),
            operation=(
                requested_intervention.operation if requested_intervention else "decrease_relative"
            ),
            value=requested_intervention.value if requested_intervention else 0.15,
        )
        if intervention.node_id not in snapshot.node_values:
            raise ValueError(f"Unsupported intervention node: {intervention.node_id}")
        if request.target_node_id is not None and request.target_node_id not in snapshot.node_values:
            raise ValueError(f"Unsupported target node: {request.target_node_id}")

        interventions = [intervention]
        baseline_result = simulate_scenario(graph, snapshot, [], steps=4)
        scenario_result = simulate_scenario(graph, snapshot, interventions, steps=4)

        return ScenarioResponse(
            scenario_id="scenario_demo_001",
            structured_intervention={
                "sourceMessage": request.message,
                "targetNodeId": request.target_node_id,
                "interventions": [intervention.model_dump() for intervention in interventions],
            },
            predicted_impact={
                node_id: scenario_result.final_state.get(node_id, 0.0) - baseline_value
                for node_id, baseline_value in baseline_result.final_state.items()
            },
            baseline_state=baseline_result.final_state,
            scenario_state=scenario_result.final_state,
            side_effects=[],
            propagation_frames=scenario_result.propagation_frames,
        )
