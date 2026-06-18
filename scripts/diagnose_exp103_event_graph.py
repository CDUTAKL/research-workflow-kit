#!/usr/bin/env python3
from __future__ import annotations

"""诊断 EXP-103 事件图为什么能赢、何时会被强 baseline 追上。

这个脚本不参与训练，而是读取已经完成的 run 目录，对三类证据做二次分析：

1. 全局 MAE/RMSE 排名：判断 event graph 是否真正超过行为拼接、DTW、历史相关等强对照。
2. event-window / stable-window 分层：判断优势是否集中在事件扰动窗口。
3. 图结构距离：比较真实事件图与 shuffled/random/deleted/historical 图的边重合度和权重距离。

这些诊断输出用于论文中的“为什么有效”和“负控是否充分”两类论证。
"""

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from evcs.data.tensor_cache import load_tensor_cache  # noqa: E402
from evcs.utils.config import load_experiment_config  # noqa: E402

GLOBAL_BASELINES = [
    "event_graph_dynamic",
    "behavior_concat",
    "dtw_demand_graph",
    "historical_correlation_graph",
    "random_event_graph",
    "shuffled_event_graph",
    "deleted_event_graph",
    "no_graph",
]

DIAG_COLUMNS = [
    "question_id",
    "diagnostic",
    "value",
    "interpretation",
]


@dataclass(frozen=True)
class SampledGraph:
    """只保存被抽样 origin 的 top-k 图，避免诊断时构造完整动态图导致内存过大。"""

    baseline_id: str
    indices: np.ndarray
    weights: np.ndarray
    nodes: list[str]
    top_k: int


def main() -> None:
    """命令行入口：收集 run 目录、生成诊断 CSV 和一份 Markdown 解释报告。"""

    parser = argparse.ArgumentParser(description="Diagnose why EXP-103 event graph does or does not beat hard baselines.")
    parser.add_argument("--outputs-root", default="outputs")
    parser.add_argument("--run-glob", default="EXP-103-train-optimized-*-5090")
    parser.add_argument("--run-dir", action="append", default=[])
    parser.add_argument("--graph-run-dir", help="Run directory whose config_resolved.json should be used for graph diagnostics.")
    parser.add_argument("--sample-origins", type=int, default=2000)
    parser.add_argument("--out-dir", default="outputs/EXP-103-diagnostics")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_dirs = _discover_run_dirs(Path(args.outputs_root), args.run_glob, args.run_dir)
    if not run_dirs:
        raise SystemExit("No EXP-103 run directories found for diagnosis.")
    graph_run_dir = Path(args.graph_run_dir) if args.graph_run_dir else run_dirs[0]

    global_rows = _collect_global_metrics(run_dirs)
    event_window_rows = _collect_event_window_metrics(run_dirs)
    gate_rows = _collect_gate_metrics(run_dirs)
    graph_rows = _graph_structure_diagnostics(graph_run_dir, args.sample_origins)

    global_summary = _summarize_metric_rows(global_rows, metric="MAE")
    event_window_summary = _summarize_event_windows(event_window_rows)
    gate_summary = _summarize_gate_rows(gate_rows)
    diagnostic_rows = _diagnostic_rows(global_summary, event_window_summary, gate_summary, graph_rows)

    _write_csv(out_dir / "global_metric_summary.csv", _ordered_dict_rows(global_summary))
    _write_csv(out_dir / "event_window_delta_summary.csv", event_window_summary)
    _write_csv(out_dir / "gate_summary.csv", gate_summary)
    _write_csv(out_dir / "graph_structure_diagnostics.csv", graph_rows)
    _write_csv(out_dir / "diagnostic_answers.csv", diagnostic_rows)
    _write_report(out_dir / "EXP-103-event-graph-diagnosis.md", run_dirs, graph_run_dir, global_summary, event_window_summary, gate_summary, graph_rows, diagnostic_rows)
    print(f"wrote EXP-103 diagnostic outputs to {out_dir}")


def _discover_run_dirs(outputs_root: Path, run_glob: str, explicit_dirs: list[str]) -> list[Path]:
    dirs = [Path(value) for value in explicit_dirs]
    if not dirs:
        dirs = sorted(path for path in outputs_root.glob(run_glob) if path.is_dir())
    return [path for path in dirs if (path / "baseline_metrics.csv").exists()]


