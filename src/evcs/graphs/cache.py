from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from evcs.data.tensor_cache import EVCSTensorCache


@dataclass(frozen=True)
class SparseGraphCache:
    baseline_id: str
    indices: np.ndarray
    weights: np.ndarray
    nodes: list[str]
    dynamic: bool
    train_origin_end: int | None
    top_k: int

    def manifest(self) -> dict[str, Any]:
        return {
            "baseline_id": self.baseline_id,
            "dynamic": self.dynamic,
            "node_count": len(self.nodes),
            "top_k": self.top_k,
            "train_origin_end": self.train_origin_end,
            "origin_count": int(self.indices.shape[0]),
            "edge_count_per_origin_budget": int(np.count_nonzero(self.weights[0])) if len(self.weights) else 0,
        }


def build_exp103_graph_cache(
    cache: EVCSTensorCache,
    baseline_ids: list[str],
    top_k: int,
    seed: int = 42,
    dtw_max_points: int | None = None,
    rho: float = 0.0,
    lambda_event: float = 0.3,
) -> dict[str, SparseGraphCache]:
    if top_k < 1:
        raise ValueError("top_k must be >= 1")
    if not 0.0 <= rho <= 1.0:
        raise ValueError("rho must be in [0, 1]")
    if not 0.0 <= lambda_event <= 1.0:
        raise ValueError("lambda_event must be in [0, 1]")
    if not cache.origin_indices:
        raise ValueError("tensor cache has no valid prediction origins")
    top_k = min(top_k, max(1, len(cache.nodes) - 1))
    event_graph = _dynamic_event_graph(cache, top_k)
    smoothed_event_graph = _smooth_dynamic_event_graph(cache, event_graph, top_k, rho)
    train_end = max(cache.split_indices.get("train", []) or [cache.origin_indices[0]])
    dtw_graph: SparseGraphCache | None = None
    rng = np.random.default_rng(seed)
    graphs: dict[str, SparseGraphCache] = {}
    for baseline_id in baseline_ids:
        if baseline_id == "event_graph_dynamic":
            graphs[baseline_id] = event_graph
        elif baseline_id == "event_graph_dynamic_rho":
            graphs[baseline_id] = smoothed_event_graph
        elif baseline_id == "dtw_demand_graph":
            dtw_graph = dtw_graph or _dtw_graph(cache, top_k, train_end, dtw_max_points)
            graphs[baseline_id] = dtw_graph
        elif baseline_id == "historical_correlation_graph":
            values = cache.load[: train_end + 1].T
            similarity = _safe_positive_correlation(values)
            similarity = np.clip(similarity, 0.0, None)
            np.fill_diagonal(similarity, 0.0)
            graphs[baseline_id] = _static_graph(baseline_id, cache, similarity, top_k, train_end)
        elif baseline_id == "event_dtw_fusion_graph":
            dtw_graph = dtw_graph or _dtw_graph(cache, top_k, train_end, dtw_max_points)
            graphs[baseline_id] = _fusion_graph(cache, smoothed_event_graph, dtw_graph, top_k, lambda_event, train_end)
        elif baseline_id == "random_event_graph":
            graphs[baseline_id] = _random_like_event(cache, event_graph, rng)
        elif baseline_id == "shuffled_event_graph":
            graphs[baseline_id] = _shuffled_like_event(cache, event_graph, rng)
        elif baseline_id == "deleted_event_graph":
            graphs[baseline_id] = SparseGraphCache(
                baseline_id,
                event_graph.indices.copy(),
                np.zeros_like(event_graph.weights),
                cache.nodes,
                dynamic=True,
                train_origin_end=None,
                top_k=top_k,
            )
        elif baseline_id in {"no_graph", "behavior_concat"}:
            graphs[baseline_id] = SparseGraphCache(
                baseline_id,
                np.zeros_like(event_graph.indices),
                np.zeros_like(event_graph.weights),
                cache.nodes,
                dynamic=False,
                train_origin_end=None,
                top_k=top_k,
            )
        else:
            raise ValueError(f"unsupported EXP-103 graph baseline: {baseline_id}")
    return graphs


def _dtw_graph(cache: EVCSTensorCache, top_k: int, train_end: int, dtw_max_points: int | None) -> SparseGraphCache:
    return _static_graph(
        "dtw_demand_graph",
        cache,
        _dtw_similarity(_prepare_static_load(cache.load[: train_end + 1], dtw_max_points)),
        top_k,
        train_end,
    )


