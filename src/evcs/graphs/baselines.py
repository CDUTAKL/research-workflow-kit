from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from evcs.graphs.event_graph import EventAdjacency, build_event_adjacency


@dataclass(frozen=True)
class GraphBaseline:
    baseline_id: str
    nodes: list[str]
    adjacency: np.ndarray
    top_edges: list[dict[str, Any]]


def build_graph_baseline(
    baseline_id: str,
    frame: pd.DataFrame,
    node_field: str,
    timestamp_field: str,
    target_field: str,
    event_feature_fields: list[str],
    top_k: int,
    seed: int = 42,
    dtw_resample: str | None = None,
    dtw_max_points: int | None = None,
    event: EventAdjacency | None = None,
    target_pivot: pd.DataFrame | None = None,
) -> GraphBaseline:
    if event is None:
        event = build_event_adjacency(frame, node_field=node_field, feature_fields=event_feature_fields, top_k=top_k)
    if baseline_id in {"event_graph", "A_event,t"}:
        return _from_event(baseline_id, event)
    if baseline_id == "dtw_demand_graph":
        return _from_similarity(
            baseline_id,
            frame,
            node_field,
            timestamp_field,
            target_field,
            top_k,
            metric="dtw",
            resample=dtw_resample,
            max_points=dtw_max_points,
            pivot=target_pivot,
        )
    if baseline_id == "historical_correlation_graph":
        return _from_similarity(
            baseline_id,
            frame,
            node_field,
            timestamp_field,
            target_field,
            top_k,
            metric="correlation",
            pivot=target_pivot,
        )
    if baseline_id == "random_event_graph":
        return _random_like(event, seed=seed)
    if baseline_id == "shuffled_event_graph":
        return _shuffled(event, seed=seed)
    if baseline_id == "deleted_event_graph":
        return GraphBaseline(baseline_id, event.nodes, np.zeros_like(event.adjacency), [])
    if baseline_id == "behavior_concat":
        return GraphBaseline(baseline_id, event.nodes, np.eye(len(event.nodes)), [])
    raise ValueError(f"unsupported graph baseline: {baseline_id}")


def graph_lag_prediction(
    frame: pd.DataFrame,
    graph: GraphBaseline,
    timestamp_field: str,
    node_field: str,
    target_field: str,
) -> pd.DataFrame:
    data = frame.copy()
    data[timestamp_field] = pd.to_datetime(data[timestamp_field], errors="coerce")
    pivot = data.pivot_table(index=timestamp_field, columns=node_field, values=target_field, aggfunc="mean")
    pivot = pivot.reindex(columns=graph.nodes).sort_index().fillna(0.0)
    lagged = pivot.shift(1).dropna()
    actual = pivot.loc[lagged.index]
    predicted = lagged.to_numpy(dtype=float) @ graph.adjacency.T
    rows = []
    for row_index, timestamp in enumerate(lagged.index):
        for node_index, node in enumerate(graph.nodes):
            rows.append(
                {
                    "timestamp": timestamp,
                    "node_id": node,
                    "actual": float(actual.iloc[row_index, node_index]),
                    "prediction": float(predicted[row_index, node_index]),
                }
            )
    return pd.DataFrame.from_records(rows)


def graph_lag_metrics(
    frame: pd.DataFrame,
    graph: GraphBaseline,
    timestamp_field: str,
    node_field: str,
    target_field: str,
) -> dict[str, float | int]:
    pivot = _node_target_matrix(frame, node_field, timestamp_field, target_field)
    return graph_lag_metrics_from_pivot(pivot, graph)


