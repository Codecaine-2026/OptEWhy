from api.schemas.query import ScenarioRequest, ScenarioResponse
from api.services.demo_data import build_demo_graph, build_demo_snapshot
from causal_engine.models import ScenarioIntervention
from causal_engine.simulation import simulate_scenario


class ScenarioOrchestrator:
    def handle(self, request: ScenarioRequest) -> ScenarioResponse:
        graph = build_demo_graph()
        snapshot = build_demo_snapshot()
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

        interventions = [intervention]
        result = simulate_scenario(graph, snapshot, interventions, steps=4)

        return ScenarioResponse(
            scenario_id="scenario_demo_001",
            structured_intervention={
                "sourceMessage": request.message,
                "interventions": [intervention.model_dump() for intervention in interventions],
            },
            predicted_impact={
                node_id: result.final_state.get(node_id, 0.0) - baseline_value
                for node_id, baseline_value in result.baseline.items()
            },
            baseline_state=result.baseline,
            scenario_state=result.final_state,
            side_effects=[],
            propagation_frames=result.propagation_frames,
        )
