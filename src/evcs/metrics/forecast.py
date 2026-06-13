from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np


def mean_absolute_error(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    truth, pred = _paired_arrays(y_true, y_pred)
    return float(np.mean(np.abs(truth - pred)))


def root_mean_squared_error(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    truth, pred = _paired_arrays(y_true, y_pred)
    return float(math.sqrt(np.mean((truth - pred) ** 2)))


def picp(y_true: Sequence[float], lower: Sequence[float], upper: Sequence[float]) -> float:
    truth, lo = _paired_arrays(y_true, lower)
    _, hi = _paired_arrays(y_true, upper)
    return float(np.mean((truth >= lo) & (truth <= hi)))


def pinaw(y_true: Sequence[float], lower: Sequence[float], upper: Sequence[float]) -> float:
    truth, lo = _paired_arrays(y_true, lower)
    _, hi = _paired_arrays(y_true, upper)
    value_range = float(np.max(truth) - np.min(truth))
    if value_range == 0:
        return 0.0
    return float(np.mean(hi - lo) / value_range)


def wis(y_true: Sequence[float], lower: Sequence[float], upper: Sequence[float], alpha: float) -> float:
    truth, lo = _paired_arrays(y_true, lower)
    _, hi = _paired_arrays(y_true, upper)
    width = hi - lo
    lower_penalty = (2.0 / alpha) * (lo - truth) * (truth < lo)
    upper_penalty = (2.0 / alpha) * (truth - hi) * (truth > hi)
    return float(np.mean(width + lower_penalty + upper_penalty))


def _paired_arrays(left: Sequence[float], right: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    left_array = np.asarray(left, dtype=float)
    right_array = np.asarray(right, dtype=float)
    if left_array.shape != right_array.shape:
        raise ValueError(f"shape mismatch: {left_array.shape} != {right_array.shape}")
    if left_array.size == 0:
        raise ValueError("metric inputs must not be empty")
    return left_array, right_array

