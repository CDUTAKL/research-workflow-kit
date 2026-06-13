from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class EVCSTensorCache:
    load: np.ndarray
    event_features: np.ndarray
    timestamps: list[str]
    nodes: list[str]
    event_feature_names: list[str]
    origin_indices: list[int]
    split_indices: dict[str, list[int]]
    history_steps: int
    horizon_steps: int
    normalization: dict[str, Any]
    manifest: dict[str, Any]


def build_tensor_cache(
    frame: pd.DataFrame,
    timestamp_field: str,
    node_field: str,
    target_field: str,
    event_feature_fields: list[str],
    history_steps: int,
    horizon_steps: int,
    split_rule: dict[str, float] | None = None,
    include_time_context: bool = False,
    include_enhanced_events: bool = False,
    near_capacity_quantile: float = 0.9,
) -> EVCSTensorCache:
    if history_steps < 1:
        raise ValueError("history_steps must be >= 1")
    if horizon_steps < 1:
        raise ValueError("horizon_steps must be >= 1")
    required = [timestamp_field, node_field, target_field, *event_feature_fields]
    missing = [field for field in required if field not in frame.columns]
    if missing:
        raise ValueError(f"missing tensor cache fields: {missing}")

    data = frame[required].copy()
    data[timestamp_field] = pd.to_datetime(data[timestamp_field], errors="coerce")
    data[node_field] = data[node_field].astype(str)
    data[target_field] = pd.to_numeric(data[target_field], errors="coerce").fillna(0.0)
    for field in event_feature_fields:
        data[field] = pd.to_numeric(data[field], errors="coerce").fillna(0.0)
    data = data.dropna(subset=[timestamp_field, node_field]).sort_values([timestamp_field, node_field])

    load_pivot = data.pivot_table(index=timestamp_field, columns=node_field, values=target_field, aggfunc="mean")
    load_pivot = load_pivot.sort_index().fillna(0.0)
    timestamps = [pd.Timestamp(value).isoformat() for value in load_pivot.index]
    timestamp_index = pd.DatetimeIndex(load_pivot.index)
    nodes = [str(node) for node in load_pivot.columns.tolist()]
    load = load_pivot.to_numpy(dtype=np.float32)

    event_arrays = []
    for field in event_feature_fields:
        pivot = data.pivot_table(index=timestamp_field, columns=node_field, values=field, aggfunc="mean")
        pivot = pivot.reindex(index=load_pivot.index, columns=load_pivot.columns).fillna(0.0)
        event_arrays.append(pivot.to_numpy(dtype=np.float32))
    feature_names = list(event_feature_fields)
    event_features = (
        np.stack(event_arrays, axis=-1).astype(np.float32)
        if event_arrays
        else np.zeros((len(timestamps), len(nodes), 0), dtype=np.float32)
    )

    origin_indices = list(range(history_steps - 1, max(history_steps - 1, len(timestamps) - horizon_steps)))
    split_indices = _chronological_split(origin_indices, split_rule or {"train": 0.7, "validation": 0.15, "test": 0.15})
    derived_names: list[str] = []
    if include_time_context:
        time_context, names = _time_context_features(timestamp_index, len(nodes))
        event_features = _append_event_features(event_features, time_context)
        feature_names.extend(names)
        derived_names.extend(names)
    if include_enhanced_events:
        enhanced, names = _enhanced_event_features(
            load,
            event_features,
            feature_names,
            split_indices,
            near_capacity_quantile=near_capacity_quantile,
        )
        event_features = _append_event_features(event_features, enhanced)
        feature_names.extend(names)
        derived_names.extend(names)
    normalization = _train_only_normalization(load, event_features, split_indices)
    manifest = {
        "row_count": int(len(data)),
        "time_count": int(len(timestamps)),
        "node_count": int(len(nodes)),
        "event_feature_count": int(len(feature_names)),
        "history_steps": int(history_steps),
        "horizon_steps": int(horizon_steps),
        "target_mode": "multi_step",
        "split": "chronological_70_15_15",
        "normalization": "train_only",
        "origin_count": int(len(origin_indices)),
        "split_counts": {name: len(values) for name, values in split_indices.items()},
        "event_feature_names": feature_names,
        "feature_engineering": {
            "include_time_context": bool(include_time_context),
            "include_enhanced_events": bool(include_enhanced_events),
            "derived_feature_names": derived_names,
            "near_capacity_quantile": float(near_capacity_quantile),
            "near_capacity_threshold_source": "train_only" if include_enhanced_events else "not_applicable",
        },
    }
    return EVCSTensorCache(
        load=load,
        event_features=event_features,
        timestamps=timestamps,
        nodes=nodes,
        event_feature_names=feature_names,
        origin_indices=origin_indices,
        split_indices=split_indices,
        history_steps=history_steps,
        horizon_steps=horizon_steps,
        normalization=normalization,
        manifest=manifest,
    )


