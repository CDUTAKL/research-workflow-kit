from __future__ import annotations

from typing import Any

import numpy as np

from evcs.data.tensor_cache import EVCSTensorCache


def event_window_masks(cache: EVCSTensorCache, origins: list[int] | np.ndarray) -> dict[str, np.ndarray]:
    origin_array = np.asarray(origins, dtype=int)
    current_events = cache.event_features[origin_array] if len(origin_array) else np.zeros((0, len(cache.nodes), 0))
    feature_names = list(cache.event_feature_names)
    masks: dict[str, np.ndarray] = {}
    for name in ("access_count", "departure_count", "load_jump_flag"):
        if name in feature_names:
            masks[name] = current_events[:, :, feature_names.index(name)] > 0
    for name in ("active_count", "occupancy_rate"):
        if name in feature_names:
            index = feature_names.index(name)
            train_origins = cache.split_indices.get("train", [])
            train_values = cache.event_features[train_origins, :, index] if train_origins else cache.event_features[:, :, index]
            threshold = float(np.quantile(train_values, 0.9)) if train_values.size else float("inf")
            masks[f"{name}_high"] = current_events[:, :, index] >= threshold
    train_origins = cache.split_indices.get("train", [])
    train_load = cache.load[train_origins] if train_origins else cache.load
    threshold = np.quantile(train_load, 0.9, axis=0) if train_load.size else np.zeros((len(cache.nodes),), dtype=np.float32)
    masks["near_capacity_proxy"] = cache.load[origin_array] >= threshold if len(origin_array) else np.zeros((0, len(cache.nodes)), dtype=bool)
    return masks


def build_event_loss_weights(cache: EVCSTensorCache, origins: list[int] | np.ndarray, config: dict[str, Any] | None) -> np.ndarray:
    origin_array = np.asarray(origins, dtype=int)
    base = float((config or {}).get("base_weight", 1.0))
    weights = np.full((len(origin_array), len(cache.nodes)), base, dtype=np.float32)
    if not config or not bool(config.get("enabled", False)):
        return np.repeat(weights[:, np.newaxis, :], cache.horizon_steps, axis=1)
    max_weight = float(config.get("max_weight", base))
    window_weights = config.get("windows", {}) if isinstance(config.get("windows", {}), dict) else {}
    # 训练权重只来自预测时刻已经可见的事件状态；它不是模型输入，只改变优化重点。
    for window_name, mask in event_window_masks(cache, origin_array).items():
        if window_name not in window_weights:
            continue
        weights = np.maximum(weights, np.where(mask, float(window_weights[window_name]), base).astype(np.float32))
    weights = np.clip(weights, 0.0, max_weight)
    return np.repeat(weights[:, np.newaxis, :], cache.horizon_steps, axis=1).astype(np.float32)
