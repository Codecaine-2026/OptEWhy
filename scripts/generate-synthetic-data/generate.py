import argparse
import csv
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
from causal_engine.models import FcmGraph
from causal_engine.port_graph import build_reference_port_graph
from numpy.typing import NDArray

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPOSITORY_ROOT / "data/synthetic/sample_causal_training.csv"
DEFAULT_ROWS = 2400

BASELINE_STATE = {
    "import_volume_pressure": 0.00,
    "vessel_bunching": 0.00,
    "weather_severity": -0.10,
    "vessel_arrival_delay": -0.05,
    "gate_throughput": 0.15,
    "gate_queue_length": -0.15,
    "truck_arrival_peaking": -0.10,
    "truck_appointment_compliance": 0.20,
    "document_error_rate": -0.20,
    "gate_exception_rate": -0.20,
    "chassis_availability": 0.25,
    "warehouse_capacity_pressure": -0.10,
    "import_dwell_time": -0.20,
    "berth_occupancy": -0.05,
    "yard_density": -0.15,
    "yard_rehandle_rate": -0.20,
    "yard_crane_availability": 0.20,
    "empty_container_imbalance": 0.00,
    "truck_travel_time": -0.15,
    "truck_turn_time": -0.15,
    "qc_waiting": -0.15,
    "qc_productivity": 0.20,
    "crane_equipment_availability": 0.20,
    "labor_availability": 0.20,
    "berth_productivity": 0.20,
    "vessel_turnaround_time": -0.10,
}

REGIME_OFFSETS = {
    "normal": {},
    "congested": {
        "import_volume_pressure": 0.15,
        "berth_occupancy": 0.20,
        "yard_density": 0.20,
        "truck_travel_time": 0.15,
        "qc_waiting": 0.15,
        "qc_productivity": -0.15,
        "truck_turn_time": 0.15,
    },
    "weather_disruption": {
        "weather_severity": 0.55,
        "truck_travel_time": 0.25,
        "qc_waiting": 0.15,
        "qc_productivity": -0.15,
        "vessel_turnaround_time": 0.25,
    },
}


@dataclass(frozen=True)
class ScenarioFamily:
    family_id: str
    observed_kpi: str
    surface_cause_label: str
    root_cause_label: str
    reinforcing_loop_id: str
    recommended_intervention: str
    explanation_template: str
    overrides: dict[str, float]


