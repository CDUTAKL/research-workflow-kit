"""Write a lightweight environment snapshot for formal experiment runs.

This script is designed for local and remote targets. It uses only the Python
standard library, and it treats CUDA/PyTorch as optional so it can run on the
Mac console as well as the remote RTX 4060 desktop.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import platform
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], timeout: int = 20) -> str:
    try:
        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return f"$ {' '.join(command)}\nnot found\n"
    except subprocess.TimeoutExpired:
        return f"$ {' '.join(command)}\ntimeout after {timeout}s\n"

    output = result.stdout.strip()
    error = result.stderr.strip()
    chunks = [f"$ {' '.join(command)}", f"exit={result.returncode}"]
    if output:
        chunks.append(output)
    if error:
        chunks.append(f"stderr:\n{error}")
    return "\n".join(chunks) + "\n"


def torch_snapshot() -> str:
    if importlib.util.find_spec("torch") is None:
        return "torch: not installed\n"
    try:
        import torch  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        return f"torch: import failed: {exc}\n"

    lines = [
        f"torch_version: {getattr(torch, '__version__', 'unknown')}",
        f"torch_cuda_version: {getattr(torch.version, 'cuda', None)}",
        f"cuda_available: {torch.cuda.is_available()}",
        f"cuda_device_count: {torch.cuda.device_count() if torch.cuda.is_available() else 0}",
    ]
    if torch.cuda.is_available():
        try:
            lines.append(f"cuda_device_0: {torch.cuda.get_device_name(0)}")
        except Exception as exc:  # pragma: no cover - environment dependent
            lines.append(f"cuda_device_0: unavailable: {exc}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Write an experiment environment snapshot.")
    parser.add_argument("--out", required=True, help="Snapshot path, usually outputs/<EXP>/environment.txt.")
    parser.add_argument("--label", default="local_mac", help="Target label such as local_mac or remote_desktop_4060.")
    parser.add_argument("--include-pip-freeze", action="store_true", help="Append full pip freeze output.")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    now = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")
    sections = [
        "# Experiment Environment Snapshot",
        "",
        f"timestamp: {now}",
        f"target_label: {args.label}",
        f"hostname: {platform.node()}",
        f"platform: {platform.platform()}",
        f"python: {sys.version.replace(chr(10), ' ')}",
        f"python_executable: {sys.executable}",
        "",
        "## GPU",
        run_command(["nvidia-smi"]),
        "## PyTorch",
        torch_snapshot(),
        "## Git",
        run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        run_command(["git", "rev-parse", "HEAD"]),
        run_command(["git", "status", "--short"]),
        "## Packages",
    ]
    if args.include_pip_freeze:
        sections.append(run_command([sys.executable, "-m", "pip", "freeze"], timeout=60))
    else:
        sections.append(run_command([sys.executable, "-m", "pip", "--version"]))

    out.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"wrote environment snapshot: {out}")


if __name__ == "__main__":
    main()