def _dynamic_event_graph(cache: EVCSTensorCache, top_k: int) -> SparseGraphCache:
    origin_count = len(cache.origin_indices)
    node_count = len(cache.nodes)
    indices = np.zeros((origin_count, node_count, top_k), dtype=np.int32)
    weights = np.zeros((origin_count, node_count, top_k), dtype=np.float32)
    for origin_pos, origin in enumerate(cache.origin_indices):
        start = max(0, origin - cache.history_steps + 1)
        features = cache.event_features[start : origin + 1].mean(axis=0)
        similarity = _cosine_similarity(_zscore(features))
        np.fill_diagonal(similarity, 0.0)
        row_indices, row_weights = _topk_sparse(similarity, top_k)
        indices[origin_pos] = row_indices
        weights[origin_pos] = row_weights
    return SparseGraphCache(
        baseline_id="event_graph_dynamic",
        indices=indices,
        weights=weights,
        nodes=cache.nodes,
        dynamic=True,
        train_origin_end=None,
        top_k=top_k,
    )


def _smooth_dynamic_event_graph(cache: EVCSTensorCache, event_graph: SparseGraphCache, top_k: int, rho: float) -> SparseGraphCache:
    if rho == 0.0:
        return SparseGraphCache(
            "event_graph_dynamic_rho",
            event_graph.indices.copy(),
            event_graph.weights.copy(),
            cache.nodes,
            dynamic=True,
            train_origin_end=None,
            top_k=top_k,
        )
    origin_count = len(cache.origin_indices)
    node_count = len(cache.nodes)
    smoothed_dense = np.zeros((origin_count, node_count, node_count), dtype=np.float32)
    previous = None
    for origin_pos in range(origin_count):
        raw = _sparse_origin_to_dense(event_graph.indices[origin_pos], event_graph.weights[origin_pos], node_count)
        # rho 时间平滑把相邻预测时刻的事件关系连起来，避免 A_event,t 因单个时间片噪声剧烈抖动。
        current = raw if previous is None else rho * previous + (1.0 - rho) * raw
        current = _row_normalize_dense(current)
        smoothed_dense[origin_pos] = current
        previous = current
    return _dynamic_dense_graph("event_graph_dynamic_rho", cache, smoothed_dense, top_k, train_origin_end=None)


def _fusion_graph(
    cache: EVCSTensorCache,
    event_graph: SparseGraphCache,
    dtw_graph: SparseGraphCache,
    top_k: int,
    lambda_event: float,
    train_end: int,
) -> SparseGraphCache:
    node_count = len(cache.nodes)
    event_dense = _sparse_cache_to_dense(event_graph, node_count)
    dtw_dense = _sparse_cache_to_dense(dtw_graph, node_count)
    # 融合图用于检验“行为事件关系是否能补充历史需求相似图”，而不是强行声称单一事件图全胜。
    fused = lambda_event * event_dense + (1.0 - lambda_event) * dtw_dense
    fused = np.asarray([_row_normalize_dense(matrix) for matrix in fused], dtype=np.float32)
    return _dynamic_dense_graph("event_dtw_fusion_graph", cache, fused, top_k, train_origin_end=train_end)


def _static_graph(
    baseline_id: str,
    cache: EVCSTensorCache,
    similarity: np.ndarray,
    top_k: int,
    train_end: int,
) -> SparseGraphCache:
    row_indices, row_weights = _topk_sparse(similarity, top_k)
    indices = np.repeat(row_indices[np.newaxis, :, :], len(cache.origin_indices), axis=0).astype(np.int32)
    weights = np.repeat(row_weights[np.newaxis, :, :], len(cache.origin_indices), axis=0).astype(np.float32)
    return SparseGraphCache(
        baseline_id=baseline_id,
        indices=indices,
        weights=weights,
        nodes=cache.nodes,
        dynamic=False,
        train_origin_end=train_end,
        top_k=top_k,
    )


def _dynamic_dense_graph(
    baseline_id: str,
    cache: EVCSTensorCache,
    dense: np.ndarray,
    top_k: int,
    train_origin_end: int | None,
) -> SparseGraphCache:
    origin_count = dense.shape[0]
    node_count = len(cache.nodes)
    indices = np.zeros((origin_count, node_count, top_k), dtype=np.int32)
    weights = np.zeros((origin_count, node_count, top_k), dtype=np.float32)
    for origin_pos in range(origin_count):
        row_indices, row_weights = _topk_sparse(dense[origin_pos], top_k)
        indices[origin_pos] = row_indices
        weights[origin_pos] = row_weights
    return SparseGraphCache(baseline_id, indices, weights, cache.nodes, True, train_origin_end, top_k)


