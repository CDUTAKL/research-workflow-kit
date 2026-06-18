#!/usr/bin/env python3
from __future__ import annotations

"""EXP-103 小规模超参搜索编排器。

脚本的定位是“可复现的批量实验生成器”，而不是自动调参黑箱：

1. 从一个 base config 出发，枚举 seed、top-k、graph_mode、hidden size、学习率等组合。
2. 为每个组合生成独立 config，并调用 `src/training/train_exp103.py`。
3. 每个 run 结束后立即汇总 `baseline_metrics.csv`，方便中途中断后继续 resume。

这样做可以把“某个参数为什么被采用”的证据留在 CSV 和 command log 中，便于论文审计。
"""

import argparse
import csv
import itertools
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from evcs.utils.config import load_experiment_config  # noqa: E402

DEFAULT_BASELINES = [
    "behavior_concat",
    "event_graph_dynamic",
    "dtw_demand_graph",
    "historical_correlation_graph",
    "random_event_graph",
    "shuffled_event_graph",
]

RUN_COLUMNS = [
    "search_id",
    "run_id",
    "status",
    "return_code",
    "seed",
    "batch_size",
    "graph_mode",
    "top_k",
    "hidden_channels",
    "lr",
    "dropout",
    "baseline_id",
    "MAE",
    "RMSE",
    "rank_by_MAE",
    "best_validation_loss",
    "best_epoch",
    "epochs_ran",
    "train_seconds",
    "output_dir",
    "config_path",
    "started_at",
    "finished_at",
]

SUMMARY_COLUMNS = [
    "search_id",
    "run_id",
    "status",
    "seed",
    "batch_size",
    "graph_mode",
    "top_k",
    "hidden_channels",
    "lr",
    "dropout",
    "best_baseline",
    "event_rank",
    "event_MAE",
    "behavior_concat_MAE",
    "dtw_demand_graph_MAE",
    "historical_correlation_graph_MAE",
    "random_event_graph_MAE",
    "shuffled_event_graph_MAE",
    "event_vs_behavior_delta",
    "event_vs_dtw_delta",
    "event_vs_historical_delta",
    "event_vs_random_delta",
    "event_vs_shuffled_delta",
    "mean_pressure_delta",
    "output_dir",
    "config_path",
]


