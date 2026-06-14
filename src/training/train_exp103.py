from __future__ import annotations

import argparse
import json
import math
import platform
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
from evcs.models.graph_tcn import GraphTemporalTCN
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


def main() -> None:
    if torch is None or nn is None or DataLoader is None:
        raise SystemExit(f"PyTorch is required for EXP-103 training: {TORCH_IMPORT_ERROR}")
    parser = argparse.ArgumentParser(description="Train EXP-103 Graph-TCN graph ablation baselines.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    config = load_experiment_config(args.config)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "logs").mkdir(parents=True, exist_ok=True)
    (out_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "config_resolved.json", config)
    _write_environment(out_dir / "environment.txt")

    seed = int(config.get("seed", 42))
    _set_seed(seed)
    cache = _load_or_build_cache(config)
    baseline_ids = list(config.get("baselines", DEFAULT_BASELINES))
    graph_config = config.get("graph", {})
    graphs = build_exp103_graph_cache(
        cache,
        baseline_ids=baseline_ids,
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
        },
    )

    training_config = config.get("training", {})
    device = _resolve_device(str(training_config.get("device", "auto")))
    log_lines = [f"device={device}", f"baselines={','.join(baseline_ids)}"]
    baseline_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    curve_rows: list[dict[str, Any]] = []
    sample_rows: list[dict[str, Any]] = []
    metrics_by_baseline: dict[str, dict[str, Any]] = {}
    for baseline_id in baseline_ids:
        print(f"training EXP-103 baseline: {baseline_id}", flush=True)
        train_result = _train_one_baseline(
            baseline_id,
            config,
            cache,
            graphs[baseline_id],
            device,
            out_dir / "checkpoints" / f"best_{baseline_id}.pt",
            log_lines,
            out_dir,
            baseline_ids,
        )
        baseline_rows.append(train_result["metrics"])
        event_rows.extend(train_result["event_metrics"])
        curve_rows.extend(train_result["curves"])
        sample_rows.extend(train_result["samples"])
        metrics_by_baseline[baseline_id] = train_result["metrics"]
        log_lines.append(f"{baseline_id}: test_MAE={train_result['metrics']['MAE']:.6f}")
        _write_training_dashboard(
            out_dir / "training_dashboard.html",
            curve_rows,
            baseline_rows,
            baseline_ids,
            active_baseline=None,
            refresh_seconds=int(config.get("progress", {}).get("refresh_seconds", 10)),
        )

    graph_rows = _graph_ablation_rows(baseline_rows, metrics_by_baseline)
    primary_summary = build_primary_metric_summary(baseline_rows)
    pd.DataFrame(baseline_rows).to_csv(out_dir / "baseline_metrics.csv", index=False)
    pd.DataFrame(graph_rows).to_csv(out_dir / "graph_ablation_table.csv", index=False)
    primary_summary.to_csv(out_dir / "primary_metric_summary.csv", index=False)
    pd.DataFrame(event_rows).to_csv(out_dir / "event_window_metrics.csv", index=False)
    pd.DataFrame(curve_rows).to_csv(out_dir / "training_curves.csv", index=False)
    pd.DataFrame(sample_rows).to_csv(out_dir / "predictions_sample.csv", index=False)
    write_json(out_dir / "metrics.json", {"experiment_id": "EXP-103", "baselines": metrics_by_baseline})
    (out_dir / "metric_guide.md").write_text(_metric_guide_text(), encoding="utf-8")
    (out_dir / "logs" / "train.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    artifacts = [
        "metrics.json",
        "primary_metric_summary.csv",
        "baseline_metrics.csv",
        "graph_ablation_table.csv",
        "event_window_metrics.csv",
        "graph_manifest.json",
        "training_curves.csv",
        "predictions_sample.csv",
        "config_resolved.json",
        "environment.txt",
        "metric_guide.md",
        "training_dashboard.html",
        "logs/progress_events.jsonl",
        "logs/train.log",
    ]
    write_manifest(out_dir, str(config.get("experiment_id", "EXP-103")), artifacts)
    print(f"wrote EXP-103 training outputs to {out_dir}")


