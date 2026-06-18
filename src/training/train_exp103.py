from __future__ import annotations

"""EXP-103 图事件预测实验训练入口。

这个脚本是 v3/v4/v5 正式 GPU 证据的统一训练器。它的设计目标不是只跑出一个模型，
而是在同一数据 split、同一训练预算、同一指标口径下顺序训练一组 baseline，
并把每个 baseline 的结果写成可审计的 evidence 表。

关键输出文件：

- `config_resolved.json`: 本次 run 实际使用的完整配置。
- `graph_manifest.json`: 每个 baseline 的图结构、top-k、因果边界和通道信息。
- `primary_metric_summary.csv`: 论文主表，按 test MAE 排名。
- `baseline_deltas.csv`: 与行为拼接、DTW、历史相关等 comparator 的直接差值。
- `event_window_metrics.csv`: 事件窗口内 MAE/RMSE，用来判断事件图是否在事件状态下更有价值。
- `graph_gate_metrics.csv` / `residual_diagnostics.csv`: gate 和 residual 的解释性诊断。
- `training_dashboard.html`: 长跑训练时的轻量可视化进度面板。

正式结论优先引用 test MAE；RMSE 用作大误差和尾部风险的补充诊断。
"""

import argparse
import csv
import gzip
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

try:
    import torch
    from torch import nn
    from torch.utils.data import DataLoader
except Exception as exc:  # pragma: no cover - local Mac may intentionally skip torch
    torch = None
    nn = None
    DataLoader = None
    TORCH_IMPORT_ERROR = exc
else:
    TORCH_IMPORT_ERROR = None

from evcs.data.event_windows import build_event_loss_weights, event_window_masks
from evcs.data.tensor_cache import build_tensor_cache, load_tensor_cache, save_tensor_cache
from evcs.data.window_dataset import EVCSWindowDataset
from evcs.graphs.cache import build_exp103_graph_cache
from evcs.models.graph_tcn import GraphTemporalTCN, compute_receptive_field
from evcs.utils.artifacts import write_json, write_manifest
from evcs.utils.config import load_experiment_config

DEFAULT_BASELINES = [
    "no_graph",
    "behavior_concat",
    "event_graph_dynamic",
    "dtw_demand_graph",
    "historical_correlation_graph",
    "random_event_graph",
    "shuffled_event_graph",
    "deleted_event_graph",
]

