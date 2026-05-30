"""
Compute a stable content hash for a data directory.

Hashes each file individually (sorted by path for determinism), then hashes
the concatenation. This is stable across filesystem operations (copy, move)
and OS differences, but NOT across format changes (e.g., re-encoding a PNG).

Usage:
    python scripts/data_hash.py <data_dir>               # print hash to stdout
    python scripts/data_hash.py <data_dir> --manifest    # write manifest to data_dir
    python scripts/data_hash.py <data_dir> --verify      # verify against existing manifest
"""
import hashlib
import json
import sys
from pathlib import Path

MANIFEST_NAME = "data_manifest.json"
# Extensions to skip (not data files)
SKIP_EXTENSIONS = {".py", ".pyc", ".md", ".txt", ".json", ".log", ".gitkeep"}
# Max file size to hash (skip files larger than 500MB to avoid hanging)
MAX_FILE_SIZE = 500 * 1024 * 1024


def _should_hash(filepath: Path) -> bool:
    """Skip non-data files and large binaries."""
    if filepath.suffix.lower() in SKIP_EXTENSIONS:
        return False
    if filepath.name == MANIFEST_NAME:
        return False
    try:
        if filepath.stat().st_size > MAX_FILE_SIZE:
            print(f"[data_hash] Skipping large file: {filepath}", file=sys.stderr)
            return False
    except OSError:
        return False
    return True


def compute_data_hash(data_dir: Path) -> tuple[str, dict[str, str]]:
    """Compute a directory-level hash and per-file hashes.

    Returns (directory_hash, {relative_path: sha256}).
    """
    if not data_dir.is_dir():
        raise NotADirectoryError(f"{data_dir} is not a directory")

    file_hashes: dict[str, str] = {}
    files = sorted(
        [f for f in data_dir.rglob("*") if f.is_file() and _should_hash(f)]
    )

    if not files:
        return "empty", {}

    for fpath in files:
        sha = hashlib.sha256()
        with open(fpath, "rb") as fh:
            while True:
                chunk = fh.read(8192)
                if not chunk:
                    break
                sha.update(chunk)
        rel = str(fpath.relative_to(data_dir)).replace("\\", "/")
        file_hashes[rel] = sha.hexdigest()

    # Composite hash: sort keys, concat, hash
    composite = hashlib.sha256()
    for rel in sorted(file_hashes):
        composite.update(rel.encode())
        composite.update(file_hashes[rel].encode())
    return composite.hexdigest(), file_hashes


def write_manifest(data_dir: Path, dir_hash: str, file_hashes: dict) -> Path:
    manifest = {
        "data_dir": str(data_dir.resolve()),
        "dir_hash": dir_hash,
        "files": file_hashes,
    }
    manifest_path = data_dir / MANIFEST_NAME
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path


def verify_manifest(data_dir: Path) -> bool:
    """Check actual hash against stored manifest. Returns True if match."""
    manifest_path = data_dir / MANIFEST_NAME
    if not manifest_path.exists():
        print(f"[data_hash] No manifest found at {manifest_path}", file=sys.stderr)
        return False

    stored = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = stored["dir_hash"]
    actual, _ = compute_data_hash(data_dir)

    if expected != actual:
        print(f"[data_hash] MISMATCH: expected {expected[:16]}... got {actual[:16]}...", file=sys.stderr)
        return False

    print(f"[data_hash] Verified: {expected[:16]}...")
    return True


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print(__doc__)
        sys.exit(1)

    data_dir = Path(sys.argv[1]).resolve()

    if "--verify" in sys.argv:
        ok = verify_manifest(data_dir)
        sys.exit(0 if ok else 1)

    dir_hash, file_hashes = compute_data_hash(data_dir)
    print(dir_hash)

    if "--manifest" in sys.argv:
        mpath = write_manifest(data_dir, dir_hash, file_hashes)
        print(f"[data_hash] Manifest written to {mpath}")


if __name__ == "__main__":
    main()