def graph_lag_metrics_from_pivot(pivot: pd.DataFrame, graph: GraphBaseline) -> dict[str, float | int]:
    pivot = pivot.reindex(columns=graph.nodes).sort_index().fillna(0.0)
    actual = np.nan_to_num(pivot.iloc[1:].to_numpy(dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    lagged = np.nan_to_num(pivot.iloc[:-1].to_numpy(dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    adjacency = np.nan_to_num(graph.adjacency, nan=0.0, posinf=0.0, neginf=0.0)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        predicted = lagged @ adjacency.T
    predicted = np.nan_to_num(predicted, nan=0.0, posinf=0.0, neginf=0.0)
    error = actual - predicted
    return {
        "MAE": float(np.mean(np.abs(error))),
        "RMSE": float(np.sqrt(np.mean(error**2))),
        "prediction_count": int(error.size),
    }


def _from_event(baseline_id: str, event: EventAdjacency) -> GraphBaseline:
    return GraphBaseline(baseline_id, event.nodes, event.adjacency, event.top_edges)


def _from_similarity(
    baseline_id: str,
    frame: pd.DataFrame,
    node_field: str,
    timestamp_field: str,
    target_field: str,
    top_k: int,
    metric: str,
    resample: str | None = None,
    max_points: int | None = None,
    pivot: pd.DataFrame | None = None,
) -> GraphBaseline:
    if pivot is None:
        pivot = _node_target_matrix(frame, node_field, timestamp_field, target_field)
    pivot = _prepare_similarity_pivot(pivot, resample=resample, max_points=max_points)
    nodes = [str(node) for node in pivot.columns.tolist()]
    values = np.nan_to_num(pivot.to_numpy(dtype=float).T, nan=0.0, posinf=0.0, neginf=0.0)
    if metric == "dtw":
        similarity = _dtw_similarity(values)
    elif metric == "correlation":
        similarity = np.corrcoef(values)
        similarity = np.nan_to_num(similarity, nan=0.0)
        similarity = np.clip(similarity, 0.0, None)
    else:
        raise ValueError(f"unsupported metric: {metric}")
    np.fill_diagonal(similarity, 0.0)
    adjacency = _topk_row_normalize(similarity, min(top_k, max(1, len(nodes) - 1)))
    return GraphBaseline(baseline_id, nodes, adjacency, _edge_rows(nodes, adjacency))


def _node_target_matrix(
    frame: pd.DataFrame,
    node_field: str,
    timestamp_field: str,
    target_field: str,
) -> pd.DataFrame:
    data = frame.copy()
    data[timestamp_field] = pd.to_datetime(data[timestamp_field], errors="coerce")
    return data.pivot_table(index=timestamp_field, columns=node_field, values=target_field, aggfunc="mean").sort_index().fillna(0.0)


def _prepare_similarity_pivot(pivot: pd.DataFrame, resample: str | None = None, max_points: int | None = None) -> pd.DataFrame:
    pivot = pivot.sort_index().fillna(0.0)
    if resample:
        pivot = pivot.resample(resample).mean().fillna(0.0)
    if max_points and len(pivot) > max_points:
        indices = np.linspace(0, len(pivot) - 1, num=max_points, dtype=int)
        pivot = pivot.iloc[sorted(set(indices))]
    return pivot


def _dtw_similarity(values: np.ndarray) -> np.ndarray:
    count = values.shape[0]
    similarity = np.zeros((count, count), dtype=float)
    for i in range(count):
        for j in range(i + 1, count):
            distance = _dtw_distance(values[i], values[j])
            weight = 1.0 / (1.0 + distance)
            similarity[i, j] = weight
            similarity[j, i] = weight
    return similarity


def _dtw_distance(left: np.ndarray, right: np.ndarray) -> float:
    rows = len(left) + 1
    cols = len(right) + 1
    table = np.full((rows, cols), np.inf)
    table[0, 0] = 0.0
    for row in range(1, rows):
        for col in range(1, cols):
            cost = abs(float(left[row - 1]) - float(right[col - 1]))
            table[row, col] = cost + min(table[row - 1, col], table[row, col - 1], table[row - 1, col - 1])
    return float(table[-1, -1])


def _random_like(event: EventAdjacency, seed: int) -> GraphBaseline:
    rng = np.random.default_rng(seed)
    random_weights = rng.random(event.adjacency.shape)
    random_weights[event.adjacency <= 0] = 0.0
    adjacency = _row_normalize(random_weights)
    return GraphBaseline("random_event_graph", event.nodes, adjacency, _edge_rows(event.nodes, adjacency))


def _shuffled(event: EventAdjacency, seed: int) -> GraphBaseline:
    rng = np.random.default_rng(seed)
    flat = event.adjacency.flatten()
    rng.shuffle(flat)
    adjacency = flat.reshape(event.adjacency.shape)
    np.fill_diagonal(adjacency, 0.0)
    adjacency = _row_normalize(adjacency)
    return GraphBaseline("shuffled_event_graph", event.nodes, adjacency, _edge_rows(event.nodes, adjacency))


def _topk_row_normalize(similarity: np.ndarray, top_k: int) -> np.ndarray:
    adjacency = np.zeros_like(similarity, dtype=float)
    for row_index, row in enumerate(similarity):
        candidates = [index for index in np.argsort(row)[::-1] if index != row_index][:top_k]
        total = sum(max(float(row[index]), 0.0) for index in candidates)
        if total == 0:
            total = float(len(candidates))
            for index in candidates:
                adjacency[row_index, index] = 1.0 / total if total else 0.0
        else:
            for index in candidates:
                adjacency[row_index, index] = max(float(row[index]), 0.0) / total
    return adjacency


def _row_normalize(values: np.ndarray) -> np.ndarray:
    out = values.copy().astype(float)
    row_sums = out.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    return out / row_sums


def _edge_rows(nodes: list[str], adjacency: np.ndarray) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source_index, source in enumerate(nodes):
        for target_index, target in enumerate(nodes):
            weight = float(adjacency[source_index, target_index])
            if weight > 0:
                rows.append({"source": source, "target": target, "weight": weight})
    return rows
