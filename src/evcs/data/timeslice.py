from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

TIMESLICE_COLUMNS = [
    "timestamp",
    "node_id",
    "load",
    "access_count",
    "departure_count",
    "active_count",
    "occupancy_rate",
    "demand_intensity",
    "load_jump_flag",
]


def build_time_slices(
    sessions: pd.DataFrame,
    node_field: str,
    freq: str = "15min",
    load_jump_quantile: float = 0.9,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build causal EVCS time slices from session-level ACN data.

    When true time-series current/power is unavailable, load is reconstructed as
    uniform delivered energy over connected intervals. The manifest records this
    explicitly so EXP-101 can decide whether the processed data are acceptable.
    """
    if node_field not in sessions.columns:
        raise ValueError(f"node field not found: {node_field}")
    required = ["connectionTime", "disconnectTime", "kWhDelivered"]
    missing = [field for field in required if field not in sessions.columns]
    if missing:
        raise ValueError(f"missing required session fields: {missing}")

    frame = sessions.copy()
    frame["connectionTime"] = pd.to_datetime(frame["connectionTime"], errors="coerce")
    frame["disconnectTime"] = pd.to_datetime(frame["disconnectTime"], errors="coerce")
    frame["kWhDelivered"] = pd.to_numeric(frame["kWhDelivered"], errors="coerce").fillna(0.0)
    frame = frame.dropna(subset=["connectionTime", "disconnectTime", node_field])
    frame = frame[frame["disconnectTime"] >= frame["connectionTime"]].copy()
    if frame.empty:
        return pd.DataFrame(columns=TIMESLICE_COLUMNS), _empty_manifest(node_field, freq)

    start = frame["connectionTime"].min().floor(freq)
    end = frame["disconnectTime"].max().ceil(freq)
    timestamps = pd.date_range(start, end, freq=freq)
    nodes = sorted(str(node) for node in frame[node_field].dropna().astype(str).unique())
    index = pd.MultiIndex.from_product([timestamps, nodes], names=["timestamp", "node_id"])
    out = pd.DataFrame(index=index).reset_index()
    activity_rows: list[dict[str, Any]] = []
    access_rows: list[dict[str, Any]] = []
    departure_rows: list[dict[str, Any]] = []
    for session in frame.itertuples(index=False):
        node = str(getattr(session, node_field))
        connection = session.connectionTime
        disconnect = session.disconnectTime
        energy = float(session.kWhDelivered)
        active_slots = _active_slots(connection, disconnect, freq)
        energy_per_slot = energy / len(active_slots) if active_slots else 0.0
        for slot in active_slots:
            activity_rows.append({"timestamp": slot, "node_id": node, "load": energy_per_slot, "active_count": 1})
        access_rows.append({"timestamp": connection.floor(freq), "node_id": node, "access_count": 1})
        departure_rows.append({"timestamp": disconnect.floor(freq), "node_id": node, "departure_count": 1})

    out = out.merge(_sum_rows(activity_rows, ["load", "active_count"]), on=["timestamp", "node_id"], how="left")
    out = out.merge(_sum_rows(access_rows, ["access_count"]), on=["timestamp", "node_id"], how="left")
    out = out.merge(_sum_rows(departure_rows, ["departure_count"]), on=["timestamp", "node_id"], how="left")
    for column in ("load", "access_count", "departure_count", "active_count"):
        out[column] = out[column].fillna(0)
    out[["access_count", "departure_count", "active_count"]] = out[
        ["access_count", "departure_count", "active_count"]
    ].astype(int)
    out["occupancy_rate"] = _occupancy_rate(out)
    out["demand_intensity"] = out["load"]
    out["load_jump_flag"] = _load_jump_flag(out, load_jump_quantile)
    out = out[TIMESLICE_COLUMNS].sort_values(["timestamp", "node_id"]).reset_index(drop=True)
    manifest = {
        "node_field": node_field,
        "node_count": len(nodes),
        "row_count": int(len(out)),
        "time_start": start.isoformat(),
        "time_end": end.isoformat(),
        "time_granularity": freq,
        "load_unit": "kWh_per_time_slice",
        "load_reconstruction": "uniform_session_energy",
        "source_has_time_series": bool(frame.get("has_time_series", pd.Series([False])).fillna(False).astype(bool).any()),
        "time_series_policy": "use_true_current_or_power_when_available_else_uniform_session_energy",
    }
    return out, manifest


def _active_slots(connection: pd.Timestamp, disconnect: pd.Timestamp, freq: str) -> list[pd.Timestamp]:
    if disconnect <= connection:
        return []
    freq_delta = pd.Timedelta(freq)
    first = connection.floor(freq)
    slots = []
    current = first
    while current < disconnect:
        if current + freq_delta > connection:
            slots.append(current)
        current += freq_delta
    return slots


def _sum_rows(rows: list[dict[str, Any]], value_fields: list[str]) -> pd.DataFrame:
    columns = ["timestamp", "node_id", *value_fields]
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame.from_records(rows).groupby(["timestamp", "node_id"], as_index=False)[value_fields].sum()


def _occupancy_rate(frame: pd.DataFrame) -> pd.Series:
    max_by_node = frame.groupby("node_id")["active_count"].transform("max").replace(0, np.nan)
    return (frame["active_count"] / max_by_node).fillna(0.0).clip(0.0, 1.0)


def _load_jump_flag(frame: pd.DataFrame, quantile: float) -> pd.Series:
    diffs = frame.sort_values(["node_id", "timestamp"]).groupby("node_id")["load"].diff().abs().fillna(0.0)
    positive = diffs[diffs > 0]
    threshold = float(positive.quantile(quantile)) if not positive.empty else float("inf")
    return (diffs > threshold).astype(int)


def _empty_manifest(node_field: str, freq: str) -> dict[str, Any]:
    return {
        "node_field": node_field,
        "node_count": 0,
        "row_count": 0,
        "time_start": None,
        "time_end": None,
        "time_granularity": freq,
        "load_unit": "kWh_per_time_slice",
        "load_reconstruction": "uniform_session_energy",
        "source_has_time_series": False,
        "time_series_policy": "use_true_current_or_power_when_available_else_uniform_session_energy",
    }
