"""Render a lightweight research experiment project skeleton.

This creates directories and placeholder files only when they do not already
exist. It is meant for new projects or for documenting a proposed layout.
"""
from __future__ import annotations

import argparse
from pathlib import Path


DIRS = [
    "src/data",
    "src/models",
    "src/training",
    "src/evaluation",
    "src/metrics",
    "src/utils",
    "configs/experiment",
    "configs/smoke",
    "scripts/figures",
    "tests",
]

FILES = {
    "src/__init__.py": "",
    "src/data/__init__.py": "",
    "src/models/__init__.py": "",
    "src/training/__init__.py": "",
    "src/evaluation/__init__.py": "",
    "src/metrics/__init__.py": "",
    "src/utils/__init__.py": "",
    "configs/experiment/EXP-001.yaml": "seed: 42\nsplit: TBD\nmetric: TBD\noutput: outputs/EXP-001\n",
    "configs/smoke/EXP-001-smoke.yaml": "seed: 42\nsplit: smoke\nmetric: TBD\noutput: outputs/EXP-001-smoke\n",
    "scripts/figures/README.md": "# Figure Scripts\n\nPut reproducible thesis figure/table scripts here.\n",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a minimal research code skeleton.")
    parser.add_argument("--project", default=".", help="Project root.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned paths without writing.")
    args = parser.parse_args()

    root = Path(args.project).resolve()
    planned = [root / item for item in DIRS] + [root / item for item in FILES]
    if args.dry_run:
        for path in planned:
            print(path)
        return

    for dirname in DIRS:
        (root / dirname).mkdir(parents=True, exist_ok=True)
    for filename, content in FILES.items():
        path = root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8")
    print(f"Rendered research project skeleton in: {root}")


if __name__ == "__main__":
    main()