def _collect_global_metrics(run_dirs: list[Path]) -> list[dict[str, Any]]:
    rows = []
    for run_dir in run_dirs:
        config = _read_json(run_dir / "config_resolved.json")
        for row in _read_csv(run_dir / "baseline_metrics.csv"):
            row = dict(row)
            row["run_id"] = run_dir.name
            row["seed"] = config.get("seed", "")
            rows.append(row)
    return rows


def _collect_event_window_metrics(run_dirs: list[Path]) -> list[dict[str, Any]]:
    rows = []
    for run_dir in run_dirs:
        config = _read_json(run_dir / "config_resolved.json")
        for row in _read_csv(run_dir / "event_window_metrics.csv"):
            row = dict(row)
            row["run_id"] = run_dir.name
            row["seed"] = config.get("seed", "")
            rows.append(row)
    return rows


def _collect_gate_metrics(run_dirs: list[Path]) -> list[dict[str, Any]]:
    rows = []
    for run_dir in run_dirs:
        config = _read_json(run_dir / "config_resolved.json")
        for row in _read_csv(run_dir / "baseline_metrics.csv"):
            rows.append(
                {
                    "run_id": run_dir.name,
                    "seed": config.get("seed", ""),
                    "baseline_id": row.get("baseline_id", ""),
                    "gate_mean": row.get("gate_mean", ""),
                    "gate_std": row.get("gate_std", ""),
                    "graph_mode": row.get("graph_mode", ""),
                }
            )
    return rows


def _graph_structure_diagnostics(run_dir: Path, sample_origins: int) -> list[dict[str, Any]]:
    """抽样比较事件图与各类对照图的结构差异。

    这里故意只抽一部分 origin：结构诊断关注“图是否真的不同”，不是重新评估预测指标。
    抽样能把运行时间控制在可交互范围内，同时保留对不同 baseline 的相对判断。
    """

    config_path = run_dir / "config_resolved.json"
    if not config_path.exists():
        return [{"metric": "graph_diagnostics_status", "value": "missing_config", "detail": str(config_path)}]
    config = load_experiment_config(config_path)
    cache_config = config.get("cache", {})
    graph_config = config.get("graph", {})
    print(f"diagnosis: loading tensor cache from {cache_config['tensor_cache_path']}", flush=True)
    cache = load_tensor_cache(cache_config["tensor_cache_path"], cache_config.get("manifest_path"))
    origin_count = len(cache.origin_indices)
    sample_positions = _sample_positions(origin_count, sample_origins)
    sampled_origins = [cache.origin_indices[pos] for pos in sample_positions]
    top_k = min(int(graph_config.get("top_k", 5)), max(1, len(cache.nodes) - 1))
    train_end = max(cache.split_indices.get("train", []) or [cache.origin_indices[0]])
    seed = int(config.get("seed", 42))
    rng = np.random.default_rng(seed)
    print(
        f"diagnosis: building sampled event graphs origins={len(sampled_origins)} node_count={len(cache.nodes)} top_k={top_k}",
        flush=True,
    )
    event_graph = _sampled_event_graph(cache, sampled_origins, top_k, "event_graph_dynamic")
    shuffled_origin_pool = np.asarray(cache.origin_indices, dtype=int)
    rng.shuffle(shuffled_origin_pool)
    shuffled_origins = shuffled_origin_pool[: len(sampled_origins)].astype(int).tolist()
    shuffled_graph = _sampled_event_graph(cache, shuffled_origins, top_k, "shuffled_event_graph")
    historical_graph = _sampled_static_graph(
        "historical_correlation_graph",
        cache,
        _safe_positive_correlation(cache.load[: train_end + 1].T),
        top_k,
        len(sampled_origins),
    )
    random_graph = _sampled_random_graph(cache, top_k, len(sampled_origins), rng)
    deleted_graph = SampledGraph(
        "deleted_event_graph",
        event_graph.indices.copy(),
        np.zeros_like(event_graph.weights),
        cache.nodes,
        top_k,
    )
    graphs = {
        "shuffled_event_graph": shuffled_graph,
        "historical_correlation_graph": historical_graph,
        "random_event_graph": random_graph,
        "deleted_event_graph": deleted_graph,
    }
    sample_row_positions = list(range(len(sample_positions)))
    rows = [
        {"metric": "sampled_origin_count", "value": len(sample_positions), "detail": f"origin_count={origin_count}"},
        {"metric": "node_count", "value": len(cache.nodes), "detail": ""},
        {"metric": "top_k", "value": event_graph.top_k, "detail": ""},
        {
            "metric": "event_edge_entropy_mean",
            "value": _mean(_edge_entropy(event_graph, sample_row_positions)),
            "detail": "higher means event graph distributes weights more evenly across top-k neighbors",
        },
        {
            "metric": "event_adjacent_origin_edge_overlap",
            "value": _adjacent_overlap(event_graph, sample_row_positions),
            "detail": "low values mean event edges change sharply over time",
        },
    ]
    for baseline_id in ("shuffled_event_graph", "historical_correlation_graph", "random_event_graph", "deleted_event_graph"):
        baseline = graphs[baseline_id]
        pair = _pairwise_graph_distance(event_graph, baseline, sample_row_positions)
        rows.extend(
            [
                {
                    "metric": f"event_vs_{baseline_id}_edge_overlap",
                    "value": pair["edge_overlap"],
                    "detail": "mean same-neighbor overlap per source node; lower means relation semantics differ more",
                },
                {
                    "metric": f"event_vs_{baseline_id}_weight_l1",
                    "value": pair["weight_l1"],
                    "detail": "mean row-wise L1 distance; higher means weights differ more",
                },
            ]
        )
    return rows


