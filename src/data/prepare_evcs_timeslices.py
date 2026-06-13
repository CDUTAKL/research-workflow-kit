from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from evcs.data.timeslice import build_time_slices
from evcs.utils.artifacts import write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare EVCS time-slice data from normalized ACN sessions.")
    parser.add_argument("--input", default="data/raw/acn_sessions.csv")
    parser.add_argument("--out", default="data/processed/evcs_timeslice.csv")
    parser.add_argument("--manifest", default="data/processed/evcs_timeslice_manifest.json")
    parser.add_argument("--node-field", default="stationID")
    parser.add_argument("--time-granularity", default="15min")
    parser.add_argument("--load-jump-quantile", type=float, default=0.9)
    args = parser.parse_args()

    source = Path(args.input)
    sessions = pd.read_csv(source)
    timeslice, manifest = build_time_slices(
        sessions,
        node_field=args.node_field,
        freq=args.time_granularity,
        load_jump_quantile=args.load_jump_quantile,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    timeslice.to_csv(out, index=False)
    manifest.update({"source_path": str(source), "output_path": str(out)})
    write_json(args.manifest, manifest)
    print(f"wrote EVCS time-slice data to {out} ({len(timeslice)} rows)")


if __name__ == "__main__":
    main()
