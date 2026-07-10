#!/usr/bin/env python3
from __future__ import annotations

"""Run EXP-108 external baselines under one frozen data/evaluation contract."""

import argparse
import csv
import gzip
import hashlib
import json
import platform
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from evcs.data.tensor_cache import build_tensor_cache, load_tensor_cache, save_tensor_cache
from evcs.utils.config import load_experiment_config

try:
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, Dataset
except Exception:
    torch = None
    nn = None
    DataLoader = None
    Dataset = object

try:
    import lightgbm as lgb
except Exception:
    lgb = None

from evcs.models.standard_baselines import GRUForecast, STGCNForecast

SUPPORTED = {"persistence", "lightgbm", "gru", "stgcn"}


class WindowDataset(Dataset):
    def __init__(self, cache, split: str):
        self.cache = cache
        self.origins = list(cache.split_indices[split])

    def __len__(self):
        return len(self.origins)

    def __getitem__(self, index):
        origin = self.origins[index]
        start = origin - self.cache.history_steps + 1
        load = self.cache.load[start : origin + 1]
        events = self.cache.event_features[start : origin + 1]
        load_z = (load - self.cache.normalization["load_mean"]) / self.cache.normalization["load_std"]
        event_z = (events - self.cache.normalization["event_mean"]) / self.cache.normalization["event_std"]
        x = np.concatenate([load_z[..., None], event_z], axis=-1).astype(np.float32)
        target = self.cache.load[origin + 1 : origin + 1 + self.cache.horizon_steps].astype(np.float32)
        return torch.from_numpy(x), torch.from_numpy(target), int(origin)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--methods", default="")
    parser.add_argument("--contract-only", action="store_true", help="Validate data/config without optional ML dependencies.")
    args = parser.parse_args()
    config = load_experiment_config(args.config)
    seed = int(args.seed if args.seed is not None else config.get("seed", 42))
    methods = [item.strip().lower() for item in args.methods.split(",") if item.strip()] or list(config["methods"])
    unknown = sorted(set(methods) - SUPPORTED)
    if unknown:
        raise SystemExit(f"unsupported methods: {unknown}")
    out = Path(args.out)
    (out / "logs").mkdir(parents=True, exist_ok=True)
    (out / "checkpoints").mkdir(parents=True, exist_ok=True)
    _set_seed(seed)
    cache = _load_or_build_cache(config)
    contract = _validate_contract(config, cache, methods, seed)
    _write_json(out / "config_resolved.json", {**config, "seed": seed, "methods": methods})
    _write_json(out / "data_contract.json", contract)
    _write_environment(out / "environment.txt")
    if args.contract_only:
        _finish(out, config, seed, methods, {}, "contract_only")
        print(json.dumps(contract, ensure_ascii=False, indent=2))
        return
    _require_dependencies(methods)
    all_metrics: dict[str, Any] = {}
    log = []
    for method in methods:
        started = time.perf_counter()
        if method == "persistence":
            rows = _persistence(cache, seed)
            checkpoint_note = "deterministic; no checkpoint\n"
        elif method == "lightgbm":
            rows = _run_lightgbm(cache, config, seed, log)
            checkpoint_note = "LightGBM model is serialized separately when formal training completes.\n"
        else:
            rows = _run_neural(cache, config, seed, method, out, log)
            checkpoint_note = "see best.pt\n"
        method_dir = out / method
        method_dir.mkdir(parents=True, exist_ok=True)
        _write_json(method_dir / "config_resolved.json", {**config, "seed": seed, "method": method})
        (method_dir / "environment.txt").write_text((out / "environment.txt").read_text(encoding="utf-8"), encoding="utf-8")
        (method_dir / "checkpoint_status.txt").write_text(checkpoint_note, encoding="utf-8")
        _write_predictions(method_dir / "predictions.csv.gz", rows)
        metrics = _evaluate_rows(rows)
        metrics["runtime_seconds"] = time.perf_counter() - started
        all_metrics[method] = metrics
        _write_method_tables(method_dir, metrics)
    _finish(out, config, seed, methods, all_metrics, "completed")
    (out / "logs" / "train.log").write_text("\n".join(log) + "\n", encoding="utf-8")