def main() -> None:
    """命令行入口：生成配置、运行训练、持续刷新搜索明细和汇总表。"""

    parser = argparse.ArgumentParser(
        description=(
            "Run a compact EXP-103 hyperparameter search by generating configs, "
            "calling src/training/train_exp103.py, and summarizing each run."
        )
    )
    parser.add_argument("--base-config", default="configs/experiment/EXP-103-train-optimized.yaml")
    parser.add_argument("--search-id", default="EXP-103-hparam-search")
    parser.add_argument("--out-root", default="outputs/EXP-103-hparam-search")
    parser.add_argument("--generated-config-dir", default="configs/generated/EXP-103-hparam-search")
    parser.add_argument("--summary-out", default="outputs/EXP-103-hparam-search-summary.csv")
    parser.add_argument("--runs-out", default="outputs/EXP-103-hparam-search-runs.csv")
    parser.add_argument("--command-log", default="outputs/EXP-103-hparam-search-commands.sh")
    parser.add_argument("--seeds", default="42")
    parser.add_argument("--batch-sizes", default="512")
    parser.add_argument("--graph-modes", default="concat,gated_residual")
    parser.add_argument("--top-ks", default="3,5,8,10")
    parser.add_argument("--hidden-channels", default="64,96")
    parser.add_argument("--lrs", default="0.001")
    parser.add_argument("--dropouts", default="0.1")
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--early-stopping-patience", type=int)
    parser.add_argument("--num-workers", type=int)
    parser.add_argument("--baselines", default=",".join(DEFAULT_BASELINES))
    parser.add_argument("--max-runs", type=int)
    parser.add_argument("--resume", action="store_true", help="Skip runs whose baseline_metrics.csv already exists.")
    parser.add_argument("--dry-run", action="store_true", help="Only generate configs, command log, and dry-run tables.")
    args = parser.parse_args()

    base_config = load_experiment_config(Path(args.base_config))
    search_root = Path(args.out_root)
    config_root = Path(args.generated_config_dir)
    search_root.mkdir(parents=True, exist_ok=True)
    config_root.mkdir(parents=True, exist_ok=True)
    Path(args.summary_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.runs_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.command_log).parent.mkdir(parents=True, exist_ok=True)

    combinations = _build_combinations(args)
    run_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    commands: list[str] = ["#!/usr/bin/env bash", "set -euo pipefail", ""]
    for index, params in enumerate(combinations, start=1):
        run_id = _run_id(args.search_id, index, params)
        output_dir = search_root / run_id
        config_path = config_root / f"{run_id}.json"
        config = _build_config(base_config, params, output_dir, args)
        _write_json(config_path, config)
        command = f"python src/training/train_exp103.py --config {config_path} --out {output_dir}"
        commands.append(command)
        commands.append("")

        if args.resume and (output_dir / "baseline_metrics.csv").exists():
            status = "skipped_existing"
            return_code = 0
            started_at = finished_at = ""
        elif args.dry_run:
            status = "dry_run"
            return_code = 0
            started_at = finished_at = ""
        else:
            started_at = _timestamp()
            return_code = subprocess.run(command.split(), cwd=REPO_ROOT, check=False).returncode
            finished_at = _timestamp()
            status = "ok" if return_code == 0 else "failed"

        baseline_rows = _read_baseline_metrics(output_dir / "baseline_metrics.csv")
        if baseline_rows:
            ranked = _rank_rows(baseline_rows)
            for row in ranked:
                run_rows.append(_run_row(args.search_id, run_id, status, return_code, params, row, output_dir, config_path, started_at, finished_at))
            summary_rows.append(_summary_row(args.search_id, run_id, status, params, ranked, output_dir, config_path))
        else:
            run_rows.append(_empty_run_row(args.search_id, run_id, status, return_code, params, output_dir, config_path, started_at, finished_at))
            summary_rows.append(_empty_summary_row(args.search_id, run_id, status, params, output_dir, config_path))

        _write_csv(Path(args.runs_out), RUN_COLUMNS, run_rows)
        _write_csv(Path(args.summary_out), SUMMARY_COLUMNS, _sort_summary(summary_rows))

        if return_code != 0 and not args.dry_run:
            raise SystemExit(f"EXP-103 hparam run failed: {run_id} return_code={return_code}")

    Path(args.command_log).write_text("\n".join(commands) + "\n", encoding="utf-8")
    print(f"generated {len(combinations)} EXP-103 hparam configs under {config_root}")
    print(f"wrote command log: {args.command_log}")
    print(f"wrote run table: {args.runs_out}")
    print(f"wrote summary table: {args.summary_out}")
    if args.dry_run:
        print("dry run only; no training commands were executed")


def _build_combinations(args: argparse.Namespace) -> list[dict[str, Any]]:
    """把命令行传入的逗号分隔网格展开成 run 参数列表。"""

    grids = itertools.product(
        _parse_ints(args.seeds),
        _parse_ints(args.batch_sizes),
        _parse_strings(args.graph_modes),
        _parse_ints(args.top_ks),
        _parse_ints(args.hidden_channels),
        _parse_floats(args.lrs),
        _parse_floats(args.dropouts),
    )
    combinations = [
        {
            "seed": seed,
            "batch_size": batch_size,
            "graph_mode": graph_mode,
            "top_k": top_k,
            "hidden_channels": hidden_channels,
            "lr": lr,
            "dropout": dropout,
        }
        for seed, batch_size, graph_mode, top_k, hidden_channels, lr, dropout in grids
    ]
    return combinations[: args.max_runs] if args.max_runs else combinations


