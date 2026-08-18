import argparse
import csv
import json
from pathlib import Path

from causal_engine.models import FcmEdge
from causal_engine.port_graph import build_reference_port_graph
from causal_engine.training import EdgeTrainingSpec, LearnedEdgeWeight, fit_static_weights

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = REPOSITORY_ROOT / "data/synthetic/sample_causal_training.csv"
DEFAULT_OUTPUT = REPOSITORY_ROOT / "data/synthetic/trained_causal_model.json"
REFERENCE_GRAPH = build_reference_port_graph()
EDGE_SPECS = tuple(
    EdgeTrainingSpec(edge.source_node_id, edge.target_node_id) for edge in REFERENCE_GRAPH.edges
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train static FCM weights from synthetic data.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--ridge-alpha", type=float, default=1e-3)
    args = parser.parse_args()

    training_rows, excluded_rows = load_observational_rows(args.input)
    result = fit_static_weights(training_rows, EDGE_SPECS, ridge_alpha=args.ridge_alpha)
    reference_edges = {
        (edge.source_node_id, edge.target_node_id): edge for edge in REFERENCE_GRAPH.edges
    }
    absolute_errors = [
        abs(edge.weight - reference_edges[(edge.source_node_id, edge.target_node_id)].base_weight)
        for edge in result.edges
    ]

    artifact = {
        "model_type": "static_fcm",
        "graph_id": REFERENCE_GRAPH.id,
        "terminal_id": REFERENCE_GRAPH.terminal_id,
        "equation": "X(t+1) = tanh(X(t) + X(t)W)",
        "source_dataset": _display_path(args.input),
        "training_rows": result.training_rows,
        "excluded_intervention_rows": excluded_rows,
        "ridge_alpha": args.ridge_alpha,
        "overall_rmse": round(result.overall_rmse, 6),
        "weight_mae": round(sum(absolute_errors) / len(absolute_errors), 6),
        "target_rmse": {target: round(rmse, 6) for target, rmse in result.target_rmse.items()},
        "nodes": [
            {
                "id": node.id,
                "label": node.label,
                "node_type": node.node_type.value,
                "subsystem": node.subsystem,
            }
            for node in REFERENCE_GRAPH.nodes
        ],
        "edges": [
            _edge_artifact(edge, reference_edges[(edge.source_node_id, edge.target_node_id)])
            for edge in result.edges
        ],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(f"Trained {len(result.edges)} edges from {result.training_rows} rows")
    print(f"Excluded {excluded_rows} intervention rows")
    print(f"Overall RMSE: {result.overall_rmse:.6f}")
    print(f"Weight MAE: {sum(absolute_errors) / len(absolute_errors):.6f}")
    print(f"Model written to {_display_path(args.output)}")


def load_observational_rows(path: Path) -> tuple[list[dict[str, float]], int]:
    required_columns = {
        f"{node_id}_{suffix}"
        for edge in EDGE_SPECS
        for node_id, suffix in (
            (edge.source_node_id, "t"),
            (edge.target_node_id, "t"),
            (edge.target_node_id, "next"),
        )
    }
    training_rows: list[dict[str, float]] = []
    excluded_rows = 0

    with path.open(newline="", encoding="utf-8") as dataset:
        reader = csv.DictReader(dataset)
        missing_columns = required_columns.difference(reader.fieldnames or [])
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Dataset is missing required columns: {missing}")

        for row in reader:
            if row.get("intervention_type", "none") != "none":
                excluded_rows += 1
                continue
            training_rows.append({column: float(row[column]) for column in required_columns})

    return training_rows, excluded_rows


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPOSITORY_ROOT))
    except ValueError:
        return str(resolved)


def _edge_artifact(learned_edge: LearnedEdgeWeight, reference_edge: FcmEdge) -> dict[str, object]:
    learned_weight = learned_edge.weight
    reference_weight = reference_edge.base_weight
    return {
        "id": reference_edge.id,
        "source_node_id": learned_edge.source_node_id,
        "target_node_id": learned_edge.target_node_id,
        "base_weight": round(learned_weight, 6),
        "polarity": "positive" if learned_weight >= 0.0 else "negative",
        "ground_truth_weight": reference_weight,
        "absolute_error": round(abs(learned_weight - reference_weight), 6),
    }


if __name__ == "__main__":
    main()
