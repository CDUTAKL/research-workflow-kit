from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def default_codex_skills_dir() -> Path:
    return Path.home() / ".codex" / "skills"


def copy_tree(src: Path, dst: Path, overwrite: bool) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    if dst.exists() and not overwrite:
        print(f"skip existing: {dst}")
        return
    if dst.exists() and overwrite:
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"installed: {dst}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Install bundled research skills into the local Codex skills directory.")
    parser.add_argument("--skills-dir", default=str(default_codex_skills_dir()), help="Target Codex skills directory.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing skills with the bundled versions.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    source = root / "skills"
    target = Path(args.skills_dir).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)

    for skill_dir in sorted(p for p in source.iterdir() if p.is_dir()):
        copy_tree(skill_dir, target / skill_dir.name, args.overwrite)


if __name__ == "__main__":
    main()