def _build_config(base_config: dict[str, Any], params: dict[str, Any], output_dir: Path, args: argparse.Namespace) -> dict[str, Any]:
    """基于 base config 生成单次训练配置。

    这里使用 JSON 深拷贝保留原配置结构，只覆盖搜索维度；这样可以避免超参搜索脚本
    和训练配置模板之间出现两套默认值。
    """

    config = json.loads(json.dumps(base_config))
    config["seed"] = params["seed"]
    config["output"] = str(output_dir)
    config["baselines"] = _parse_strings(args.baselines)
    graph = config.setdefault("graph", {})
    graph["top_k"] = params["top_k"]
    # top_k 改变后，DTW 图的邻居预算也改变，因此缓存文件名必须随 top_k 变化，避免误读旧图。
    graph["dtw_cache_path"] = str(_dtw_cache_path(graph, params["top_k"]))
    training = config.setdefault("training", {})
    training["batch_size"] = params["batch_size"]
    training["graph_mode"] = params["graph_mode"]
    training["hidden_channels"] = params["hidden_channels"]
    training["lr"] = params["lr"]
    training["dropout"] = params["dropout"]
    if args.epochs is not None:
        training["epochs"] = args.epochs
    if args.early_stopping_patience is not None:
        training["early_stopping_patience"] = args.early_stopping_patience
    if args.num_workers is not None:
        training["num_workers"] = args.num_workers
    return config


def _dtw_cache_path(graph_config: dict[str, Any], top_k: int) -> Path:
    """根据 top-k 生成 DTW 图缓存路径，避免不同邻居数误用同一个缓存。"""

    current = Path(str(graph_config.get("dtw_cache_path", "data/processed/graphs/dtw_demand_graph.npz")))
    dtw_max_points = graph_config.get("dtw_max_points", "all")
    return current.parent / f"dtw_demand_graph_top{top_k}_points{dtw_max_points}.npz"


def _run_id(search_id: str, index: int, params: dict[str, Any]) -> str:
    lr = _compact_float(params["lr"])
    dropout = _compact_float(params["dropout"])
    return (
        f"{search_id}-{index:03d}-seed{params['seed']}-bs{params['batch_size']}-"
        f"{params['graph_mode']}-k{params['top_k']}-h{params['hidden_channels']}-lr{lr}-do{dropout}"
    )