def _random_like_event(cache: EVCSTensorCache, event_graph: SparseGraphCache, rng: np.random.Generator) -> SparseGraphCache:
    indices = np.zeros_like(event_graph.indices)
    weights = np.zeros_like(event_graph.weights)
    node_count = len(cache.nodes)
    for origin_pos in range(indices.shape[0]):
        for node_index in range(node_count):
            candidates = [index for index in range(node_count) if index != node_index]
            chosen = rng.choice(candidates, size=event_graph.top_k, replace=False)
            raw = rng.random(event_graph.top_k).astype(np.float32)
            indices[origin_pos, node_index] = chosen
            weights[origin_pos, node_index] = raw / raw.sum()
    return SparseGraphCache("random_event_graph", indices, weights, cache.nodes, True, None, event_graph.top_k)


def _shuffled_like_event(cache: EVCSTensorCache, event_graph: SparseGraphCache, rng: np.random.Generator) -> SparseGraphCache:
    order = np.arange(event_graph.indices.shape[0])
    rng.shuffle(order)
    return SparseGraphCache(
        "shuffled_event_graph",
        event_graph.indices[order].copy(),
        event_graph.weights[order].copy(),
        cache.nodes,
        True,
        None,
        event_graph.top_k,
    )


def _prepare_static_load(load: np.ndarray, max_points: int | None) -> np.ndarray:
    values = load
    if max_points and len(values) > max_points:
        indices = np.linspace(0, len(values) - 1, num=max_points, dtype=int)
        values = values[sorted(set(indices))]
    return values.T


def _dtw_similarity(values: np.ndarray) -> np.ndarray:
    count = values.shape[0]
    similarity = np.zeros((count, count), dtype=np.float32)
    for left in range(count):
        for right in range(left + 1, count):
            distance = _dtw_distance(values[left], values[right])
            weight = 1.0 / (1.0 + distance)
            similarity[left, right] = weight
            similarity[right, left] = weight
    return similarity


def _dtw_distance(left: np.ndarray, right: np.ndarray) -> float:
    rows = len(left) + 1
    cols = len(right) + 1
    table = np.full((rows, cols), np.inf, dtype=np.float32)
    table[0, 0] = 0.0
    for row in range(1, rows):
        for col in range(1, cols):
            cost = abs(float(left[row - 1]) - float(right[col - 1]))
            table[row, col] = cost + min(table[row - 1, col], table[row, col - 1], table[row - 1, col - 1])
    return float(table[-1, -1])


def _safe_positive_correlation(values: np.ndarray) -> np.ndarray:
    centered = values - values.mean(axis=1, keepdims=True)
    norm = np.linalg.norm(centered, axis=1, keepdims=True)
    normalized = np.divide(centered, norm, out=np.zeros_like(centered), where=norm > 0)
    return normalized @ normalized.T


def _sparse_cache_to_dense(graph: SparseGraphCache, node_count: int) -> np.ndarray:
    dense = np.zeros((graph.indices.shape[0], node_count, node_count), dtype=np.float32)
    for origin_pos in range(graph.indices.shape[0]):
        dense[origin_pos] = _sparse_origin_to_dense(graph.indices[origin_pos], graph.weights[origin_pos], node_count)
    return dense


def _sparse_origin_to_dense(indices: np.ndarray, weights: np.ndarray, node_count: int) -> np.ndarray:
    dense = np.zeros((node_count, node_count), dtype=np.float32)
    for row_index in range(node_count):
        dense[row_index, indices[row_index]] = weights[row_index]
    return dense


def _row_normalize_dense(values: np.ndarray) -> np.ndarray:
    normalized = values.astype(np.float32).copy()
    row_sum = normalized.sum(axis=1, keepdims=True)
    return np.divide(normalized, row_sum, out=np.zeros_like(normalized), where=row_sum > 0)


def _topk_sparse(similarity: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
    node_count = similarity.shape[0]
    indices = np.zeros((node_count, top_k), dtype=np.int32)
    weights = np.zeros((node_count, top_k), dtype=np.float32)
    for row_index, row in enumerate(similarity):
        candidates = [index for index in np.argsort(row)[::-1] if index != row_index][:top_k]
        if not candidates:
            continue
        raw = np.asarray([max(float(row[index]), 0.0) for index in candidates], dtype=np.float32)
        if float(raw.sum()) == 0.0:
            raw[:] = 1.0
        indices[row_index, : len(candidates)] = np.asarray(candidates, dtype=np.int32)
        weights[row_index, : len(candidates)] = raw / raw.sum()
    return indices, weights


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
