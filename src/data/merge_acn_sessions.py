from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from evcs.utils.artifacts import write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge segmented ACN session CSV files and drop duplicate sessions.")
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--out", default="data/raw/acn_sessions.csv")
    parser.add_argument("--manifest", default="data/raw/acn_sessions_merged_manifest.json")
    parser.add_argument("--dedupe-field", default="sessionID")
    args = parser.parse_args()

    frames = []
    input_rows = {}
    for pattern in args.inputs:
        for path in sorted(Path().glob(pattern)):
            frame = pd.read_csv(path)
            input_rows[str(path)] = int(len(frame))
            if not frame.empty:
                frames.append(frame)
    if not frames:
        raise SystemExit("no input CSV files matched")

    merged = pd.concat(frames, ignore_index=True)
    before = len(merged)
    if args.dedupe_field in merged.columns:
        merged = merged.drop_duplicates(subset=[args.dedupe_field], keep="first")
    merged = merged.sort_values(["connectionTime", args.dedupe_field]).reset_index(drop=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(out, index=False)
    write_json(
        args.manifest,
        {
            "inputs": input_rows,
            "input_row_count": int(before),
            "output_row_count": int(len(merged)),
            "dedupe_field": args.dedupe_field,
            "duplicates_removed": int(before - len(merged)),
            "output_path": str(out),
        },
    )
    print(f"wrote merged ACN sessions to {out} ({len(merged)} rows; removed {before - len(merged)} duplicates)")


if __name__ == "__main__":
    main()