def _load_or_build_cache(config):
    cc, dc, fc = config["cache"], config["data"], config["features"]
    cache_path, manifest_path = Path(cc["tensor_cache_path"]), Path(cc["manifest_path"])
    if cache_path.exists() and manifest_path.exists():
        cache = load_tensor_cache(cache_path, manifest_path)
    else:
        if not cc.get("auto_build", False):
            raise FileNotFoundError(cache_path)
        frame = pd.read_csv(dc["source_path"])
        cache = build_tensor_cache(
            frame, dc["timestamp_field"], dc["node_field"], dc["target_field"],
            list(fc["event_feature_fields"]), int(cc["history_steps"]), int(cc["horizon_steps"]),
            dict(cc["split_rule"]), bool(fc.get("include_time_context", False)),
            bool(fc.get("include_enhanced_events", False)),
        )
        save_tensor_cache(cache, cache_path, cc["split_path"], manifest_path)
    return cache


def _validate_contract(config, cache, methods, seed):
    errors = []
    if cache.history_steps != int(config["cache"]["history_steps"]): errors.append("history_steps mismatch")
    if cache.horizon_steps != int(config["cache"]["horizon_steps"]): errors.append("horizon_steps mismatch")
    if config["features"].get("event_flag_as_input", True): errors.append("future event flag input must be disabled")
    if config["graph"].get("test_statistics_forbidden") is not True: errors.append("STGCN test-statistics guard missing")
    for split in ("train", "validation", "test"):
        if not cache.split_indices.get(split): errors.append(f"empty split: {split}")
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "status": "pass", "seed": seed, "methods": methods,
        "history_steps": cache.history_steps, "horizon_steps": cache.horizon_steps,
        "node_count": len(cache.nodes), "event_features": cache.event_feature_names,
        "split_sizes": {key: len(value) for key, value in cache.split_indices.items()},
        "normalization_source": "train_only_tensor_cache",
        "causal_policy": config["features"]["causal_policy"],
        "stgcn_graph_source": "training_load_only",
    }


def _persistence(cache, seed):
    rows = []
    for origin in cache.split_indices["test"]:
        pred = np.repeat(cache.load[origin][None, :], cache.horizon_steps, axis=0)
        rows.extend(_rows_for_origin(cache, origin, cache.load[origin + 1 : origin + 1 + cache.horizon_steps], pred, "persistence", seed))
    return rows


def _run_lightgbm(cache, config, seed, log):
    def matrix(split):
        features, targets, meta = [], [], []
        for origin in cache.split_indices[split]:
            start = origin - cache.history_steps + 1
            history = cache.load[start : origin + 1].T
            current_events = cache.event_features[origin]
            base = np.concatenate([history, current_events], axis=1)
            for horizon in range(cache.horizon_steps):
                features.append(np.column_stack([base, np.full((len(cache.nodes),), horizon + 1)]))
                targets.append(cache.load[origin + 1 + horizon])
                meta.extend((origin, horizon, node) for node in range(len(cache.nodes)))
        return np.concatenate(features), np.concatenate(targets), meta
    x_train, y_train, _ = matrix("train")
    x_val, y_val, _ = matrix("validation")
    x_test, y_test, meta = matrix("test")
    best = None
    for leaves in config["lightgbm"]["num_leaves"]:
        for lr in config["lightgbm"]["learning_rate"]:
            model = lgb.LGBMRegressor(
                objective="regression_l1", num_leaves=int(leaves), learning_rate=float(lr),
                n_estimators=int(config["lightgbm"]["n_estimators"]), random_state=seed,
                feature_fraction=float(config["lightgbm"].get("feature_fraction", 1.0)),
                bagging_fraction=float(config["lightgbm"].get("bagging_fraction", 1.0)),
                bagging_freq=int(config["lightgbm"].get("bagging_freq", 0)),
            )
            model.fit(x_train, y_train, eval_set=[(x_val, y_val)], callbacks=[lgb.early_stopping(int(config["lightgbm"]["early_stopping_rounds"]), verbose=False)])
            score = float(np.mean(np.abs(y_val - model.predict(x_val))))
            if best is None or score < best[0]: best = (score, model)
    pred = best[1].predict(x_test)
    rows = []
    for value, target, (origin, horizon, node) in zip(pred, y_test, meta):
        rows.append(_one_row(cache, origin, horizon, node, target, value, "lightgbm", seed))
    log.append(f"lightgbm validation_MAE={best[0]:.8f}")
    return rows


