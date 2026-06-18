#!/usr/bin/env python3
from __future__ import annotations

"""基于 EXP-103 V5 Plus full predictions 做 validation-only stacking 和 seed ensemble。

防泄漏原则：

1. stacking 权重只从 validation split 学习。
2. test split 只用固定权重评估一次。
3. seed ensemble 只做同一 baseline 跨 seed 的简单平均，不根据 test 学 seed 权重。

因此，本脚本输出的是“已固定预测文件上的后处理评估”，不是新的训练流程。
"""

import argparse
import csv
import gzip
import itertools
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_MEMBERS = [
    "event_graph_dynamic_v5",
    "event_dtw_fusion_graph_v5",
    "historical_event_dual_graph_v5",
    "historical_correlation_graph_v5",
]
DEFAULT_SEED_ENSEMBLES = ["event_graph_dynamic_v5", "event_dtw_fusion_graph_v5"]
KEY_COLUMNS = ["seed", "split", "origin_index", "timestamp", "node_id", "horizon_step"]
SEED_ENSEMBLE_KEYS = ["split", "origin_index", "timestamp", "node_id", "horizon_step"]
READ_COLUMNS = [
    "seed",
    "split",
    "origin_index",
    "timestamp",
    "node_id",
    "horizon_step",
    "target",
    "prediction",
    "event_window_any",
    "event_window_access",
    "event_window_departure",
    "event_window_load_jump",
]
OUTPUT_COLUMNS = [
    "baseline_id",
    "seed",
    "split",
    "origin_index",
    "timestamp",
    "node_id",
    "horizon_step",
    "target",
    "prediction",
    "abs_error",
    "squared_error",
    "event_window_any",
    "event_window_access",
    "event_window_departure",
    "event_window_load_jump",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Stack EXP-103 V5 Plus full prediction files without test leakage.")
    parser.add_argument("--runs", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--members", default=",".join(DEFAULT_MEMBERS))
    parser.add_argument("--seed-ensemble-baselines", default=",".join(DEFAULT_SEED_ENSEMBLES))
    parser.add_argument("--grid-step", type=float, default=0.05)
    args = parser.parse_args()

    run_dirs = [Path(path) for path in args.runs]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    members = [value.strip() for value in args.members.split(",") if value.strip()]
    seed_baselines = [value.strip() for value in args.seed_ensemble_baselines.split(",") if value.strip()]

    validation = _aligned_member_frame(run_dirs, members, split="validation")
    test = _aligned_member_frame(run_dirs, members, split="test")
    weights = _learn_convex_weights(validation, members, args.grid_step)
    stacked_test = _apply_stack(test, members, weights)
    _write_prediction_rows(out_dir / "stacking_test_predictions.csv.gz", "v5_plus_validation_stack", stacked_test)
    _write_csv(out_dir / "stacking_weights.csv", [{"baseline_id": member, "weight": weights[index]} for index, member in enumerate(members)])
    _write_csv(out_dir / "stacking_metrics.csv", [_metric_row("v5_plus_validation_stack", stacked_test, extra={"member_count": len(members), "grid_step": args.grid_step})])

    seed_metric_rows = []
    seed_prediction_frames = []
    for baseline_id in seed_baselines:
        ensemble = _seed_ensemble_frame(run_dirs, baseline_id, split="test")
        ensemble_id = f"{baseline_id}_seed_ensemble"
        seed_metric_rows.append(_metric_row(ensemble_id, ensemble, extra={"seed_count": int(ensemble["seed_count"].max()) if len(ensemble) else 0}))
        seed_prediction_frames.append((ensemble_id, ensemble))
    _write_csv(out_dir / "seed_ensemble_metrics.csv", seed_metric_rows)
    _write_seed_ensemble_predictions(out_dir / "seed_ensemble_predictions.csv.gz", seed_prediction_frames)
    print(f"wrote V5 Plus stacking outputs to {out_dir}")


def _aligned_member_frame(run_dirs: list[Path], members: list[str], split: str) -> pd.DataFrame:
    base = None
    for member in members:
        frame = _load_predictions(run_dirs, member, split)
        rename = {
            "target": f"target_{member}",
            "prediction": f"prediction_{member}",
            "event_window_any": f"event_window_any_{member}",
            "event_window_access": f"event_window_access_{member}",
            "event_window_departure": f"event_window_departure_{member}",
            "event_window_load_jump": f"event_window_load_jump_{member}",
        }
        frame = frame.rename(columns=rename)
        if base is None:
            base = frame
        else:
            base = base.merge(frame, on=KEY_COLUMNS, how="inner")
    if base is None or base.empty:
        raise SystemExit(f"no aligned full predictions for split={split} members={members}")
    target_columns = [f"target_{member}" for member in members]
    base["target"] = base[target_columns[0]]
    return base


def _load_predictions(run_dirs: list[Path], baseline_id: str, split: str) -> pd.DataFrame:
    frames = []
    for run_dir in run_dirs:
        path = run_dir / "predictions_full" / f"{split}_{baseline_id}.csv.gz"
        if not path.exists():
            raise SystemExit(f"missing full prediction file for stacking: {path}")
        frame = pd.read_csv(path, usecols=READ_COLUMNS)
        if frame.empty:
            raise SystemExit(f"empty full prediction file for stacking: {path}")
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def _learn_convex_weights(frame: pd.DataFrame, members: list[str], step: float) -> np.ndarray:
    """在 validation 上搜索非负且和为 1 的权重。

    使用粗网格是为了避免引入 scipy 依赖；网格只看 validation，不接触 test。
    """

    prediction_matrix = np.column_stack([frame[f"prediction_{member}"].to_numpy(dtype=float) for member in members])
    target = frame["target"].to_numpy(dtype=float)
    best_weights = None
    best_mae = float("inf")
    for weights in _simplex_grid(len(members), step):
        prediction = prediction_matrix @ weights
        mae = float(np.mean(np.abs(prediction - target)))
        if mae < best_mae:
            best_mae = mae
            best_weights = weights
    assert best_weights is not None
    return best_weights


def _simplex_grid(size: int, step: float) -> list[np.ndarray]:
    units = int(round(1.0 / step))
    weights = []
    for parts in itertools.product(range(units + 1), repeat=size):
        if sum(parts) != units:
            continue
        weights.append(np.asarray(parts, dtype=float) / float(units))
    return weights


def _apply_stack(frame: pd.DataFrame, members: list[str], weights: np.ndarray) -> pd.DataFrame:
    result = frame[KEY_COLUMNS + ["target"]].copy()
    prediction_matrix = np.column_stack([frame[f"prediction_{member}"].to_numpy(dtype=float) for member in members])
    result["prediction"] = prediction_matrix @ weights
    first_member = members[0]
    for column in ("event_window_any", "event_window_access", "event_window_departure", "event_window_load_jump"):
        result[column] = frame[f"{column}_{first_member}"]
    return result


def _seed_ensemble_frame(run_dirs: list[Path], baseline_id: str, split: str) -> pd.DataFrame:
    frame = _load_predictions(run_dirs, baseline_id, split)
    grouped = (
        frame.groupby(SEED_ENSEMBLE_KEYS, dropna=False)
        .agg(
            target=("target", "first"),
            prediction=("prediction", "mean"),
            event_window_any=("event_window_any", "max"),
            event_window_access=("event_window_access", "max"),
            event_window_departure=("event_window_departure", "max"),
            event_window_load_jump=("event_window_load_jump", "max"),
            seed_count=("seed", "nunique"),
        )
        .reset_index()
    )
    grouped.insert(0, "seed", -1)
    return grouped


def _metric_row(baseline_id: str, frame: pd.DataFrame, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    error = frame["prediction"].to_numpy(dtype=float) - frame["target"].to_numpy(dtype=float)
    row = {
        "baseline_id": baseline_id,
        "MAE": float(np.mean(np.abs(error))) if error.size else np.nan,
        "RMSE": float(np.sqrt(np.mean(error**2))) if error.size else np.nan,
        "prediction_count": int(error.size),
    }
    row.update(extra or {})
    return row


def _write_prediction_rows(path: Path, baseline_id: str, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in frame.itertuples(index=False):
            error = float(row.prediction) - float(row.target)
            writer.writerow(
                {
                    "baseline_id": baseline_id,
                    "seed": int(row.seed),
                    "split": row.split,
                    "origin_index": int(row.origin_index),
                    "timestamp": row.timestamp,
                    "node_id": row.node_id,
                    "horizon_step": int(row.horizon_step),
                    "target": float(row.target),
                    "prediction": float(row.prediction),
                    "abs_error": abs(error),
                    "squared_error": error * error,
                    "event_window_any": int(row.event_window_any),
                    "event_window_access": int(row.event_window_access),
                    "event_window_departure": int(row.event_window_departure),
                    "event_window_load_jump": int(row.event_window_load_jump),
                }
            )


def _write_seed_ensemble_predictions(path: Path, frames: list[tuple[str, pd.DataFrame]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for baseline_id, frame in frames:
            for row in frame.itertuples(index=False):
                error = float(row.prediction) - float(row.target)
                writer.writerow(
                    {
                        "baseline_id": baseline_id,
                        "seed": -1,
                        "split": row.split,
                        "origin_index": int(row.origin_index),
                        "timestamp": row.timestamp,
                        "node_id": row.node_id,
                        "horizon_step": int(row.horizon_step),
                        "target": float(row.target),
                        "prediction": float(row.prediction),
                        "abs_error": abs(error),
                        "squared_error": error * error,
                        "event_window_any": int(row.event_window_any),
                        "event_window_access": int(row.event_window_access),
                        "event_window_departure": int(row.event_window_departure),
                        "event_window_load_jump": int(row.event_window_load_jump),
                    }
                )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