CHECKPOINT_METRICS = {"validation_loss", "val_MAE_raw", "val_RMSE_raw"}
FULL_PREDICTION_COLUMNS = [
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
    """读取配置、构图、逐 baseline 训练，并写出 EXP-103 evidence。"""

    if torch is None or nn is None or DataLoader is None:
        raise SystemExit(f"PyTorch is required for EXP-103 training: {TORCH_IMPORT_ERROR}")
    parser = argparse.ArgumentParser(description="Train EXP-103 Graph-TCN graph ablation baselines.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    config = load_experiment_config(args.config)
    _attach_model_contract(config)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "logs").mkdir(parents=True, exist_ok=True)
    (out_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "config_resolved.json", config)
    _write_environment(out_dir / "environment.txt")

    seed = int(config.get("seed", 42))
    _set_seed(seed)
    # tensor cache 是所有 baseline 的共同输入，只有 manifest 与配置匹配时才复用，
    # 防止 history/horizon/event feature 开关变化后误读旧缓存。
    cache = _load_or_build_cache(config)
    baseline_ids = list(config.get("baselines", DEFAULT_BASELINES))
    # 带 _v4/_v5 后缀的 baseline 会映射回同一个图构造入口；
    # 后缀只代表实验版本身份，不改变底层图语义。
    graph_baseline_ids = list(dict.fromkeys(_canonical_exp103_baseline_id(baseline_id) for baseline_id in baseline_ids))
    graph_config = config.get("graph", {})
    graphs = build_exp103_graph_cache(
        cache,
        baseline_ids=graph_baseline_ids,
        top_k=int(graph_config.get("top_k", 5)),
        seed=seed,
        dtw_max_points=int(graph_config["dtw_max_points"]) if graph_config.get("dtw_max_points") else None,
        rho=float(graph_config.get("rho", 0.0)),
        lambda_event=float(graph_config.get("lambda_event", 0.3)),
        dtw_cache_path=graph_config.get("dtw_cache_path"),
        verbose=bool(graph_config.get("verbose", True)),
    )
    write_json(
        out_dir / "graph_manifest.json",
        {
            "experiment_id": str(config.get("experiment_id", "EXP-103")),
            "graph_contract": {
                "top_k": int(graph_config.get("top_k", 5)),
                "rho": float(graph_config.get("rho", 0.0)),
                "lambda_event": float(graph_config.get("lambda_event", 0.3)),
                "dtw_cache_path": str(graph_config.get("dtw_cache_path", "")),
                "causal_static_graph_policy": "dtw/correlation use train split load only",
                "causal_dynamic_graph_policy": "event graph uses each origin history window only",
            },
            "graphs": {baseline_id: graph.manifest() for baseline_id, graph in graphs.items()},
            "requested_baselines": baseline_ids,
            "graph_baselines": graph_baseline_ids,
        },
    )

    training_config = config.get("training", {})
    device = _resolve_device(str(training_config.get("device", "auto")))
    log_lines = [f"device={device}", f"baselines={','.join(baseline_ids)}"]
    baseline_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    horizon_rows: list[dict[str, Any]] = []
    gate_rows: list[dict[str, Any]] = []
    residual_rows: list[dict[str, Any]] = []
    event_loss_rows: list[dict[str, Any]] = []
    curve_rows: list[dict[str, Any]] = []
    sample_rows: list[dict[str, Any]] = []
    metrics_by_baseline: dict[str, dict[str, Any]] = {}
    for baseline_id in baseline_ids:
        print(f"training EXP-103 baseline: {baseline_id}", flush=True)
        train_result = _train_one_baseline(
            baseline_id,
            config,
            cache,
            graphs[_canonical_exp103_baseline_id(baseline_id)],
            device,
            out_dir / "checkpoints" / f"best_{baseline_id}.pt",
            log_lines,
            out_dir,
            baseline_ids,
        )
        baseline_rows.append(train_result["metrics"])
        event_rows.extend(train_result["event_metrics"])
        horizon_rows.extend(train_result["horizon_metrics"])
        gate_rows.extend(train_result["gate_metrics"])
        residual_rows.extend(train_result["residual_metrics"])
        event_loss_rows.extend(train_result["event_loss_metrics"])
        curve_rows.extend(train_result["curves"])
        sample_rows.extend(train_result["samples"])
        metrics_by_baseline[baseline_id] = train_result["metrics"]
        log_lines.append(f"{baseline_id}: test_MAE={train_result['metrics']['MAE']:.6f}")
        # 每个 baseline 完成后立即刷新 dashboard 和 CSV；远程训练中断时也能保留已完成证据。
        _write_training_dashboard(
            out_dir / "training_dashboard.html",
            curve_rows,
            baseline_rows,
            baseline_ids,
            active_baseline=None,
            refresh_seconds=int(config.get("progress", {}).get("refresh_seconds", 10)),
        )
        _write_exp103_tables(out_dir, baseline_rows, event_rows, horizon_rows, gate_rows, residual_rows, event_loss_rows, curve_rows, sample_rows, metrics_by_baseline)

    _write_exp103_tables(out_dir, baseline_rows, event_rows, horizon_rows, gate_rows, residual_rows, event_loss_rows, curve_rows, sample_rows, metrics_by_baseline)
    write_json(out_dir / "metrics.json", {"experiment_id": "EXP-103", "baselines": metrics_by_baseline})
    _write_run_manifest(out_dir, config, args.config, args.out, status="completed")
    (out_dir / "exit_code.txt").write_text("0\n", encoding="utf-8")
    (out_dir / "metric_guide.md").write_text(_metric_guide_text(), encoding="utf-8")
    (out_dir / "logs" / "train.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    _write_checksums(out_dir)
    artifacts = [
        "metrics.json",
        "primary_metric_summary.csv",
        "baseline_metrics.csv",
        "graph_ablation_table.csv",
        "baseline_deltas.csv",
        "event_window_metrics.csv",
        "horizon_metrics.csv",
        "graph_gate_metrics.csv",
        "residual_diagnostics.csv",
        "event_loss_diagnostics.csv",
        "graph_manifest.json",
        "training_curves.csv",
        "predictions_sample.csv",
        "config_resolved.json",
        "environment.txt",
        "run_manifest.json",
        "exit_code.txt",
        "checksums.sha256",
        "metric_guide.md",
        "training_dashboard.html",
        "logs/progress_events.jsonl",
        "logs/train.log",
    ]
    if bool(config.get("training", {}).get("write_full_predictions", False)):
        predictions_dir = out_dir / "predictions_full"
        artifacts.extend(
            str(path.relative_to(out_dir))
            for path in sorted(predictions_dir.glob("*.csv.gz"))
        )
    write_manifest(out_dir, str(config.get("experiment_id", "EXP-103")), artifacts)
    print(f"wrote EXP-103 training outputs to {out_dir}")


def _load_or_build_cache(config: dict[str, Any]):
    """加载或按配置构建 tensor cache。

    训练缓存固定节点顺序、滑动窗口 origin、train/validation/test split、
    标准化统计量和事件特征列。正式训练默认不悄悄重建，除非配置显式允许
    `cache.auto_build=true`。
    """

    data_config = config.get("data", {})
    cache_config = config.get("cache", {})
    feature_config = config.get("features", {})
    cache_path = Path(str(cache_config.get("tensor_cache_path", "data/processed/evcs_tensor_cache.npz")))
    manifest_path = Path(str(cache_config.get("manifest_path", "data/processed/evcs_tensor_cache_manifest.json")))
    split_path = Path(str(cache_config.get("split_path", "data/processed/splits/chronological_70_15_15.json")))
    should_build = not cache_path.exists()
    if cache_path.exists() and not _tensor_cache_manifest_matches(manifest_path, cache_config, feature_config):
        if not bool(cache_config.get("auto_build", False)):
            raise ValueError(f"tensor cache manifest does not match config and auto_build is false: {manifest_path}")
        should_build = True
    if should_build:
        if not bool(cache_config.get("auto_build", False)):
            raise FileNotFoundError(f"tensor cache not found: {cache_path}")
        frame = pd.read_csv(Path(str(data_config["source_path"])))
        cache = build_tensor_cache(
            frame,
            timestamp_field=str(data_config.get("timestamp_field", "timestamp")),
            node_field=str(data_config.get("node_field", "node_id")),
            target_field=str(data_config.get("target_field", "load")),
            event_feature_fields=list(config.get("graph", {}).get("event_feature_fields", [])),
            history_steps=int(cache_config.get("history_steps", 96)),
            horizon_steps=int(cache_config.get("horizon_steps", 4)),
            split_rule=dict(cache_config.get("split_rule", {"train": 0.7, "validation": 0.15, "test": 0.15})),
            include_time_context=bool(feature_config.get("include_time_context", False)),
            include_enhanced_events=bool(feature_config.get("include_enhanced_events", False)),
            near_capacity_quantile=float(feature_config.get("near_capacity_quantile", 0.9)),
        )
        save_tensor_cache(cache, cache_path, split_path, manifest_path)
    return load_tensor_cache(cache_path, manifest_path)


def _tensor_cache_manifest_matches(manifest_path: Path, cache_config: dict[str, Any], feature_config: dict[str, Any]) -> bool:
    """检查缓存 manifest 是否与当前配置兼容。"""

    if not manifest_path.exists():
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    feature_manifest = manifest.get("feature_engineering", {}) if isinstance(manifest.get("feature_engineering", {}), dict) else {}
    return (
        int(manifest.get("history_steps", -1)) == int(cache_config.get("history_steps", 96))
        and int(manifest.get("horizon_steps", -1)) == int(cache_config.get("horizon_steps", 4))
        and bool(feature_manifest.get("include_time_context", False)) == bool(feature_config.get("include_time_context", False))
        and bool(feature_manifest.get("include_enhanced_events", False)) == bool(feature_config.get("include_enhanced_events", False))
    )


def _train_one_baseline(
    baseline_id: str,
    config: dict[str, Any],
    cache,
    graph,
    device,
    checkpoint_path: Path,
    log_lines: list[str],
    out_dir: Path,
    baseline_ids: list[str],
) -> dict[str, Any]:
    """训练单个 baseline 并返回所有 evidence 行。

    同一个函数处理 proposed model 和对照模型，确保 loader、optimizer、loss、
    early stopping、test evaluation 与输出表完全一致。这样 MAE/RMSE 差异更能归因于
    `use_events`、`use_graph`、`graph_mode` 和具体图结构，而不是训练流程差异。
    """

    training_config = config.get("training", {})
    canonical_baseline_id = _canonical_exp103_baseline_id(baseline_id)
    # baseline 身份到输入开关的映射：
    # no_graph 不看事件也不用图；behavior_concat 看事件但不用图；
    # 其余 graph baselines 同时使用事件特征和对应图结构。
    use_events = canonical_baseline_id != "no_graph"
    use_graph = canonical_baseline_id not in {"no_graph", "behavior_concat"}
    loss_weight_config = config.get("loss_weighting", {})
    context_config = config.get("context_features", {})
    normalization_config = config.get("normalization", {"mode": "zscore"})
    train_dataset = EVCSWindowDataset(
        cache,
        "train",
        graph,
        use_events=use_events,
        normalize=True,
        loss_weight_config=loss_weight_config,
        context_config=context_config,
        normalization_config=normalization_config,
    )
    val_dataset = EVCSWindowDataset(
        cache,
        "validation",
        graph,
        use_events=use_events,
        normalize=True,
        loss_weight_config=loss_weight_config,
        context_config=context_config,
        normalization_config=normalization_config,
    )
    test_dataset = EVCSWindowDataset(
        cache,
        "test",
        graph,
        use_events=use_events,
        normalize=True,
        loss_weight_config=loss_weight_config,
        context_config=context_config,
        normalization_config=normalization_config,
    )
    batch_size = int(training_config.get("batch_size", 128))
    workers = int(training_config.get("num_workers", 0))
    graph_mode = _graph_mode_for_baseline(training_config, baseline_id)
    pin_memory = bool(training_config.get("pin_memory", False)) and device.type == "cuda"
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=workers, pin_memory=pin_memory)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=workers, pin_memory=pin_memory)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=workers, pin_memory=pin_memory)
    setup_line = (
        f"[{baseline_id}] setup train={len(train_dataset)} val={len(val_dataset)} test={len(test_dataset)} "
        f"train_batches={len(train_loader)} val_batches={len(val_loader)} test_batches={len(test_loader)} "
        f"batch_size={batch_size} num_workers={workers} use_events={use_events} use_graph={use_graph} graph_mode={graph_mode}"
    )
    log_lines.append(setup_line)
    if bool(training_config.get("verbose", True)):
        print(setup_line, flush=True)
    model = GraphTemporalTCN(
        load_channels=1,
        event_channels=len(cache.event_feature_names) if use_events else 0,
        hidden_channels=int(training_config.get("hidden_channels", 64)),
        tcn_layers=int(training_config.get("tcn_layers", 4)),
        kernel_size=int(training_config.get("kernel_size", 3)),
        dropout=float(training_config.get("dropout", 0.1)),
        horizon_steps=cache.horizon_steps,
        use_events=use_events,
        use_graph=use_graph,
        graph_mode=graph_mode,
        graph_channel_count=len(graph.channel_names or []),
        branch_alpha_init=float(training_config.get("branch_alpha_init", 0.2)),
        temporal_block=str(training_config.get("temporal_block", "residual")),
        dilation_schedule=list(training_config.get("dilation_schedule", [])) if training_config.get("dilation_schedule") else None,
        graph_message_stage=str(training_config.get("graph_message_stage", "raw_history")),
        event_context_channels=_event_context_channel_count(context_config),
        node_count=len(cache.nodes),
        node_embedding_dim=int(training_config.get("node_embedding_dim", 0)),
        residual_clip=float(training_config.get("residual_clip", 0.0)),
        event_gate_init_bias=training_config.get("event_gate_init_bias"),
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(training_config.get("lr", 1e-3)))
    scheduler = _make_scheduler(optimizer, training_config)
    criterion = nn.SmoothL1Loss(reduction="none") if str(training_config.get("loss", "SmoothL1")).lower() == "smoothl1" else nn.L1Loss(reduction="none")
    use_amp = bool(training_config.get("amp", False)) and device.type == "cuda"
    scaler = _make_grad_scaler(use_amp)
    epochs = int(training_config.get("epochs", 20))
    patience = int(training_config.get("early_stopping_patience", 4))
    early_stop_min_epochs = _early_stopping_min_epochs(training_config, baseline_id, epochs)
    checkpoint_metric = _checkpoint_metric(training_config)
    verbose = bool(training_config.get("verbose", True))
    progress_config = config.get("progress", {})
    terminal_progress = bool(progress_config.get("terminal_bar", True))
    live_html = bool(progress_config.get("live_html", True))
    refresh_seconds = int(progress_config.get("refresh_seconds", 10))
    best_val = float("inf")
    best_checkpoint_score = float("inf")
    best_validation_mae = float("inf")
    best_validation_rmse = float("inf")
    stale_epochs = 0
    curve_rows = []
    baseline_started_at = time.perf_counter()
    best_epoch = 0
    for epoch in range(1, epochs + 1):
        epoch_started_at = time.perf_counter()
        train_loss = _run_epoch(model, train_loader, criterion, optimizer, scaler, device, config, train=True, use_amp=use_amp)
        val_loss = _run_epoch(model, val_loader, criterion, None, scaler, device, config, train=False, use_amp=use_amp)
        if checkpoint_metric == "validation_loss":
            # 旧实验默认仍以 validation loss 保存 checkpoint。此时不额外跑 raw-scale
            # 预测评估，避免无意中把历史训练时间放大；曲线中保留列但写 NaN。
            val_mae_raw = float("nan")
            val_rmse_raw = float("nan")
        else:
            val_eval_payload = _evaluate(
                model,
                val_loader,
                device,
                cache,
                loss_weight_config,
                graph,
                config.get("event_loss", {}),
                split_name="validation",
            )
            val_mae_raw = float(val_eval_payload["MAE"])
            val_rmse_raw = float(val_eval_payload["RMSE"])
        # V5 Plus 允许用 raw-scale validation MAE/RMSE 选择 checkpoint。
        # 训练 loss 可能包含 SmoothL1、事件窗口权重和 gate 正则项，它对优化有帮助，
        # 但论文主结论锁定 MAE 时，best checkpoint 应可选择与主指标一致的验证指标。
        checkpoint_score = _checkpoint_score(checkpoint_metric, val_loss, val_mae_raw, val_rmse_raw)
        if scheduler is not None:
            scheduler.step(val_loss)
        current_lr = float(optimizer.param_groups[0]["lr"])
        epoch_seconds = time.perf_counter() - epoch_started_at
        improved = checkpoint_score < best_checkpoint_score
        best_val_display = min(best_val, val_loss)
        best_checkpoint_display = min(best_checkpoint_score, checkpoint_score)
        curve_rows.append(
            {
                "baseline_id": baseline_id,
                "epoch": epoch,
                "epochs": epochs,
                "train_loss": train_loss,
                "validation_loss": val_loss,
                "best_validation_loss": best_val_display,
                "val_MAE_raw": val_mae_raw,
                "val_RMSE_raw": val_rmse_raw,
                "checkpoint_metric": checkpoint_metric,
                "checkpoint_score": checkpoint_score,
                "best_checkpoint_score": best_checkpoint_display,
                "improved": improved,
                "epoch_seconds": epoch_seconds,
                "lr": current_lr,
                "early_stop_min_epochs": early_stop_min_epochs,
            }
        )
        progress_line = _format_epoch_progress(
            baseline_id,
            epoch,
            epochs,
            train_loss,
            val_loss,
            best_checkpoint_display,
            current_lr,
            epoch_seconds,
            curve_rows,
            improved=improved,
            terminal_bar=terminal_progress,
        )
        log_lines.append(progress_line)
        if verbose:
            print(progress_line, flush=True)
        _append_progress_event(
            out_dir / "logs" / "progress_events.jsonl",
            {
                "event": "epoch",
                "baseline_id": baseline_id,
                "epoch": epoch,
                "epochs": epochs,
                "train_loss": train_loss,
                "validation_loss": val_loss,
                "best_validation_loss": best_val_display,
                "val_MAE_raw": val_mae_raw,
                "val_RMSE_raw": val_rmse_raw,
                "checkpoint_metric": checkpoint_metric,
                "checkpoint_score": checkpoint_score,
                "best_checkpoint_score": best_checkpoint_display,
                "lr": current_lr,
                "epoch_seconds": epoch_seconds,
                "improved": improved,
            },
        )
        if live_html:
            _write_training_dashboard(
                out_dir / "training_dashboard.html",
                curve_rows,
                [],
                baseline_ids,
                active_baseline=baseline_id,
                refresh_seconds=refresh_seconds,
            )
        best_val = min(best_val, val_loss)
        if improved:
            # 只保存 validation 指标最优 checkpoint；test set 在训练结束后统一评估一次。
            # 这里绝不读取 test 指标做选择，避免把测试集变成调参集。
            best_checkpoint_score = checkpoint_score
            best_validation_mae = val_mae_raw
            best_validation_rmse = val_rmse_raw
            best_epoch = epoch
            stale_epochs = 0
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "config": config,
                    "baseline_id": baseline_id,
                    "checkpoint_metric": checkpoint_metric,
                    "checkpoint_score": checkpoint_score,
                },
                checkpoint_path,
            )
        else:
            stale_epochs += 1
            if stale_epochs >= patience and epoch >= early_stop_min_epochs:
                stop_line = (
                    f"[{baseline_id}] early_stop epoch={epoch} patience={patience} "
                    f"min_epochs={early_stop_min_epochs}"
                )
                log_lines.append(stop_line)
                if verbose:
                    print(stop_line, flush=True)
                break
    if checkpoint_path.exists():
        state = _load_checkpoint(checkpoint_path, device)
        model.load_state_dict(state["model_state_dict"])
    validation_eval_payload = _evaluate(
        model,
        val_loader,
        device,
        cache,
        loss_weight_config,
        graph,
        config.get("event_loss", {}),
        split_name="validation",
    )
    if not math.isfinite(best_validation_mae):
        best_validation_mae = float(validation_eval_payload["MAE"])
    if not math.isfinite(best_validation_rmse):
        best_validation_rmse = float(validation_eval_payload["RMSE"])
    if not math.isfinite(best_checkpoint_score):
        best_checkpoint_score = float(best_val)
    # 所有报告指标都来自 best checkpoint 在 test split 上的预测，避免使用最后一轮偶然波动。
    eval_payload = _evaluate(
        model,
        test_loader,
        device,
        cache,
        loss_weight_config,
        graph,
        config.get("event_loss", {}),
        split_name="test",
    )
    if bool(training_config.get("write_full_predictions", False)):
        predictions_dir = out_dir / "predictions_full"
        _write_full_predictions_gzip(predictions_dir / f"validation_{baseline_id}.csv.gz", baseline_id, seed=int(config.get("seed", 42)), split_name="validation", eval_payload=validation_eval_payload, cache=cache)
        _write_full_predictions_gzip(predictions_dir / f"test_{baseline_id}.csv.gz", baseline_id, seed=int(config.get("seed", 42)), split_name="test", eval_payload=eval_payload, cache=cache)
    baseline_seconds = time.perf_counter() - baseline_started_at
    metrics = {
        "baseline_id": baseline_id,
        "MAE": eval_payload["MAE"],
        "RMSE": eval_payload["RMSE"],
        "event_weighted_MAE": eval_payload["event_weighted_MAE"],
        "prediction_count": eval_payload["prediction_count"],
        "best_validation_loss": best_val,
        "weighted_validation_loss": best_val,
        "best_checkpoint_metric": checkpoint_metric,
        "best_checkpoint_score": best_checkpoint_score,
        "best_validation_MAE": best_validation_mae,
        "best_validation_RMSE": best_validation_rmse,
        "best_epoch": best_epoch,
        "epochs_ran": len(curve_rows),
        "early_stop_min_epochs": early_stop_min_epochs,
        "train_seconds": baseline_seconds,
        "uses_events": use_events,
        "uses_graph": use_graph,
        "graph_mode": graph_mode,
        "temporal_block": str(training_config.get("temporal_block", "residual")),
        "graph_message_stage": str(training_config.get("graph_message_stage", "raw_history")),
        "receptive_field": int(config.get("model_contract", {}).get("receptive_field", 0)),
        "gate_mean": eval_payload["gate_mean"],
        "gate_std": eval_payload["gate_std"],
        "event_gate_event_window_mean": eval_payload["event_gate_event_window_mean"],
        "event_gate_stable_window_mean": eval_payload["event_gate_stable_window_mean"],
        "alpha_hist": eval_payload["alpha_hist"],
        "alpha_event": eval_payload["alpha_event"],
        "event_residual_clip_rate": eval_payload["event_residual_clip_rate"],
    }
    metrics.update(eval_payload["channel_weights"])
    summary_line = (
        f"[{baseline_id}] test MAE={metrics['MAE']:.6f} RMSE={metrics['RMSE']:.6f} "
        f"best_epoch={best_epoch} epochs_ran={len(curve_rows)} seconds={baseline_seconds:.1f}"
    )
    log_lines.append(summary_line)
    if verbose:
        print(summary_line, flush=True)
    _append_progress_event(
        out_dir / "logs" / "progress_events.jsonl",
        {
            "event": "baseline_complete",
            "baseline_id": baseline_id,
            "MAE": metrics["MAE"],
            "RMSE": metrics["RMSE"],
            "best_epoch": best_epoch,
            "epochs_ran": len(curve_rows),
            "train_seconds": baseline_seconds,
        },
    )
    return {
        "metrics": metrics,
        "event_metrics": _event_window_metrics(baseline_id, eval_payload, cache),
        "horizon_metrics": _horizon_metrics(baseline_id, eval_payload, cache),
        "gate_metrics": _graph_gate_metrics(baseline_id, eval_payload, cache),
        "residual_metrics": _residual_diagnostics(baseline_id, eval_payload, cache),
        "event_loss_metrics": _event_loss_diagnostics(baseline_id, eval_payload, cache),
        "curves": curve_rows,
        "samples": _prediction_samples(baseline_id, eval_payload, cache),
    }


