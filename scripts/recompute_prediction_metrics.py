"""Independently recompute paired regression metrics from prediction rows."""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Prediction:
    sample_id: str
    model_id: str
    y_true: float
    y_pred: float
    cluster_id: str | None


def read_predictions(path: Path, cluster_column: str) -> list[Prediction]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            required = {"sample_id", "model_id", "y_true", "y_pred"}
            missing = required.difference(reader.fieldnames or [])
            if missing:
                raise ValueError(f"missing required columns: {', '.join(sorted(missing))}")
            rows: list[Prediction] = []
            seen: set[tuple[str, str]] = set()
            truth_by_sample: dict[str, float] = {}
            cluster_by_sample: dict[str, str] = {}
            for line_number, row in enumerate(reader, start=2):
                sample_id = (row.get("sample_id") or "").strip()
                model_id = (row.get("model_id") or "").strip()
                if not sample_id or not model_id:
                    raise ValueError(f"row {line_number}: sample_id and model_id must be non-empty")
                key = (sample_id, model_id)
                if key in seen:
                    raise ValueError(f"row {line_number}: duplicate sample/model pair {key!r}")
                seen.add(key)
                try:
                    y_true = float(row["y_true"])
                    y_pred = float(row["y_pred"])
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"row {line_number}: y_true and y_pred must be numbers") from exc
                if not math.isfinite(y_true) or not math.isfinite(y_pred):
                    raise ValueError(f"row {line_number}: y_true and y_pred must be finite")
                if sample_id in truth_by_sample and truth_by_sample[sample_id] != y_true:
                    raise ValueError(f"row {line_number}: y_true differs between models for {sample_id!r}")
                truth_by_sample[sample_id] = y_true
                cluster_value = (row.get(cluster_column) or "").strip() if cluster_column in (reader.fieldnames or []) else ""
                if cluster_value:
                    previous = cluster_by_sample.setdefault(sample_id, cluster_value)
                    if previous != cluster_value:
                        raise ValueError(f"row {line_number}: cluster differs between models for {sample_id!r}")
                rows.append(Prediction(sample_id, model_id, y_true, y_pred, cluster_value or None))
    except OSError as exc:
        raise ValueError(f"cannot read predictions file: {exc}") from exc
    if not rows:
        raise ValueError("predictions file contains no data rows")
    return rows


def summarize(rows: Iterable[Prediction]) -> dict[str, float | int]:
    values = list(rows)
    if not values:
        raise ValueError("cannot calculate metrics from an empty model prediction set")
    count = len(values)
    absolute_error = sum(abs(row.y_pred - row.y_true) for row in values)
    squared_error = sum((row.y_pred - row.y_true) ** 2 for row in values)
    bias = sum(row.y_pred - row.y_true for row in values)
    return {
        "n": count,
        "mae": absolute_error / count,
        "rmse": math.sqrt(squared_error / count),
        "mean_error_pred_minus_true": bias / count,
    }


