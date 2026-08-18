import csv
import importlib.util
from collections import defaultdict
from pathlib import Path

from causal_engine.port_graph import build_reference_port_graph

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
GENERATOR_PATH = REPOSITORY_ROOT / "scripts/generate-synthetic-data/generate.py"


def _load_generator():
    spec = importlib.util.spec_from_file_location("synthetic_generator", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load synthetic generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_synthetic_data_contains_structural_scenario_labels() -> None:
    generator = _load_generator()
    graph = build_reference_port_graph()
    rows = generator.generate_rows(graph, 2400, 2026, 0.0)

    families = {row["scenario_family"] for row in rows}
    assert families >= {
        "baseline_normal",
        "qc_productivity_down_yard_dwell_root",
        "qc_productivity_down_chassis_root",
        "qc_productivity_down_equipment_root",
        "truck_turn_time_up_document_root",
        "truck_turn_time_up_yard_retrieval_root",
        "vessel_turnaround_up_bunching_root",
        "yard_density_up_warehouse_root",
        "berth_productivity_down_yard_crane_root",
    }
    assert all(
        f"{node.id}_t" in rows[0] and f"{node.id}_next" in rows[0] for node in graph.nodes
    )


def test_same_observed_kpi_maps_to_multiple_root_causes() -> None:
    generator = _load_generator()
    rows = generator.generate_rows(build_reference_port_graph(), 2400, 2026, 0.0)
    roots_by_kpi: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        if row["observed_kpi"] != "none":
            roots_by_kpi[str(row["observed_kpi"])].add(str(row["root_cause_label"]))

    assert len(roots_by_kpi["qc_productivity_down"]) >= 3
    assert len(roots_by_kpi["truck_turn_time_up"]) >= 2


def test_surface_cause_labels_map_to_multiple_root_causes() -> None:
    generator = _load_generator()
    rows = generator.generate_rows(build_reference_port_graph(), 2400, 2026, 0.0)
    roots_by_surface: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        if row["surface_cause_label"] != "none":
            roots_by_surface[str(row["surface_cause_label"])].add(str(row["root_cause_label"]))

    assert len(roots_by_surface["qc_waiting"]) >= 3
    assert len(roots_by_surface["gate_congestion"]) >= 3
    assert len(roots_by_surface["berth_occupancy"]) >= 3
    assert len(roots_by_surface["qc_productivity"]) >= 2


def test_synthetic_writer_includes_required_columns(tmp_path: Path) -> None:
    generator = _load_generator()
    output = tmp_path / "synthetic.csv"
    graph = build_reference_port_graph()
    rows = generator.generate_rows(graph, 2400, 2026, 0.0)
    generator.write_rows(output, graph, rows)

    with output.open(newline="", encoding="utf-8") as dataset:
        reader = csv.DictReader(dataset)
        assert reader.fieldnames is not None
        assert {
            "scenario_id",
            "scenario_family",
            "observed_kpi",
            "surface_cause_label",
            "root_cause_label",
            "reinforcing_loop_id",
            "recommended_intervention",
            "explanation_template",
        }.issubset(reader.fieldnames)