def _run_epoch(model, loader, criterion, optimizer, scaler, device, config: dict[str, Any], train: bool, use_amp: bool) -> float:
    """运行一个 train 或 eval epoch，返回平均训练 loss。

    这里的 loss 可以是普通加权 MAE/SmoothL1，也可以是 V5 的事件窗口残差加权 loss；
    但最终论文主指标仍由 `_evaluate` 在真实尺度上计算。
    """

    model.train(train)
    training_config = config.get("training", {})
    event_loss_config = config.get("event_loss", {})
    total_loss = 0.0
    total_batches = 0
    max_batches = training_config.get("max_train_batches" if train else "max_eval_batches")
    for batch_index, batch in enumerate(loader):
        if max_batches is not None and batch_index >= int(max_batches):
            break
        history_load = batch["history_load"].to(device)
        history_events = batch["history_events"].to(device)
        target = batch["target"].to(device)
        graph_indices = batch["graph_indices"].to(device)
        graph_weights = batch["graph_weights"].to(device)
        loss_weight = batch["loss_weight"].to(device)
        historical_graph_indices = batch["historical_graph_indices"].to(device)
        historical_graph_weights = batch["historical_graph_weights"].to(device)
        event_channel_indices = batch["event_channel_indices"].to(device)
        event_channel_weights = batch["event_channel_weights"].to(device)
        event_context = batch["event_context"].to(device)
        if train:
            optimizer.zero_grad(set_to_none=True)
        with torch.set_grad_enabled(train):
            with _autocast_context(device, use_amp):
                prediction = model(
                    history_load,
                    history_events,
                    graph_indices,
                    graph_weights,
                    historical_graph_indices=historical_graph_indices,
                    historical_graph_weights=historical_graph_weights,
                    event_channel_indices=event_channel_indices,
                    event_channel_weights=event_channel_weights,
                    event_context=event_context,
                )
                loss = compute_event_residual_loss(batch, prediction, model, target, criterion, loss_weight, event_loss_config)
            if train:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
        total_loss += float(loss.detach().cpu())
        total_batches += 1
    return total_loss / max(1, total_batches)


def _checkpoint_metric(training_config: dict[str, Any]) -> str:
    """解析 checkpoint 选择指标，并对拼写错误尽早报错。

    默认仍是旧版 `validation_loss`，保证历史配置可复现；V5 Plus 新增的
    `val_MAE_raw` / `val_RMSE_raw` 用来让 best checkpoint 与论文主指标口径对齐。
    """

    metric = str(training_config.get("checkpoint_metric", "validation_loss"))
    if metric not in CHECKPOINT_METRICS:
        raise ValueError(f"unsupported checkpoint_metric={metric!r}; expected one of {sorted(CHECKPOINT_METRICS)}")
    return metric


def _checkpoint_score(metric: str, validation_loss: float, val_mae_raw: float, val_rmse_raw: float) -> float:
    """把不同 validation 指标统一成“越小越好”的 checkpoint score。"""

    if metric == "validation_loss":
        return float(validation_loss)
    if metric == "val_MAE_raw":
        return float(val_mae_raw)
    if metric == "val_RMSE_raw":
        return float(val_rmse_raw)
    raise ValueError(f"unsupported checkpoint_metric={metric!r}")


