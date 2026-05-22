"""
Auto-generate an experiment entry in experiment-log.md.

Reads experiment parameters from a JSON file (default: last_experiment.json)
or command-line overrides, auto-fills date, git commit, experiment ID, data hash
(or computes it via --data-dir), and appends a completed entry to
docs/thesis/experiment-log.md.

Usage:
    python scripts/new_experiment.py                              # read last_experiment.json
    python scripts/new_experiment.py --status 成功                 # override single field
    python scripts/new_experiment.py --data-dir data/raw_v3       # auto-compute data hash
    python scripts/new_experiment.py --data-hash abc123           # provide hash manually
    python scripts/new_experiment.py --help                       # show all fields
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

THESIS_DIR = Path("docs/thesis")
ELOG_PATH = THESIS_DIR / "experiment-log.md"
CONFIG_PATH = Path("last_experiment.json")

TEMPLATE = """## EXP-{exp_id}

### 绑定
- **假设**: {hypothesis}
- **前序实验**: {prev_exp}
- **实验脚本**: `{script}`
- **Git commit**: `{git_commit}`

### 配置
- **关键超参**: {hyperparams}
- **数据版本**: {data_version}
- **数据哈希**: `{data_hash}`
- **种子**: global={seed_global}, numpy={seed_numpy}, torch={seed_torch}, cuda_deterministic={cuda_det}
- **环境**: `requirements-freeze-{env_date}.txt`

### 结果
- **核心指标**: {primary_metric} (阈值: {threshold})
- **辅助指标**: {secondary_metrics}
- **状态**: [{status}]

### 失败诊断
{diagnosis}

### 对假设的影响
- 假设本身是否需要修正？[ ] 是 [ ] 否
- 说明: {hypothesis_impact}

### 产出
- **Checkpoint 路径**: {checkpoint_path}
- **日志路径**: {log_path}
- **TensorBoard 路径**: {tensorboard_path}
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
        "status": " ",  # space so template renders as "[ ]"
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

    # --- Generate sequential ID ---
    if ELOG_PATH.exists():
        existing = ELOG_PATH.read_text(encoding="utf-8")
        ids = []
        import re as _re
        for m in _re.findall(r"EXP-(\d{4}-\d{2}-\d{2})-(\d{3})", existing):
            ids.append((m[0], int(m[1])))
        if ids:
            latest_date, latest_num = max(ids, key=lambda x: (x[0], x[1]))
            if latest_date == today:
                cfg["exp_id"] = f"{today}-{latest_num + 1:03d}"
            else:
                cfg["exp_id"] = f"{today}-001"
        else:
            cfg["exp_id"] = f"{today}-001"
    else:
        cfg["exp_id"] = f"{today}-001"

    entry = TEMPLATE.format(**cfg)

    # --- Append to experiment log ---
    ELOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if ELOG_PATH.exists():
        current = ELOG_PATH.read_text(encoding="utf-8")
        entry = "\n" + entry
    else:
        current = "# Experiment Log\n\n> 结构化实验日志\n\n---\n"
    ELOG_PATH.write_text(current + entry, encoding="utf-8")

    # --- Save for next time (without volatile fields) ---
    save_cfg = {k: v for k, v in cfg.items()
                if k not in ("exp_id", "git_commit", "env_date", "data_hash")}
    CONFIG_PATH.write_text(
        json.dumps(save_cfg, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"EXP-{cfg['exp_id']} appended to {ELOG_PATH}")
    print(f"Config saved to {CONFIG_PATH} (will be reused next time)")


if __name__ == "__main__":
    main()