def save_tensor_cache(
    cache: EVCSTensorCache,
    npz_path: str | Path,
    split_path: str | Path,
    manifest_path: str | Path,
) -> None:
    npz_target = Path(npz_path)
    split_target = Path(split_path)
    manifest_target = Path(manifest_path)
    npz_target.parent.mkdir(parents=True, exist_ok=True)
    split_target.parent.mkdir(parents=True, exist_ok=True)
    manifest_target.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        npz_target,
        load=cache.load,
        event_features=cache.event_features,
        timestamps=np.asarray(cache.timestamps),
        nodes=np.asarray(cache.nodes),
        event_feature_names=np.asarray(cache.event_feature_names),
        origin_indices=np.asarray(cache.origin_indices, dtype=np.int32),
        train_origins=np.asarray(cache.split_indices["train"], dtype=np.int32),
        validation_origins=np.asarray(cache.split_indices["validation"], dtype=np.int32),
        test_origins=np.asarray(cache.split_indices["test"], dtype=np.int32),
        load_mean=np.asarray(cache.normalization["load_mean"], dtype=np.float32),
        load_std=np.asarray(cache.normalization["load_std"], dtype=np.float32),
        event_mean=np.asarray(cache.normalization["event_mean"], dtype=np.float32),
        event_std=np.asarray(cache.normalization["event_std"], dtype=np.float32),
    )
    split_target.write_text(json.dumps(cache.split_indices, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_target.write_text(json.dumps(cache.manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_tensor_cache(npz_path: str | Path, manifest_path: str | Path | None = None) -> EVCSTensorCache:
    payload = np.load(Path(npz_path), allow_pickle=False)
    split_indices = {
        "train": payload["train_origins"].astype(int).tolist(),
        "validation": payload["validation_origins"].astype(int).tolist(),
        "test": payload["test_origins"].astype(int).tolist(),
    }
    manifest = {}
    if manifest_path and Path(manifest_path).exists():
        manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    return EVCSTensorCache(
        load=payload["load"].astype(np.float32),
        event_features=payload["event_features"].astype(np.float32),
        timestamps=[str(value) for value in payload["timestamps"].tolist()],
        nodes=[str(value) for value in payload["nodes"].tolist()],
        event_feature_names=[str(value) for value in payload["event_feature_names"].tolist()],
        origin_indices=payload["origin_indices"].astype(int).tolist(),
        split_indices=split_indices,
        history_steps=int(manifest.get("history_steps", 1)),
        horizon_steps=int(manifest.get("horizon_steps", 1)),
        normalization={
            "load_mean": payload["load_mean"].astype(np.float32),
            "load_std": payload["load_std"].astype(np.float32),
            "event_mean": payload["event_mean"].astype(np.float32),
            "event_std": payload["event_std"].astype(np.float32),
        },
        manifest=manifest,
    )


def _chronological_split(origin_indices: list[int], split_rule: dict[str, float]) -> dict[str, list[int]]:
    total = len(origin_indices)
    train_count = int(total * float(split_rule.get("train", 0.7)))
    validation_count = int(total * float(split_rule.get("validation", 0.15)))
    if total >= 3:
        train_count = max(1, train_count)
        validation_count = max(1, validation_count)
    train_end = min(train_count, total)
    validation_end = min(train_end + validation_count, total)
    return {
        "train": origin_indices[:train_end],
        "validation": origin_indices[train_end:validation_end],
        "test": origin_indices[validation_end:],
    }


def _append_event_features(event_features: np.ndarray, additions: np.ndarray) -> np.ndarray:
    if additions.shape[-1] == 0:
        return event_features
    if event_features.shape[-1] == 0:
        return additions.astype(np.float32)
    return np.concatenate([event_features, additions.astype(np.float32)], axis=-1)


def _time_context_features(timestamps: pd.DatetimeIndex, node_count: int) -> tuple[np.ndarray, list[str]]:
    hour = timestamps.hour.to_numpy(dtype=np.float32) + timestamps.minute.to_numpy(dtype=np.float32) / 60.0
    dow = timestamps.dayofweek.to_numpy(dtype=np.float32)
    month = timestamps.month.to_numpy(dtype=np.float32)
    base = np.stack(
        [
            np.sin(2.0 * np.pi * hour / 24.0),
            np.cos(2.0 * np.pi * hour / 24.0),
            np.sin(2.0 * np.pi * dow / 7.0),
            np.cos(2.0 * np.pi * dow / 7.0),
            (dow >= 5).astype(np.float32),
            np.sin(2.0 * np.pi * (month - 1.0) / 12.0),
            np.cos(2.0 * np.pi * (month - 1.0) / 12.0),
        ],
        axis=-1,
    ).astype(np.float32)
    repeated = np.repeat(base[:, np.newaxis, :], node_count, axis=1)
    return repeated, ["hour_sin", "hour_cos", "dow_sin", "dow_cos", "weekend_flag", "month_sin", "month_cos"]


def _enhanced_event_features(
    load: np.ndarray,
    event_features: np.ndarray,
    feature_names: list[str],
    split_indices: dict[str, list[int]],
    near_capacity_quantile: float,
) -> tuple[np.ndarray, list[str]]:
    def get_feature(name: str) -> np.ndarray:
        if name not in feature_names:
            return np.zeros_like(load, dtype=np.float32)
        return event_features[:, :, feature_names.index(name)].astype(np.float32)

    access = get_feature("access_count")
    departure = get_feature("departure_count")
    active = get_feature("active_count")
    occupancy = get_feature("occupancy_rate")
    load_jump = get_feature("load_jump_flag")
    active_diff = np.zeros_like(active, dtype=np.float32)
    active_diff[1:] = active[1:] - active[:-1]
    train_origins = split_indices.get("train", [])
    train_end = max(train_origins) if train_origins else max(0, len(load) - 1)
    threshold = np.quantile(load[: train_end + 1], near_capacity_quantile, axis=0) if len(load) else np.zeros((load.shape[1],))
    near_capacity = (load >= threshold).astype(np.float32)
    # 这些派生事件只使用当前及历史切片，是为了增强事件向量表达力，同时维持因果可用性。
    arrays = [
        _rolling_sum(access, 4),
        _rolling_sum(departure, 4),
        active_diff,
        _rolling_max(occupancy, 12),
        _rolling_sum(load_jump, 12),
        _rolling_mean(near_capacity, 96),
    ]
    names = [
        "access_count_roll_1h",
        "departure_count_roll_1h",
        "active_count_diff",
        "occupancy_rate_roll_max_3h",
        "load_jump_roll_count_3h",
        "near_capacity_history_rate_24h",
    ]
    return np.stack(arrays, axis=-1).astype(np.float32), names


def _rolling_sum(values: np.ndarray, window: int) -> np.ndarray:
    return _rolling_reduce(values, window, "sum")


def _rolling_max(values: np.ndarray, window: int) -> np.ndarray:
    return _rolling_reduce(values, window, "max")


def _rolling_mean(values: np.ndarray, window: int) -> np.ndarray:
    return _rolling_reduce(values, window, "mean")


def _rolling_reduce(values: np.ndarray, window: int, method: str) -> np.ndarray:
    output = np.zeros_like(values, dtype=np.float32)
    for index in range(values.shape[0]):
        start = max(0, index - window + 1)
        current = values[start : index + 1]
        if method == "sum":
            output[index] = current.sum(axis=0)
        elif method == "max":
            output[index] = current.max(axis=0)
        elif method == "mean":
            output[index] = current.mean(axis=0)
        else:  # pragma: no cover - internal guard
            raise ValueError(f"unsupported rolling method: {method}")
    return output


def _train_only_normalization(
    load: np.ndarray,
    event_features: np.ndarray,
    split_indices: dict[str, list[int]],
) -> dict[str, Any]:
    train_origins = split_indices.get("train", [])
    train_end = max(train_origins) if train_origins else max(0, len(load) - 1)
    train_load = load[: train_end + 1]
    load_mean = np.asarray([float(train_load.mean())], dtype=np.float32)
    load_std = np.asarray([float(train_load.std())], dtype=np.float32)
    load_std[load_std == 0] = 1.0
    if event_features.shape[-1] == 0:
        event_mean = np.zeros((0,), dtype=np.float32)
        event_std = np.ones((0,), dtype=np.float32)
    else:
        train_events = event_features[: train_end + 1]
        event_mean = train_events.reshape(-1, train_events.shape[-1]).mean(axis=0).astype(np.float32)
        event_std = train_events.reshape(-1, train_events.shape[-1]).std(axis=0).astype(np.float32)
        event_std[event_std == 0] = 1.0
    return {
        "load_mean": load_mean,
        "load_std": load_std,
        "event_mean": event_mean,
        "event_std": event_std,
    }