def compute_event_residual_loss(batch, prediction, model, target, criterion, loss_weight, event_loss_config: dict[str, Any] | None = None):
    """计算 V5 事件窗口感知 loss。

    默认关闭时退化为普通加权 loss。开启后会额外关注事件窗口、departure/access/load_jump
    等局部状态，并可约束 gate 在事件窗口与稳定窗口之间拉开差异。这个 loss 用来引导模型
    “在事件发生时更认真地使用事件图”，不是论文最终指标本身。
    """

    config = event_loss_config or {}
    mode = str(config.get("mode", "event_residual_weighted_mae" if config.get("enabled") else "")).lower()
    if not bool(config.get("enabled", False)) or mode != "event_residual_weighted_mae":
        return _weighted_loss(criterion, prediction, target, loss_weight)
    absolute_error = torch.abs(prediction - target)
    global_loss = absolute_error.mean()
    masks = batch.get("event_window_masks", batch.get("event_window_mask_summary"))
    if masks is None:
        return global_loss
    masks = masks.to(device=prediction.device, dtype=prediction.dtype)
    components = [float(config.get("global_weight", 1.0)) * global_loss]
    event_union = torch.clamp(masks.sum(dim=-1), max=1.0)
    event_mask = event_union.unsqueeze(1).expand_as(absolute_error)
    components.append(float(config.get("event_window_weight", 0.0)) * _masked_mean(absolute_error, event_mask))
    name_to_index = _event_window_name_to_index()
    for name, weight_key in (
        ("departure_count", "departure_weight"),
        ("load_jump_flag", "load_jump_weight"),
        ("access_count", "access_weight"),
    ):
        weight = float(config.get(weight_key, 0.0))
        if weight <= 0.0:
            continue
        mask = masks[..., name_to_index[name]].unsqueeze(1).expand_as(absolute_error)
        components.append(weight * _masked_mean(absolute_error, mask))
    gate = getattr(model, "last_gate", None)
    correction = getattr(model, "last_event_correction", None)
    if gate is not None and float(config.get("gate_separation_weight", 0.0)) > 0.0:
        # gate 分离项鼓励事件窗口 gate 高于稳定窗口 gate，用于增强可解释性。
        gate_2d = gate.squeeze(-1)
        event_gate = _masked_mean(gate_2d, event_union)
        stable_gate = _masked_mean(gate_2d, 1.0 - event_union)
        margin = float(config.get("gate_margin", 0.05))
        components.append(float(config.get("gate_separation_weight", 0.0)) * torch.relu(torch.as_tensor(margin, device=prediction.device) - (event_gate - stable_gate)))
    if correction is not None and float(config.get("residual_l1_weight", 0.0)) > 0.0:
        # 残差 L1 防止事件修正分支无约束放大，尤其适合 residual_correction 结构。
        correction_for_loss = correction.permute(0, 2, 1).contiguous()
        components.append(float(config.get("residual_l1_weight", 0.0)) * correction_for_loss.abs().mean())
    return sum(components)


def _masked_mean(values, mask):
    mask = mask.to(device=values.device, dtype=values.dtype)
    denominator = torch.clamp(mask.sum(), min=1.0)
    return (values * mask).sum() / denominator


def _event_window_name_to_index() -> dict[str, int]:
    return {
        "access_count": 0,
        "departure_count": 1,
        "load_jump_flag": 2,
        "near_capacity_proxy": 3,
        "active_count_high": 4,
        "occupancy_rate_high": 5,
    }


def _evaluate(
    model,
    loader,
    device,
    cache,
    loss_weight_config: dict[str, Any] | None = None,
    graph=None,
    event_loss_config: dict[str, Any] | None = None,
    split_name: str = "",
) -> dict[str, Any]:
    """在 test/validation loader 上评估并收集诊断中间量。

    评估时会把标准化预测还原到原始负载尺度；因此输出 MAE/RMSE 可以直接跨 baseline 比较。
    gate、residual 和 channel weights 只在对应模型分支存在时记录。
    """

    model.eval()
    predictions = []
    targets = []
    origins = []
    gate_values = []
    residual_values = []
    correction_values = []
    hist_prediction_values = []
    residual_clip_rates = []
    channel_weight_values = []
    with torch.no_grad():
        for batch in loader:
            output = model(
                batch["history_load"].to(device),
                batch["history_events"].to(device),
                batch["graph_indices"].to(device),
                batch["graph_weights"].to(device),
                historical_graph_indices=batch["historical_graph_indices"].to(device),
                historical_graph_weights=batch["historical_graph_weights"].to(device),
                event_channel_indices=batch["event_channel_indices"].to(device),
                event_channel_weights=batch["event_channel_weights"].to(device),
                event_context=batch["event_context"].to(device),
            )
            center = batch.get("target_center")
            scale = batch.get("target_scale")
            if center is not None and scale is not None:
                # RevIN 或 z-score 都通过 center/scale 还原到真实负载尺度。
                raw_output = output.detach().cpu().numpy() * scale.numpy()[:, np.newaxis, :] + center.numpy()[:, np.newaxis, :]
            else:
                raw_output = output.detach().cpu().numpy() * cache.normalization["load_std"] + cache.normalization["load_mean"]
            predictions.append(raw_output.astype(np.float32))
            targets.append(batch["target_raw"].numpy().astype(np.float32))
            origins.extend(batch["origin"].numpy().astype(int).tolist())
            gate = getattr(model, "last_gate", None)
            if gate is not None:
                gate_values.append(gate.detach().cpu().numpy().astype(np.float32))
            residual = getattr(model, "last_event_residual", None)
            correction = getattr(model, "last_event_correction", None)
            hist_prediction = getattr(model, "last_hist_prediction", None)
            if residual is not None and scale is not None:
                scale_np = scale.numpy()[:, np.newaxis, :]
                residual_values.append(residual.detach().cpu().numpy().astype(np.float32).transpose(0, 2, 1) * scale_np)
            if correction is not None and scale is not None:
                scale_np = scale.numpy()[:, np.newaxis, :]
                correction_values.append(correction.detach().cpu().numpy().astype(np.float32).transpose(0, 2, 1) * scale_np)
            if hist_prediction is not None and center is not None and scale is not None:
                hist_prediction_values.append(
                    hist_prediction.detach().cpu().numpy().astype(np.float32).transpose(0, 2, 1) * scale.numpy()[:, np.newaxis, :]
                    + center.numpy()[:, np.newaxis, :]
                )
            clip_rate = getattr(model, "last_event_residual_clip_rate", None)
            if clip_rate is not None:
                residual_clip_rates.append(float(clip_rate.detach().cpu()))
            channel_weights = getattr(model, "last_channel_weights", None)
            if channel_weights is not None:
                channel_weight_values.append(channel_weights.detach().cpu().numpy().astype(np.float32))
    prediction = np.concatenate(predictions, axis=0) if predictions else np.zeros((0, cache.horizon_steps, len(cache.nodes)), dtype=np.float32)
    target = np.concatenate(targets, axis=0) if targets else np.zeros_like(prediction)
    error = prediction - target
    loss_weight = build_event_loss_weights(cache, origins, loss_weight_config or {}) if origins else np.zeros_like(error)
    weighted_abs = np.abs(error) * loss_weight if error.size else error
    alpha_hist = getattr(model, "last_alpha_hist", None)
    alpha_event = getattr(model, "last_alpha_event", None)
    channel_weight_metrics = {}
    if channel_weight_values:
        channel_names = list(getattr(graph, "channel_names", None) or [])
        mean_weights = np.mean(np.stack(channel_weight_values, axis=0), axis=0)
        for index, value in enumerate(mean_weights):
            channel_name = channel_names[index] if index < len(channel_names) else str(index)
            channel_weight_metrics[f"channel_weight_{channel_name}"] = float(value)
    gate_array = np.concatenate(gate_values, axis=0) if gate_values else np.zeros((0, len(cache.nodes), 1), dtype=np.float32)
    empty_prediction_like = np.zeros((0, cache.horizon_steps, len(cache.nodes)), dtype=np.float32)
    residual_array = np.concatenate(residual_values, axis=0) if residual_values else empty_prediction_like
    correction_array = np.concatenate(correction_values, axis=0) if correction_values else empty_prediction_like
    hist_prediction_array = np.concatenate(hist_prediction_values, axis=0) if hist_prediction_values else empty_prediction_like
    gate_window_stats = _gate_window_stats(gate_array, origins, cache)
    return {
        "prediction": prediction,
        "target": target,
        "origins": origins,
        "split": split_name,
        "MAE": float(np.mean(np.abs(error))) if error.size else float("nan"),
        "RMSE": float(np.sqrt(np.mean(error**2))) if error.size else float("nan"),
        "event_weighted_MAE": float(weighted_abs.sum() / max(float(loss_weight.sum()), 1.0)) if error.size else float("nan"),
        "prediction_count": int(error.size),
        "gate_mean": float(np.concatenate([values.reshape(-1) for values in gate_values]).mean()) if gate_values else np.nan,
        "gate_std": float(np.concatenate([values.reshape(-1) for values in gate_values]).std()) if gate_values else np.nan,
        "gate_values": gate_array,
        "event_residual": residual_array,
        "event_correction": correction_array,
        "hist_prediction": hist_prediction_array,
        "event_gate_event_window_mean": gate_window_stats["event_window_mean"],
        "event_gate_stable_window_mean": gate_window_stats["stable_window_mean"],
        "alpha_hist": float(alpha_hist.detach().cpu()) if alpha_hist is not None else np.nan,
        "alpha_event": float(alpha_event.detach().cpu()) if alpha_event is not None else np.nan,
        "event_residual_clip_rate": float(np.mean(residual_clip_rates)) if residual_clip_rates else np.nan,
        "channel_weights": channel_weight_metrics,
        "event_loss_config": event_loss_config or {},
    }


