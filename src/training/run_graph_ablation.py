from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from evcs.graphs.baselines import build_graph_baseline, graph_lag_metrics_from_pivot
from evcs.graphs.event_graph import build_event_adjacency
from evcs.utils.artifacts import write_json, write_manifest
from evcs.utils.config import load_experiment_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Run EXP-103 graph baseline smoke ablations.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    config = load_experiment_config(args.config)
    data_config = config.get("data", {})
    graph_config = config.get("graph", {})
    out_dir = Path(args.out)
    logs_dir = out_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    source_path = Path(str(data_config["source_path"]))
    timestamp_field = str(data_config.get("timestamp_field", "timestamp"))
    node_field = str(data_config.get("node_field", "node_id"))
    target_field = str(data_config.get("target_field", "load"))
    event_feature_fields = list(graph_config.get("event_feature_fields", []))
    usecols = sorted({timestamp_field, node_field, target_field, *event_feature_fields})
    frame = pd.read_csv(source_path, usecols=usecols)
    frame[timestamp_field] = pd.to_datetime(frame[timestamp_field], errors="coerce")
    top_k = int(graph_config.get("top_k", 1))
    dtw_resample = graph_config.get("dtw_resample")
    dtw_max_points = graph_config.get("dtw_max_points")
    dtw_max_points = int(dtw_max_points) if dtw_max_points else None
    seed = int(config.get("seed", 42))
    baselines = ["event_graph", *list(config.get("baselines", []))]

    table_rows = []
    graph_manifest = {
        "experiment_id": str(config.get("experiment_id", "EXP-103")),
        "source_path": str(source_path),
        "baseline_ids": baselines,
        "graph_contract": {
            "top_k": top_k,
            "event_feature_fields": event_feature_fields,
            "dtw_resample": dtw_resample,
            "dtw_max_points": dtw_max_points,
            "smoke_metric_note": "lagged-neighbor-load proxy only; not a formal training result",
        },
        "graphs": {},
    }
    print("building shared target pivot", flush=True)
    target_pivot = frame.pivot_table(
        index=timestamp_field,
        columns=node_field,
        values=target_field,
        aggfunc="mean",
    ).sort_index().fillna(0.0)
    print("building shared event graph", flush=True)
    event_graph = build_event_adjacency(frame, node_field=node_field, feature_fields=event_feature_fields, top_k=top_k)
    event_adjacency = None
    for baseline_id in baselines:
        print(f"building graph baseline: {baseline_id}", flush=True)
        graph = build_graph_baseline(
            baseline_id,
            frame,
            node_field=node_field,
            timestamp_field=timestamp_field,
            target_field=target_field,
            event_feature_fields=event_feature_fields,
            top_k=top_k,
            seed=seed,
            dtw_resample=str(dtw_resample) if dtw_resample else None,
            dtw_max_points=dtw_max_points,
            event=event_graph,
            target_pivot=target_pivot,
        )
        if baseline_id == "event_graph":
            event_adjacency = graph.adjacency
        print(f"evaluating lag proxy: {baseline_id}", flush=True)
        metrics = graph_lag_metrics_from_pivot(target_pivot, graph)
        adjacency_delta = _adjacency_l1_delta(event_adjacency, graph.adjacency)
        table_rows.append(
            {
                "baseline_id": baseline_id,
                "node_count": len(graph.nodes),
                "edge_count": int(np.count_nonzero(graph.adjacency)),
                "lag_proxy_MAE": metrics["MAE"],
                "lag_proxy_RMSE": metrics["RMSE"],
                "prediction_count": metrics["prediction_count"],
                "adjacency_l1_delta_vs_event": adjacency_delta,
                "conclusion_level": "smoke_only",
            }
        )
        graph_manifest["graphs"][baseline_id] = {
            "nodes": graph.nodes,
            "edge_count": int(np.count_nonzero(graph.adjacency)),
            "top_edges": graph.top_edges[:20],
            "row_sums": [float(value) for value in graph.adjacency.sum(axis=1)],
        }

    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(table_rows).to_csv(out_dir / "graph_ablation_table.csv", index=False)
    write_json(out_dir / "graph_manifest.json", graph_manifest)
    write_json(out_dir / "config_resolved.json", config)
    (logs_dir / "run.log").write_text(
        f"EXP-103 graph ablation smoke completed\nsource={source_path}\nbaselines={','.join(baselines)}\n",
        encoding="utf-8",
    )
    artifacts = ["graph_ablation_table.csv", "graph_manifest.json", "config_resolved.json", "logs/run.log"]
    write_manifest(out_dir, str(config.get("experiment_id", "EXP-103")), artifacts)
    print(f"wrote EXP-103 graph ablation smoke outputs to {out_dir}")


def _adjacency_l1_delta(reference: np.ndarray | None, candidate: np.ndarray) -> float:
    if reference is None or reference.shape != candidate.shape:
        return 0.0
    return float(np.abs(reference - candidate).sum())


if __name__ == "__main__":
    main()