SCENARIO_FAMILIES = [
    ScenarioFamily(
        family_id="qc_productivity_down_yard_dwell_root",
        observed_kpi="qc_productivity_down",
        surface_cause_label="qc_waiting",
        root_cause_label="import_dwell_time_yard_density_yard_rehandle_rate",
        reinforcing_loop_id="berth_yard_quay_congestion_loop",
        recommended_intervention=(
            "Accelerate import pickup and reduce rehandles before adding quay resources."
        ),
        explanation_template=(
            "Surface cause is QC waiting, but the upstream pattern is high import dwell, "
            "yard density, and rehandles raising internal truck travel time."
        ),
        overrides={
            "import_dwell_time": 0.72,
            "yard_density": 0.76,
            "yard_rehandle_rate": 0.66,
            "truck_travel_time": 0.62,
            "qc_waiting": 0.58,
            "qc_productivity": -0.62,
            "crane_equipment_availability": 0.18,
            "labor_availability": 0.18,
            "berth_occupancy": 0.45,
        },
    ),
    ScenarioFamily(
        family_id="qc_productivity_down_chassis_root",
        observed_kpi="qc_productivity_down",
        surface_cause_label="qc_waiting",
        root_cause_label="chassis_availability_shortage",
        reinforcing_loop_id="landside_yard_pickup_loop",
        recommended_intervention=(
            "Restore chassis supply and pickup flow to reduce dwell-driven congestion."
        ),
        explanation_template=(
            "Surface cause is QC waiting, but low chassis availability suppresses gate "
            "throughput, increasing import dwell and yard density."
        ),
        overrides={
            "chassis_availability": -0.76,
            "gate_throughput": -0.62,
            "import_dwell_time": 0.70,
            "yard_density": 0.66,
            "truck_travel_time": 0.48,
            "qc_waiting": 0.52,
            "qc_productivity": -0.58,
            "crane_equipment_availability": 0.18,
        },
    ),
    ScenarioFamily(
        family_id="qc_productivity_down_equipment_root",
        observed_kpi="qc_productivity_down",
        surface_cause_label="qc_waiting",
        root_cause_label="crane_equipment_availability",
        reinforcing_loop_id="none",
        recommended_intervention=(
            "Recover quay crane equipment availability before changing yard or gate plans."
        ),
        explanation_template=(
            "QC productivity is down because quay crane availability is low while yard "
            "density and import dwell remain near normal."
        ),
        overrides={
            "crane_equipment_availability": -0.76,
            "qc_productivity": -0.62,
            "qc_waiting": 0.22,
            "yard_density": -0.08,
            "import_dwell_time": -0.08,
            "truck_travel_time": 0.02,
        },
    ),
    ScenarioFamily(
        family_id="truck_turn_time_up_document_root",
        observed_kpi="truck_turn_time_up",
        surface_cause_label="gate_congestion",
        root_cause_label="document_error_rate_gate_exception_rate",
        reinforcing_loop_id="landside_yard_pickup_loop",
        recommended_intervention=(
            "Reduce document exceptions and pre-clear problematic transactions."
        ),
        explanation_template=(
            "Truck turn time is high at the gate, but the root signal is document errors "
            "creating gate exceptions and lowering throughput."
        ),
        overrides={
            "document_error_rate": 0.72,
            "gate_exception_rate": 0.70,
            "gate_throughput": -0.55,
            "gate_queue_length": 0.64,
            "truck_turn_time": 0.66,
            "yard_density": -0.04,
        },
    ),
    ScenarioFamily(
        family_id="truck_turn_time_up_yard_retrieval_root",
        observed_kpi="truck_turn_time_up",
        surface_cause_label="gate_congestion",
        root_cause_label="yard_density_yard_rehandle_rate",
        reinforcing_loop_id="landside_yard_pickup_loop",
        recommended_intervention=(
            "Improve yard retrieval sequencing and lower density before adding gate lanes."
        ),
        explanation_template=(
            "The gate delay is downstream of yard retrieval friction: dense stacks and "
            "rehandles raise travel time and truck turn time."
        ),
        overrides={
            "yard_density": 0.72,
            "yard_rehandle_rate": 0.70,
            "truck_travel_time": 0.62,
            "truck_turn_time": 0.68,
            "document_error_rate": -0.18,
            "gate_exception_rate": -0.16,
            "gate_queue_length": 0.20,
        },
    ),
    ScenarioFamily(
        family_id="vessel_turnaround_up_bunching_root",
        observed_kpi="vessel_turnaround_time_up",
        surface_cause_label="berth_occupancy",
        root_cause_label="vessel_bunching",
        reinforcing_loop_id="berth_yard_quay_congestion_loop",
        recommended_intervention=(
            "Smooth berth windows and prioritize bunching relief across berth and yard plans."
        ),
        explanation_template=(
            "Vessel turnaround is high because vessel bunching raises berth occupancy, "
            "which reinforces yard and quay congestion."
        ),
        overrides={
            "vessel_bunching": 0.76,
            "berth_occupancy": 0.76,
            "yard_density": 0.50,
            "truck_travel_time": 0.44,
            "qc_waiting": 0.52,
            "vessel_turnaround_time": 0.72,
        },
    ),
    ScenarioFamily(
        family_id="yard_density_up_warehouse_root",
        observed_kpi="yard_density_up",
        surface_cause_label="gate_congestion",
        root_cause_label="warehouse_capacity_pressure_pickup_failure",
        reinforcing_loop_id="landside_yard_pickup_loop",
        recommended_intervention="Coordinate warehouse receiving capacity and pickup appointments.",
        explanation_template=(
            "Yard density appears volume-driven, but warehouse capacity pressure is "
            "holding import boxes in the terminal and raising dwell."
        ),
        overrides={
            "warehouse_capacity_pressure": 0.74,
            "gate_throughput": -0.28,
            "import_dwell_time": 0.68,
            "yard_density": 0.70,
            "import_volume_pressure": 0.12,
            "truck_turn_time": 0.35,
        },
    ),
    ScenarioFamily(
        family_id="berth_productivity_down_yard_crane_root",
        observed_kpi="berth_productivity_down",
        surface_cause_label="qc_productivity",
        root_cause_label="yard_crane_availability",
        reinforcing_loop_id="berth_yard_quay_congestion_loop",
        recommended_intervention=(
            "Recover yard crane capacity to restore internal truck flow to quay cranes."
        ),
        explanation_template=(
            "Berth productivity is down through QC productivity, but yard crane "
            "availability is the upstream constraint slowing internal truck travel."
        ),
        overrides={
            "yard_crane_availability": -0.74,
            "truck_travel_time": 0.62,
            "qc_waiting": 0.56,
            "qc_productivity": -0.58,
            "berth_productivity": -0.60,
            "crane_equipment_availability": 0.18,
        },
    ),
]

