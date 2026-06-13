#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

LEDGER_COLUMNS = [
    "run_id",
    "seed",
    "rho",
    "lambda_event",
    "graph_mode",
    "feature_set",
    "output_dir",
    "baseline_id",
    "rank_by_MAE",
    "MAE",
    "RMSE",
    "delta_vs_behavior_concat",
    "delta_vs_dtw_graph",
    "graph_destruction_delta",
    "best_baseline",
    "event_graph_MAE",
    "behavior_concat_MAE",
    "dtw_demand_graph_MAE",
    "historical_correlation_graph_MAE",
    "prediction_count",
    "best_validation_loss",
    "best_epoch",
    "epochs_ran",
    "train_seconds",
    "uses_events",
    "uses_graph",
    "manifest_path",
    "baseline_metrics_hash",
]

SUMMARY_COLUMNS = [
    "baseline_id",
    "run_count",
    "MAE_mean",
    "MAE_std",
    "MAE_min",
    "MAE_max",
    "RMSE_mean",
    "RMSE_std",
]

OPTIMIZATION_COLUMNS = [
    "run_id",
    "seed",
    "rho",
    "lambda_event",
    "graph_mode",
    "feature_set",
    "best_baseline",
    "event_vs_behavior_delta",
    "event_vs_dtw_delta",
    "event_vs_historical_delta",
    "event_vs_random_delta",
    "event_vs_shuffled_delta",
    "fusion_vs_behavior_delta",
    "fusion_vs_dtw_delta",
    "fusion_vs_historical_delta",
    "fusion_vs_random_delta",
    "fusion_vs_shuffled_delta",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect EXP-103 training outputs into one reproducible ledger.")
    parser.add_argument("--outputs-root", default="outputs")
    parser.add_argument("--out", default="outputs/EXP-103-run-ledger.csv")
    parser.add_argument("--summary-out", default="outputs/EXP-103-run-summary.csv")
    parser.add_argument("--optimization-out", default="outputs/EXP-103-optimization-ledger.csv")
    args = parser.parse_args()

    outputs_root = Path(args.outputs_root)
    rows, optimization_rows = collect_exp103_rows(outputs_root)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    summary_path = Path(args.summary_out)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        writer.writerows(build_summary_rows(rows))
    optimization_path = Path(args.optimization_out)
    optimization_path.parent.mkdir(parents=True, exist_ok=True)
    with optimization_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OPTIMIZATION_COLUMNS)
        writer.writeheader()
        writer.writerows(optimization_rows)
    print(f"wrote EXP-103 run ledger: {out_path} ({len(rows)} rows)")
    print(f"wrote EXP-103 run summary: {summary_path}")
    print(f"wrote EXP-103 optimization ledger: {optimization_path} ({len(optimization_rows)} rows)")