def _event_window_metrics(baseline_id: str, eval_payload: dict[str, Any], cache) -> list[dict[str, Any]]:
    """按事件窗口拆分 MAE/RMSE，验证模型收益是否发生在事件相关时段。"""

    prediction = eval_payload["prediction"]
    target = eval_payload["target"]
    origins = eval_payload["origins"]
    rows = []
    masks = _event_masks(cache, origins)
    for window_name, mask in masks.items():
        expanded = np.repeat(mask[:, np.newaxis, :], cache.horizon_steps, axis=1)
        if not expanded.any():
            continue
        error = prediction[expanded] - target[expanded]
        rows.append(
            {
                "baseline_id": baseline_id,
                "event_window": window_name,
                "MAE": float(np.mean(np.abs(error))),
                "RMSE": float(np.sqrt(np.mean(error**2))),
                "prediction_count": int(error.size),
            }
        )
    return rows


def _horizon_metrics(baseline_id: str, eval_payload: dict[str, Any], cache) -> list[dict[str, Any]]:
    """按预测步长拆分指标，检查提升是否只来自最近一步。"""

    prediction = eval_payload["prediction"]
    target = eval_payload["target"]
    rows = []
    for horizon_index in range(cache.horizon_steps):
        error = prediction[:, horizon_index, :] - target[:, horizon_index, :]
        rows.append(
            {
                "baseline_id": baseline_id,
                "horizon_step": horizon_index + 1,
                "MAE": float(np.mean(np.abs(error))) if error.size else np.nan,
                "RMSE": float(np.sqrt(np.mean(error**2))) if error.size else np.nan,
                "prediction_count": int(error.size),
            }
        )
    return rows


def _graph_gate_metrics(baseline_id: str, eval_payload: dict[str, Any], cache) -> list[dict[str, Any]]:
    """汇总 gate 在全局、事件窗口和稳定窗口中的使用情况。"""

    gate_values = eval_payload.get("gate_values")
    if gate_values is None or not np.asarray(gate_values).size:
        return []
    gate_array = np.asarray(gate_values, dtype=np.float32).squeeze(-1)
    origins = eval_payload["origins"]
    masks = _event_masks(cache, origins)
    union = np.zeros(gate_array.shape, dtype=bool)
    for mask in masks.values():
        union |= mask
    stable = ~union
    event_mean = float(np.mean(gate_array[union])) if union.any() else np.nan
    stable_mean = float(np.mean(gate_array[stable])) if stable.any() else np.nan
    summary = {
        "baseline_id": baseline_id,
        "gate_scope": "summary",
        "gate_mean": float(np.mean(gate_array)),
        "gate_std": float(np.std(gate_array)),
        "sample_count": int(gate_array.size),
        "event_gate_mean": float(np.mean(gate_array)),
        "event_gate_event_window_mean": event_mean,
        "event_gate_stable_window_mean": stable_mean,
        "gate_event_minus_stable": event_mean - stable_mean if not np.isnan(event_mean) and not np.isnan(stable_mean) else np.nan,
        "alpha_hist": eval_payload.get("alpha_hist", np.nan),
        "alpha_event": eval_payload.get("alpha_event", np.nan),
    }
    rows = [
        summary,
        {
            "baseline_id": baseline_id,
            "gate_scope": "global",
            "gate_mean": float(np.mean(gate_array)),
            "gate_std": float(np.std(gate_array)),
            "sample_count": int(gate_array.size),
        },
        {
            "baseline_id": baseline_id,
            "gate_scope": "event_window",
            "gate_mean": event_mean,
            "gate_std": float(np.std(gate_array[union])) if union.any() else np.nan,
            "sample_count": int(union.sum()),
        },
        {
            "baseline_id": baseline_id,
            "gate_scope": "stable_window",
            "gate_mean": stable_mean,
            "gate_std": float(np.std(gate_array[stable])) if stable.any() else np.nan,
            "sample_count": int(stable.sum()),
        },
    ]
    return rows


def _residual_diagnostics(baseline_id: str, eval_payload: dict[str, Any], cache) -> list[dict[str, Any]]:
    """汇总事件残差修正量，辅助解释 residual_correction 分支是否过度修正。"""

    correction = np.asarray(eval_payload.get("event_correction"), dtype=np.float32)
    residual = np.asarray(eval_payload.get("event_residual"), dtype=np.float32)
    if not correction.size:
        return []
    origins = eval_payload["origins"]
    union = np.zeros((len(origins), len(cache.nodes)), dtype=bool)
    for mask in _event_masks(cache, origins).values():
        union |= mask
    expanded_event = np.repeat(union[:, np.newaxis, :], cache.horizon_steps, axis=1)
    expanded_stable = ~expanded_event
    abs_correction = np.abs(correction)
    row = {
        "baseline_id": baseline_id,
        "residual_abs_mean": float(np.mean(abs_correction)) if abs_correction.size else np.nan,
        "residual_abs_event_window_mean": float(np.mean(abs_correction[expanded_event])) if expanded_event.any() else np.nan,
        "residual_abs_stable_window_mean": float(np.mean(abs_correction[expanded_stable])) if expanded_stable.any() else np.nan,
        "residual_signed_mean": float(np.mean(correction)) if correction.size else np.nan,
        "event_residual_raw_abs_mean": float(np.mean(np.abs(residual))) if residual.size else np.nan,
        "event_residual_clip_rate": eval_payload.get("event_residual_clip_rate", np.nan),
    }
    return [row]


def _event_loss_diagnostics(baseline_id: str, eval_payload: dict[str, Any], cache) -> list[dict[str, Any]]:
    """按训练 loss 的事件组件回放 test MAE，检查加权目标是否确实覆盖有效样本。"""

    config = dict(eval_payload.get("event_loss_config") or {})
    prediction = eval_payload["prediction"]
    target = eval_payload["target"]
    origins = eval_payload["origins"]
    absolute_error = np.abs(prediction - target)
    rows = [
        {
            "baseline_id": baseline_id,
            "component": "global",
            "weight": float(config.get("global_weight", 1.0)),
            "MAE": float(np.mean(absolute_error)) if absolute_error.size else np.nan,
            "prediction_count": int(absolute_error.size),
            "skipped": False,
            "skipped_mask_count": 0,
        }
    ]
    masks = _event_masks(cache, origins)
    union = np.zeros((len(origins), len(cache.nodes)), dtype=bool)
    for mask in masks.values():
        union |= mask
    component_specs = [
        ("event_window", union, "event_window_weight"),
        ("departure_count", masks.get("departure_count", np.zeros_like(union)), "departure_weight"),
        ("load_jump_flag", masks.get("load_jump_flag", np.zeros_like(union)), "load_jump_weight"),
        ("access_count", masks.get("access_count", np.zeros_like(union)), "access_weight"),
    ]
    for component, mask, weight_key in component_specs:
        expanded = np.repeat(mask[:, np.newaxis, :], cache.horizon_steps, axis=1)
        rows.append(
            {
                "baseline_id": baseline_id,
                "component": component,
                "weight": float(config.get(weight_key, 0.0)),
                "MAE": float(np.mean(absolute_error[expanded])) if expanded.any() else np.nan,
                "prediction_count": int(expanded.sum()),
                "skipped": not bool(expanded.any()),
                "skipped_mask_count": int(not bool(expanded.any())),
            }
        )
    return rows


def _gate_window_stats(gate_array: np.ndarray, origins: list[int], cache) -> dict[str, float]:
    if not gate_array.size:
        return {"event_window_mean": np.nan, "stable_window_mean": np.nan}
    gate_2d = np.asarray(gate_array, dtype=np.float32).squeeze(-1)
    union = np.zeros(gate_2d.shape, dtype=bool)
    for mask in _event_masks(cache, origins).values():
        union |= mask
    stable = ~union
    return {
        "event_window_mean": float(np.mean(gate_2d[union])) if union.any() else np.nan,
        "stable_window_mean": float(np.mean(gate_2d[stable])) if stable.any() else np.nan,
    }


def _event_masks(cache, origins: list[int]) -> dict[str, np.ndarray]:
    return event_window_masks(cache, origins)


def _prediction_samples(baseline_id: str, eval_payload: dict[str, Any], cache, limit: int = 200) -> list[dict[str, Any]]:
    """导出少量预测样本，便于人工抽查 dashboard 或论文附录示例。"""

    rows = []
    prediction = eval_payload["prediction"]
    target = eval_payload["target"]
    for sample_index, origin in enumerate(eval_payload["origins"]):
        for horizon_index in range(cache.horizon_steps):
            timestamp_index = origin + 1 + horizon_index
            timestamp = cache.timestamps[timestamp_index] if timestamp_index < len(cache.timestamps) else ""
            for node_index, node in enumerate(cache.nodes):
                rows.append(
                    {
                        "baseline_id": baseline_id,
                        "origin_index": origin,
                        "timestamp": timestamp,
                        "node_id": node,
                        "horizon_step": horizon_index + 1,
                        "prediction": float(prediction[sample_index, horizon_index, node_index]),
                        "target": float(target[sample_index, horizon_index, node_index]),
                    }
                )
                if len(rows) >= limit:
                    return rows
    return rows


