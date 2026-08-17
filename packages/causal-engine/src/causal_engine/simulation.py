from causal_engine.models import FcmGraph, FcmSnapshot, ScenarioIntervention, ScenarioResult
from causal_engine.propagation import propagate


def simulate_scenario(
    graph: FcmGraph,
    snapshot: FcmSnapshot,
    interventions: list[ScenarioIntervention],
    steps: int = 3,
) -> ScenarioResult:
    scenario_values = dict(snapshot.node_values)
    for intervention in interventions:
        current = scenario_values.get(intervention.node_id, 0.0)
        if intervention.operation == "set":
            next_value = intervention.value
        elif intervention.operation == "increase_relative":
            next_value = current + abs(intervention.value)
        elif intervention.operation == "decrease_relative":
            next_value = current - abs(intervention.value)
        else:
            raise ValueError(f"Unsupported intervention operation: {intervention.operation}")
        scenario_values[intervention.node_id] = max(-1.0, min(1.0, next_value))

    scenario_snapshot = snapshot.model_copy(update={"node_values": scenario_values})
    frames = propagate(graph, scenario_snapshot, steps=steps)
    return ScenarioResult(
        baseline=snapshot.node_values,
        final_state=frames[-1] if frames else scenario_values,
        propagation_frames=frames,
    )