def _run_neural(cache, config, seed, method, out, log):
    train = WindowDataset(cache, "train"); val = WindowDataset(cache, "validation"); test = WindowDataset(cache, "test")
    tc = config["training"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    loaders = {
        "train": DataLoader(train, batch_size=int(tc["batch_size"]), shuffle=True, num_workers=int(tc.get("num_workers", 0))),
        "validation": DataLoader(val, batch_size=int(tc["batch_size"]), shuffle=False, num_workers=int(tc.get("num_workers", 0))),
        "test": DataLoader(test, batch_size=int(tc["batch_size"]), shuffle=False, num_workers=int(tc.get("num_workers", 0))),
    }
    channels = 1 + cache.event_features.shape[-1]
    if method == "gru":
        model = GRUForecast(channels, int(tc["hidden_channels"]), int(tc["num_layers"]), float(tc["dropout"]), cache.horizon_steps)
    else:
        adjacency = torch.from_numpy(_train_adjacency(cache, int(config["graph"]["top_k"])))
        model = STGCNForecast(channels, int(tc["hidden_channels"]), float(tc["dropout"]), cache.horizon_steps, adjacency)
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(tc["lr"]))
    best, stale, best_state = float("inf"), 0, None
    max_train = tc.get("max_train_batches"); max_eval = tc.get("max_eval_batches")
    for epoch in range(int(tc["epochs"])):
        _epoch(model, loaders["train"], optimizer, device, cache, max_train)
        val_mae = _epoch(model, loaders["validation"], None, device, cache, max_eval)
        log.append(f"{method} epoch={epoch + 1} validation_MAE={val_mae:.8f}")
        if val_mae < best:
            best, stale = val_mae, 0
            best_state = {key: value.detach().cpu() for key, value in model.state_dict().items()}
        else:
            stale += 1
            if stale >= int(tc["early_stopping_patience"]): break
    model.load_state_dict(best_state)
    checkpoint = out / "checkpoints" / method / "best.pt"
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    torch.save(best_state, checkpoint)
    return _predict_neural(model, loaders["test"], device, cache, method, seed, max_eval)


def _epoch(model, loader, optimizer, device, cache, max_batches):
    model.train(optimizer is not None); errors = []
    for batch_index, (x, target, _) in enumerate(loader):
        if max_batches is not None and batch_index >= int(max_batches): break
        x, target = x.to(device), target.to(device)
        pred_z = model(x)
        mean = torch.as_tensor(cache.normalization["load_mean"], device=device)
        std = torch.as_tensor(cache.normalization["load_std"], device=device)
        pred = pred_z * std[None, None, :] + mean[None, None, :]
        loss = torch.mean(torch.abs(pred - target))
        if optimizer is not None:
            optimizer.zero_grad(); loss.backward(); optimizer.step()
        errors.append(float(loss.detach().cpu()))
    return float(np.mean(errors))


def _predict_neural(model, loader, device, cache, method, seed, max_batches):
    rows = []; model.eval()
    with torch.no_grad():
        for batch_index, (x, target, origins) in enumerate(loader):
            if max_batches is not None and batch_index >= int(max_batches): break
            pred_z = model(x.to(device)).cpu().numpy()
            pred = pred_z * cache.normalization["load_std"][None, None, :] + cache.normalization["load_mean"][None, None, :]
            for i, origin in enumerate(origins.numpy().tolist()):
                rows.extend(_rows_for_origin(cache, origin, target[i].numpy(), pred[i], method, seed))
    return rows


def _train_adjacency(cache, top_k):
    train_end = max(cache.split_indices["train"])
    corr = np.nan_to_num(np.corrcoef(cache.load[: train_end + 1].T), nan=0.0)
    corr = np.clip(corr, 0.0, None); np.fill_diagonal(corr, 0.0)
    adjacency = np.zeros_like(corr, dtype=np.float32)
    for node in range(len(cache.nodes)):
        keep = np.argsort(corr[node])[-min(top_k, len(cache.nodes) - 1):]
        adjacency[node, keep] = corr[node, keep]
    adjacency += np.eye(len(cache.nodes), dtype=np.float32)
    degree = np.maximum(adjacency.sum(axis=1), 1e-8)
    inv = np.diag(1.0 / np.sqrt(degree))
    return (inv @ adjacency @ inv).astype(np.float32)


def _rows_for_origin(cache, origin, truth, pred, method, seed):
    return [_one_row(cache, origin, h, n, truth[h, n], pred[h, n], method, seed) for h in range(cache.horizon_steps) for n in range(len(cache.nodes))]