def _load_or_build_cache(config: dict[str, Any]):
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
    training_config = config.get("training", {})
    use_events = baseline_id != "no_graph"
    use_graph = baseline_id not in {"no_graph", "behavior_concat"}
    loss_weight_config = config.get("loss_weighting", {})
    train_dataset = EVCSWindowDataset(cache, "train", graph, use_events=use_events, normalize=True, loss_weight_config=loss_weight_config)
    val_dataset = EVCSWindowDataset(cache, "validation", graph, use_events=use_events, normalize=True, loss_weight_config=loss_weight_config)
    test_dataset = EVCSWindowDataset(cache, "test", graph, use_events=use_events, normalize=True, loss_weight_config=loss_weight_config)
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
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(training_config.get("lr", 1e-3)))
    scheduler = _make_scheduler(optimizer, training_config)
    criterion = nn.SmoothL1Loss(reduction="none") if str(training_config.get("loss", "SmoothL1")).lower() == "smoothl1" else nn.L1Loss(reduction="none")
    use_amp = bool(training_config.get("amp", False)) and device.type == "cuda"
    scaler = _make_grad_scaler(use_amp)
    epochs = int(training_config.get("epochs", 20))
    patience = int(training_config.get("early_stopping_patience", 4))
    early_stop_min_epochs = _early_stopping_min_epochs(training_config, baseline_id, epochs)
    verbose = bool(training_config.get("verbose", True))
    progress_config = config.get("progress", {})
    terminal_progress = bool(progress_config.get("terminal_bar", True))
    live_html = bool(progress_config.get("live_html", True))
    refresh_seconds = int(progress_config.get("refresh_seconds", 10))
    best_val = float("inf")
    stale_epochs = 0
    curve_rows = []
    baseline_started_at = time.perf_counter()
    best_epoch = 0
    for epoch in range(1, epochs + 1):
        epoch_started_at = time.perf_counter()
        train_loss = _run_epoch(model, train_loader, criterion, optimizer, scaler, device, training_config, train=True, use_amp=use_amp)
        val_loss = _run_epoch(model, val_loader, criterion, None, scaler, device, training_config, train=False, use_amp=use_amp)
        if scheduler is not None:
            scheduler.step(val_loss)
        current_lr = float(optimizer.param_groups[0]["lr"])
        epoch_seconds = time.perf_counter() - epoch_started_at
        improved = val_loss < best_val
        curve_rows.append(
            {
                "baseline_id": baseline_id,
                "epoch": epoch,
                "train_loss": train_loss,
                "validation_loss": val_loss,
                "best_validation_loss": min(best_val, val_loss),
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
            min(best_val, val_loss),
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
                "best_validation_loss": min(best_val, val_loss),
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
        if improved:
            best_val = val_loss
            best_epoch = epoch
            stale_epochs = 0
            torch.save({"model_state_dict": model.state_dict(), "config": config, "baseline_id": baseline_id}, checkpoint_path)
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
    eval_payload = _evaluate(model, test_loader, device, cache, loss_weight_config, graph)
    baseline_seconds = time.perf_counter() - baseline_started_at
    metrics = {
        "baseline_id": baseline_id,
        "MAE": eval_payload["MAE"],
        "RMSE": eval_payload["RMSE"],
        "event_weighted_MAE": eval_payload["event_weighted_MAE"],
        "prediction_count": eval_payload["prediction_count"],
        "best_validation_loss": best_val,
        "weighted_validation_loss": best_val,
        "best_epoch": best_epoch,
        "epochs_ran": len(curve_rows),
        "early_stop_min_epochs": early_stop_min_epochs,
        "train_seconds": baseline_seconds,
        "uses_events": use_events,
        "uses_graph": use_graph,
        "graph_mode": graph_mode,
        "gate_mean": eval_payload["gate_mean"],
        "gate_std": eval_payload["gate_std"],
        "alpha_hist": eval_payload["alpha_hist"],
        "alpha_event": eval_payload["alpha_event"],
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
        "curves": curve_rows,
        "samples": _prediction_samples(baseline_id, eval_payload, cache),
    }


def _run_epoch(model, loader, criterion, optimizer, scaler, device, training_config, train: bool, use_amp: bool) -> float:
    model.train(train)
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
                )
                loss = _weighted_loss(criterion, prediction, target, loss_weight)
            if train:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
        total_loss += float(loss.detach().cpu())
        total_batches += 1
    return total_loss / max(1, total_batches)


def _evaluate(model, loader, device, cache, loss_weight_config: dict[str, Any] | None = None, graph=None) -> dict[str, Any]:
    model.eval()
    predictions = []
    targets = []
    origins = []
    gate_values = []
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
            )
            raw_output = output.detach().cpu().numpy() * cache.normalization["load_std"] + cache.normalization["load_mean"]
            predictions.append(raw_output.astype(np.float32))
            targets.append(batch["target_raw"].numpy().astype(np.float32))
            origins.extend(batch["origin"].numpy().astype(int).tolist())
            gate = getattr(model, "last_gate", None)
            if gate is not None:
                gate_values.append(gate.detach().cpu().numpy().astype(np.float32))
    prediction = np.concatenate(predictions, axis=0) if predictions else np.zeros((0, cache.horizon_steps, len(cache.nodes)), dtype=np.float32)
    target = np.concatenate(targets, axis=0) if targets else np.zeros_like(prediction)
    error = prediction - target
    loss_weight = build_event_loss_weights(cache, origins, loss_weight_config or {}) if origins else np.zeros_like(error)
    weighted_abs = np.abs(error) * loss_weight if error.size else error
    alpha_hist = getattr(model, "last_alpha_hist", None)
    alpha_event = getattr(model, "last_alpha_event", None)
    channel_weights = getattr(model, "last_channel_weights", None)
    channel_weight_metrics = {}
    if channel_weights is not None:
        channel_names = list(getattr(graph, "channel_names", None) or [])
        for index, value in enumerate(channel_weights.detach().cpu().numpy().astype(np.float32)):
            channel_name = channel_names[index] if index < len(channel_names) else str(index)
            channel_weight_metrics[f"channel_weight_{channel_name}"] = float(value)
    return {
        "prediction": prediction,
        "target": target,
        "origins": origins,
        "MAE": float(np.mean(np.abs(error))) if error.size else float("nan"),
        "RMSE": float(np.sqrt(np.mean(error**2))) if error.size else float("nan"),
        "event_weighted_MAE": float(weighted_abs.sum() / max(float(loss_weight.sum()), 1.0)) if error.size else float("nan"),
        "prediction_count": int(error.size),
        "gate_mean": float(np.concatenate([values.reshape(-1) for values in gate_values]).mean()) if gate_values else np.nan,
        "gate_std": float(np.concatenate([values.reshape(-1) for values in gate_values]).std()) if gate_values else np.nan,
        "alpha_hist": float(alpha_hist.detach().cpu()) if alpha_hist is not None else np.nan,
        "alpha_event": float(alpha_event.detach().cpu()) if alpha_event is not None else np.nan,
        "channel_weights": channel_weight_metrics,
    }


