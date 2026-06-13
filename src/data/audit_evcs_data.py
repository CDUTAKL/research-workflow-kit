from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from evcs.data.audit import audit_sessions
from evcs.utils.artifacts import write_json, write_manifest
from evcs.utils.config import load_experiment_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit EVCS session data for EXP-101.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    config = load_experiment_config(args.config)
    data_config = config.get("data", {})
    out_dir = Path(args.out)
    logs_dir = out_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    source_path = Path(str(data_config["source_path"]))
    sessions = pd.read_csv(source_path)
    report = audit_sessions(
        sessions,
        required_fields=list(data_config.get("required_fields", [])),
        blocked_feature_fields=list(data_config.get("blocked_feature_fields", [])),
        timestamp_field=str(data_config.get("timestamp_field", "connectionTime")),
        node_candidates=list(data_config.get("node_candidates", [])),
        split_rule=dict(data_config.get("split_rule", {"train": 0.7, "validation": 0.15, "test": 0.15})),
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(report.field_availability).to_csv(out_dir / "field_availability.csv", index=False)
    pd.DataFrame(report.node_stability).to_csv(out_dir / "node_stability.csv", index=False)
    write_json(out_dir / "split_manifest.json", report.split_manifest)
    write_json(out_dir / "leakage_flags.json", report.leakage_flags)
    write_json(out_dir / "data_manifest.json", report.data_manifest)
    write_json(out_dir / "config_resolved.json", config)
    (logs_dir / "audit.log").write_text(
        f"EXP-101 audit completed\nsource={source_path}\nrows={len(sessions)}\n",
        encoding="utf-8",
    )
    artifacts = [
        "field_availability.csv",
        "node_stability.csv",
        "split_manifest.json",
        "leakage_flags.json",
        "data_manifest.json",
        "config_resolved.json",
        "logs/audit.log",
    ]
    write_manifest(out_dir, str(config.get("experiment_id", "EXP-101")), artifacts)
    print(f"wrote EXP-101 audit outputs to {out_dir}")


if __name__ == "__main__":
    main()