def _write_full_predictions_gzip(path: Path, baseline_id: str, seed: int, split_name: str, eval_payload: dict[str, Any], cache) -> None:
    """流式写出 validation/test 全量预测。

    V5 Plus 的 full prediction 文件是 paired bootstrap、validation stacking 和 seed ensemble
    的共同证据底座。这里故意不使用 test 指标做任何选择，只把已经固定 checkpoint 的
    预测结果写盘；后续脚本只能读取这些文件，不能反向影响训练。

    正式 test 大约有数百万行，若先构造 DataFrame 会占用大量内存，所以使用 gzip +
    csv.writer 逐行写出。
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    prediction = eval_payload["prediction"]
    target = eval_payload["target"]
    origins = list(eval_payload["origins"])
    masks = event_window_masks(cache, origins)
    access_mask = masks.get("access_count", np.zeros((len(origins), len(cache.nodes)), dtype=bool))
    departure_mask = masks.get("departure_count", np.zeros((len(origins), len(cache.nodes)), dtype=bool))
    load_jump_mask = masks.get("load_jump_flag", np.zeros((len(origins), len(cache.nodes)), dtype=bool))
    any_mask = access_mask | departure_mask | load_jump_mask
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FULL_PREDICTION_COLUMNS)
        writer.writeheader()
        for sample_index, origin in enumerate(origins):
            for horizon_index in range(cache.horizon_steps):
                timestamp_index = int(origin) + 1 + horizon_index
                timestamp = cache.timestamps[timestamp_index] if timestamp_index < len(cache.timestamps) else ""
                for node_index, node in enumerate(cache.nodes):
                    y_pred = float(prediction[sample_index, horizon_index, node_index])
                    y_true = float(target[sample_index, horizon_index, node_index])
                    error = y_pred - y_true
                    writer.writerow(
                        {
                            "baseline_id": baseline_id,
                            "seed": seed,
                            "split": split_name,
                            "origin_index": int(origin),
                            "timestamp": timestamp,
                            "node_id": node,
                            "horizon_step": horizon_index + 1,
                            "target": y_true,
                            "prediction": y_pred,
                            "abs_error": abs(error),
                            "squared_error": error * error,
                            "event_window_any": int(bool(any_mask[sample_index, node_index])),
                            "event_window_access": int(bool(access_mask[sample_index, node_index])),
                            "event_window_departure": int(bool(departure_mask[sample_index, node_index])),
                            "event_window_load_jump": int(bool(load_jump_mask[sample_index, node_index])),
                        }
                    )


def _graph_ablation_rows(baseline_rows: list[dict[str, Any]], metrics_by_baseline: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """生成图消融表：把主模型和行为拼接、DTW、删除图做直接差值。"""

    behavior = metrics_by_baseline.get("behavior_concat", metrics_by_baseline.get("behavior_concat_v4", metrics_by_baseline.get("behavior_concat_v5", {})))
    dtw = metrics_by_baseline.get("dtw_demand_graph", {})
    event = metrics_by_baseline.get("event_graph_dynamic", metrics_by_baseline.get("event_graph_dynamic_v4", metrics_by_baseline.get("event_graph_dynamic_v5", {})))
    rows = []
    for row in baseline_rows:
        mae = float(row["MAE"])
        rows.append(
            {
                "baseline_id": row["baseline_id"],
                "MAE": mae,
                "RMSE": row["RMSE"],
                "delta_vs_behavior_concat": mae - float(behavior["MAE"]) if "MAE" in behavior else np.nan,
                "delta_vs_dtw_graph": mae - float(dtw["MAE"]) if "MAE" in dtw else np.nan,
                "graph_destruction_delta": float(metrics_by_baseline["deleted_event_graph"]["MAE"]) - float(event["MAE"])
                if row["baseline_id"] == "event_graph_dynamic" and "deleted_event_graph" in metrics_by_baseline
                else np.nan,
                "conclusion_level": "training_smoke_or_formal_lite",
            }
        )
    return rows


def _baseline_delta_rows(baseline_rows: list[dict[str, Any]], metrics_by_baseline: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """生成所有关键 comparator 的 MAE 差值，负数代表当前 baseline 更好。"""

    rows = []
    comparators = [
        "behavior_concat",
        "behavior_concat_v4",
        "behavior_concat_v5",
        "semantic_shuffled_event_graph",
        "semantic_shuffled_event_graph_v4",
        "semantic_shuffled_event_residual_graph_v5",
        "historical_correlation_graph",
        "historical_correlation_graph_v4",
        "historical_correlation_graph_v5",
    ]
    for row in baseline_rows:
        baseline_id = str(row["baseline_id"])
        mae = float(row["MAE"])
        for comparator in comparators:
            if comparator == baseline_id or comparator not in metrics_by_baseline:
                continue
            rows.append(
                {
                    "baseline_id": baseline_id,
                    "comparator_baseline": comparator,
                    "metric": "MAE",
                    "baseline_value": mae,
                    "comparator_value": float(metrics_by_baseline[comparator]["MAE"]),
                    "delta": mae - float(metrics_by_baseline[comparator]["MAE"]),
                    "interpretation": "negative_delta_is_better",
                }
            )
    return rows


def build_primary_metric_summary(baseline_rows: list[dict[str, Any]]) -> pd.DataFrame:
    """构建主指标表。

    EXP-103 正式结论以 test MAE 为排序标准；RMSE 保留为补充指标。
    """

    frame = pd.DataFrame(baseline_rows).copy()
    if frame.empty:
        return frame
    behavior_mae = _baseline_metric(frame, "behavior_concat", "MAE")
    if behavior_mae is None:
        behavior_mae = _baseline_metric(frame, "behavior_concat_v4", "MAE")
    if behavior_mae is None:
        behavior_mae = _baseline_metric(frame, "behavior_concat_v5", "MAE")
    dtw_mae = _baseline_metric(frame, "dtw_demand_graph", "MAE")
    best_mae = float(frame["MAE"].min())
    frame["rank_by_MAE"] = frame["MAE"].rank(method="min", ascending=True).astype(int)
    frame["is_best_mae"] = frame["MAE"] == best_mae
    frame["delta_vs_behavior_concat"] = frame["MAE"] - behavior_mae if behavior_mae is not None else np.nan
    frame["delta_vs_dtw_graph"] = frame["MAE"] - dtw_mae if dtw_mae is not None else np.nan
    columns = [
        "rank_by_MAE",
        "baseline_id",
        "MAE",
        "RMSE",
        "delta_vs_behavior_concat",
        "delta_vs_dtw_graph",
        "is_best_mae",
        "best_validation_loss",
        "best_epoch",
        "epochs_ran",
        "train_seconds",
        "prediction_count",
        "uses_events",
        "uses_graph",
        "graph_mode",
        "gate_mean",
        "gate_std",
    ]
    existing = [column for column in columns if column in frame.columns]
    return frame.sort_values(["MAE", "baseline_id"])[existing].reset_index(drop=True)


def _baseline_metric(frame: pd.DataFrame, baseline_id: str, metric: str) -> float | None:
    values = frame.loc[frame["baseline_id"] == baseline_id, metric]
    if values.empty:
        return None
    return float(values.iloc[0])


def _write_exp103_tables(
    out_dir: Path,
    baseline_rows: list[dict[str, Any]],
    event_rows: list[dict[str, Any]],
    horizon_rows: list[dict[str, Any]],
    gate_rows: list[dict[str, Any]],
    residual_rows: list[dict[str, Any]],
    event_loss_rows: list[dict[str, Any]],
    curve_rows: list[dict[str, Any]],
    sample_rows: list[dict[str, Any]],
    metrics_by_baseline: dict[str, dict[str, Any]],
) -> None:
    """写出所有 EXP-103 CSV evidence 表。

    该函数在每个 baseline 完成后会被调用一次，所以远程训练即使中断，
    也能保留已经完成 baseline 的部分证据。
    """

    pd.DataFrame(baseline_rows).to_csv(out_dir / "baseline_metrics.csv", index=False)
    pd.DataFrame(_graph_ablation_rows(baseline_rows, metrics_by_baseline)).to_csv(out_dir / "graph_ablation_table.csv", index=False)
    pd.DataFrame(_baseline_delta_rows(baseline_rows, metrics_by_baseline)).to_csv(out_dir / "baseline_deltas.csv", index=False)
    build_primary_metric_summary(baseline_rows).to_csv(out_dir / "primary_metric_summary.csv", index=False)
    pd.DataFrame(event_rows).to_csv(out_dir / "event_window_metrics.csv", index=False)
    pd.DataFrame(horizon_rows).to_csv(out_dir / "horizon_metrics.csv", index=False)
    pd.DataFrame(gate_rows).to_csv(out_dir / "graph_gate_metrics.csv", index=False)
    pd.DataFrame(residual_rows).to_csv(out_dir / "residual_diagnostics.csv", index=False)
    pd.DataFrame(event_loss_rows).to_csv(out_dir / "event_loss_diagnostics.csv", index=False)
    pd.DataFrame(curve_rows).to_csv(out_dir / "training_curves.csv", index=False)
    pd.DataFrame(sample_rows).to_csv(out_dir / "predictions_sample.csv", index=False)


def _write_run_manifest(out_dir: Path, config: dict[str, Any], config_path: str, output_dir: str, status: str) -> None:
    """写出 run 级 manifest，连接配置、输出目录、git commit 和完成状态。"""

    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    existing = {}
    manifest_path = out_dir / "run_manifest.json"
    if manifest_path.exists():
        try:
            existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            existing = {}
    payload = {
        "experiment_id": str(config.get("experiment_id", "EXP-103")),
        "seed": int(config.get("seed", 42)),
        "config": str(config_path),
        "output_dir": str(output_dir),
        "git_commit": _git_commit(),
        "started_at": existing.get("started_at", now),
        "finished_at": now,
        "status": status,
    }
    write_json(manifest_path, payload)


def _write_checksums(out_dir: Path) -> None:
    """为轻量 evidence 文件生成 SHA-256，方便远程打包后校验。"""

    candidates = []
    for pattern in ("*.csv", "*.json", "*.txt", "*.md", "*.html"):
        candidates.extend(out_dir.glob(pattern))
    candidates.extend((out_dir / "logs").glob("*.log") if (out_dir / "logs").exists() else [])
    candidates.extend((out_dir / "logs").glob("*.jsonl") if (out_dir / "logs").exists() else [])
    rows = []
    for path in sorted(set(candidates)):
        if path.name == "checksums.sha256" or not path.is_file():
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(f"{digest}  {path.relative_to(out_dir)}")
    (out_dir / "checksums.sha256").write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return "unknown"
    return result.stdout.strip() or "unknown"


def _metric_guide_text() -> str:
    return """# EXP-103 Metric Guide

Read outputs in this order:

