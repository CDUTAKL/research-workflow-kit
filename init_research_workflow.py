from __future__ import annotations

import argparse
import shutil
from pathlib import Path

TEMPLATE_ROOT = Path(__file__).resolve().parent

SKIP_NAMES = {
    "result-scan-summary.md",
    "result-scan-table.csv",
    "dashboard-data.json",
    "evidence-graph.json",
    "evidence-graph.mmd",
}
SKIP_PARTS = {"node_modules", "dist", "__pycache__"}
SKIP_SUFFIXES = {".pyc", ".pyo"}


def copy_tree(src: Path, dst: Path, overwrite: bool) -> list[str]:
    copied: list[str] = []
    if not src.exists():
        return copied
    for path in src.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        if rel.name in SKIP_NAMES or rel.suffix in SKIP_SUFFIXES or any(part in SKIP_PARTS for part in rel.parts):
            continue
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not overwrite:
            continue
        shutil.copy2(path, target)
        copied.append(str(target))
    return copied


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize project-local research workflow files.")
    parser.add_argument("--project", default=".", help="Project root to initialize. Defaults to current directory.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing project files with template versions.")
    parser.add_argument("--with-claude-hook", action="store_true", help="Copy .claude/settings.local.template.json if settings.local.json does not exist, or overwrite with --overwrite.")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    project.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    copied += copy_tree(TEMPLATE_ROOT / "docs", project / "docs", args.overwrite)
    copied += copy_tree(TEMPLATE_ROOT / "figures", project / "figures", args.overwrite)
    copied += copy_tree(TEMPLATE_ROOT / "scripts", project / "scripts", args.overwrite)
    copied += copy_tree(TEMPLATE_ROOT / "dashboard-web", project / "dashboard-web", args.overwrite)

    launcher_src = TEMPLATE_ROOT / "open-dashboard.command"
    launcher_dst = project / "open-dashboard.command"
    if launcher_src.exists() and (not launcher_dst.exists() or args.overwrite):
        shutil.copy2(launcher_src, launcher_dst)
        copied.append(str(launcher_dst))

    if args.with_claude_hook:
        src = TEMPLATE_ROOT / ".claude" / "settings.local.template.json"
        dst = project / ".claude" / "settings.local.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or args.overwrite:
            shutil.copy2(src, dst)
            copied.append(str(dst))

    print(f"Initialized research workflow in: {project}")
    print(f"Files copied: {len(copied)}")
    if copied:
        for item in copied:
            print(f"  {item}")
    else:
        print("No files copied. Existing files were preserved; use --overwrite to refresh them.")


if __name__ == "__main__":
    main()
