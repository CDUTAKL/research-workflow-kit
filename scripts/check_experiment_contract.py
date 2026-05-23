"""Check a thesis experiment contract before or after running.

The script is intentionally lightweight and offline. It validates that an
experiment has a stable ID, config, registry entry, smoke config, and optional
machine-readable output artifacts.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_OUTPUTS = ("manifest.json", "config_resolved.json", "metrics.json", "logs")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def infer_config(exp_id: str) -> Path | None:
    for suffix in (".yaml", ".yml", ".json"):
        candidate = Path("configs") / "experiment" / f"{exp_id}{suffix}"
        if candidate.exists():
            return candidate
    return None


def infer_smoke_config(exp_id: str) -> Path | None:
    candidates = [
        Path("configs") / "smoke" / f"{exp_id}-smoke.yaml",
        Path("configs") / "smoke" / f"{exp_id}.yaml",
        Path("configs") / "experiment" / f"{exp_id}-smoke.yaml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def markdown_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append(cells)
    return rows


def registry_has_experiment(registry: Path, exp_id: str) -> tuple[bool, str]:
    text = read_text(registry)
    for cells in markdown_rows(text):
        if cells and cells[0] == exp_id:
            return True, " | ".join(cells)
    return False, ""


def text_has_field(text: str, field: str) -> bool:
    return re.search(rf"\b{re.escape(field)}\b", text, flags=re.IGNORECASE) is not None


def check_outputs(output_dir: Path) -> list[str]:
    missing: list[str] = []
    for name in REQUIRED_OUTPUTS:
        if not (output_dir / name).exists():
            missing.append(name)
    return missing


def main() -> None:
    parser = argparse.ArgumentParser(description="Check EXP-* experiment contract files and records.")
    parser.add_argument("--experiment-id", required=True, help="Experiment ID such as EXP-001.")
    parser.add_argument("--config", help="Experiment config path. Defaults to configs/experiment/<EXP>.yaml|yml|json.")
    parser.add_argument("--smoke-config", help="Smoke config path. Defaults to configs/smoke/<EXP>-smoke.yaml when present.")
    parser.add_argument("--registry", default="docs/thesis/experiment-registry.md")
    parser.add_argument("--output", help="Output directory. Defaults to outputs/<EXP>.")
    parser.add_argument("--require-outputs", action="store_true", help="Require manifest/config/metrics/logs to exist.")
    parser.add_argument("--warn-only", action="store_true", help="Exit 0 even when blocking issues are found.")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    exp_id = args.experiment_id.strip()

    if not re.fullmatch(r"EXP-(?:AUTO-)?[A-Za-z0-9.-]+", exp_id):
        errors.append(f"invalid experiment id: {exp_id}")

    config = Path(args.config) if args.config else infer_config(exp_id)
    if config is None or not config.exists():
        errors.append("experiment config not found")
        config_text = ""
    else:
        config_text = read_text(config)
        for field in ("seed", "split", "metric"):
            if not text_has_field(config_text, field):
                warnings.append(f"config does not mention `{field}`")
        if not text_has_field(config_text, "output"):
            warnings.append("config does not mention output path")

    registry = Path(args.registry)
    if not registry.exists():
        errors.append(f"registry not found: {registry}")
        registry_row = ""
    else:
        found, registry_row = registry_has_experiment(registry, exp_id)
        if not found:
            errors.append(f"{exp_id} is not registered in {registry}")

    smoke_config = Path(args.smoke_config) if args.smoke_config else infer_smoke_config(exp_id)
    if smoke_config is None or not smoke_config.exists():
        warnings.append("smoke config not found")

    output_dir = Path(args.output) if args.output else Path("outputs") / exp_id
    if args.require_outputs:
        if not output_dir.exists():
            errors.append(f"output directory not found: {output_dir}")
        else:
            missing_outputs = check_outputs(output_dir)
            if missing_outputs:
                errors.append(f"output directory missing: {', '.join(missing_outputs)}")
    elif registry_row and str(output_dir) not in registry_row and "TBD" not in registry_row:
        warnings.append(f"registry row does not mention expected output path `{output_dir}`")

    print(f"Experiment: {exp_id}")
    print(f"Errors: {len(errors)}  |  Warnings: {len(warnings)}")
    if config:
        print(f"Config: {config}")
    print(f"Registry: {registry}")
    print(f"Output: {output_dir}")
    if errors:
        print("BLOCKING ERRORS:")
        for item in errors:
            print(f"  [x] {item}")
    if warnings:
        print("WARNINGS:")
        for item in warnings:
            print(f"  [!] {item}")

    if errors and not args.warn_only:
        sys.exit(1)


if __name__ == "__main__":
    main()