BASELINE_FAMILY = ScenarioFamily(
    family_id="baseline_normal",
    observed_kpi="none",
    surface_cause_label="none",
    root_cause_label="none",
    reinforcing_loop_id="none",
    recommended_intervention="Continue monitoring.",
    explanation_template="Baseline row with no structural disruption label.",
    overrides={},
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic FCM transition data.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--noise-std", type=float, default=0.015)
    args = parser.parse_args()

    graph = build_reference_port_graph()
    rows = generate_rows(graph, args.rows, args.seed, args.noise_std)
    write_rows(args.output, graph, rows)
    intervention_rows = sum(row["intervention_type"] != "none" for row in rows)

    print(f"Generated {len(rows)} rows for {len(graph.nodes)} nodes")
    print(f"Included {intervention_rows} intervention rows")
    print(f"Dataset written to {_display_path(args.output)}")


def generate_rows(
    graph: FcmGraph, row_count: int, seed: int, noise_std: float
) -> list[dict[str, object]]:
    if row_count < DEFAULT_ROWS:
        raise ValueError(f"row_count must be at least {DEFAULT_ROWS}")
    if noise_std < 0.0:
        raise ValueError("noise_std cannot be negative")

    rng = np.random.default_rng(seed)
    node_ids = [node.id for node in graph.nodes]
    index = {node_id: offset for offset, node_id in enumerate(node_ids)}
    weights = _weight_matrix(graph, node_ids)
    started_at = datetime(2026, 1, 1, tzinfo=UTC)
    regimes = tuple(REGIME_OFFSETS)
    rows: list[dict[str, object]] = []
    family_counts: dict[str, int] = {}

    schedule = _scenario_schedule(row_count)
    for row_index, family in enumerate(schedule):
        regime = "normal" if family.family_id == BASELINE_FAMILY.family_id else str(
            rng.choice(regimes, p=(0.45, 0.45, 0.10))
        )
        current = _state_vector(family, regime, node_ids, rng)
        intervention_type = "none"
        intervention_node_id = ""
        intervention_value = 0.0

        if row_index % 30 == 0:
            intervention_type = "increase_gate_throughput"
            intervention_node_id = "gate_throughput"
            intervention_value = 0.12
        elif row_index % 45 == 0:
            intervention_type = "increase_yard_crane_availability"
            intervention_node_id = "yard_crane_availability"
            intervention_value = 0.14

        if intervention_node_id:
            current[index[intervention_node_id]] = min(
                1.0, current[index[intervention_node_id]] + intervention_value
            )

        occurrence_index = family_counts.get(family.family_id, 0)
        family_counts[family.family_id] = occurrence_index + 1
        labels = _row_labels(family, occurrence_index)
        noise = rng.normal(0.0, noise_std, size=len(node_ids))
        next_state = np.tanh(current + current @ weights + noise)
        row: dict[str, object] = {
            "timestamp": (started_at + timedelta(minutes=15 * row_index)).isoformat(),
            "terminal_id": graph.terminal_id,
            "scenario_id": f"{family.family_id}_{row_index:05d}",
            "scenario_family": family.family_id,
            "operating_regime": regime,
            "intervention_type": intervention_type,
            "intervention_node_id": intervention_node_id,
            "intervention_value": intervention_value,
            "observed_kpi": labels["observed_kpi"],
            "surface_cause_label": labels["surface_cause_label"],
            "root_cause_label": labels["root_cause_label"],
            "reinforcing_loop_id": labels["reinforcing_loop_id"],
            "recommended_intervention": labels["recommended_intervention"],
            "explanation_template": labels["explanation_template"],
        }
        row.update(
            {f"{node_id}_t": round(float(current[index[node_id]]), 6) for node_id in node_ids}
        )
        row.update(
            {f"{node_id}_next": round(float(next_state[index[node_id]]), 6) for node_id in node_ids}
        )
        rows.append(row)

    return rows


def _row_labels(family: ScenarioFamily, occurrence_index: int) -> dict[str, str]:
    if (
        family.family_id == "qc_productivity_down_yard_dwell_root"
        and occurrence_index % 4 == 0
    ):
        return {
            "observed_kpi": "vessel_turnaround_time_up",
            "surface_cause_label": "berth_occupancy",
            "root_cause_label": "yard_congestion_import_dwell",
            "reinforcing_loop_id": family.reinforcing_loop_id,
            "recommended_intervention": family.recommended_intervention,
            "explanation_template": (
                "Vessel turnaround is high through QC waiting, but the upstream root "
                "is import dwell and yard congestion."
            ),
        }
    if (
        family.family_id == "qc_productivity_down_equipment_root"
        and occurrence_index % 4 == 1
    ):
        return {
            "observed_kpi": "berth_productivity_down",
            "surface_cause_label": "qc_productivity",
            "root_cause_label": "crane_equipment_availability",
            "reinforcing_loop_id": "none",
            "recommended_intervention": family.recommended_intervention,
            "explanation_template": (
                "Berth productivity is down through QC productivity, but the root "
                "is quay crane equipment availability."
            ),
        }
    if (
        family.family_id == "qc_productivity_down_equipment_root"
        and occurrence_index % 4 == 2
    ):
        return {
            "observed_kpi": "vessel_turnaround_time_up",
            "surface_cause_label": "berth_occupancy",
            "root_cause_label": "crane_equipment_availability",
            "reinforcing_loop_id": "none",
            "recommended_intervention": family.recommended_intervention,
            "explanation_template": (
                "Vessel turnaround is high because crane equipment availability "
                "reduces QC productivity, not because yard density is abnormal."
            ),
        }
    return {
        "observed_kpi": family.observed_kpi,
        "surface_cause_label": family.surface_cause_label,
        "root_cause_label": family.root_cause_label,
        "reinforcing_loop_id": family.reinforcing_loop_id,
        "recommended_intervention": family.recommended_intervention,
        "explanation_template": family.explanation_template,
    }


def write_rows(path: Path, graph: FcmGraph, rows: list[dict[str, object]]) -> None:
    node_ids = [node.id for node in graph.nodes]
    fieldnames = [
        "timestamp",
        "terminal_id",
        "scenario_id",
        "scenario_family",
        "operating_regime",
        *(f"{node_id}_t" for node_id in node_ids),
        "intervention_type",
        "intervention_node_id",
        "intervention_value",
        *(f"{node_id}_next" for node_id in node_ids),
        "observed_kpi",
        "surface_cause_label",
        "root_cause_label",
        "reinforcing_loop_id",
        "recommended_intervention",
        "explanation_template",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as dataset:
        writer = csv.DictWriter(dataset, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _scenario_schedule(row_count: int) -> list[ScenarioFamily]:
    scenario_count = int(row_count * 0.875)
    baseline_count = row_count - scenario_count
    schedule = [BASELINE_FAMILY] * baseline_count
    scenario_index = 0
    while len(schedule) < row_count:
        schedule.append(SCENARIO_FAMILIES[scenario_index % len(SCENARIO_FAMILIES)])
        scenario_index += 1
    return schedule


def _state_vector(
    family: ScenarioFamily,
    regime: str,
    node_ids: list[str],
    rng: np.random.Generator,
) -> NDArray[np.float64]:
    state = {node_id: BASELINE_STATE.get(node_id, 0.0) for node_id in node_ids}
    for node_id, offset in REGIME_OFFSETS[regime].items():
        state[node_id] = state.get(node_id, 0.0) + offset
    state.update(family.overrides)
    values = np.array([state[node_id] for node_id in node_ids], dtype=float)
    jitter_std = 0.08 if family.family_id != BASELINE_FAMILY.family_id else 0.12
    jitter = rng.normal(0.0, jitter_std, len(node_ids))
    return np.clip(values + jitter, -0.95, 0.95)


def _weight_matrix(graph: FcmGraph, node_ids: list[str]) -> NDArray[np.float64]:
    index = {node_id: offset for offset, node_id in enumerate(node_ids)}
    weights: NDArray[np.float64] = np.zeros((len(node_ids), len(node_ids)), dtype=float)
    for edge in graph.edges:
        weights[index[edge.source_node_id], index[edge.target_node_id]] = edge.base_weight
    return weights


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPOSITORY_ROOT))
    except ValueError:
        return str(resolved)


if __name__ == "__main__":
    main()
