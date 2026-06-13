from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def write_json(path: str | Path, data: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(out_dir: str | Path, experiment_id: str, artifacts: list[str]) -> None:
    root = Path(out_dir)
    payload = {
        "experiment_id": experiment_id,
        "artifacts": artifacts,
        "hashes": {
            artifact: file_sha256(root / artifact)
            for artifact in artifacts
            if (root / artifact).is_file()
        },
    }
    write_json(root / "manifest.json", payload)