1. primary_metric_summary.csv: main ranking by test MAE, plus deltas vs behavior_concat and dtw_demand_graph.
2. graph_ablation_table.csv: graph-specific claim checks, especially event_graph_dynamic vs behavior_concat, dtw_demand_graph, and deleted_event_graph.
3. event_window_metrics.csv: event-state checks for access_count, departure_count, load_jump_flag, high occupancy, and near_capacity_proxy.
4. horizon_metrics.csv: horizon-step MAE/RMSE, useful for checking whether gains are only at the closest forecast step.
5. graph_gate_metrics.csv: graph gate usage split by event-window and stable-window states.
6. residual_diagnostics.csv: V5 event residual correction size, event/stable split, and clip rate.
7. event_loss_diagnostics.csv: V5 event-window weighted-loss component MAE and skipped masks.
8. baseline_deltas.csv: direct MAE deltas against behavior, semantic shuffled, and historical comparators when present.
9. training_curves.csv: train/validation loss, best epoch, early stopping behavior, and epoch runtime.
10. baseline_metrics.csv: complete per-baseline test MAE/RMSE and runtime fields.

Interpretation rules:

- Lower MAE/RMSE is better.
- For delta columns, negative means the row baseline is better than the comparator.
- event_graph_dynamic supports a strong C1 claim only if it improves over behavior_concat and responds competitively to dtw_demand_graph / historical_correlation_graph.
- For v4, historical_event_dual_graph_v4 is strongest when it beats or closely matches historical_correlation_graph_v4 globally while showing higher event-window gate usage.
- For v5, historical_event_residual_graph_v5 supports the main claim when it beats semantic_shuffled_event_residual_graph_v5, stays within 0.0001 MAE of historical_correlation_graph_v5, and has higher event-window than stable-window gate.
- If behavior_concat improves over no_graph but event_graph_dynamic does not beat strong graph baselines, write the result as behavior-event feature value plus graph-boundary evidence.
"""


def _resolve_device(requested: str):
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(requested)


def _make_grad_scaler(use_amp: bool):
    if hasattr(torch, "amp") and hasattr(torch.amp, "GradScaler"):
        return torch.amp.GradScaler("cuda", enabled=use_amp)
    return torch.cuda.amp.GradScaler(enabled=use_amp)


def _format_epoch_progress(
    baseline_id: str,
    epoch: int,
    epochs: int,
    train_loss: float,
    val_loss: float,
    best_val: float,
    lr: float,
    epoch_seconds: float,
    curve_rows: list[dict[str, Any]],
    improved: bool,
    terminal_bar: bool = True,
) -> str:
    if not terminal_bar:
        return (
            f"[{baseline_id}] epoch {epoch}/{epochs} "
            f"train_loss={train_loss:.6f} val_loss={val_loss:.6f} best_val={best_val:.6f} "
            f"lr={lr:.6g} seconds={epoch_seconds:.1f}"
        )
    fraction = min(1.0, max(0.0, epoch / max(1, epochs)))
    bar = _ascii_progress_bar(fraction, width=24)
    recent_val = [float(row["validation_loss"]) for row in curve_rows if row.get("baseline_id") == baseline_id][-12:]
    spark = _sparkline(recent_val)
    marker = "best" if improved else "wait"
    return (
        f"[{baseline_id}] {bar} {epoch:02d}/{epochs:02d} {marker:<4} "
        f"train={train_loss:.6f} val={val_loss:.6f} best={best_val:.6f} "
        f"lr={lr:.3g} {epoch_seconds:.1f}s val:{spark}"
    )


def _ascii_progress_bar(fraction: float, width: int = 24) -> str:
    filled = int(round(width * fraction))
    return "[" + "#" * filled + "." * (width - filled) + f"] {fraction * 100:5.1f}%"


def _sparkline(values: list[float]) -> str:
    if not values:
        return ""
    ticks = "▁▂▃▄▅▆▇█"
    low = min(values)
    high = max(values)
    if math.isclose(low, high):
        return ticks[0] * len(values)
    return "".join(ticks[min(len(ticks) - 1, int((value - low) / (high - low) * (len(ticks) - 1)))] for value in values)


def _append_progress_event(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), **payload}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def _write_training_dashboard(
    path: Path,
    curve_rows: list[dict[str, Any]],
    baseline_rows: list[dict[str, Any]],
    baseline_ids: list[str],
    active_baseline: str | None,
    refresh_seconds: int,
) -> None:
    """生成训练中的 HTML dashboard。

    该 dashboard 只展示训练曲线和当前 test ranking，不参与指标计算；
    作用是远程长跑时快速判断是否卡住、发散或已经早停。
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    latest_rows = _latest_curve_by_baseline(curve_rows)
    ranking_rows = sorted(baseline_rows, key=lambda row: float(row.get("MAE", "inf")))
    completed_ids = {str(row["baseline_id"]) for row in baseline_rows}
    cards = "".join(
        _baseline_card(baseline_id, latest_rows.get(baseline_id), active_baseline, completed_ids)
        for baseline_id in baseline_ids
    )
    completed_count = len(completed_ids)
    best_row = ranking_rows[0] if ranking_rows else None
    best_label = f"{best_row['baseline_id']} · MAE {float(best_row['MAE']):.6f}" if best_row else "等待首个 baseline 完成"
    ranking = "".join(
        f"<tr><td>{index + 1}</td><td>{row['baseline_id']}</td><td>{float(row['MAE']):.6f}</td>"
        f"<td>{float(row['RMSE']):.6f}</td><td>{int(row.get('best_epoch', 0))}</td></tr>"
        for index, row in enumerate(ranking_rows)
    )
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="{max(3, refresh_seconds)}">
  <title>EXP-103 Training Dashboard</title>
  <style>
    :root {{ color-scheme: light; --ink:#17202a; --muted:#5d6d7e; --line:#d7dbdd; --blue:#246bfe; --green:#138d75; --amber:#b9770e; --red:#b03a2e; }}
    body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif; color:var(--ink); background:#f4f7fb; }}
    main {{ max-width:1180px; margin:0 auto; padding:28px; }}
    h1 {{ margin:0 0 6px; font-size:28px; letter-spacing:0; }}
    h2 {{ margin:0 0 14px; font-size:18px; letter-spacing:0; }}
    .sub {{ color:var(--muted); margin-bottom:20px; }}
    .summary {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin:18px 0; }}
    .summary-item {{ background:white; border:1px solid var(--line); border-radius:8px; padding:14px; }}
    .summary-label {{ color:var(--muted); font-size:12px; text-transform:uppercase; }}
    .summary-value {{ font-size:20px; font-weight:700; margin-top:4px; }}
    .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin:18px 0 24px; }}
    .card {{ background:white; border:1px solid var(--line); border-radius:8px; padding:14px; box-shadow:0 1px 2px rgba(0,0,0,.04); }}
    .active {{ border-color:var(--blue); box-shadow:0 0 0 2px rgba(36,107,254,.10); }}
    .done {{ border-color:rgba(19,141,117,.45); }}
    .name {{ font-weight:700; margin-bottom:8px; overflow-wrap:anywhere; }}
    .metric {{ color:var(--muted); font-size:13px; line-height:1.7; }}
    .badge {{ display:inline-block; border:1px solid var(--line); border-radius:999px; padding:2px 8px; font-size:12px; color:var(--muted); margin-bottom:8px; }}
    .badge.running {{ color:var(--blue); border-color:rgba(36,107,254,.45); }}
    .badge.done {{ color:var(--green); border-color:rgba(19,141,117,.45); }}
    .bar {{ height:8px; background:#eaeef5; border-radius:999px; overflow:hidden; margin-top:10px; }}
    .fill {{ height:100%; background:linear-gradient(90deg,var(--blue),var(--green)); }}
    .panel {{ background:white; border:1px solid var(--line); border-radius:8px; padding:18px; margin-bottom:18px; }}
    svg {{ width:100%; height:auto; display:block; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th,td {{ border-bottom:1px solid var(--line); padding:9px 8px; text-align:left; }}
    th {{ color:var(--muted); font-weight:600; }}
    .foot {{ color:var(--muted); font-size:12px; margin-top:16px; }}
  </style>
</head>
<body>
<main>
  <h1>EXP-103 Training Dashboard</h1>
  <div class="sub">自动刷新：{max(3, refresh_seconds)} 秒。粗线为 validation loss，细线为 train loss；checkpoint metric 只来自 validation，不看 test。</div>
  <section class="summary">
    <div class="summary-item"><div class="summary-label">Baselines</div><div class="summary-value">{completed_count}/{len(baseline_ids)} completed</div></div>
    <div class="summary-item"><div class="summary-label">Active</div><div class="summary-value">{active_baseline or "idle"}</div></div>
    <div class="summary-item"><div class="summary-label">Best So Far</div><div class="summary-value">{best_label}</div></div>
  </section>
  <section class="cards">{cards}</section>
  <section class="panel">
    <h2>Loss Curves</h2>
    {_svg_loss_chart(curve_rows)}
  </section>
  <section class="panel">
    <h2>Current Test Ranking</h2>
    <table><thead><tr><th>Rank</th><th>Baseline</th><th>MAE</th><th>RMSE</th><th>Best Epoch</th></tr></thead><tbody>{ranking}</tbody></table>
  </section>
  <div class="foot">Generated at {time.strftime("%Y-%m-%d %H:%M:%S")} from training_curves.csv-compatible rows.</div>
</main>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def _latest_curve_by_baseline(curve_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in curve_rows:
        latest[str(row["baseline_id"])] = row
    return latest


def _baseline_card(baseline_id: str, row: dict[str, Any] | None, active_baseline: str | None, completed_ids: set[str] | None = None) -> str:
    completed_ids = completed_ids or set()
    is_active = baseline_id == active_baseline
    is_done = baseline_id in completed_ids
    css_class = "card active" if is_active else "card done" if is_done else "card"
    badge = "running" if is_active else "done" if is_done else "waiting"
    badge_class = f"badge {badge}" if badge in {"running", "done"} else "badge"
    if row is None:
        return f'<div class="{css_class}"><span class="{badge_class}">{badge}</span><div class="name">{baseline_id}</div><div class="metric">等待训练</div><div class="bar"><div class="fill" style="width:0%"></div></div></div>'
    epoch = int(row["epoch"])
    epochs = int(row.get("epochs", epoch))
    width = min(100.0, 100.0 * epoch / max(1, epochs))
    remaining_seconds = max(0, epochs - epoch) * float(row["epoch_seconds"])
    eta_text = _format_duration(remaining_seconds)
    checkpoint_metric = str(row.get("checkpoint_metric", "validation_loss"))
    checkpoint_score = float(row.get("checkpoint_score", row.get("validation_loss", float("nan"))))
    mae = row.get("val_MAE_raw", float("nan"))
    mae_text = f" · val_MAE {float(mae):.6f}" if _is_finite_number(mae) else ""
    return (
        f'<div class="{css_class}"><span class="{badge_class}">{badge}</span><div class="name">{baseline_id}</div>'
        f'<div class="metric">epoch {epoch}/{epochs} · ETA {eta_text}<br>'
        f'train {float(row["train_loss"]):.6f} · val_loss {float(row["validation_loss"]):.6f}<br>'
        f'{checkpoint_metric} {checkpoint_score:.6f}{mae_text}<br>'
        f'lr {float(row["lr"]):.3g} · {float(row["epoch_seconds"]):.1f}s/epoch</div>'
        f'<div class="bar"><div class="fill" style="width:{width:.1f}%"></div></div></div>'
    )


def _format_duration(seconds: float) -> str:
    if not math.isfinite(seconds):
        return "n/a"
    seconds = max(0, int(round(seconds)))
    minutes, sec = divmod(seconds, 60)
    hours, minute = divmod(minutes, 60)
    if hours:
        return f"{hours}h{minute:02d}m"
    if minute:
        return f"{minute}m{sec:02d}s"
    return f"{sec}s"


def _is_finite_number(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _svg_loss_chart(curve_rows: list[dict[str, Any]]) -> str:
    if not curve_rows:
        return '<svg viewBox="0 0 760 260" role="img"><text x="24" y="132" fill="#5d6d7e">等待第一个 epoch...</text></svg>'
    width, height = 760, 260
    pad_left, pad_top, pad_right, pad_bottom = 56, 24, 20, 44
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom
    values = [float(row["train_loss"]) for row in curve_rows] + [float(row["validation_loss"]) for row in curve_rows]
    low, high = min(values), max(values)
    if math.isclose(low, high):
        high = low + 1.0
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in curve_rows:
        grouped.setdefault(str(row["baseline_id"]), []).append(row)
    colors = ["#246bfe", "#138d75", "#b9770e", "#8e44ad", "#c0392b", "#2e86c1", "#566573", "#16a085", "#d35400", "#7d3c98"]
    paths = []
    legends = []
    for index, (baseline_id, rows) in enumerate(grouped.items()):
        color = colors[index % len(colors)]
        max_epoch = max(int(row["epoch"]) for row in rows)
        train_points = _svg_points(rows, "train_loss", max_epoch, low, high, pad_left, pad_top, plot_w, plot_h)
        val_points = _svg_points(rows, "validation_loss", max_epoch, low, high, pad_left, pad_top, plot_w, plot_h)
        paths.append(f'<polyline points="{train_points}" fill="none" stroke="{color}" stroke-width="2" opacity=".45"/>')
        paths.append(f'<polyline points="{val_points}" fill="none" stroke="{color}" stroke-width="3"/>')
        legends.append(f'<span style="display:inline-block;margin-right:14px;color:{color}">● {baseline_id}</span>')
    grid = "".join(
        f'<line x1="{pad_left}" y1="{pad_top + plot_h * i / 4:.1f}" x2="{width - pad_right}" y2="{pad_top + plot_h * i / 4:.1f}" stroke="#e5e8ec"/>'
        for i in range(5)
    )
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img">'
        f'{grid}<line x1="{pad_left}" y1="{pad_top}" x2="{pad_left}" y2="{height - pad_bottom}" stroke="#85929e"/>'
        f'<line x1="{pad_left}" y1="{height - pad_bottom}" x2="{width - pad_right}" y2="{height - pad_bottom}" stroke="#85929e"/>'
        f'{"".join(paths)}'
        f'<text x="{pad_left}" y="{height - 14}" fill="#5d6d7e">epoch</text>'
        f'<text x="8" y="{pad_top + 12}" fill="#5d6d7e">loss</text>'
        f'</svg><div class="foot">{"".join(legends)}<br>粗线 validation loss，细线 train loss。</div>'
    )


def _svg_points(
    rows: list[dict[str, Any]],
    field: str,
    max_epoch: int,
    low: float,
    high: float,
    pad_left: int,
    pad_top: int,
    plot_w: int,
    plot_h: int,
) -> str:
    points = []
    for row in rows:
        epoch = int(row["epoch"])
        x = pad_left + plot_w * (epoch - 1) / max(1, max_epoch - 1)
        y = pad_top + plot_h * (1.0 - (float(row[field]) - low) / (high - low))
        points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points)


def _make_scheduler(optimizer, training_config):
    """按配置创建学习率调度器；正式 run 只支持已审计的 ReduceLROnPlateau。"""

    scheduler_name = str(training_config.get("scheduler", "none")).lower()
    if scheduler_name in {"", "none", "null"}:
        return None
    if scheduler_name != "reduce_on_plateau":
        raise ValueError(f"unsupported scheduler: {scheduler_name}")
    return torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="min",
        factor=float(training_config.get("scheduler_factor", 0.5)),
        patience=int(training_config.get("scheduler_patience", 3)),
        min_lr=float(training_config.get("min_lr", 1e-5)),
    )


def _attach_model_contract(config: dict[str, Any]) -> None:
    """把模型结构摘要写回 resolved config，便于 evidence 包复现和论文描述。"""

    training_config = config.get("training", {})
    kernel_size = int(training_config.get("kernel_size", 3))
    tcn_layers = int(training_config.get("tcn_layers", 4))
    dilation_schedule = training_config.get("dilation_schedule")
    receptive_field = compute_receptive_field(kernel_size, tcn_layers, dilation_schedule if isinstance(dilation_schedule, list) else None)
    contract = dict(config.get("model_contract", {}))
    contract.update(
        {
            "temporal_block": str(training_config.get("temporal_block", "residual")),
            "dilation_schedule": dilation_schedule or [1 for _ in range(tcn_layers)],
            "receptive_field": int(receptive_field),
            "history_steps": int(config.get("cache", {}).get("history_steps", 0)),
            "graph_message_stage": str(training_config.get("graph_message_stage", "raw_history")),
            "node_embedding_dim": int(training_config.get("node_embedding_dim", 0)),
            "residual_clip": float(training_config.get("residual_clip", 0.0)),
        }
    )
    config["model_contract"] = contract


def _canonical_exp103_baseline_id(baseline_id: str) -> str:
    """去掉版本后缀，让同一图构造逻辑可复用于 v4/v5 baseline 命名。"""

    if baseline_id.endswith("_v4") or baseline_id.endswith("_v5"):
        return baseline_id[:-3]
    return baseline_id


def _event_context_channel_count(context_config: dict[str, Any]) -> int:
    """根据 context feature 开关计算 gate 需要接收的事件上下文通道数。"""

    count = 0
    if bool(context_config.get("event_window_summary", False)):
        count += 6
    if bool(context_config.get("event_recency", False)):
        count += 4
    if bool(context_config.get("time_context", False)):
        count += 5
    return count


def _graph_mode_for_baseline(training_config: dict[str, Any], baseline_id: str) -> str:
    """解析 baseline 专属 graph_mode；没有 override 时使用全局 graph_mode。"""

    overrides = training_config.get("baseline_graph_modes", {})
    if isinstance(overrides, dict) and baseline_id in overrides:
        return str(overrides[baseline_id])
    canonical_id = _canonical_exp103_baseline_id(baseline_id)
    if isinstance(overrides, dict) and canonical_id in overrides:
        return str(overrides[canonical_id])
    return str(training_config.get("graph_mode", "concat"))


def _weighted_loss(criterion, prediction, target, loss_weight):
    """按样本/节点/ horizon 权重计算训练损失。"""

    unreduced = criterion(prediction, target)
    if loss_weight.shape != unreduced.shape:
        loss_weight = loss_weight.expand_as(unreduced)
    return (unreduced * loss_weight).sum() / torch.clamp(loss_weight.sum(), min=1.0)


def _early_stopping_min_epochs(training_config: dict[str, Any], baseline_id: str, epochs: int) -> int:
    """返回某个 baseline 的最小早停轮数。

    事件图是 EXP-103 的核心候选模型，验证集短期波动时不应该和普通基线一样过早停止。
    配置可以给特定 baseline 单独设置最小训练轮数；若总 epoch 更小，则自动截断到总 epoch。
    """
    raw_config = training_config.get("early_stopping_min_epochs", 0)
    if isinstance(raw_config, dict):
        raw_value = raw_config.get(baseline_id, raw_config.get(_canonical_exp103_baseline_id(baseline_id), raw_config.get("default", 0)))
    else:
        raw_value = raw_config
    min_epochs = max(0, int(raw_value))
    return min(int(epochs), min_epochs)


def _autocast_context(device, use_amp: bool):
    if hasattr(torch, "amp") and hasattr(torch.amp, "autocast"):
        return torch.amp.autocast(device_type=device.type, enabled=use_amp)
    return torch.cuda.amp.autocast(enabled=use_amp)


def _load_checkpoint(checkpoint_path: Path, device):
    try:
        return torch.load(checkpoint_path, map_location=device, weights_only=True)
    except TypeError:
        return torch.load(checkpoint_path, map_location=device)


def _set_seed(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _write_environment(path: Path) -> None:
    lines = [
        f"python={sys.version.split()[0]}",
        f"platform={platform.platform()}",
        f"torch={torch.__version__ if torch is not None else 'not-installed'}",
        f"cuda_available={torch.cuda.is_available() if torch is not None else False}",
    ]
    if torch is not None and torch.cuda.is_available():
        lines.append(f"cuda_device={torch.cuda.get_device_name(0)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