def _read_baseline_metrics(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _rank_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted(rows, key=lambda row: (_to_float(row.get("MAE")), str(row.get("baseline_id", ""))))
    for index, row in enumerate(ranked, start=1):
        row["rank_by_MAE"] = index
    return ranked


def _run_row(
    search_id: str,
    run_id: str,
    status: str,
    return_code: int,
    params: dict[str, Any],
    metric_row: dict[str, Any],
    output_dir: Path,
    config_path: Path,
    started_at: str,
    finished_at: str,
) -> dict[str, Any]:
    return {
        "search_id": search_id,
        "run_id": run_id,
        "status": status,
        "return_code": return_code,
        **params,
        "baseline_id": metric_row.get("baseline_id", ""),
        "MAE": metric_row.get("MAE", ""),
        "RMSE": metric_row.get("RMSE", ""),
        "rank_by_MAE": metric_row.get("rank_by_MAE", ""),
        "best_validation_loss": metric_row.get("best_validation_loss", ""),
        "best_epoch": metric_row.get("best_epoch", ""),
        "epochs_ran": metric_row.get("epochs_ran", ""),
        "train_seconds": metric_row.get("train_seconds", ""),
        "output_dir": str(output_dir),
        "config_path": str(config_path),
        "started_at": started_at,
        "finished_at": finished_at,
    }


def _summary_row(
    search_id: str,
    run_id: str,
    status: str,
    params: dict[str, Any],
    rows: list[dict[str, Any]],
    output_dir: Path,
    config_path: Path,
) -> dict[str, Any]:
    """把一个 run 的多 baseline 指标压成搜索层面的胜负摘要。"""

    by_baseline = {str(row.get("baseline_id", "")): row for row in rows}
    best_baseline = str(rows[0].get("baseline_id", "")) if rows else ""
    event_mae = _metric(by_baseline, "event_graph_dynamic", "MAE")
    comparators = {
        "behavior_concat": _metric(by_baseline, "behavior_concat", "MAE"),
        "dtw_demand_graph": _metric(by_baseline, "dtw_demand_graph", "MAE"),
        "historical_correlation_graph": _metric(by_baseline, "historical_correlation_graph", "MAE"),
        "random_event_graph": _metric(by_baseline, "random_event_graph", "MAE"),
        "shuffled_event_graph": _metric(by_baseline, "shuffled_event_graph", "MAE"),
    }
    deltas = {name: _delta(event_mae, value) for name, value in comparators.items()}
    pressure_deltas = [value for value in deltas.values() if value != ""]
    return {
        "search_id": search_id,
        "run_id": run_id,
        "status": status,
        **params,
        "best_baseline": best_baseline,
        "event_rank": by_baseline.get("event_graph_dynamic", {}).get("rank_by_MAE", ""),
        "event_MAE": event_mae,
        "behavior_concat_MAE": comparators["behavior_concat"],
        "dtw_demand_graph_MAE": comparators["dtw_demand_graph"],
        "historical_correlation_graph_MAE": comparators["historical_correlation_graph"],
        "random_event_graph_MAE": comparators["random_event_graph"],
        "shuffled_event_graph_MAE": comparators["shuffled_event_graph"],
        # delta = comparator - event；正值代表 event_graph_dynamic 更好。
        "event_vs_behavior_delta": deltas["behavior_concat"],
        "event_vs_dtw_delta": deltas["dtw_demand_graph"],
        "event_vs_historical_delta": deltas["historical_correlation_graph"],
        "event_vs_random_delta": deltas["random_event_graph"],
        "event_vs_shuffled_delta": deltas["shuffled_event_graph"],
        "mean_pressure_delta": sum(pressure_deltas) / len(pressure_deltas) if pressure_deltas else "",
        "output_dir": str(output_dir),
        "config_path": str(config_path),
    }


def _empty_run_row(
    search_id: str,
    run_id: str,
    status: str,
    return_code: int,
    params: dict[str, Any],
    output_dir: Path,
    config_path: Path,
    started_at: str,
    finished_at: str,
) -> dict[str, Any]:
    return {
        "search_id": search_id,
        "run_id": run_id,
        "status": status,
        "return_code": return_code,
        **params,
        "baseline_id": "",
        "MAE": "",
        "RMSE": "",
        "rank_by_MAE": "",
        "best_validation_loss": "",
        "best_epoch": "",
        "epochs_ran": "",
        "train_seconds": "",
        "output_dir": str(output_dir),
        "config_path": str(config_path),
        "started_at": started_at,
        "finished_at": finished_at,
    }


def _empty_summary_row(
    search_id: str,
    run_id: str,
    status: str,
    params: dict[str, Any],
    output_dir: Path,
    config_path: Path,
) -> dict[str, Any]:
    return {
        "search_id": search_id,
        "run_id": run_id,
        "status": status,
        **params,
        "best_baseline": "",
        "event_rank": "",
        "event_MAE": "",
        "behavior_concat_MAE": "",
        "dtw_demand_graph_MAE": "",
        "historical_correlation_graph_MAE": "",
        "random_event_graph_MAE": "",
        "shuffled_event_graph_MAE": "",
        "event_vs_behavior_delta": "",
        "event_vs_dtw_delta": "",
        "event_vs_historical_delta": "",
        "event_vs_random_delta": "",
        "event_vs_shuffled_delta": "",
        "mean_pressure_delta": "",
        "output_dir": str(output_dir),
        "config_path": str(config_path),
    }


def _sort_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: (_rank_sort_value(row.get("event_rank")), -_to_float(row.get("mean_pressure_delta"))))


def _metric(rows: dict[str, dict[str, Any]], baseline_id: str, metric: str) -> float | str:
    if baseline_id not in rows:
        return ""
    value = rows[baseline_id].get(metric, "")
    try:
        return float(value)
    except (TypeError, ValueError):
        return ""


def _delta(event_mae: float | str, comparator_mae: float | str) -> float | str:
    if event_mae == "" or comparator_mae == "":
        return ""
    return float(comparator_mae) - float(event_mae)


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("inf")


def _rank_sort_value(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("inf")


def _parse_strings(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_ints(value: str) -> list[int]:
    return [int(item) for item in _parse_strings(value)]


def _parse_floats(value: str) -> list[float]:
    return [float(item) for item in _parse_strings(value)]


def _compact_float(value: float) -> str:
    return f"{value:g}".replace(".", "p").replace("-", "m")


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


if __name__ == "__main__":
    main()
