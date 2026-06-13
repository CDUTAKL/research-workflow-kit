from __future__ import annotations

import pandas as pd


def persistence_predictions(
    series: pd.DataFrame,
    timestamp_field: str,
    node_field: str,
    target_field: str,
) -> pd.DataFrame:
    required = {timestamp_field, node_field, target_field}
    missing = required.difference(series.columns)
    if missing:
        raise ValueError(f"missing required columns: {', '.join(sorted(missing))}")
    frame = series.copy()
    frame[timestamp_field] = pd.to_datetime(frame[timestamp_field], errors="coerce")
    if frame[timestamp_field].isna().any():
        raise ValueError(f"timestamp field contains unparsable values: {timestamp_field}")
    frame = frame.sort_values([node_field, timestamp_field])
    frame["prediction"] = frame.groupby(node_field)[target_field].shift(1)
    predictions = frame.dropna(subset=["prediction"]).copy()
    return predictions[[timestamp_field, node_field, target_field, "prediction"]]