def _sampled_event_graph(cache, origins: list[int], top_k: int, baseline_id: str) -> SampledGraph:
    """按指定 origin 构造事件动态图的抽样 top-k 邻接。"""

    node_count = len(cache.nodes)
    indices = np.zeros((len(origins), node_count, top_k), dtype=np.int32)
    weights = np.zeros((len(origins), node_count, top_k), dtype=np.float32)
    progress_interval = max(1, len(origins) // 10)
    for origin_pos, origin in enumerate(origins):
        start = max(0, origin - cache.history_steps + 1)
        features = cache.event_features[start : origin + 1].mean(axis=0)
        similarity = _cosine_similarity(_zscore(features))
        np.fill_diagonal(similarity, 0.0)
        row_indices, row_weights = _topk_sparse(similarity, top_k)
        indices[origin_pos] = row_indices
        weights[origin_pos] = row_weights
        if origin_pos == 0 or origin_pos + 1 == len(origins) or (origin_pos + 1) % progress_interval == 0:
            percent = (origin_pos + 1) / max(1, len(origins)) * 100.0
            print(f"diagnosis: {baseline_id} sampled graph {origin_pos + 1}/{len(origins)} ({percent:.1f}%)", flush=True)
    return SampledGraph(baseline_id, indices, weights, cache.nodes, top_k)


def _sampled_static_graph(baseline_id: str, cache, similarity: np.ndarray, top_k: int, origin_count: int) -> SampledGraph:
    """把静态相似度图复制到多个抽样 origin，方便与动态图使用同一距离函数比较。"""

    np.fill_diagonal(similarity, 0.0)
    similarity = np.clip(similarity, 0.0, None)
    row_indices, row_weights = _topk_sparse(similarity, top_k)
    indices = np.repeat(row_indices[np.newaxis, :, :], origin_count, axis=0).astype(np.int32)
    weights = np.repeat(row_weights[np.newaxis, :, :], origin_count, axis=0).astype(np.float32)
    return SampledGraph(baseline_id, indices, weights, cache.nodes, top_k)


def _sampled_random_graph(cache, top_k: int, origin_count: int, rng: np.random.Generator) -> SampledGraph:
    """构造随机负控图，用来回答“是不是任意稀疏图都能带来提升”。"""

    node_count = len(cache.nodes)
    indices = np.zeros((origin_count, node_count, top_k), dtype=np.int32)
    weights = np.zeros((origin_count, node_count, top_k), dtype=np.float32)
    for origin_pos in range(origin_count):
        for node_index in range(node_count):
            candidates = [index for index in range(node_count) if index != node_index]
            chosen = rng.choice(candidates, size=top_k, replace=False)
            raw = rng.random(top_k).astype(np.float32)
            indices[origin_pos, node_index] = chosen
            weights[origin_pos, node_index] = raw / raw.sum()
    return SampledGraph("random_event_graph", indices, weights, cache.nodes, top_k)


def _sample_positions(origin_count: int, sample_origins: int) -> list[int]:
    if origin_count <= sample_origins:
        return list(range(origin_count))
    return np.linspace(0, origin_count - 1, num=sample_origins, dtype=int).tolist()


def _edge_entropy(graph, positions: list[int]) -> list[float]:
    values = []
    for pos in positions:
        weights = graph.weights[pos]
        positive = weights[weights > 0]
        if positive.size == 0:
            continue
        values.append(float(-(positive * np.log(positive + 1e-12)).sum() / positive.size))
    return values


def _adjacent_overlap(graph, positions: list[int]) -> float:
    overlaps = []
    last_pos = None
    for pos in positions:
        if last_pos is None:
            last_pos = pos
            continue
        overlaps.append(_origin_edge_overlap(graph.indices[last_pos], graph.indices[pos], graph.weights[last_pos], graph.weights[pos]))
        last_pos = pos
    return _mean(overlaps)


def _pairwise_graph_distance(left_graph, right_graph, positions: list[int]) -> dict[str, float]:
    """计算两个抽样图在邻居集合和边权上的平均距离。"""

    overlaps = []
    l1_values = []
    for pos in positions:
        right_pos = min(pos, right_graph.indices.shape[0] - 1)
        overlaps.append(_origin_edge_overlap(left_graph.indices[pos], right_graph.indices[right_pos], left_graph.weights[pos], right_graph.weights[right_pos]))
        l1_values.append(_origin_l1(left_graph.indices[pos], right_graph.indices[right_pos], left_graph.weights[pos], right_graph.weights[right_pos], len(left_graph.nodes)))
    return {"edge_overlap": _mean(overlaps), "weight_l1": _mean(l1_values)}


def _origin_edge_overlap(left_indices: np.ndarray, right_indices: np.ndarray, left_weights: np.ndarray, right_weights: np.ndarray) -> float:
    overlaps = []
    for row in range(left_indices.shape[0]):
        left = {int(value) for value, weight in zip(left_indices[row], left_weights[row]) if float(weight) > 0.0}
        right = {int(value) for value, weight in zip(right_indices[row], right_weights[row]) if float(weight) > 0.0}
        denom = max(1, min(len(left), len(right)))
        overlaps.append(len(left & right) / denom)
    return _mean(overlaps)


def _origin_l1(left_indices: np.ndarray, right_indices: np.ndarray, left_weights: np.ndarray, right_weights: np.ndarray, node_count: int) -> float:
    values = []
    for row in range(left_indices.shape[0]):
        left = np.zeros(node_count, dtype=np.float32)
        right = np.zeros(node_count, dtype=np.float32)
        left[left_indices[row]] = left_weights[row]
        right[right_indices[row]] = right_weights[row]
        values.append(float(np.abs(left - right).sum()))
    return _mean(values)


def _safe_positive_correlation(values: np.ndarray) -> np.ndarray:
    centered = values - values.mean(axis=1, keepdims=True)
    norm = np.linalg.norm(centered, axis=1, keepdims=True)
    normalized = np.divide(centered, norm, out=np.zeros_like(centered), where=norm > 0)
    return np.clip(normalized @ normalized.T, 0.0, None)


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


def _summarize_metric_rows(rows: list[dict[str, Any]], metric: str) -> dict[str, dict[str, Any]]:
    by_baseline: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        baseline = str(row.get("baseline_id", ""))
        value = _to_float_or_none(row.get(metric))
        if baseline and value is not None and math.isfinite(value):
            by_baseline[baseline].append(value)
    summary = {}
    for baseline in GLOBAL_BASELINES:
        values = by_baseline.get(baseline, [])
        if values:
            summary[baseline] = {
                "baseline_id": baseline,
                "run_count": len(values),
                f"{metric}_mean": _mean(values),
                f"{metric}_std": _std(values),
                f"{metric}_min": min(values),
                f"{metric}_max": max(values),
            }
    return summary


def _summarize_event_windows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        baseline = str(row.get("baseline_id", ""))
        window = str(row.get("event_window", ""))
        value = _to_float_or_none(row.get("MAE"))
        if baseline and window and value is not None:
            grouped[(window, baseline)].append(value)
    windows = sorted({window for window, _ in grouped})
    out = []
    for window in windows:
        event = _mean(grouped.get((window, "event_graph_dynamic"), []))
        if event == "":
            continue
        row: dict[str, Any] = {"event_window": window, "event_MAE": event}
        best_baseline = "event_graph_dynamic"
        best_value = float(event)
        for baseline in ("behavior_concat", "dtw_demand_graph", "historical_correlation_graph", "random_event_graph", "shuffled_event_graph"):
            value = _mean(grouped.get((window, baseline), []))
            row[f"{baseline}_MAE"] = value
            row[f"event_vs_{baseline}_delta"] = _delta(float(event), value)
            if value != "" and float(value) < best_value:
                best_baseline = baseline
                best_value = float(value)
        row["best_baseline"] = best_baseline
        row["event_rank_signal"] = "best" if best_baseline == "event_graph_dynamic" else f"behind_{best_baseline}"
        out.append(row)
    return out


def _summarize_gate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, float]]] = defaultdict(list)
    graph_mode = {}
    for row in rows:
        baseline = str(row.get("baseline_id", ""))
        mean = _to_float_or_none(row.get("gate_mean"))
        std = _to_float_or_none(row.get("gate_std"))
        if baseline and mean is not None and math.isfinite(mean):
            grouped[baseline].append({"gate_mean": mean, "gate_std": std or 0.0})
            graph_mode[baseline] = row.get("graph_mode", "")
    out = []
    for baseline, values in sorted(grouped.items()):
        out.append(
            {
                "baseline_id": baseline,
                "run_count": len(values),
                "graph_mode": graph_mode.get(baseline, ""),
                "gate_mean_mean": _mean([value["gate_mean"] for value in values]),
                "gate_mean_std": _std([value["gate_mean"] for value in values]),
                "gate_std_mean": _mean([value["gate_std"] for value in values]),
            }
        )
    return out


