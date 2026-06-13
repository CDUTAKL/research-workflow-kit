from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from evcs.data.acn import load_acn_export, normalize_acn_sessions
from evcs.utils.artifacts import write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch or normalize ACN-Data sessions into data/raw/acn_sessions.csv.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input-export", help="Local ACN JSON/CSV export to normalize.")
    source.add_argument("--use-api", action="store_true", help="Use acnportal with ACN_API_TOKEN from the environment.")
    parser.add_argument("--site", default="caltech", help="ACN site id, e.g. caltech, jpl, office001.")
    parser.add_argument("--out", default="data/raw/acn_sessions.csv")
    parser.add_argument("--manifest", default="data/raw/acn_sessions_manifest.json")
    parser.add_argument("--checkpoint", default="data/raw/acn_sessions_checkpoint.jsonl")
    parser.add_argument("--resume", action="store_true", help="Resume ACN API download from checkpoint/state files.")
    parser.add_argument("--start", help="Optional API start datetime.")
    parser.add_argument("--end", help="Optional API end datetime.")
    parser.add_argument("--with-time-series", action="store_true", help="Use the slower /ts endpoint.")
    parser.add_argument("--page-size", type=int, default=1000, help="ACN API page size request.")
    parser.add_argument("--max-pages", type=int, help="Optional safety cap for debugging slow downloads.")
    parser.add_argument("--retries", type=int, default=5, help="Retries per page for transient ACN network errors.")
    parser.add_argument("--retry-backoff", type=float, default=3.0, help="Initial retry backoff seconds.")
    parser.add_argument("--page-delay", type=float, default=0.0, help="Seconds to sleep after each successful page.")
    parser.add_argument("--quiet", action="store_true", help="Suppress page-level progress output.")
    args = parser.parse_args()

    if args.input_export:
        sessions = load_acn_export(args.input_export, site=args.site)
        source_kind = "local_export"
    else:
        sessions = _fetch_from_api(
            args.site,
            start=args.start,
            end=args.end,
            with_time_series=args.with_time_series,
            page_size=args.page_size,
            max_pages=args.max_pages,
            retries=args.retries,
            retry_backoff=args.retry_backoff,
            page_delay=args.page_delay,
            checkpoint=Path(args.checkpoint),
            resume=args.resume,
            quiet=args.quiet,
        )
        source_kind = "acn_rest_api"

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    sessions.to_csv(out, index=False)
    write_json(
        args.manifest,
        {
            "source_kind": source_kind,
            "site": args.site,
            "row_count": int(len(sessions)),
            "output_path": str(out),
            "checkpoint_path": str(args.checkpoint) if args.use_api else None,
            "has_time_series_rows": int(sessions["has_time_series"].sum()) if "has_time_series" in sessions else 0,
            "api_token_policy": "ACN_API_TOKEN is read from environment and is never written to artifacts",
        },
    )
    print(f"wrote normalized ACN sessions to {out} ({len(sessions)} rows)")


def _fetch_from_api(
    site: str,
    start: str | None = None,
    end: str | None = None,
    with_time_series: bool = False,
    page_size: int = 1000,
    max_pages: int | None = None,
    retries: int = 5,
    retry_backoff: float = 3.0,
    page_delay: float = 0.0,
    checkpoint: Path | None = None,
    resume: bool = False,
    quiet: bool = False,
):
    token = os.environ.get("ACN_API_TOKEN")
    if not token:
        raise SystemExit("ACN_API_TOKEN is required for --use-api; register at the official ACN-Data site and export it locally.")

    endpoint = f"sessions/{site}/ts" if with_time_series else f"sessions/{site}"
    url = urljoin("https://ev.caltech.edu/api/v1/", endpoint)
    where = _where_clause(start, end)
    params = {"max_results": str(page_size), "sort": "connectionTime"}
    if where:
        params["where"] = where
    records = _fetch_paginated(
        url,
        token=token,
        params=params,
        max_pages=max_pages,
        retries=retries,
        retry_backoff=retry_backoff,
        page_delay=page_delay,
        checkpoint=checkpoint,
        resume=resume,
        quiet=quiet,
    )
    return normalize_acn_sessions(records, site=site)


def _where_clause(start: str | None, end: str | None) -> str | None:
    clauses = []
    if start:
        clauses.append(f'connectionTime >= "{_http_date(start)}"')
    if end:
        clauses.append(f'connectionTime <= "{_http_date(end)}"')
    return " and ".join(clauses) if clauses else None


def _http_date(value: str) -> str:
    normalized = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")