def collect_exp103_rows(outputs_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    optimization_rows: list[dict[str, Any]] = []
    for run_dir in sorted(outputs_root.glob("EXP-103*")):
        metrics_path = run_dir / "baseline_metrics.csv"
        if not metrics_path.exists():
            continue
        baseline_rows = _read_csv(metrics_path)
        if not baseline_rows:
            continue
        ablation_rows = {row["baseline_id"]: row for row in _read_csv(run_dir / "graph_ablation_table.csv")}
        manifest = _read_json(run_dir / "manifest.json")
        config = _read_json(run_dir / "config_resolved.json")
        metrics_by_baseline = {row["baseline_id"]: row for row in baseline_rows}
        ranked = sorted(baseline_rows, key=lambda row: (float(row.get("MAE", "inf")), row.get("baseline_id", "")))
        rank_by_baseline = {row["baseline_id"]: index + 1 for index, row in enumerate(ranked)}
        best_baseline = ranked[0]["baseline_id"]
        run_id = run_dir.name
        run_config = _run_config_fields(run_id, config)
        run_summary = {
            "run_id": run_id,
            **run_config,
            "output_dir": str(run_dir),
            "best_baseline": best_baseline,
            "event_graph_MAE": _metric(metrics_by_baseline, "event_graph_dynamic", "MAE"),
            "behavior_concat_MAE": _metric(metrics_by_baseline, "behavior_concat", "MAE"),
            "dtw_demand_graph_MAE": _metric(metrics_by_baseline, "dtw_demand_graph", "MAE"),
            "historical_correlation_graph_MAE": _metric(metrics_by_baseline, "historical_correlation_graph", "MAE"),
            "manifest_path": str(run_dir / "manifest.json") if (run_dir / "manifest.json").exists() else "",
            "baseline_metrics_hash": manifest.get("hashes", {}).get("baseline_metrics.csv", ""),
        }
        for row in baseline_rows:
            baseline_id = row["baseline_id"]
            ablation = ablation_rows.get(baseline_id, {})
            rows.append(
                {
                    **run_summary,
                    "baseline_id": baseline_id,
                    "rank_by_MAE": rank_by_baseline[baseline_id],
                    "MAE": row.get("MAE", ""),
                    "RMSE": row.get("RMSE", ""),
                    "delta_vs_behavior_concat": ablation.get("delta_vs_behavior_concat", ""),
                    "delta_vs_dtw_graph": ablation.get("delta_vs_dtw_graph", ""),
                    "graph_destruction_delta": ablation.get("graph_destruction_delta", ""),
                    "prediction_count": row.get("prediction_count", ""),
                    "best_validation_loss": row.get("best_validation_loss", ""),
                    "best_epoch": row.get("best_epoch", ""),
                    "epochs_ran": row.get("epochs_ran", ""),
                    "train_seconds": row.get("train_seconds", ""),
                    "uses_events": row.get("uses_events", ""),
                    "uses_graph": row.get("uses_graph", ""),
                }
            )
        optimization_rows.append(_optimization_row(run_id, run_config, best_baseline, metrics_by_baseline))
    return rows, optimization_rows


def build_summary_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_baseline: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_baseline.setdefault(str(row["baseline_id"]), []).append(row)
    summary_rows = []
    for baseline_id, baseline_rows in sorted(by_baseline.items()):
        mae_values = _float_values(baseline_rows, "MAE")
        rmse_values = _float_values(baseline_rows, "RMSE")
        summary_rows.append(
            {
                "baseline_id": baseline_id,
                "run_count": len(baseline_rows),
                "MAE_mean": _mean(mae_values),
                "MAE_std": _std(mae_values),
                "MAE_min": min(mae_values) if mae_values else "",
                "MAE_max": max(mae_values) if mae_values else "",
                "RMSE_mean": _mean(rmse_values),
                "RMSE_std": _std(rmse_values),
            }
        )
    return summary_rows


def _optimization_row(
    run_id: str,
    run_config: dict[str, Any],
    best_baseline: str,
    metrics_by_baseline: dict[str, dict[str, str]],
) -> dict[str, Any]:
    event_mae = _float_metric(metrics_by_baseline, "event_graph_dynamic", "MAE")
    fusion_mae = _float_metric(metrics_by_baseline, "event_dtw_fusion_graph", "MAE")
    comparators = {
        "behavior": _float_metric(metrics_by_baseline, "behavior_concat", "MAE"),
        "dtw": _float_metric(metrics_by_baseline, "dtw_demand_graph", "MAE"),
        "historical": _float_metric(metrics_by_baseline, "historical_correlation_graph", "MAE"),
        "random": _float_metric(metrics_by_baseline, "random_event_graph", "MAE"),
        "shuffled": _float_metric(metrics_by_baseline, "shuffled_event_graph", "MAE"),
    }
    row = {"run_id": run_id, **run_config, "best_baseline": best_baseline}
    for name, value in comparators.items():
        row[f"event_vs_{name}_delta"] = _delta(event_mae, value)
        row[f"fusion_vs_{name}_delta"] = _delta(fusion_mae, value)
    return row


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _infer_seed(run_id: str) -> str:
    match = re.search(r"(?:seed|multiseed)-(\d+)", run_id)
    return match.group(1) if match else ""


def _run_config_fields(run_id: str, config: dict[str, Any]) -> dict[str, Any]:
    graph_config = config.get("graph", {}) if isinstance(config.get("graph", {}), dict) else {}
    training_config = config.get("training", {}) if isinstance(config.get("training", {}), dict) else {}
    feature_config = config.get("features", {}) if isinstance(config.get("features", {}), dict) else {}
    enabled_features = []
    if feature_config.get("include_time_context"):
        enabled_features.append("time_context")
    if feature_config.get("include_enhanced_events"):
        enabled_features.append("enhanced_events")
    return {
        "seed": config.get("seed", _infer_seed(run_id)),
        "rho": graph_config.get("rho", ""),
        "lambda_event": graph_config.get("lambda_event", ""),
        "graph_mode": training_config.get("graph_mode", ""),
        "feature_set": "+".join(enabled_features) if enabled_features else "base",
    }


def _metric(rows: dict[str, dict[str, str]], baseline_id: str, metric: str) -> str:
    return rows.get(baseline_id, {}).get(metric, "")


def _float_metric(rows: dict[str, dict[str, str]], baseline_id: str, metric: str) -> float | None:
    value = _metric(rows, baseline_id, metric)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _float_values(rows: list[dict[str, Any]], key: str) -> list[float]:
    values = []
    for row in rows:
        try:
            values.append(float(row[key]))
        except (KeyError, TypeError, ValueError):
            continue
    return values


def _delta(left: float | None, right: float | None) -> float | str:
    if left is None or right is None:
        return ""
    return left - right


def _mean(values: list[float]) -> float | str:
    return sum(values) / len(values) if values else ""


def _std(values: list[float]) -> float | str:
    if len(values) < 2:
        return 0.0 if values else ""
    mean = sum(values) / len(values)
    return (sum((value - mean) ** 2 for value in values) / (len(values) - 1)) ** 0.5


if __name__ == "__main__":
    main()