def _diagnostic_rows(
    global_summary: dict[str, dict[str, Any]],
    event_window_summary: list[dict[str, Any]],
    gate_summary: list[dict[str, Any]],
    graph_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    graph = {row["metric"]: row["value"] for row in graph_rows if "metric" in row}
    gate = {row["baseline_id"]: row for row in gate_summary if "baseline_id" in row}
    event_mean = _summary_value(global_summary, "event_graph_dynamic", "MAE_mean")
    shuffled_mean = _summary_value(global_summary, "shuffled_event_graph", "MAE_mean")
    historical_mean = _summary_value(global_summary, "historical_correlation_graph", "MAE_mean")
    behavior_mean = _summary_value(global_summary, "behavior_concat", "MAE_mean")
    dtw_mean = _summary_value(global_summary, "dtw_demand_graph", "MAE_mean")
    event_wins = [row for row in event_window_summary if row.get("best_baseline") == "event_graph_dynamic"]
    return [
        {
            "question_id": "Q1",
            "diagnostic": "event_vs_shuffled_structure",
            "value": graph.get("event_vs_shuffled_event_graph_edge_overlap", ""),
            "interpretation": "若 edge overlap 不低，shuffled 仍保留了大量动态图拓扑预算；若很低但性能接近，模型可能只吃到图聚合正则而非事件语义。",
        },
        {
            "question_id": "Q1",
            "diagnostic": "event_vs_historical_structure",
            "value": graph.get("event_vs_historical_correlation_graph_edge_overlap", ""),
            "interpretation": "该值描述事件边与历史相关边的邻居重合度；低重合但 historical 更强，说明长期负荷相似性仍是强信号。",
        },
        {
            "question_id": "Q2",
            "diagnostic": "event_gate_mean",
            "value": gate.get("event_graph_dynamic", {}).get("gate_mean_mean", ""),
            "interpretation": "gate 均值很低表示 gated_residual 主动压低图分支，事件语义难以充分进入预测头。",
        },
        {
            "question_id": "Q3",
            "diagnostic": "event_window_wins",
            "value": len(event_wins),
            "interpretation": f"event_graph_dynamic 在 {len(event_wins)} 个事件窗口平均 MAE 最优；窗口级优势决定 C2/C3 是否更适合发力。",
        },
        {
            "question_id": "Q4",
            "diagnostic": "global_mae_order",
            "value": json.dumps(
                {
                    "historical": historical_mean,
                    "event": event_mean,
                    "shuffled": shuffled_mean,
                    "behavior": behavior_mean,
                    "dtw": dtw_mean,
                },
                ensure_ascii=False,
            ),
            "interpretation": "若 historical 全局领先，说明长期站点相似性是强基线；事件图需要改成短时扰动补充或加事件窗口加权。",
        },
    ]


def _write_report(
    path: Path,
    run_dirs: list[Path],
    graph_run_dir: Path,
    global_summary: dict[str, dict[str, Any]],
    event_window_summary: list[dict[str, Any]],
    gate_summary: list[dict[str, Any]],
    graph_rows: list[dict[str, Any]],
    diagnostic_rows: list[dict[str, Any]],
) -> None:
    lines = [
        "# EXP-103 Event Graph Diagnosis",
        "",
        "## Inputs",
        "",
        f"- Run dirs: {', '.join(path.name for path in run_dirs)}",
        f"- Graph diagnostic config: `{graph_run_dir}`",
        "",
        "## 1. Global Baseline Ranking",
        "",
        "| baseline | run_count | MAE_mean | MAE_std |",
        "|---|---:|---:|---:|",
    ]
    for _, row in sorted(global_summary.items(), key=lambda item: item[1].get("MAE_mean", float("inf"))):
        lines.append(
            f"| {row['baseline_id']} | {row['run_count']} | {_fmt(row.get('MAE_mean'))} | {_fmt(row.get('MAE_std'))} |"
        )
    lines.extend(["", "## 2. Four Diagnostic Questions", ""])
    for row in diagnostic_rows:
        lines.append(f"- **{row['question_id']} {row['diagnostic']}**: `{row['value']}`. {row['interpretation']}")
    lines.extend(["", "## 3. Event Window Summary", ""])
    lines.append("| event_window | best_baseline | event_MAE | event_vs_historical_delta | event_vs_shuffled_delta |")
    lines.append("|---|---|---:|---:|---:|")
    for row in event_window_summary:
        lines.append(
            "| {event_window} | {best_baseline} | {event_MAE} | {hist} | {shuf} |".format(
                event_window=row["event_window"],
                best_baseline=row["best_baseline"],
                event_MAE=_fmt(row.get("event_MAE")),
                hist=_fmt(row.get("event_vs_historical_correlation_graph_delta")),
                shuf=_fmt(row.get("event_vs_shuffled_event_graph_delta")),
            )
        )
    lines.extend(["", "## 4. Gate Summary", ""])
    lines.append("| baseline | graph_mode | gate_mean_mean | gate_std_mean |")
    lines.append("|---|---|---:|---:|")
    for row in gate_summary:
        lines.append(
            f"| {row['baseline_id']} | {row.get('graph_mode', '')} | {_fmt(row.get('gate_mean_mean'))} | {_fmt(row.get('gate_std_mean'))} |"
        )
    lines.extend(["", "## 5. Graph Structure Diagnostics", ""])
    lines.append("| metric | value | detail |")
    lines.append("|---|---:|---|")
    for row in graph_rows:
        lines.append(f"| {row.get('metric', '')} | {_fmt(row.get('value'))} | {row.get('detail', '')} |")
    lines.extend(
        [
            "",
            "## Initial Engineering Implications",
            "",
            "1. If gate_mean is near zero, run `graph_mode=concat` and consider gate regularization or a stronger event branch.",
            "2. If shuffled remains close despite low edge overlap, add event-window weighted loss and semantic edge-channel separation.",
            "3. If historical dominates globally, model historical graph as long-term structure and event graph as short-term residual rather than forcing replacement.",
            "4. If event wins selected windows, prioritize those windows in EXP-103-v3 and later EXP-105 risk proxy.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _ordered_dict_rows(summary: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for _, row in sorted(summary.items(), key=lambda item: item[1].get("MAE_mean", float("inf")))]


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = sorted({key for row in rows for key in row}) if rows else DIAG_COLUMNS
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _to_float_or_none(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _mean(values: list[float]) -> float | str:
    return sum(values) / len(values) if values else ""


def _std(values: list[float]) -> float | str:
    if not values:
        return ""
    if len(values) == 1:
        return 0.0
    mean = sum(values) / len(values)
    return (sum((value - mean) ** 2 for value in values) / (len(values) - 1)) ** 0.5


def _delta(event_mae: float, comparator_mae: float | str) -> float | str:
    if comparator_mae == "":
        return ""
    return float(comparator_mae) - event_mae


def _summary_value(summary: dict[str, dict[str, Any]], baseline: str, key: str) -> float | str:
    return summary.get(baseline, {}).get(key, "")


def _fmt(value: Any) -> str:
    try:
        return f"{float(value):.6f}"
    except (TypeError, ValueError):
        return str(value)


if __name__ == "__main__":
    main()
