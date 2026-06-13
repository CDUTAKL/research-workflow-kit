from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


def load_experiment_config(path: str | Path) -> dict[str, Any]:
    """Load a JSON or lightweight YAML experiment config."""
    config_path = Path(path)
    text = config_path.read_text(encoding="utf-8")
    data = json.loads(text) if config_path.suffix.lower() == ".json" else _parse_simple_yaml(text)
    if not isinstance(data, dict):
        raise ValueError(f"config must be a mapping: {config_path}")
    return data


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    rows: list[tuple[int, str]] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        rows.append((len(raw) - len(raw.lstrip(" ")), stripped))
    result, index = _parse_mapping(rows, 0, 0)
    if index != len(rows):
        raise ValueError("could not parse full config")
    return result


def _parse_mapping(rows: list[tuple[int, str]], index: int, indent: int) -> tuple[dict[str, Any], int]:
    data: dict[str, Any] = {}
    while index < len(rows):
        current_indent, line = rows[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ValueError(f"unexpected indentation at line: {line}")
        if line.startswith("- "):
            raise ValueError(f"unexpected list item in mapping: {line}")
        if ":" not in line:
            raise ValueError(f"expected key-value line: {line}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        index += 1
        if raw_value:
            data[key] = _parse_scalar(raw_value)
        elif index < len(rows) and rows[index][0] > current_indent and rows[index][1].startswith("- "):
            data[key], index = _parse_list(rows, index, rows[index][0])
        elif index < len(rows) and rows[index][0] > current_indent:
            data[key], index = _parse_mapping(rows, index, rows[index][0])
        else:
            data[key] = {}
    return data, index


def _parse_list(rows: list[tuple[int, str]], index: int, indent: int) -> tuple[list[Any], int]:
    values: list[Any] = []
    while index < len(rows):
        current_indent, line = rows[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ValueError(f"unexpected nested list indentation at line: {line}")
        if not line.startswith("- "):
            break
        values.append(_parse_scalar(line[2:].strip()))
        index += 1
    return values, index


def _parse_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None
    if (value.startswith("[") and value.endswith("]")) or (value.startswith("{") and value.endswith("}")):
        return ast.literal_eval(value)
    for parser in (int, float):
        try:
            return parser(value)
        except ValueError:
            continue
    return value.strip('"').strip("'")
