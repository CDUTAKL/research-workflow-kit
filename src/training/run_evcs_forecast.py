from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from evcs.metrics.forecast import mean_absolute_error, root_mean_squared_error
from evcs.models.baselines import persistence_predictions
from evcs.utils.artifacts import write_json, write_manifest
from evcs.utils.config import load_experiment_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Run lightweight EVCS forecast baselines.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    config = load_experiment_config(args.config)
    data_config = config.get("data", {})
    model_config = config.get("model", {})
    out_dir = Path(args.out)
    logs_dir = out_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    baseline_id = str(model_config.get("baseline_id", "persistence"))
    if baseline_id != "persistence":
        raise ValueError(f"unsupported baseline_id for lightweight runner: {baseline_id}")

    source_path = Path(str(data_config["source_path"]))
    frame = pd.read_csv(source_path)
    predictions = persistence_predictions(
        frame,
        timestamp_field=str(data_config.get("timestamp_field", "timestamp")),
        node_field=str(data_config.get("node_field", "node_id")),
        target_field=str(data_config.get("target_field", "load")),
    )
    target_field = str(data_config.get("target_field", "load"))
    metrics = {
        "experiment_id": str(config.get("experiment_id", "EXP-102")),
        "baseline_id": baseline_id,
        "MAE": mean_absolute_error(predictions[target_field], predictions["prediction"]),
        "RMSE": root_mean_squared_error(predictions[target_field], predictions["prediction"]),
        "prediction_count": int(len(predictions)),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(out_dir / "predictions.csv", index=False)
    write_json(out_dir / "metrics.json", metrics)
    write_json(out_dir / "config_resolved.json", config)
    (logs_dir / "run.log").write_text(
        f"{baseline_id} baseline completed\nsource={source_path}\npredictions={len(predictions)}\n",
        encoding="utf-8",
    )
    artifacts = ["metrics.json", "predictions.csv", "config_resolved.json", "logs/run.log"]
    write_manifest(out_dir, str(config.get("experiment_id", "EXP-102")), artifacts)
    print(f"wrote EXP-102 forecast outputs to {out_dir}")


if __name__ == "__main__":
    main()
