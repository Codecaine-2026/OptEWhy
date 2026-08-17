from api.schemas.query import ScenarioRequest, ScenarioResponse, SideEffect
from api.services.demo_data import build_demo_graph, build_demo_snapshot
from causal_engine.models import ScenarioIntervention
from causal_engine.simulation import simulate_scenario


class ScenarioOrchestrator:
    def handle(self, request: ScenarioRequest) -> ScenarioResponse:
        graph = build_demo_graph()
        snapshot = build_demo_snapshot()
        interventions = [
            ScenarioIntervention(
                node_id="yard_density",
                operation="decrease_relative",
                value=0.15,
            )
        ]
        result = simulate_scenario(graph, snapshot, interventions, steps=4)

        return ScenarioResponse(
            scenario_id="scenario_demo_001",
            structured_intervention={
                "sourceMessage": request.message,
                "interventions": [intervention.model_dump() for intervention in interventions],
            },
            predicted_impact={
                "qc_productivity": result.final_state.get("qc_productivity", 0.0)
                - snapshot.node_values.get("qc_productivity", 0.0),
                "vessel_turnaround_time_minutes": -19.0,
            },
            side_effects=[
                SideEffect(
                    node_id="gate_retrieval_time",
                    impact=0.02,
                    description=(
                        "Gate retrieval time may increase if load is shifted to a denser block."
                    ),
                )
            ],
            propagation_frames=result.propagation_frames,
        )
