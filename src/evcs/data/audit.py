from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class DataAuditReport:
    field_availability: list[dict[str, Any]]
    node_stability: list[dict[str, Any]]
    recommended_node_field: str | None
    split_manifest: dict[str, Any]
    leakage_flags: dict[str, Any]
    data_manifest: dict[str, Any]


def audit_sessions(
    sessions: pd.DataFrame,
    required_fields: list[str],
    blocked_feature_fields: list[str],
    timestamp_field: str,
    node_candidates: list[str],
    split_rule: dict[str, float],
) -> DataAuditReport:
    if timestamp_field not in sessions.columns:
        raise ValueError(f"timestamp field not found: {timestamp_field}")
    frame = sessions.copy()
    frame[timestamp_field] = pd.to_datetime(frame[timestamp_field], errors="coerce")
    if frame[timestamp_field].isna().any():
        raise ValueError(f"timestamp field contains unparsable values: {timestamp_field}")

    field_availability = [_field_row(frame, field) for field in required_fields]
    node_stability = [_node_row(frame, field) for field in node_candidates]
    recommended_node_field = _recommend_node_field(node_stability)
    split_manifest = _chronological_split_manifest(frame, timestamp_field, split_rule)
    leakage_flags = _leakage_flags(frame, blocked_feature_fields)
    time_series_availability = _time_series_availability(frame)
    data_manifest = {
        "row_count": int(len(frame)),
        "column_count": int(len(frame.columns)),
        "columns": list(frame.columns),
        "timestamp_field": timestamp_field,
        "time_start": frame[timestamp_field].min().isoformat(),
        "time_end": frame[timestamp_field].max().isoformat(),
        "recommended_node_field": recommended_node_field,
        "time_series_availability": time_series_availability,
    }
    return DataAuditReport(
        field_availability=field_availability,
        node_stability=node_stability,
        recommended_node_field=recommended_node_field,
        split_manifest=split_manifest,
        leakage_flags=leakage_flags,
        data_manifest=data_manifest,
    )


def _field_row(frame: pd.DataFrame, field: str) -> dict[str, Any]:
    present = field in frame.columns
    series = frame[field] if present else pd.Series(dtype=object)
    non_null = int(series.notna().sum()) if present else 0
    return {
        "field": field,
        "present": bool(present),
        "dtype": str(series.dtype) if present else "missing",
        "non_null_count": non_null,
        "missing_count": int(len(frame) - non_null) if present else int(len(frame)),
        "non_null_rate": float(non_null / len(frame)) if len(frame) else 0.0,
    }


def _node_row(frame: pd.DataFrame, field: str) -> dict[str, Any]:
    if field not in frame.columns:
        return {
            "node_field": field,
            "present": False,
            "unique_nodes": 0,
            "min_sessions_per_node": 0,
            "median_sessions_per_node": 0.0,
            "max_sessions_per_node": 0,
        }
    counts = frame[field].dropna().value_counts()
    return {
        "node_field": field,
        "present": True,
        "unique_nodes": int(counts.shape[0]),
        "min_sessions_per_node": int(counts.min()) if not counts.empty else 0,
        "median_sessions_per_node": float(counts.median()) if not counts.empty else 0.0,
        "max_sessions_per_node": int(counts.max()) if not counts.empty else 0,
    }


def _recommend_node_field(node_rows: list[dict[str, Any]]) -> str | None:
    for row in node_rows:
        if row["present"] and row["unique_nodes"] > 0:
            return str(row["node_field"])
    return None


def _chronological_split_manifest(
    frame: pd.DataFrame,
    timestamp_field: str,
    split_rule: dict[str, float],
) -> dict[str, Any]:
    sorted_frame = frame.sort_values(timestamp_field)
    total = len(sorted_frame)
    train_count = int(total * float(split_rule.get("train", 0.7)))
    validation_count = int(total * float(split_rule.get("validation", 0.15)))
    if total and train_count == 0:
        train_count = 1
    if total - train_count > 1 and validation_count == 0:
        validation_count = 1
    test_count = total - train_count - validation_count
    counts = {"train": train_count, "validation": validation_count, "test": test_count}
    boundaries: dict[str, dict[str, str | None]] = {}
    start = 0
    for split, count in counts.items():
        subset = sorted_frame.iloc[start : start + count]
        boundaries[split] = {
            "start": subset[timestamp_field].min().isoformat() if not subset.empty else None,
            "end": subset[timestamp_field].max().isoformat() if not subset.empty else None,
        }
        start += count
    return {"rule": split_rule, "counts": counts, "boundaries": boundaries}


def _leakage_flags(frame: pd.DataFrame, blocked_feature_fields: list[str]) -> dict[str, Any]:
    present = [field for field in blocked_feature_fields if field in frame.columns]
    missing = [field for field in blocked_feature_fields if field not in frame.columns]
    return {
        "blocked_fields_present": present,
        "blocked_fields_missing": missing,
        "feature_use_policy": "blocked_fields_present_must_not_be_used_as_prediction_time_features",
        "risk_level": "high" if present else "low",
    }


def _time_series_availability(frame: pd.DataFrame) -> dict[str, Any]:
    marker_fields = [
        "has_time_series",
        "time_series_path",
        "Charging Current (A)",
        "Voltage (V)",
        "Power (kW)",
        "pilotSignal",
    ]
    present_markers = [field for field in marker_fields if field in frame.columns]
    rows_with_time_series = 0
    if "has_time_series" in frame.columns:
        rows_with_time_series = int(frame["has_time_series"].fillna(False).astype(bool).sum())
    elif present_markers:
        rows_with_time_series = int(frame[present_markers].notna().any(axis=1).sum())
    return {
        "present_marker_fields": present_markers,
        "rows_with_time_series_markers": rows_with_time_series,
        "has_time_series_evidence": rows_with_time_series > 0,
        "policy": "prefer_true_current_or_power_series_when_available_else_uniform_session_energy_reconstruction",
    }
