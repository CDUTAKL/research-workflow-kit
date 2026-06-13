from __future__ import annotations

import argparse
import platform
import sys
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
    )
    write_json(
        out_dir / "graph_manifest.json",
        {
            "experiment_id": str(config.get("experiment_id", "EXP-103")),
            "graph_contract": {
                "top_k": int(graph_config.get("top_k", 5)),
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
        )
        baseline_rows.append(train_result["metrics"])
        event_rows.extend(train_result["event_metrics"])
        curve_rows.extend(train_result["curves"])
        sample_rows.extend(train_result["samples"])
        metrics_by_baseline[baseline_id] = train_result["metrics"]
        log_lines.append(f"{baseline_id}: test_MAE={train_result['metrics']['MAE']:.6f}")

    graph_rows = _graph_ablation_rows(baseline_rows, metrics_by_baseline)
    pd.DataFrame(baseline_rows).to_csv(out_dir / "baseline_metrics.csv", index=False)
    pd.DataFrame(graph_rows).to_csv(out_dir / "graph_ablation_table.csv", index=False)
    pd.DataFrame(event_rows).to_csv(out_dir / "event_window_metrics.csv", index=False)
    pd.DataFrame(curve_rows).to_csv(out_dir / "training_curves.csv", index=False)
    pd.DataFrame(sample_rows).to_csv(out_dir / "predictions_sample.csv", index=False)
    write_json(out_dir / "metrics.json", {"experiment_id": "EXP-103", "baselines": metrics_by_baseline})
    (out_dir / "logs" / "train.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    artifacts = [
        "metrics.json",
        "baseline_metrics.csv",
        "graph_ablation_table.csv",
        "event_window_metrics.csv",
        "graph_manifest.json",
        "training_curves.csv",
        "predictions_sample.csv",
        "config_resolved.json",
        "environment.txt",
        "logs/train.log",
    ]
    write_manifest(out_dir, str(config.get("experiment_id", "EXP-103")), artifacts)
    print(f"wrote EXP-103 training outputs to {out_dir}")


def _load_or_build_cache(config: dict[str, Any]):
    data_config = config.get("data", {})
    cache_config = config.get("cache", {})
    cache_path = Path(str(cache_config.get("tensor_cache_path", "data/processed/evcs_tensor_cache.npz")))
    manifest_path = Path(str(cache_config.get("manifest_path", "data/processed/evcs_tensor_cache_manifest.json")))
    split_path = Path(str(cache_config.get("split_path", "data/processed/splits/chronological_70_15_15.json")))
    if not cache_path.exists():
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
        )
        save_tensor_cache(cache, cache_path, split_path, manifest_path)
    return load_tensor_cache(cache_path, manifest_path)


def _train_one_baseline(
    baseline_id: str,
    config: dict[str, Any],
    cache,
    graph,
    device,
    checkpoint_path: Path,
    log_lines: list[str],
) -> dict[str, Any]:
    training_config = config.get("training", {})
    use_events = baseline_id != "no_graph"
    use_graph = baseline_id not in {"no_graph", "behavior_concat"}
    train_dataset = EVCSWindowDataset(cache, "train", graph, use_events=use_events, normalize=True)
    val_dataset = EVCSWindowDataset(cache, "validation", graph, use_events=use_events, normalize=True)
    test_dataset = EVCSWindowDataset(cache, "test", graph, use_events=use_events, normalize=True)
    batch_size = int(training_config.get("batch_size", 128))
    workers = int(training_config.get("num_workers", 0))
    pin_memory = bool(training_config.get("pin_memory", False)) and device.type == "cuda"
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=workers, pin_memory=pin_memory)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=workers, pin_memory=pin_memory)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=workers, pin_memory=pin_memory)
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
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(training_config.get("lr", 1e-3)))
    criterion = nn.SmoothL1Loss() if str(training_config.get("loss", "SmoothL1")).lower() == "smoothl1" else nn.L1Loss()
    use_amp = bool(training_config.get("amp", False)) and device.type == "cuda"
    scaler = _make_grad_scaler(use_amp)
    epochs = int(training_config.get("epochs", 20))
    patience = int(training_config.get("early_stopping_patience", 4))
    verbose = bool(training_config.get("verbose", True))
    best_val = float("inf")
    stale_epochs = 0
    curve_rows = []
    for epoch in range(1, epochs + 1):
        train_loss = _run_epoch(model, train_loader, criterion, optimizer, scaler, device, training_config, train=True, use_amp=use_amp)
        val_loss = _run_epoch(model, val_loader, criterion, None, scaler, device, training_config, train=False, use_amp=use_amp)
        improved = val_loss < best_val
        curve_rows.append(
            {
                "baseline_id": baseline_id,
                "epoch": epoch,
                "train_loss": train_loss,
                "validation_loss": val_loss,
                "best_validation_loss": min(best_val, val_loss),
                "improved": improved,
            }
        )
        progress_line = (
            f"[{baseline_id}] epoch {epoch}/{epochs} "
            f"train_loss={train_loss:.6f} val_loss={val_loss:.6f} "
            f"best_val={min(best_val, val_loss):.6f}"
        )
        log_lines.append(progress_line)
        if verbose:
            print(progress_line, flush=True)
        if improved:
            best_val = val_loss
            stale_epochs = 0
            torch.save({"model_state_dict": model.state_dict(), "config": config, "baseline_id": baseline_id}, checkpoint_path)
        else:
            stale_epochs += 1
            if stale_epochs >= patience:
                stop_line = f"[{baseline_id}] early_stop epoch={epoch} patience={patience}"
                log_lines.append(stop_line)
                if verbose:
                    print(stop_line, flush=True)
                break
    if checkpoint_path.exists():
        state = _load_checkpoint(checkpoint_path, device)
        model.load_state_dict(state["model_state_dict"])
    eval_payload = _evaluate(model, test_loader, device, cache)
    metrics = {
        "baseline_id": baseline_id,
        "MAE": eval_payload["MAE"],
        "RMSE": eval_payload["RMSE"],
        "prediction_count": eval_payload["prediction_count"],
        "best_validation_loss": best_val,
        "epochs_ran": len(curve_rows),
        "uses_events": use_events,
        "uses_graph": use_graph,
    }
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
        if train:
            optimizer.zero_grad(set_to_none=True)
        with torch.set_grad_enabled(train):
            with _autocast_context(device, use_amp):
                prediction = model(history_load, history_events, graph_indices, graph_weights)
                loss = criterion(prediction, target)
            if train:
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
        total_loss += float(loss.detach().cpu())
        total_batches += 1
    return total_loss / max(1, total_batches)


