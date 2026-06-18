from __future__ import annotations

"""EXP-103 图结构缓存与 baseline 构造。

这里的“图”不是静态论文插图，而是训练时喂给 GraphTemporalTCN 的稀疏邻接张量：

- 静态图：`indices/weights` 在所有 prediction origin 上重复，例如 DTW 图和历史相关图。
- 动态图：每个 prediction origin 都有自己的 top-k 邻居，例如事件动态图。
- 双分支图：主 `indices/weights` 保存事件图，同时 `historical_*` 保存历史相关图。
- 多通道图：`channel_indices/channel_weights` 为 access、departure、occupancy 等事件族各建一张图。

因果边界非常重要：历史相关图和 DTW 图只使用 train split 的负载历史；
事件动态图只使用当前预测 origin 之前的 history window。这样训练和测试都不会偷看未来。
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from evcs.data.tensor_cache import EVCSTensorCache


@dataclass(frozen=True)
class SparseGraphCache:
    """训练阶段使用的稀疏图缓存。

    `indices[o, i, k]` 表示第 `o` 个预测起点、源节点 `i` 的第 `k` 个邻居；
    `weights[o, i, k]` 是对应归一化权重。即使是静态图，也会复制到 origin 维度，
    这样 Dataset/Model 可以使用同一套张量接口。
    """

    baseline_id: str
    indices: np.ndarray
    weights: np.ndarray
    nodes: list[str]
    dynamic: bool
    train_origin_end: int | None
    top_k: int
    historical_indices: np.ndarray | None = None
    historical_weights: np.ndarray | None = None
    channel_indices: np.ndarray | None = None
    channel_weights: np.ndarray | None = None
    channel_names: list[str] | None = None
    channel_feature_names: dict[str, list[str]] | None = None

    def manifest(self) -> dict[str, Any]:
        """导出可写入 `graph_manifest.json` 的轻量说明，便于 evidence 包审计。"""

        manifest = {
            "baseline_id": self.baseline_id,
            "dynamic": self.dynamic,
            "node_count": len(self.nodes),
            "top_k": self.top_k,
            "train_origin_end": self.train_origin_end,
            "origin_count": int(self.indices.shape[0]),
            "edge_count_per_origin_budget": int(np.count_nonzero(self.weights[0])) if len(self.weights) else 0,
        }
        if self.historical_indices is not None:
            manifest["has_historical_branch"] = True
        if self.channel_indices is not None:
            manifest["channel_count"] = int(self.channel_indices.shape[1])
            manifest["channel_names"] = list(self.channel_names or [])
            manifest["channel_feature_names"] = self.channel_feature_names or {}
        return manifest


DEFAULT_EVENT_CHANNELS = {
    "access": ["access_count", "access_count_roll_1h"],
    "departure": ["departure_count", "departure_count_roll_1h"],
    "activity": ["active_count", "active_count_diff"],
    "occupancy": ["occupancy_rate", "occupancy_rate_roll_max_3h"],
    "demand": ["demand_intensity", "near_capacity_history_rate_24h"],
    "load_jump": ["load_jump_flag", "load_jump_roll_count_3h"],
}


def build_exp103_graph_cache(
    cache: EVCSTensorCache,
    baseline_ids: list[str],
    top_k: int,
    seed: int = 42,
    dtw_max_points: int | None = None,
    rho: float = 0.0,
    lambda_event: float = 0.3,
    dtw_cache_path: str | Path | None = None,
    verbose: bool = False,
) -> dict[str, SparseGraphCache]:
    """根据 baseline 列表构造 EXP-103 所需图缓存。

    该函数是 baseline 身份的总入口：训练脚本传入配置中的 baseline id，
    这里负责映射到真实图结构。为了保证对照公平，所有图共享 `top_k` 和节点顺序；
    只有边权来源不同。
    """

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
    historical_graph: SparseGraphCache | None = None
    rng = np.random.default_rng(seed)
    graphs: dict[str, SparseGraphCache] = {}
    for baseline_id in baseline_ids:
        if baseline_id == "event_graph_dynamic":
            # 主事件图：按每个预测起点的近期事件特征相似度动态选邻居。
            graphs[baseline_id] = event_graph
        elif baseline_id == "event_graph_dynamic_rho":
            # 平滑事件图：检验动态事件图是否受单个时间片噪声影响过大。
            graphs[baseline_id] = smoothed_event_graph
        elif baseline_id == "event_graph_multichannel":
            graphs[baseline_id] = _dynamic_multichannel_event_graph(cache, top_k)
        elif baseline_id == "dtw_demand_graph":
            # 强传统图 baseline：只看历史负载形状相似，不使用事件特征。
            dtw_graph = dtw_graph or _dtw_graph(cache, top_k, train_end, dtw_max_points, dtw_cache_path, verbose)
            graphs[baseline_id] = dtw_graph
        elif baseline_id == "historical_correlation_graph":
            # 另一个强 baseline：训练期负载相关性图，不能用测试期负载。
            historical_graph = historical_graph or _historical_correlation_graph(cache, top_k, train_end)
            graphs[baseline_id] = historical_graph
        elif baseline_id == "historical_event_dual_graph":
            # 双分支候选：事件图和历史相关图同时输入模型，用于证明事件结构可补充稳态相关结构。
            historical_graph = historical_graph or _historical_correlation_graph(cache, top_k, train_end)
            graphs[baseline_id] = SparseGraphCache(
                baseline_id,
                event_graph.indices.copy(),
                event_graph.weights.copy(),
                cache.nodes,
                dynamic=True,
                train_origin_end=train_end,
                top_k=top_k,
                historical_indices=historical_graph.indices.copy(),
                historical_weights=historical_graph.weights.copy(),
            )
        elif baseline_id == "historical_event_residual_graph":
            historical_graph = historical_graph or _historical_correlation_graph(cache, top_k, train_end)
            graphs[baseline_id] = SparseGraphCache(
                baseline_id,
                event_graph.indices.copy(),
                event_graph.weights.copy(),
                cache.nodes,
                dynamic=True,
                train_origin_end=train_end,
                top_k=top_k,
                historical_indices=historical_graph.indices.copy(),
                historical_weights=historical_graph.weights.copy(),
            )
        elif baseline_id == "event_dtw_fusion_graph":
            # 事件图与 DTW 图线性融合，作为“结构融合是否更稳”的候选模型。
            dtw_graph = dtw_graph or _dtw_graph(cache, top_k, train_end, dtw_max_points, dtw_cache_path, verbose)
            graphs[baseline_id] = _fusion_graph(cache, smoothed_event_graph, dtw_graph, top_k, lambda_event, train_end)
        elif baseline_id == "random_event_graph":
            # 随机图对照：验证收益不是来自“任意邻居聚合”。
            graphs[baseline_id] = _random_like_event(cache, event_graph, rng)
        elif baseline_id == "shuffled_event_graph":
            # 时间打乱对照：保留事件图边权分布，但破坏事件发生时序。
            graphs[baseline_id] = _shuffled_like_event(cache, event_graph, rng)
        elif baseline_id == "semantic_shuffled_event_graph":
            # 语义打乱对照：按事件族内部打乱特征，检验事件语义是否真的有用。
            graphs[baseline_id] = _semantic_shuffled_event_graph(cache, top_k, rng)
        elif baseline_id == "semantic_shuffled_event_residual_graph":
            historical_graph = historical_graph or _historical_correlation_graph(cache, top_k, train_end)
            semantic_graph = _semantic_shuffled_event_graph(cache, top_k, rng)
            graphs[baseline_id] = SparseGraphCache(
                baseline_id,
                semantic_graph.indices.copy(),
                semantic_graph.weights.copy(),
                cache.nodes,
                dynamic=True,
                train_origin_end=train_end,
                top_k=top_k,
                historical_indices=historical_graph.indices.copy(),
                historical_weights=historical_graph.weights.copy(),
            )
        elif baseline_id == "deleted_event_graph":
            # 删除图对照：保留接口和训练预算，但把边权置零，隔离图结构贡献。
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
            # 非图 baseline 仍返回空图缓存，让 Dataset 和 Model 接口保持一致。
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


def _historical_correlation_graph(cache: EVCSTensorCache, top_k: int, train_end: int) -> SparseGraphCache:
    """用训练期负载相关性构造静态图，负相关会被裁剪为 0。"""

    values = cache.load[: train_end + 1].T
    similarity = _safe_positive_correlation(values)
    similarity = np.clip(similarity, 0.0, None)
    np.fill_diagonal(similarity, 0.0)
    return _static_graph("historical_correlation_graph", cache, similarity, top_k, train_end)


def _dtw_graph(
    cache: EVCSTensorCache,
    top_k: int,
    train_end: int,
    dtw_max_points: int | None,
    dtw_cache_path: str | Path | None,
    verbose: bool,
) -> SparseGraphCache:
    """构造或读取 DTW 需求相似图。

    DTW 计算昂贵，所以正式 run 会按 metadata 缓存。metadata 包含节点、top_k、train_end
    和负载指纹，避免不同实验误读旧缓存。
    """

    metadata = _dtw_metadata(cache, top_k, train_end, dtw_max_points)
    if dtw_cache_path:
        cached = _load_cached_dtw_graph(Path(dtw_cache_path), metadata, cache)
        if cached is not None:
            if verbose:
                print(f"loaded cached DTW graph: {dtw_cache_path}", flush=True)
            return cached
    if verbose:
        print(
            "building DTW graph: "
            f"nodes={len(cache.nodes)} train_end={train_end} dtw_max_points={dtw_max_points or 'full'}",
            flush=True,
        )
    similarity = _dtw_similarity(_prepare_static_load(cache.load[: train_end + 1], dtw_max_points), verbose=verbose)
    graph = _static_graph("dtw_demand_graph", cache, similarity, top_k, train_end)
    if dtw_cache_path:
        _save_cached_dtw_graph(Path(dtw_cache_path), graph, metadata)
        if verbose:
            print(f"saved DTW graph cache: {dtw_cache_path}", flush=True)
    return graph


def _dynamic_event_graph(
    cache: EVCSTensorCache,
    top_k: int,
    event_features: np.ndarray | None = None,
    baseline_id: str = "event_graph_dynamic",
) -> SparseGraphCache:
    """构造预测起点相关的事件动态图。

    每个 origin 只聚合 `[origin-history+1, origin]` 的事件特征均值，再对节点做 z-score
    和余弦相似度。这样 A_event,t 随时间变化，但不会使用预测 horizon 内的信息。
    """

    features_source = event_features if event_features is not None else cache.event_features
    origin_count = len(cache.origin_indices)
    node_count = len(cache.nodes)
    indices = np.zeros((origin_count, node_count, top_k), dtype=np.int32)
    weights = np.zeros((origin_count, node_count, top_k), dtype=np.float32)
    for origin_pos, origin in enumerate(cache.origin_indices):
        start = max(0, origin - cache.history_steps + 1)
        features = features_source[start : origin + 1].mean(axis=0)
        similarity = _cosine_similarity(_zscore(features))
        np.fill_diagonal(similarity, 0.0)
        row_indices, row_weights = _topk_sparse(similarity, top_k)
        indices[origin_pos] = row_indices
        weights[origin_pos] = row_weights
    return SparseGraphCache(
        baseline_id=baseline_id,
        indices=indices,
        weights=weights,
        nodes=cache.nodes,
        dynamic=True,
        train_origin_end=None,
        top_k=top_k,
    )


def _dynamic_multichannel_event_graph(cache: EVCSTensorCache, top_k: int) -> SparseGraphCache:
    """按事件语义族分别建图，并保存多通道稀疏邻接。"""

    origin_count = len(cache.origin_indices)
    node_count = len(cache.nodes)
    feature_names = list(cache.event_feature_names)
    channel_names = list(DEFAULT_EVENT_CHANNELS)
    channel_feature_names: dict[str, list[str]] = {}
    channel_indices = np.zeros((origin_count, len(channel_names), node_count, top_k), dtype=np.int32)
    channel_weights = np.zeros((origin_count, len(channel_names), node_count, top_k), dtype=np.float32)
    dense_sum = np.zeros((origin_count, node_count, node_count), dtype=np.float32)
    for channel_pos, channel_name in enumerate(channel_names):
        selected = [name for name in DEFAULT_EVENT_CHANNELS[channel_name] if name in feature_names]
        if not selected:
            selected = [name for name in DEFAULT_EVENT_CHANNELS[channel_name][:1] if name in feature_names] or feature_names[:1]
        channel_feature_names[channel_name] = selected
        selected_indices = [feature_names.index(name) for name in selected]
        for origin_pos, origin in enumerate(cache.origin_indices):
            start = max(0, origin - cache.history_steps + 1)
            features = cache.event_features[start : origin + 1, :, selected_indices].mean(axis=0)
            similarity = _cosine_similarity(_zscore(features))
            np.fill_diagonal(similarity, 0.0)
            row_indices, row_weights = _topk_sparse(similarity, top_k)
            channel_indices[origin_pos, channel_pos] = row_indices
            channel_weights[origin_pos, channel_pos] = row_weights
            dense_sum[origin_pos] += _sparse_origin_to_dense(row_indices, row_weights, node_count)
    combined = np.asarray([_row_normalize_dense(matrix) for matrix in dense_sum], dtype=np.float32)
    combined_graph = _dynamic_dense_graph("event_graph_multichannel", cache, combined, top_k, train_origin_end=None)
    return SparseGraphCache(
        "event_graph_multichannel",
        combined_graph.indices,
        combined_graph.weights,
        cache.nodes,
        dynamic=True,
        train_origin_end=None,
        top_k=top_k,
        channel_indices=channel_indices,
        channel_weights=channel_weights,
        channel_names=channel_names,
        channel_feature_names=channel_feature_names,
    )


def _smooth_dynamic_event_graph(cache: EVCSTensorCache, event_graph: SparseGraphCache, top_k: int, rho: float) -> SparseGraphCache:
    """对动态图做一阶时间平滑，rho 越大越依赖上一时刻图。"""

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
    """融合事件图和 DTW 图。

    `lambda_event` 控制事件图占比；融合后重新 row-normalize 并截取 top-k，
    因此输出仍满足模型的稀疏图接口。
    """

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
    """把静态相似度矩阵转成每个 origin 复用的 top-k 稀疏图。"""

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
    """把 dense dynamic adjacency 转成统一的 top-k 稀疏缓存。"""

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
    """生成随机邻居图，保持 top-k 预算但不保留事件语义。"""

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
    """打乱 origin 顺序，保留边权分布但破坏时间对应关系。"""

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


def _semantic_shuffled_event_graph(cache: EVCSTensorCache, top_k: int, rng: np.random.Generator) -> SparseGraphCache:
    """在事件族内部打乱特征行，破坏事件语义和节点-时间对应关系。"""

    shuffled = cache.event_features.copy()
    feature_names = list(cache.event_feature_names)
    for channel_features in DEFAULT_EVENT_CHANNELS.values():
        selected = [feature_names.index(name) for name in channel_features if name in feature_names]
        if not selected:
            continue
        values = shuffled[:, :, selected].reshape(-1, len(selected)).copy()
        order = np.arange(values.shape[0])
        rng.shuffle(order)
        shuffled[:, :, selected] = values[order].reshape(shuffled.shape[0], shuffled.shape[1], len(selected))
    return _dynamic_event_graph(cache, top_k, event_features=shuffled, baseline_id="semantic_shuffled_event_graph")


def _prepare_static_load(load: np.ndarray, max_points: int | None) -> np.ndarray:
    values = load
    if max_points and len(values) > max_points:
        indices = np.linspace(0, len(values) - 1, num=max_points, dtype=int)
        values = values[sorted(set(indices))]
    return values.T


def _dtw_similarity(values: np.ndarray, verbose: bool = False) -> np.ndarray:
    """计算所有节点两两 DTW 相似度，返回越大越相似的权重矩阵。"""

    count = values.shape[0]
    similarity = np.zeros((count, count), dtype=np.float32)
    total_pairs = count * (count - 1) // 2
    completed_pairs = 0
    progress_interval = max(1, total_pairs // 20)
    for left in range(count):
        for right in range(left + 1, count):
            distance = _dtw_distance(values[left], values[right])
            weight = 1.0 / (1.0 + distance)
            similarity[left, right] = weight
            similarity[right, left] = weight
            completed_pairs += 1
            if verbose and (completed_pairs == 1 or completed_pairs == total_pairs or completed_pairs % progress_interval == 0):
                percent = completed_pairs / max(1, total_pairs) * 100.0
                print(f"building DTW graph: pair {completed_pairs}/{total_pairs} ({percent:.1f}%)", flush=True)
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
    """将 dense 相似度矩阵转成每行 top-k 邻居及归一化权重。"""

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


def _dtw_metadata(cache: EVCSTensorCache, top_k: int, train_end: int, dtw_max_points: int | None) -> dict[str, Any]:
    train_load = cache.load[: train_end + 1]
    return {
        "baseline_id": "dtw_demand_graph",
        "node_count": len(cache.nodes),
        "nodes": cache.nodes,
        "origin_count": len(cache.origin_indices),
        "top_k": int(top_k),
        "train_end": int(train_end),
        "dtw_max_points": int(dtw_max_points) if dtw_max_points is not None else None,
        "load_shape": list(cache.load.shape),
        "train_load_fingerprint": {
            "sum": float(train_load.sum()),
            "mean": float(train_load.mean()) if train_load.size else 0.0,
            "std": float(train_load.std()) if train_load.size else 0.0,
        },
    }


def _load_cached_dtw_graph(path: Path, expected_metadata: dict[str, Any], cache: EVCSTensorCache) -> SparseGraphCache | None:
    if not path.exists():
        return None
    try:
        payload = np.load(path, allow_pickle=False)
        metadata = json.loads(str(payload["metadata"].item()))
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        return None
    if metadata != expected_metadata:
        return None
    return SparseGraphCache(
        baseline_id="dtw_demand_graph",
        indices=payload["indices"].astype(np.int32),
        weights=payload["weights"].astype(np.float32),
        nodes=cache.nodes,
        dynamic=False,
        train_origin_end=int(metadata["train_end"]),
        top_k=int(metadata["top_k"]),
    )


def _save_cached_dtw_graph(path: Path, graph: SparseGraphCache, metadata: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        indices=graph.indices.astype(np.int32),
        weights=graph.weights.astype(np.float32),
        metadata=np.asarray(json.dumps(metadata, ensure_ascii=False, sort_keys=True)),
    )
