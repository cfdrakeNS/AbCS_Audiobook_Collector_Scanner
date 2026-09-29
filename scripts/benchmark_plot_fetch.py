"""Compare plot fetching across AbCS revisions without persisting cache state.

Run from a checkout with:
    python scripts/benchmark_plot_fetch.py --label v3 --title "Glass Houses" --author "Louise Penny"

The runner emits JSON lines and never prints fetched plot text or API credentials.
"""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import nullcontext
from contextlib import ExitStack
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch


def _query_values(url: str) -> list[str]:
    parsed = urlsplit(url)
    values = parse_qs(parsed.query)
    return [
        value
        for key in ("q", "srsearch", "search")
        for value in values.get(key, [])
    ]


def _run_one(label: str, title: str, author: str, repeat: int) -> dict:
    from src.web import web_book_api as api_module

    try:
        web_http = importlib.import_module("src.web.web_http")
    except ImportError:
        web_http = None

    request_records: list[dict] = []
    original_get_json = api_module._http_get_json

    def measured_get_json(url: str, **kwargs):
        started = time.perf_counter()
        source = str(kwargs.get("source", "unknown"))
        try:
            return original_get_json(url, **kwargs)
        finally:
            request_records.append(
                {
                    "source": source,
                    "queries": _query_values(url),
                    "elapsed_seconds": round(time.perf_counter() - started, 4),
                }
            )

    cooldown_lock = getattr(web_http, "_cooldown_lock", None)
    with cooldown_lock if cooldown_lock is not None else nullcontext():
        cooldowns = getattr(web_http, "_source_cooldown_until", None)
        if isinstance(cooldowns, dict):
            cooldowns.clear()

    started = time.perf_counter()
    with ExitStack() as patches:
        patches.enter_context(
            patch.object(api_module, "_http_get_json", side_effect=measured_get_json)
        )
        if hasattr(api_module, "_load_persisted_cooldowns"):
            patches.enter_context(
                patch.object(api_module, "_load_persisted_cooldowns", lambda: None)
            )
        if web_http is not None and hasattr(web_http, "_save_persisted_cooldowns"):
            patches.enter_context(
                patch.object(web_http, "_save_persisted_cooldowns", lambda: None)
            )
        if hasattr(api_module.WebBookAPI, "_load_persistent_cache"):
            patches.enter_context(
                patch.object(
                    api_module.WebBookAPI, "_load_persistent_cache", lambda _self: None
                )
            )
        if hasattr(api_module.WebBookAPI, "_save_persistent_cache"):
            patches.enter_context(
                patch.object(
                    api_module.WebBookAPI,
                    "_save_persistent_cache",
                    lambda _self, force=False: None,
                )
            )
        client = api_module.WebBookAPI()
        result = client.get_book_metadata(
            title,
            author,
            bypass_cache=True,
            should_cancel=lambda: False,
        )
        diagnostics_getter = getattr(client, "get_last_plot_diagnostics", None)
        diagnostics = diagnostics_getter() if diagnostics_getter else {}
    elapsed = time.perf_counter() - started

    plot = str((result or {}).get("plot") or "")
    request_counts = Counter(item["source"] for item in request_records)
    candidate_diagnostics = diagnostics.get("candidates", [])
    return {
        "label": label,
        "title": title,
        "author": author,
        "repeat": repeat,
        "elapsed_seconds": round(elapsed, 4),
        "request_count": len(request_records),
        "requests_by_source": dict(sorted(request_counts.items())),
        "request_trace": request_records,
        "matched_title": (result or {}).get("title", ""),
        "matched_author": (result or {}).get("author", ""),
        "metadata_source": (result or {}).get("source", ""),
        "plot_source": (result or {}).get("plot_source", ""),
        "plot_length": len(plot),
        "plot_sha256": hashlib.sha256(plot.encode("utf-8")).hexdigest()
        if plot
        else "",
        "plot_confidence": (result or {}).get("plot_match_confidence", ""),
        "plot_auto_apply": (result or {}).get("plot_auto_apply"),
        "identifiers": {
            key: value
            for key, value in (result or {}).items()
            if key in {"isbn", "google_id", "wikidata_id"}
            and value
        },
        "candidate_diagnostics": [
            {
                key: candidate.get(key)
                for key in (
                    "source",
                    "identifiers",
                    "match_confidence",
                    "query_type",
                    "elapsed_seconds",
                    "text_length",
                    "accepted",
                    "rejection_reason",
                )
                if key in candidate
            }
            for candidate in candidate_diagnostics
        ],
        "errors_by_source": sorted(
            {
                str(error).split(":", 1)[0].strip()
                for error in (result or {}).get("_fetch_errors", [])
            }
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True, help="Revision label, e.g. main or v3")
    parser.add_argument("--title", required=True)
    parser.add_argument("--author", default="")
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")

    workspace = str(Path.cwd())
    sys.path.insert(0, workspace)
    for repeat in range(1, args.repeat + 1):
        try:
            record = _run_one(args.label, args.title, args.author, repeat)
        except Exception as exc:
            record = {
                "label": args.label,
                "title": args.title,
                "author": args.author,
                "repeat": repeat,
                "error_type": type(exc).__name__,
            }
            print(json.dumps(record, sort_keys=True))
            return 1
        print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())