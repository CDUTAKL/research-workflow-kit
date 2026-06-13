from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class EventAdjacency:
    nodes: list[str]
    adjacency: np.ndarray
    top_edges: list[dict[str, Any]]


def build_event_adjacency(
    events: pd.DataFrame,
    node_field: str,
    feature_fields: list[str],
    top_k: int,
) -> EventAdjacency:
    if node_field not in events.columns:
        raise ValueError(f"node field not found: {node_field}")
    missing = [field for field in feature_fields if field not in events.columns]
    if missing:
        raise ValueError(f"feature fields not found: {', '.join(missing)}")
    if top_k < 1:
        raise ValueError("top_k must be >= 1")

    grouped = events.groupby(node_field, sort=True)[feature_fields].mean()
    nodes = [str(node) for node in grouped.index.tolist()]
    features = grouped.to_numpy(dtype=float)
    features = _zscore(features)
    similarity = _cosine_similarity(features)
    np.fill_diagonal(similarity, 0.0)
    adjacency = _topk_row_normalize(similarity, min(top_k, max(1, len(nodes) - 1)))
    top_edges = _edge_rows(nodes, adjacency)
    return EventAdjacency(nodes=nodes, adjacency=adjacency, top_edges=top_edges)


def _zscore(values: np.ndarray) -> np.ndarray:
    mean = values.mean(axis=0, keepdims=True)
    std = values.std(axis=0, keepdims=True)
    std[std == 0] = 1.0
    return (values - mean) / std


def _cosine_similarity(values: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(values, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    normalized = values / norm
    return normalized @ normalized.T


def _topk_row_normalize(similarity: np.ndarray, top_k: int) -> np.ndarray:
    adjacency = np.zeros_like(similarity, dtype=float)
    for row_index, row in enumerate(similarity):
        if row.size <= 1:
            continue
        candidates = [index for index in np.argsort(row)[::-1] if index != row_index][:top_k]
        positive = [(index, max(float(row[index]), 0.0)) for index in candidates if index != row_index]
        total = sum(weight for _, weight in positive)
        if total == 0:
            positive = [(index, 1.0) for index in candidates if index != row_index]
            total = sum(weight for _, weight in positive)
        for index, weight in positive:
            adjacency[row_index, index] = weight / total if total else 0.0
    return adjacency


def _edge_rows(nodes: list[str], adjacency: np.ndarray) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source_index, source in enumerate(nodes):
        for target_index, target in enumerate(nodes):
            weight = float(adjacency[source_index, target_index])
            if weight > 0:
                rows.append({"source": source, "target": target, "weight": weight})
    return rows
