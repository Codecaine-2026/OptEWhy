import argparse
import csv
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
from causal_engine.models import FcmGraph
from causal_engine.port_graph import build_reference_port_graph
from numpy.typing import NDArray

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPOSITORY_ROOT / "data/synthetic/sample_causal_training.csv"
REGIME_MEANS = {
    "normal": np.array([-0.15, -0.10, 0.10, 0.05, 0.00, 0.00, 0.10, 0.05]),
    "congested": np.array([0.10, 0.15, 0.55, 0.60, 0.45, 0.50, -0.35, 0.50]),
    "weather_disruption": np.array([0.65, 0.35, 0.45, 0.40, 0.55, 0.50, -0.45, 0.60]),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic FCM transition data.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--rows", type=int, default=1000)
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
    if row_count <= 0:
        raise ValueError("row_count must be greater than zero")
    if noise_std < 0.0:
        raise ValueError("noise_std cannot be negative")

    rng = np.random.default_rng(seed)
    node_ids = [node.id for node in graph.nodes]
    index = {node_id: offset for offset, node_id in enumerate(node_ids)}
    weights: NDArray[np.float64] = np.zeros((len(node_ids), len(node_ids)), dtype=float)
    for edge in graph.edges:
        weights[index[edge.source_node_id], index[edge.target_node_id]] = edge.base_weight

    started_at = datetime(2026, 1, 1, tzinfo=UTC)
    rows: list[dict[str, object]] = []
    regime_names = tuple(REGIME_MEANS)
    regime_probabilities = (0.50, 0.35, 0.15)

    for row_index in range(row_count):
        regime = str(rng.choice(regime_names, p=regime_probabilities))
        current = np.clip(
            REGIME_MEANS[regime] + rng.normal(0.0, 0.22, size=len(node_ids)),
            -0.85,
            0.85,
        )
        intervention_type = "none"
        intervention_node_id = ""
        intervention_value = 0.0

        if row_index % 20 == 0:
            intervention_type = "decrease_yard_density"
            intervention_node_id = "yard_density"
            intervention_value = 0.15
        elif row_index % 10 == 0:
            intervention_type = "decrease_berth_occupancy"
            intervention_node_id = "berth_occupancy"
            intervention_value = 0.12

        if intervention_node_id:
            node_index = index[intervention_node_id]
            current[node_index] = max(-1.0, current[node_index] - intervention_value)

        noise = rng.normal(0.0, noise_std, size=len(node_ids))
        next_state = np.tanh(current + current @ weights + noise)
        row: dict[str, object] = {
            "timestamp": (started_at + timedelta(minutes=15 * row_index)).isoformat(),
            "terminal_id": graph.terminal_id,
            "operating_regime": regime,
            "intervention_type": intervention_type,
            "intervention_node_id": intervention_node_id,
            "intervention_value": intervention_value,
        }
        row.update(
            {f"{node_id}_t": round(float(current[index[node_id]]), 6) for node_id in node_ids}
        )
        row.update(
            {f"{node_id}_next": round(float(next_state[index[node_id]]), 6) for node_id in node_ids}
        )
        rows.append(row)

    return rows


def write_rows(path: Path, graph: FcmGraph, rows: list[dict[str, object]]) -> None:
    node_ids = [node.id for node in graph.nodes]
    fieldnames = [
        "timestamp",
        "terminal_id",
        "operating_regime",
        *(f"{node_id}_t" for node_id in node_ids),
        "intervention_type",
        "intervention_node_id",
        "intervention_value",
        *(f"{node_id}_next" for node_id in node_ids),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as dataset:
        writer = csv.DictWriter(dataset, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPOSITORY_ROOT))
    except ValueError:
        return str(resolved)


if __name__ == "__main__":
    main()
