"""
Auto-generate an experiment entry in experiment-registry.md.

Reads experiment parameters from a JSON file (default: last_experiment.json)
or command-line overrides, auto-fills date, git commit, experiment ID, data hash
(or computes it via --data-dir), and appends a completed entry to
docs/thesis/experiment-registry.md.

Usage:
    python scripts/new_experiment.py                              # read last_experiment.json
    python scripts/new_experiment.py --status done                 # override single field
    python scripts/new_experiment.py --data-dir data/raw_v3       # auto-compute data hash
    python scripts/new_experiment.py --data-hash abc123           # provide hash manually
    python scripts/new_experiment.py --help                       # show all fields
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

THESIS_DIR = Path("docs/thesis")
REGISTRY_PATH = THESIS_DIR / "experiment-registry.md"
LEGACY_ELOG_PATH = THESIS_DIR / "experiment-log.md"
CONFIG_PATH = Path("last_experiment.json")

REGISTRY_TEMPLATE = """# Experiment Registry

## Update Rules

- Register every experiment before using its result in writing.
- Keep one stable experiment ID per run or comparable run group.
- Link result files, logs, notebooks, configs, and generated figures.
- `experiment-log.md` is a legacy compatibility file; this registry is the primary evidence record.

## Experiment Table

| Experiment ID | Research Question / Claim | Method / Config | Dataset / Split | Command / Notebook | Output Path | Key Metrics | Status | Date | Notes |
|---|---|---|---|---|---|---|---|---|---|
"""


def get_git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "N/A (not a git repo or no commits)"


def compute_data_hash(data_dir: str) -> str:
    """Compute SHA256 hash of a data directory using data_hash.py logic."""
    from data_hash import compute_data_hash as cdh
    dir_hash, _ = cdh(Path(data_dir).resolve())
    return dir_hash


def get_defaults() -> dict:
    """Build default config; override with last_experiment.json if present."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    defaults = {
        "hypothesis": "H?.?",
        "prev_exp": "无",
        "script": "experiments/experiment.py",
        "hyperparams": "lr=1e-3, batch_size=32",
        "data_version": "dataset_v1",
        "data_hash": "N/A (run with --data-dir <path> to auto-fill)",
        "seed_global": "42",
        "seed_numpy": "42",
        "seed_torch": "42",
        "cuda_det": "true",
        "env_date": today,
        "primary_metric": "N/A",
        "threshold": "N/A",
        "secondary_metrics": "N/A",
        "status": "planned",
        "diagnosis": "（如成功则删除本节）",
        "hypothesis_impact": "",
        "checkpoint_path": "",
        "log_path": "",
        "tensorboard_path": "",
    }
    if CONFIG_PATH.exists():
        try:
            saved = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            defaults.update(saved)
        except json.JSONDecodeError:
            pass
    return defaults


def parse_overrides(argv: list[str]) -> dict:
    """Parse --key value pairs from command line.  --data-dir computes a hash."""
    overrides = {}
    i = 1
    while i < len(argv):
        if argv[i].startswith("--") and i + 1 < len(argv):
            key = argv[i][2:].replace("-", "_")
            overrides[key] = argv[i + 1]
            i += 2
        else:
            i += 1
    return overrides


def markdown_cell(value: str) -> str:
    value = str(value).replace("\n", " ").strip()
    return value.replace("|", r"\|")


def existing_experiment_ids() -> list[str]:
    ids: list[str] = []
    for path in (REGISTRY_PATH, LEGACY_ELOG_PATH):
        if path.exists():
            ids.extend(re.findall(r"\bEXP-\d{4}-\d{2}-\d{2}-\d{3}\b", path.read_text(encoding="utf-8")))
    return ids


def next_experiment_id(today: str) -> str:
    nums = []
    for exp_id in existing_experiment_ids():
        match = re.fullmatch(rf"EXP-{re.escape(today)}-(\d{{3}})", exp_id)
        if match:
            nums.append(int(match.group(1)))
    return f"EXP-{today}-{(max(nums) + 1) if nums else 1:03d}"


def registry_row(cfg: dict) -> str:
    experiment_id = cfg["experiment_id"]
    claim = cfg.get("claim_id") or cfg.get("hypothesis") or "TBD"
    method = cfg.get("hyperparams", "TBD")
    data = f"{cfg.get('data_version', 'TBD')} / hash={cfg.get('data_hash', 'N/A')}"
    command = f"`{cfg.get('script', 'TBD')}`"
    output_parts = [
        part for part in (
            cfg.get("checkpoint_path"),
            cfg.get("log_path"),
            cfg.get("tensorboard_path"),
        )
        if part
    ]
    output_path = "; ".join(output_parts) if output_parts else "TBD"
    metrics = "; ".join(
        part for part in (
            cfg.get("primary_metric"),
            cfg.get("secondary_metrics"),
        )
        if part and part != "N/A"
    ) or "TBD"
    notes = (
        f"prev={cfg.get('prev_exp', 'N/A')}; "
        f"seed global={cfg.get('seed_global')}, numpy={cfg.get('seed_numpy')}, "
        f"torch={cfg.get('seed_torch')}; git={cfg.get('git_commit')}"
    )
    cells = [
        experiment_id,
        claim,
        method,
        data,
        command,
        output_path,
        metrics,
        cfg.get("status", "planned"),
        cfg.get("env_date"),
        notes,
    ]
    return "| " + " | ".join(markdown_cell(str(cell)) for cell in cells) + " |"


def ensure_registry() -> str:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if REGISTRY_PATH.exists():
        return REGISTRY_PATH.read_text(encoding="utf-8")
    return REGISTRY_TEMPLATE


def append_registry_row(row: str) -> None:
    current = ensure_registry().rstrip()
    REGISTRY_PATH.write_text(current + "\n" + row + "\n", encoding="utf-8")


def main() -> None:
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        print("Overridable fields (use --field-name value):")
        for k in get_defaults():
            print(f"  --{k.replace('_', '-')}")
        sys.exit(0)

    cfg = get_defaults()
    overrides = parse_overrides(sys.argv)
    cfg.update(overrides)

    # --- Auto-fill ---
    cfg["git_commit"] = get_git_commit()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cfg["env_date"] = cfg.get("env_date", today)

    # --- Data hash: compute if --data-dir given ---
    if "--data-dir" in sys.argv:
        idx = sys.argv.index("--data-dir")
        if idx + 1 < len(sys.argv):
            data_dir = sys.argv[idx + 1]
            try:
                cfg["data_hash"] = compute_data_hash(data_dir)
                print(f"Data hash: {cfg['data_hash'][:16]}... (from {data_dir})")
            except Exception as e:
                print(f"Warning: could not hash {data_dir}: {e}", file=sys.stderr)

    # --- Generate sequential ID and append to the primary registry ---
    cfg["experiment_id"] = next_experiment_id(today)
    append_registry_row(registry_row(cfg))

    # --- Save for next time (without volatile fields) ---
    save_cfg = {k: v for k, v in cfg.items()
                if k not in ("experiment_id", "git_commit", "env_date", "data_hash")}
    CONFIG_PATH.write_text(
        json.dumps(save_cfg, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"{cfg['experiment_id']} appended to {REGISTRY_PATH}")
    print(f"Config saved to {CONFIG_PATH} (will be reused next time)")


if __name__ == "__main__":
    main()