def _one_row(cache, origin, horizon, node, truth, pred, method, seed):
    names = cache.event_feature_names
    next_index = origin + 1 + horizon
    event = cache.event_features[next_index]
    def feature(name): return float(event[node, names.index(name)]) if name in names else 0.0
    event_any = feature("access_count") > 0 or feature("departure_count") > 0 or feature("load_jump_flag") > 0
    active = feature("active_count") > 0
    return {
        "method": method, "seed": seed, "split": "test", "forecast_origin": origin,
        "timestamp": cache.timestamps[next_index], "node_id": cache.nodes[node], "horizon": horizon + 1,
        "target": float(truth), "prediction": float(pred), "abs_error": abs(float(truth) - float(pred)),
        "squared_error": (float(truth) - float(pred)) ** 2, "event_window": int(event_any),
        "active": int(active), "active_stable": int(active and not event_any),
        "inactive_zero_load": int((not active) and (not event_any) and float(truth) == 0.0),
        "positive_load": int(float(truth) > 0.0),
    }


def _evaluate_rows(rows):
    frame = pd.DataFrame(rows)
    result = {"global": _metric_block(frame)}
    for key in ("event_window", "active_stable", "inactive_zero_load", "positive_load"):
        result[key] = _metric_block(frame[frame[key] == 1])
    result["horizons"] = {str(h): _metric_block(part) for h, part in frame.groupby("horizon")}
    node = [_metric_block(part)["MAE"] for _, part in frame.groupby("node_id")]
    result["node_macro_MAE"] = float(np.mean(node)) if node else None
    return result


def _metric_block(frame):
    if frame.empty: return {"count": 0, "MAE": None, "RMSE": None, "WAPE": None}
    error = frame["target"].to_numpy() - frame["prediction"].to_numpy()
    denom = float(np.abs(frame["target"]).sum())
    return {"count": len(frame), "MAE": float(np.abs(error).mean()), "RMSE": float(np.sqrt(np.square(error).mean())), "WAPE": float(np.abs(error).sum() / denom) if denom else None}


def _write_method_tables(path, metrics):
    _write_json(path / "metrics.json", metrics)
    pd.DataFrame([{"stratum": key, **value} for key, value in metrics.items() if isinstance(value, dict) and "MAE" in value]).to_csv(path / "stratified_metrics.csv", index=False)
    pd.DataFrame([{"horizon": key, **value} for key, value in metrics["horizons"].items()]).to_csv(path / "horizon_metrics.csv", index=False)
    pd.DataFrame([{"metric": "node_macro_MAE", "value": metrics["node_macro_MAE"]}]).to_csv(path / "node_macro_metrics.csv", index=False)
    _write_json(path / "manifest.json", {"status": "completed", "artifacts": sorted(item.name for item in path.iterdir() if item.is_file())})


def _write_predictions(path, rows):
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def _finish(out, config, seed, methods, metrics, status):
    _write_json(out / "metrics.json", {"experiment_id": config["experiment_id"], "seed": seed, "methods": metrics})
    _write_json(out / "manifest.json", {"experiment_id": config["experiment_id"], "seed": seed, "methods": methods, "status": status, "config": str(config.get("output", ""))})
    if not (out / "logs" / "train.log").exists(): (out / "logs" / "train.log").write_text(f"status={status}\n", encoding="utf-8")
    (out / "exit_code.txt").write_text("0\n", encoding="utf-8")
    _checksums(out)


def _require_dependencies(methods):
    if any(item in {"gru", "stgcn"} for item in methods) and torch is None: raise SystemExit("PyTorch is required for GRU/STGCN")
    if "lightgbm" in methods and lgb is None: raise SystemExit("LightGBM is required for lightgbm")


def _set_seed(seed):
    random.seed(seed); np.random.seed(seed)
    if torch is not None: torch.manual_seed(seed)


def _write_environment(path):
    lines = [f"python={sys.version}", f"platform={platform.platform()}", f"torch={getattr(torch, '__version__', 'unavailable')}", f"lightgbm={getattr(lgb, '__version__', 'unavailable')}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _checksums(out):
    rows = []
    for path in sorted(out.rglob("*")):
        if path.is_file() and path.name != "checksums.sha256": rows.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(out)}")
    (out / "checksums.sha256").write_text("\n".join(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
