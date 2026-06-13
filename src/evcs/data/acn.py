from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

CANONICAL_SESSION_COLUMNS = [
    "sessionID",
    "siteID",
    "stationID",
    "EVSEID",
    "spaceID",
    "connectionTime",
    "disconnectTime",
    "doneChargingTime",
    "kWhDelivered",
    "has_time_series",
    "source",
]


def normalize_acn_sessions(records: list[dict[str, Any]] | pd.DataFrame, site: str | None = None) -> pd.DataFrame:
    """Normalize ACN-Data API/export records into the Stage-5 session contract."""
    frame = records.copy() if isinstance(records, pd.DataFrame) else pd.DataFrame.from_records(records)
    if frame.empty:
        return pd.DataFrame(columns=CANONICAL_SESSION_COLUMNS)

    normalized = pd.DataFrame()
    normalized["sessionID"] = _first_present(frame, ["sessionID", "session_id", "_id", "id"]).astype(str)
    normalized["siteID"] = _first_present(frame, ["siteID", "site", "networkID"], default=site or "unknown").fillna(site)
    normalized["stationID"] = _first_present(frame, ["stationID", "station_id", "station", "node_id", "spaceID", "EVSEID"])
    normalized["EVSEID"] = _first_present(frame, ["EVSEID", "evse_id", "evseID", "stationID"])
    normalized["spaceID"] = _first_present(frame, ["spaceID", "space_id", "space", "stationID", "EVSEID"])
    normalized["connectionTime"] = pd.to_datetime(_first_present(frame, ["connectionTime", "connection_time", "start"]), errors="coerce")
    normalized["disconnectTime"] = pd.to_datetime(_first_present(frame, ["disconnectTime", "disconnect_time", "end"]), errors="coerce")
    normalized["doneChargingTime"] = pd.to_datetime(
        _first_present(frame, ["doneChargingTime", "done_charging_time", "doneCharging"]),
        errors="coerce",
    )
    normalized["kWhDelivered"] = pd.to_numeric(
        _first_present(frame, ["kWhDelivered", "kwhDelivered", "energy_kwh", "energy"], default=0.0),
        errors="coerce",
    )
    normalized["has_time_series"] = _infer_time_series_flag(frame)
    normalized["source"] = _first_present(frame, ["source"], default="acn-data")

    normalized = normalized.dropna(subset=["connectionTime", "disconnectTime"]).copy()
    normalized["stationID"] = normalized["stationID"].fillna(normalized["spaceID"]).fillna(normalized["EVSEID"])
    normalized["EVSEID"] = normalized["EVSEID"].fillna(normalized["stationID"])
    normalized["spaceID"] = normalized["spaceID"].fillna(normalized["stationID"])
    normalized["siteID"] = normalized["siteID"].fillna(site or "unknown")
    normalized["kWhDelivered"] = normalized["kWhDelivered"].fillna(0.0)
    normalized["has_time_series"] = normalized["has_time_series"].fillna(False).astype(bool)
    normalized["source"] = normalized["source"].fillna("acn-data")
    return normalized[CANONICAL_SESSION_COLUMNS].reset_index(drop=True)


def load_acn_export(path: str | Path, site: str | None = None) -> pd.DataFrame:
    """Load a local ACN JSON/CSV export and normalize it."""
    source = Path(path)
    if source.suffix.lower() == ".csv":
        records: list[dict[str, Any]] | pd.DataFrame = pd.read_csv(source)
    else:
        payload = json.loads(source.read_text(encoding="utf-8"))
        records = _extract_records(payload)
    return normalize_acn_sessions(records, site=site)


def _extract_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("sessions", "data", "items", "_items"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [payload]
    raise ValueError("ACN export must be a JSON object, JSON list, or CSV file")


def _first_present(frame: pd.DataFrame, columns: list[str], default: Any = None) -> pd.Series:
    for column in columns:
        if column in frame.columns:
            return frame[column]
    return pd.Series([default] * len(frame), index=frame.index)


def _infer_time_series_flag(frame: pd.DataFrame) -> pd.Series:
    markers = [
        "has_time_series",
        "hasTimeSeries",
        "timeSeries",
        "timeseries",
        "time_series_path",
        "Charging Current (A)",
        "Voltage (V)",
        "Power (kW)",
    ]
    for marker in markers:
        if marker in frame.columns:
            values = frame[marker]
            if values.dtype == bool:
                return values
            return values.notna()
    return pd.Series([False] * len(frame), index=frame.index)
