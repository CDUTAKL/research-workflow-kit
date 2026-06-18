#!/usr/bin/env python3
from __future__ import annotations

"""分析 EXP-103 V5 Plus 的全量 paired prediction evidence。

这个脚本只读取已经固定的 `predictions_full/test_*.csv.gz` 文件，不训练模型、
不改 checkpoint、也不根据 test 结果调参数。它的作用是把“平均 MAE 小胜”
转换为 paired delta、bootstrap CI 和 event/stable 分层表，从而支撑论文里的
稳健性判断。
"""

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


KEY_COLUMNS = ["seed", "split", "origin_index", "node_id", "horizon_step"]
PREDICTION_COLUMNS = [
    "seed",
    "split",
    "origin_index",
    "node_id",
    "horizon_step",
    "target",
    "prediction",
    "abs_error",
    "event_window_any",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze EXP-103 V5 Plus paired prediction evidence.")
    parser.add_argument("--runs", nargs="+", required=True, help="Run output directories containing predictions_full/*.csv.gz.")
    parser.add_argument("--out", required=True, help="Output directory for paired evidence summaries.")
    parser.add_argument("--primary", default="event_graph_dynamic_v5")
    parser.add_argument("--comparators", default="behavior_concat_v5,historical_correlation_graph_v5,event_dtw_fusion_graph_v5")
    parser.add_argument("--bootstrap-samples", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42, help="Random seed for bootstrap resampling.")
    args = parser.parse_args()

    run_dirs = [Path(path) for path in args.runs]
    comparators = [value.strip() for value in args.comparators.split(",") if value.strip()]
    baseline_ids = [args.primary, *comparators]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    paired_rows: list[dict[str, Any]] = []
    ci_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    for comparator in comparators:
        merged = _paired_frame(run_dirs, args.primary, comparator, split="test")
        delta = (merged["abs_error_primary"] - merged["abs_error_comparator"]).to_numpy(dtype=float)
        ci_rows.append(_bootstrap_row(args.primary, comparator, "global", delta, args.bootstrap_samples, rng))
        event_rows.extend(_event_stable_rows(args.primary, comparator, merged))
        for row in merged.itertuples(index=False):
            paired_rows.append(
                {
                    "primary_baseline": args.primary,
                    "comparator_baseline": comparator,
                    "seed": row.seed,
                    "split": row.split,
                    "origin_index": row.origin_index,
                    "node_id": row.node_id,
                    "horizon_step": row.horizon_step,
                    "target": row.target_primary,
                    "primary_prediction": row.prediction_primary,
                    "comparator_prediction": row.prediction_comparator,
                    "primary_abs_error": row.abs_error_primary,
                    "comparator_abs_error": row.abs_error_comparator,
                    "delta_abs_error": row.abs_error_primary - row.abs_error_comparator,
                    "event_window_any": row.event_window_any_primary,
                }
            )
        event_delta = merged.loc[merged["event_window_any_primary"].astype(bool), "abs_error_primary"] - merged.loc[
            merged["event_window_any_primary"].astype(bool), "abs_error_comparator"
        ]
        stable_delta = merged.loc[~merged["event_window_any_primary"].astype(bool), "abs_error_primary"] - merged.loc[
            ~merged["event_window_any_primary"].astype(bool), "abs_error_comparator"
        ]
        ci_rows.append(_bootstrap_row(args.primary, comparator, "event_window", event_delta.to_numpy(dtype=float), args.bootstrap_samples, rng))
        ci_rows.append(_bootstrap_row(args.primary, comparator, "stable_window", stable_delta.to_numpy(dtype=float), args.bootstrap_samples, rng))

    pd.DataFrame(paired_rows).to_csv(out_dir / "paired_deltas.csv", index=False)
    pd.DataFrame(ci_rows).to_csv(out_dir / "bootstrap_ci.csv", index=False)
    pd.DataFrame(event_rows).to_csv(out_dir / "event_window_delta_summary.csv", index=False)
    pd.DataFrame(_event_stable_primary_table(run_dirs, baseline_ids)).to_csv(out_dir / "event_stable_primary_table.csv", index=False)
    _write_decision_summary(out_dir / "v5_plus_decision_summary.md", args.primary, ci_rows, event_rows)
    print(f"wrote V5 Plus paired evidence analysis to {out_dir}")


def _paired_frame(run_dirs: list[Path], primary: str, comparator: str, split: str) -> pd.DataFrame:
    primary_frame = _load_prediction_frames(run_dirs, primary, split)
    comparator_frame = _load_prediction_frames(run_dirs, comparator, split)
    merged = primary_frame.merge(comparator_frame, on=KEY_COLUMNS, suffixes=("_primary", "_comparator"), how="inner")
    if merged.empty:
        raise SystemExit(f"no paired rows after joining {primary} and {comparator}; check seed/split/origin/node/horizon keys")
    return merged


def _load_prediction_frames(run_dirs: list[Path], baseline_id: str, split: str) -> pd.DataFrame:
    frames = []
    missing = []
    for run_dir in run_dirs:
        path = run_dir / "predictions_full" / f"{split}_{baseline_id}.csv.gz"
        if not path.exists():
            missing.append(str(path))
            continue
        frame = pd.read_csv(path, usecols=PREDICTION_COLUMNS)
        if frame.empty:
            raise SystemExit(f"empty full prediction file: {path}")
        frames.append(frame)
    if not frames:
        raise SystemExit(f"missing full prediction files for {baseline_id}: {missing}")
    return pd.concat(frames, ignore_index=True)


def _bootstrap_row(primary: str, comparator: str, scope: str, delta: np.ndarray, samples: int, rng: np.random.Generator) -> dict[str, Any]:
    """对 paired delta 做 bootstrap CI；负数代表 primary 更好。

    bootstrap 只重采样已经固定的 test prediction 行，不会改变模型，也不会选择新参数。
    """

    clean = delta[np.isfinite(delta)]
    if clean.size == 0:
        return {
            "primary_baseline": primary,
            "comparator_baseline": comparator,
            "scope": scope,
            "row_count": 0,
            "delta_mean": np.nan,
            "ci_low_95": np.nan,
            "ci_high_95": np.nan,
            "win_rate": np.nan,
        }
    boot = np.empty(samples, dtype=float)
    for index in range(samples):
        boot[index] = float(np.mean(clean[rng.integers(0, clean.size, size=clean.size)]))
    return {
        "primary_baseline": primary,
        "comparator_baseline": comparator,
        "scope": scope,
        "row_count": int(clean.size),
        "delta_mean": float(np.mean(clean)),
        "ci_low_95": float(np.quantile(boot, 0.025)),
        "ci_high_95": float(np.quantile(boot, 0.975)),
        "win_rate": float(np.mean(clean < 0)),
    }


def _event_stable_rows(primary: str, comparator: str, merged: pd.DataFrame) -> list[dict[str, Any]]:
    event_mask = merged["event_window_any_primary"].astype(bool)
    rows = []
    for scope, mask in (("global", np.ones(len(merged), dtype=bool)), ("event_window", event_mask.to_numpy()), ("stable_window", (~event_mask).to_numpy())):
        subset = merged.loc[mask]
        rows.append(
            {
                "baseline_id": primary,
                "comparator_baseline": comparator,
                "split": "test",
                "scope": scope,
                "row_count": int(len(subset)),
                "MAE_primary": float(subset["abs_error_primary"].mean()) if len(subset) else np.nan,
                "MAE_comparator": float(subset["abs_error_comparator"].mean()) if len(subset) else np.nan,
                "delta_primary_minus_comparator": float((subset["abs_error_primary"] - subset["abs_error_comparator"]).mean()) if len(subset) else np.nan,
            }
        )
    return rows


def _event_stable_primary_table(run_dirs: list[Path], baseline_ids: list[str], behavior_id: str = "behavior_concat_v5") -> list[dict[str, Any]]:
    """生成论文主表需要的 global/event/stable MAE 与 behavior 对照差值。

    这个表仍然只读已经写盘的 test predictions。它不做模型选择，只把 event-window
    与 stable-window 拆开，回答“收益是否主要来自事件扰动窗口”。
    """

    unique_baselines = list(dict.fromkeys(baseline_ids))
    frames = {baseline_id: _load_prediction_frames(run_dirs, baseline_id, "test") for baseline_id in unique_baselines}
    behavior_frame = frames.get(behavior_id)
    behavior_metrics = _scope_mae(behavior_frame) if behavior_frame is not None else {}
    rows = []
    for baseline_id, frame in frames.items():
        metrics = _scope_mae(frame)
        rows.append(
            {
                "baseline_id": baseline_id,
                "split": "test",
                "MAE_global": metrics["global"],
                "MAE_event_window": metrics["event_window"],
                "MAE_stable_window": metrics["stable_window"],
                "delta_global_vs_behavior": _delta_or_nan(metrics, behavior_metrics, "global"),
                "delta_event_vs_behavior": _delta_or_nan(metrics, behavior_metrics, "event_window"),
                "delta_stable_vs_behavior": _delta_or_nan(metrics, behavior_metrics, "stable_window"),
            }
        )
    return rows


def _scope_mae(frame: pd.DataFrame | None) -> dict[str, float]:
    if frame is None or frame.empty:
        return {"global": np.nan, "event_window": np.nan, "stable_window": np.nan}
    event_mask = frame["event_window_any"].astype(bool)
    return {
        "global": float(frame["abs_error"].mean()),
        "event_window": float(frame.loc[event_mask, "abs_error"].mean()) if event_mask.any() else np.nan,
        "stable_window": float(frame.loc[~event_mask, "abs_error"].mean()) if (~event_mask).any() else np.nan,
    }


def _delta_or_nan(metrics: dict[str, float], behavior_metrics: dict[str, float], scope: str) -> float:
    if scope not in behavior_metrics:
        return np.nan
    return float(metrics[scope] - behavior_metrics[scope])


def _write_decision_summary(path: Path, primary: str, ci_rows: list[dict[str, Any]], event_rows: list[dict[str, Any]]) -> None:
    lines = [
        f"# EXP-103 V5 Plus Decision Summary",
        "",
        f"Primary baseline: `{primary}`",
        "",
        "负数 delta 代表 primary baseline 的 absolute error 更低。",
        "",
        "## Bootstrap CI",
        "",
    ]
    for row in ci_rows:
        lines.append(
            f"- {row['scope']}: `{row['primary_baseline']}` vs `{row['comparator_baseline']}` "
            f"delta_mean={row['delta_mean']:.8f}, 95% CI=[{row['ci_low_95']:.8f}, {row['ci_high_95']:.8f}], "
            f"win_rate={row['win_rate']:.3f}, n={row['row_count']}"
        )
    lines.extend(["", "## Event/Stable MAE", ""])
    for row in event_rows:
        lines.append(
            f"- {row['scope']}: `{primary}` vs `{row['comparator_baseline']}` "
            f"MAE_primary={row['MAE_primary']:.8f}, MAE_comparator={row['MAE_comparator']:.8f}, "
            f"delta={row['delta_primary_minus_comparator']:.8f}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