def percentile(sorted_values: list[float], probability: float) -> float:
    position = (len(sorted_values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def compare_models(
    rows: list[Prediction],
    baseline_id: str,
    candidate_id: str,
    cluster_column: str,
    resamples: int,
    seed: int,
) -> dict[str, object]:
    by_model: dict[str, dict[str, Prediction]] = defaultdict(dict)
    for row in rows:
        by_model[row.model_id][row.sample_id] = row
    if baseline_id not in by_model or candidate_id not in by_model:
        raise ValueError("baseline and candidate model IDs must both occur in the input")
    baseline = by_model[baseline_id]
    candidate = by_model[candidate_id]
    if baseline.keys() != candidate.keys():
        raise ValueError("baseline and candidate must have the same sample IDs for paired comparison")

    cluster_stats: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {baseline_id: [0.0, 0.0, 0.0], candidate_id: [0.0, 0.0, 0.0]}
    )
    for sample_id in sorted(baseline):
        base_row = baseline[sample_id]
        candidate_row = candidate[sample_id]
        if base_row.y_true != candidate_row.y_true:
            raise ValueError(f"y_true differs between models for sample {sample_id!r}")
        if not base_row.cluster_id or not candidate_row.cluster_id:
            raise ValueError(f"cluster column {cluster_column!r} must be populated for every compared sample")
        cluster = base_row.cluster_id
        for model_id, row in ((baseline_id, base_row), (candidate_id, candidate_row)):
            stats = cluster_stats[cluster][model_id]
            error = row.y_pred - row.y_true
            stats[0] += 1
            stats[1] += abs(error)
            stats[2] += error * error

    clusters = sorted(cluster_stats)
    if len(clusters) < 2:
        raise ValueError("paired cluster bootstrap requires at least two non-empty clusters")
    if resamples < 100:
        raise ValueError("bootstrap resamples must be at least 100")

    observed_base = summarize(baseline.values())
    observed_candidate = summarize(candidate.values())
    observed = {
        "mae": float(observed_candidate["mae"]) - float(observed_base["mae"]),
        "rmse": float(observed_candidate["rmse"]) - float(observed_base["rmse"]),
    }

    rng = random.Random(seed)
    bootstrap_deltas: dict[str, list[float]] = {"mae": [], "rmse": []}
    for _ in range(resamples):
        totals = {baseline_id: [0.0, 0.0, 0.0], candidate_id: [0.0, 0.0, 0.0]}
        for cluster in (rng.choice(clusters) for _ in clusters):
            for model_id in (baseline_id, candidate_id):
                stats = cluster_stats[cluster][model_id]
                for index in range(3):
                    totals[model_id][index] += stats[index]
        base_n, base_abs, base_sq = totals[baseline_id]
        candidate_n, candidate_abs, candidate_sq = totals[candidate_id]
        if base_n != candidate_n or base_n == 0:
            raise ValueError("paired bootstrap encountered incompatible cluster sample counts")
        bootstrap_deltas["mae"].append(candidate_abs / candidate_n - base_abs / base_n)
        bootstrap_deltas["rmse"].append(math.sqrt(candidate_sq / candidate_n) - math.sqrt(base_sq / base_n))

    comparisons: dict[str, object] = {}
    for metric, deltas in bootstrap_deltas.items():
        ordered = sorted(deltas)
        comparisons[metric] = {
            "delta_candidate_minus_baseline": observed[metric],
            "confidence_interval_95": [percentile(ordered, 0.025), percentile(ordered, 0.975)],
            "interval_method": "paired cluster bootstrap percentile interval",
            "resampling_unit": cluster_column,
            "cluster_count": len(clusters),
            "bootstrap_resamples": resamples,
            "seed": seed,
            "interpretation": "Negative delta favors the candidate on this metric; do not treat the interval alone as a universal significance test.",
        }
    return {
        "baseline_model": baseline_id,
        "candidate_model": candidate_id,
        "sample_count": len(baseline),
        **comparisons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Long-format CSV of sample/model predictions")
    parser.add_argument("--out", required=True, type=Path, help="Output JSON report path")
    parser.add_argument("--cluster-column", default="cluster_id", help="Prespecified dependence/block column")
    parser.add_argument("--baseline-model", help="Model ID used as the paired baseline")
    parser.add_argument("--candidate-model", help="Model ID compared with the baseline")
    parser.add_argument("--bootstrap-resamples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261016)
    parser.add_argument("--experiment-id", help="Optional EXP-* identifier to include in the report")
    parser.add_argument("--protocol-sha256", help="Optional hash of the frozen protocol/config bundle")
    args = parser.parse_args()

    if bool(args.baseline_model) != bool(args.candidate_model):
        parser.error("--baseline-model and --candidate-model must be supplied together")
    if args.baseline_model == args.candidate_model and args.baseline_model:
        parser.error("baseline and candidate model IDs must differ")
    try:
        rows = read_predictions(args.input, args.cluster_column)
        by_model: dict[str, list[Prediction]] = defaultdict(list)
        for row in rows:
            by_model[row.model_id].append(row)
        report: dict[str, object] = {
            "input_file": str(args.input),
            "metric_definitions": {
                "mae": "mean absolute error",
                "rmse": "root mean squared error",
                "mean_error_pred_minus_true": "mean(prediction - truth)",
            },
            "models": {model_id: summarize(model_rows) for model_id, model_rows in sorted(by_model.items())},
        }
        if args.experiment_id:
            report["experiment_id"] = args.experiment_id
        if args.protocol_sha256:
            report["protocol_sha256"] = args.protocol_sha256
        if args.baseline_model and args.candidate_model:
            report["comparison"] = compare_models(
                rows,
                args.baseline_model,
                args.candidate_model,
                args.cluster_column,
                args.bootstrap_resamples,
                args.seed,
            )
        output_path = args.out.resolve()
        if output_path == args.input.resolve():
            parser.error("output path must not overwrite the prediction input")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Wrote independent metric report: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