def _event_window_metrics(baseline_id: str, eval_payload: dict[str, Any], cache) -> list[dict[str, Any]]:
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


def _event_masks(cache, origins: list[int]) -> dict[str, np.ndarray]:
    return event_window_masks(cache, origins)


def _prediction_samples(baseline_id: str, eval_payload: dict[str, Any], cache, limit: int = 200) -> list[dict[str, Any]]:
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


def _graph_ablation_rows(baseline_rows: list[dict[str, Any]], metrics_by_baseline: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    behavior = metrics_by_baseline.get("behavior_concat", {})
    dtw = metrics_by_baseline.get("dtw_demand_graph", {})
    event = metrics_by_baseline.get("event_graph_dynamic", {})
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


def build_primary_metric_summary(baseline_rows: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(baseline_rows).copy()
    if frame.empty:
        return frame
    behavior_mae = _baseline_metric(frame, "behavior_concat", "MAE")
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


def _metric_guide_text() -> str:
    return """# EXP-103 Metric Guide

Read outputs in this order:

1. primary_metric_summary.csv: main ranking by test MAE, plus deltas vs behavior_concat and dtw_demand_graph.
2. graph_ablation_table.csv: graph-specific claim checks, especially event_graph_dynamic vs behavior_concat, dtw_demand_graph, and deleted_event_graph.
3. event_window_metrics.csv: event-state checks for access_count, departure_count, load_jump_flag, high occupancy, and near_capacity_proxy.
4. training_curves.csv: train/validation loss, best epoch, early stopping behavior, and epoch runtime.
5. baseline_metrics.csv: complete per-baseline test MAE/RMSE and runtime fields.

Interpretation rules:

- Lower MAE/RMSE is better.
- For delta columns, negative means the row baseline is better than the comparator.
- event_graph_dynamic supports a strong C1 claim only if it improves over behavior_concat and responds competitively to dtw_demand_graph / historical_correlation_graph.
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
    path.parent.mkdir(parents=True, exist_ok=True)
    latest_rows = _latest_curve_by_baseline(curve_rows)
    ranking_rows = sorted(baseline_rows, key=lambda row: float(row.get("MAE", "inf")))
    cards = "".join(_baseline_card(baseline_id, latest_rows.get(baseline_id), active_baseline) for baseline_id in baseline_ids)
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
    :root {{ color-scheme: light; --ink:#17202a; --muted:#5d6d7e; --line:#d7dbdd; --blue:#246bfe; --green:#138d75; --amber:#b9770e; }}
    body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif; color:var(--ink); background:#f6f8fb; }}
    main {{ max-width:1180px; margin:0 auto; padding:28px; }}
    h1 {{ margin:0 0 6px; font-size:28px; letter-spacing:0; }}
    .sub {{ color:var(--muted); margin-bottom:20px; }}
    .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin:18px 0 24px; }}
    .card {{ background:white; border:1px solid var(--line); border-radius:8px; padding:14px; box-shadow:0 1px 2px rgba(0,0,0,.04); }}
    .active {{ border-color:var(--blue); box-shadow:0 0 0 2px rgba(36,107,254,.10); }}
    .name {{ font-weight:700; margin-bottom:8px; }}
    .metric {{ color:var(--muted); font-size:13px; line-height:1.7; }}
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
  <div class="sub">自动刷新：{max(3, refresh_seconds)} 秒。蓝线为 validation loss，绿线为 train loss；数值越低越好。</div>
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


def _baseline_card(baseline_id: str, row: dict[str, Any] | None, active_baseline: str | None) -> str:
    css_class = "card active" if baseline_id == active_baseline else "card"
    if row is None:
        return f'<div class="{css_class}"><div class="name">{baseline_id}</div><div class="metric">waiting</div><div class="bar"><div class="fill" style="width:0%"></div></div></div>'
    epoch = int(row["epoch"])
    width = min(100.0, 100.0 * epoch / max(1, epoch))
    return (
        f'<div class="{css_class}"><div class="name">{baseline_id}</div>'
        f'<div class="metric">epoch {epoch} · train {float(row["train_loss"]):.6f}<br>'
        f'val {float(row["validation_loss"]):.6f} · best {float(row["best_validation_loss"]):.6f}<br>'
        f'lr {float(row["lr"]):.3g} · {float(row["epoch_seconds"]):.1f}s</div>'
        f'<div class="bar"><div class="fill" style="width:{width:.1f}%"></div></div></div>'
    )


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


def _graph_mode_for_baseline(training_config: dict[str, Any], baseline_id: str) -> str:
    overrides = training_config.get("baseline_graph_modes", {})
    if isinstance(overrides, dict) and baseline_id in overrides:
        return str(overrides[baseline_id])
    return str(training_config.get("graph_mode", "concat"))


def _weighted_loss(criterion, prediction, target, loss_weight):
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
        raw_value = raw_config.get(baseline_id, raw_config.get("default", 0))
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