def _fetch_paginated(
    url: str,
    token: str,
    params: dict[str, str] | None = None,
    max_pages: int | None = None,
    retries: int = 5,
    retry_backoff: float = 3.0,
    page_delay: float = 0.0,
    checkpoint: Path | None = None,
    resume: bool = False,
    quiet: bool = False,
) -> list[dict]:
    records: list[dict] = []
    next_url: str | None = url
    next_params = params
    page = 0
    state_path = _state_path(checkpoint) if checkpoint else None
    if checkpoint and resume:
        records, next_url, page = _load_checkpoint(checkpoint, state_path, fallback_url=url)
        next_params = None
        if not quiet:
            print(f"resuming from checkpoint: records={len(records)}, next_page={page + 1}", flush=True)
    elif checkpoint and checkpoint.exists():
        checkpoint.unlink()
        if state_path and state_path.exists():
            state_path.unlink()

    while next_url:
        page += 1
        if max_pages is not None and page > max_pages:
            if not quiet:
                print(f"stopped at --max-pages={max_pages}; downloaded {len(records)} records", flush=True)
            break
        if not quiet:
            print(f"fetching ACN page {page} ...", flush=True)
        response = _get_with_retries(
            next_url,
            token=token,
            params=next_params,
            page=page,
            retries=retries,
            retry_backoff=retry_backoff,
            quiet=quiet,
        )
        if response.status_code == 401:
            raise SystemExit("ACN API authentication failed; check ACN_API_TOKEN.")
        if response.status_code >= 500:
            raise RuntimeError(f"ACN server returned HTTP {response.status_code} on page {page}; retry budget exhausted.")
        response.raise_for_status()
        payload = response.json()
        items = payload.get("_items", payload.get("items", payload if isinstance(payload, list) else []))
        if page == 1 and not quiet:
            _print_total_hint(payload, len(items))
        item_records = [item for item in items if isinstance(item, dict)]
        records.extend(item_records)
        if not quiet:
            print(f"received {len(items)} records on page {page}; total={len(records)}", flush=True)
        href = payload.get("_links", {}).get("next", {}).get("href") if isinstance(payload, dict) else None
        next_url = urljoin("https://ev.caltech.edu/api/v1/", href) if href else None
        next_params = None
        if checkpoint:
            _append_checkpoint(checkpoint, item_records)
            if state_path:
                write_json(
                    state_path,
                    {
                        "records": len(records),
                        "last_completed_page": page,
                        "next_url": next_url,
                        "done": next_url is None,
                    },
                )
        if next_url and page_delay > 0:
            if not quiet:
                print(f"sleeping {page_delay:.1f}s before next page", flush=True)
            time.sleep(page_delay)
    return records


def _get_with_retries(
    url: str,
    token: str,
    params: dict[str, str] | None,
    page: int,
    retries: int,
    retry_backoff: float,
    quiet: bool,
) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            response = requests.get(url, params=params, auth=(token, ""), timeout=60)
            if response.status_code in {500, 502, 503, 504} and attempt <= retries:
                delay = retry_backoff * (2 ** (attempt - 1))
                if not quiet:
                    print(
                        f"page {page} server returned HTTP {response.status_code} on attempt {attempt}/{retries + 1}; "
                        f"retrying in {delay:.1f}s",
                        flush=True,
                    )
                time.sleep(delay)
                continue
            return response
        except requests.exceptions.RequestException as exc:
            last_error = exc
            if attempt > retries:
                break
            delay = retry_backoff * (2 ** (attempt - 1))
            if not quiet:
                print(
                    f"page {page} network error on attempt {attempt}/{retries + 1}: {exc}; retrying in {delay:.1f}s",
                    flush=True,
                )
            time.sleep(delay)
    raise RuntimeError(f"ACN download failed on page {page} after {retries + 1} attempts") from last_error


def _print_total_hint(payload: object, first_page_count: int) -> None:
    if not isinstance(payload, dict):
        return
    meta = payload.get("_meta", {})
    total = meta.get("total") if isinstance(meta, dict) else None
    max_results = meta.get("max_results") if isinstance(meta, dict) else None
    if isinstance(total, int) and isinstance(max_results, int) and max_results > 0:
        total_pages = math.ceil(total / max_results)
        print(f"ACN API reports total={total}, page_size={max_results}, estimated_pages={total_pages}", flush=True)
    elif first_page_count:
        print(f"ACN API first page contains {first_page_count} records; total pages not reported", flush=True)


def _state_path(checkpoint: Path | None) -> Path | None:
    if checkpoint is None:
        return None
    return checkpoint.with_suffix(checkpoint.suffix + ".state.json")


def _append_checkpoint(path: Path, records: list[dict]) -> None:
    if not records:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _load_checkpoint(checkpoint: Path, state_path: Path | None, fallback_url: str) -> tuple[list[dict], str | None, int]:
    records: list[dict] = []
    if checkpoint.exists():
        with checkpoint.open(encoding="utf-8") as handle:
            records = [json.loads(line) for line in handle if line.strip()]
    next_url: str | None = fallback_url
    page = 0
    if state_path and state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        page = int(state.get("last_completed_page", 0))
        next_url = state.get("next_url")
    return records, next_url, page


if __name__ == "__main__":
    main()
