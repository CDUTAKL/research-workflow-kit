from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from evcs.data.tensor_cache import build_tensor_cache, save_tensor_cache
from evcs.utils.config import load_experiment_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Build EXP-103 tensor cache from EVCS time-slice data.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_experiment_config(args.config)
    data_config = config.get("data", {})
    cache_config = config.get("cache", {})
    graph_config = config.get("graph", {})
    feature_config = config.get("features", {})

    source_path = Path(str(data_config["source_path"]))
    tensor_cache_path = Path(str(cache_config.get("tensor_cache_path", "data/processed/evcs_tensor_cache.npz")))
    split_path = Path(str(cache_config.get("split_path", "data/processed/splits/chronological_70_15_15.json")))
    manifest_path = Path(str(cache_config.get("manifest_path", "data/processed/evcs_tensor_cache_manifest.json")))

    frame = pd.read_csv(source_path)
    cache = build_tensor_cache(
        frame,
        timestamp_field=str(data_config.get("timestamp_field", "timestamp")),
        node_field=str(data_config.get("node_field", "node_id")),
        target_field=str(data_config.get("target_field", "load")),
        event_feature_fields=list(graph_config.get("event_feature_fields", [])),
        history_steps=int(cache_config.get("history_steps", 96)),
        horizon_steps=int(cache_config.get("horizon_steps", 4)),
        split_rule=dict(cache_config.get("split_rule", {"train": 0.7, "validation": 0.15, "test": 0.15})),
        include_time_context=bool(feature_config.get("include_time_context", False)),
        include_enhanced_events=bool(feature_config.get("include_enhanced_events", False)),
        near_capacity_quantile=float(feature_config.get("near_capacity_quantile", 0.9)),
    )
    save_tensor_cache(cache, tensor_cache_path, split_path, manifest_path)
    print(f"wrote EXP-103 tensor cache to {tensor_cache_path}")


if __name__ == "__main__":
    main()
