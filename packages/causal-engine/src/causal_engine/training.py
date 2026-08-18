from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from math import sqrt

import numpy as np


@dataclass(frozen=True)
class EdgeTrainingSpec:
    source_node_id: str
    target_node_id: str


@dataclass(frozen=True)
class LearnedEdgeWeight:
    source_node_id: str
    target_node_id: str
    weight: float


@dataclass(frozen=True)
class StaticWeightTrainingResult:
    edges: list[LearnedEdgeWeight]
    target_rmse: dict[str, float]
    overall_rmse: float
    training_rows: int


def fit_static_weights(
    rows: Sequence[Mapping[str, float]],
    edge_specs: Sequence[EdgeTrainingSpec],
    ridge_alpha: float = 1e-3,
) -> StaticWeightTrainingResult:
    """Fit static FCM edge weights for a known graph topology."""
    if not rows:
        raise ValueError("At least one training row is required")
    if not edge_specs:
        raise ValueError("At least one edge specification is required")
    if ridge_alpha <= 0.0:
        raise ValueError("ridge_alpha must be greater than zero")

    sources_by_target: dict[str, list[str]] = {}
    for edge in edge_specs:
        sources = sources_by_target.setdefault(edge.target_node_id, [])
        if edge.source_node_id in sources:
            raise ValueError(
                f"Duplicate edge specification: {edge.source_node_id} -> {edge.target_node_id}"
            )
        sources.append(edge.source_node_id)

    learned_edges: list[LearnedEdgeWeight] = []
    target_rmse: dict[str, float] = {}
    squared_errors: list[float] = []

    for target_node_id, source_node_ids in sources_by_target.items():
        design = np.array(
            [
                [_value(row, f"{source_node_id}_t") for source_node_id in source_node_ids]
                for row in rows
            ],
            dtype=float,
        )
        current_target = np.array(
            [_value(row, f"{target_node_id}_t") for row in rows], dtype=float
        )
        next_target = np.array(
            [_value(row, f"{target_node_id}_next") for row in rows], dtype=float
        )

        clipped_next = np.clip(next_target, -1.0 + 1e-7, 1.0 - 1e-7)
        transformed_target = np.arctanh(clipped_next) - current_target
        regularized_gram = design.T @ design + ridge_alpha * np.eye(len(source_node_ids))
        fitted_weights = np.linalg.solve(regularized_gram, design.T @ transformed_target)
        fitted_weights = np.clip(fitted_weights, -1.0, 1.0)

        prediction = np.tanh(current_target + design @ fitted_weights)
        errors = prediction - next_target
        rmse = sqrt(float(np.mean(np.square(errors))))
        target_rmse[target_node_id] = rmse
        squared_errors.extend(float(error**2) for error in errors)

        learned_edges.extend(
            LearnedEdgeWeight(
                source_node_id=source_node_id,
                target_node_id=target_node_id,
                weight=float(weight),
            )
            for source_node_id, weight in zip(source_node_ids, fitted_weights, strict=True)
        )

    return StaticWeightTrainingResult(
        edges=learned_edges,
        target_rmse=target_rmse,
        overall_rmse=sqrt(sum(squared_errors) / len(squared_errors)),
        training_rows=len(rows),
    )


def _value(row: Mapping[str, float], column: str) -> float:
    try:
        return float(row[column])
    except KeyError as error:
        raise ValueError(f"Missing training column: {column}") from error