def _evaluate(model, loader, device, cache) -> dict[str, Any]:
    model.eval()
    predictions = []
    targets = []
    origins = []
    with torch.no_grad():
        for batch in loader:
            output = model(
                batch["history_load"].to(device),
                batch["history_events"].to(device),
                batch["graph_indices"].to(device),
                batch["graph_weights"].to(device),
            )
            raw_output = output.detach().cpu().numpy() * cache.normalization["load_std"] + cache.normalization["load_mean"]
            predictions.append(raw_output.astype(np.float32))
            targets.append(batch["target_raw"].numpy().astype(np.float32))
            origins.extend(batch["origin"].numpy().astype(int).tolist())
    prediction = np.concatenate(predictions, axis=0) if predictions else np.zeros((0, cache.horizon_steps, len(cache.nodes)), dtype=np.float32)
    target = np.concatenate(targets, axis=0) if targets else np.zeros_like(prediction)
    error = prediction - target
    return {
        "prediction": prediction,
        "target": target,
        "origins": origins,
        "MAE": float(np.mean(np.abs(error))) if error.size else float("nan"),
        "RMSE": float(np.sqrt(np.mean(error**2))) if error.size else float("nan"),
        "prediction_count": int(error.size),
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


def _resolve_device(requested: str):
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(requested)


def _make_grad_scaler(use_amp: bool):
    if hasattr(torch, "amp") and hasattr(torch.amp, "GradScaler"):
        return torch.amp.GradScaler("cuda", enabled=use_amp)
    return torch.cuda.amp.GradScaler(enabled=use_amp)


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
