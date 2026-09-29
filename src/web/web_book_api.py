"""
Web Book API - Audiobook Collection
Facade: Open Library, Google Books, and WikiData (in that order).
HTTP, cooldown, and budget helpers live in web_http.py.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional

from src.utils.text_utils import split_series_number, web_titles_match
from src.web.web_cache import (
    CACHE_DURATION,
    NEGATIVE_CACHE_TTL_SECONDS,
    TRANSIENT_CACHE_TTL_SECONDS,
    WEB_CACHE_FILE,
    WEB_CACHE_MAX_ENTRIES,
    WEB_CACHE_SCHEMA_VERSION,
)
from src.web.web_http import (
    FETCH_BUDGET_MAX_GOOGLE,
    FETCH_BUDGET_MAX_REQUESTS,
    FETCH_BUDGET_MAX_WIKIDATA,
    FETCH_BUDGET_SECONDS,
    FetchAborted,
    FetchBudget,
    RATE_LIMIT_COOLDOWN_SECONDS,
    SERVICE_UNAVAILABLE_RETRY_DELAY_SECONDS,
    SourceCooldownError,
    TIMEOUT_DETAIL,
    TIMEOUT_SEARCH,
    USER_AGENT,
    GOOGLE_BOOKS_API_KEY_ENV,
    GOOGLE_BOOKS_API_KEY_SETTING,
    _FATAL_HTTP_CODES,
    _clear_source_cooldown,
    _resolve_web_cache_file,
    _dedupe_fetch_errors,
    _http_get_json,
    _is_rate_limit_http_code,
    _is_source_cooling_down,
    _load_persisted_cooldowns,
    _note_rate_limited,
    _raise_cooldown_http_error,
    _reraise_if_fatal_http_error,
    _seconds_until_cooldown_clears,
    _source_progress_message,
    format_web_fetch_dialog_text,
    format_web_fetch_status_message,
    get_google_books_api_key,
)
from src.web.web_matching import (
    AUTHOR_HONORIFIC_PREFIX,
    ORWELL_1984_TITLE_TOKEN,
    ORWELL_AUTHOR_LABEL,
    STOPWORDS,
)
from src.web.plot_resolver import (
    PLOT_MIN_LENGTH,
    PlotCandidate,
    PlotFetchDiagnostics,
    PlotResolver,
    candidate_identifiers,
    candidate_provenance,
)

PLOT_MAX_WIKIPEDIA_SENTENCES = 20
PLOT_FETCH_MAX_WORKERS = 3
PLOT_CANDIDATE_GRACE_SECONDS = 0.35

_PLOT_RESOLVER = PlotResolver(PLOT_MIN_LENGTH)

_cache_write_warned = False
_shared_web_api: Optional["WebBookAPI"] = None


def get_web_api() -> "WebBookAPI":
    """Return the process-wide WebBookAPI (shared in-memory + disk cache)."""
    global _shared_web_api
    if _shared_web_api is None:
        _load_persisted_cooldowns()
        _shared_web_api = WebBookAPI()
    return _shared_web_api


def _reset_shared_web_api_for_tests() -> None:
    """Drop the shared client (tests only)."""
    global _shared_web_api
    _shared_web_api = None


class WebBookAPI:
    """API client for fetching book metadata from web sources."""

    def _move_article_to_beginning(self, title: str) -> str:
        """Move trailing articles (comma, optional space, then article) to beginning of title."""
        if not title:
            return title
        # Accept variations: ',the', ', the', ',  the', ',An', etc.
        match = re.match(r"^(.*?)[,\s]+(the|a|an)$", title.strip(), re.IGNORECASE)
        if match:
            base = match.group(1).strip()
            article = match.group(2).capitalize()
            return f"{article} {base}"
        return title

    def _strip_author_honorifics(self, author: str) -> str:
        """Remove leading titles/honorifics used in library author fields."""
        cleaned = (author or "").strip()
        while cleaned:
            match = AUTHOR_HONORIFIC_PREFIX.match(cleaned)
            if not match:
                break
            cleaned = cleaned[match.end() :].strip()
        return cleaned

    @staticmethod
    def _fold_apostrophes(text: str) -> str:
        return re.sub(r"[\u2018\u2019\u201b`']", "'", text or "")

    def _strip_leading_author_from_title(
        self, title: str, author: str | None
    ) -> str:
        """Remove a leading author name (and optional possessive) from the title."""
        title = (title or "").strip()
        author = self._strip_author_honorifics(
            self._apply_author_transformations(author or "")
        ).strip()
        if not title or not author:
            return ""

        folded_title = self._fold_apostrophes(title)
        prefixes = [self._fold_apostrophes(author)]
        if "," in author:
            last_part, given_part = [p.strip() for p in author.split(",", 1)]
            if last_part and given_part:
                prefixes.append(self._fold_apostrophes(f"{given_part} {last_part}"))

        title_lower = folded_title.lower()
        for prefix in prefixes:
            prefix_lower = prefix.lower()
            if not title_lower.startswith(prefix_lower):
                continue
            rest = folded_title[len(prefix) :].lstrip()
            rest = re.sub(r"^'s\b", "", rest, flags=re.IGNORECASE).lstrip(" -:–—").strip()
            if rest and rest.lower() != title_lower:
                return rest
        return ""

    def _db_title_match_candidates(
        self, db_title: str, db_author: str | None
    ) -> list[str]:
        """Titles used when comparing library rows to web results."""
        candidates: list[str] = []
        seen: set[str] = set()

        def _add(value: str) -> None:
            key = (value or "").strip().lower()
            if not key or key in seen:
                return
            seen.add(key)
            candidates.append(value.strip())

        _add(db_title or "")
        stripped = self._strip_leading_author_from_title(db_title, db_author)
        if stripped:
            _add(stripped)
        return candidates

    def _query_titles_for_metadata(
        self, title: str, db_author: str | None
    ) -> list[str]:
        """Return original and known-normalized titles for metadata search."""
        stripped = self._strip_leading_author_from_title(title, db_author)
        candidates = [stripped, title] if stripped else [title]
        series_prefix_match = re.match(
            r"^.+?\s+\d+(?:\.\d+)?\s*[-:]\s*(.+)$", title or ""
        )
        if series_prefix_match:
            candidates.append(series_prefix_match.group(1).strip())

        title_aliases = {
            normalize_title("The Murder Stone"): "A Rule Against Murder",
            normalize_title("A Rule Against Murder"): "The Murder Stone",
        }
        for candidate in list(candidates):
            alias = title_aliases.get(normalize_title(candidate))
            if alias:
                candidates.append(alias)

        result: list[str] = []
        seen: set[str] = set()
        for candidate in candidates:
            value = (candidate or "").strip()
            key = normalize_title(value)
            if value and key not in seen:
                seen.add(key)
                result.append(value)
        return result

    @staticmethod
    def _google_fetch_error_is_transient(err: str) -> bool:
        low = (err or "").lower()
        if not low.startswith("google_books:"):
            return False
        return any(
            token in low
            for token in ("429", "403", "paused", "too many", "rate limit")
        )

    @staticmethod
    def _negative_cache_is_transient_google_only(payload: dict) -> bool:
        errors = payload.get("_fetch_errors") or []
        if not errors:
            return False
        return all(
            WebBookAPI._google_fetch_error_is_transient(err) for err in errors
        )

    @staticmethod
    def _fetch_error_is_transient(error: str) -> bool:
        lowered = str(error or "").lower()
        return any(
            token in lowered
            for token in (
                "timeout",
                "timed out",
                "temporarily",
                "temporary",
                "connection",
                "network",
                "unavailable",
                "paused",
                "rate limit",
                "too many",
                "quota",
                "429",
                "403",
                "502",
                "503",
            )
        )

    @classmethod
    def _cache_entry_kind(cls, payload: dict | None) -> str:
        if not isinstance(payload, dict):
            return "positive"
        explicit = payload.get("_cache_kind")
        if explicit in {"positive", "negative", "transient"}:
            return explicit
        if not payload.get("_no_result"):
            return "positive"
        errors = payload.get("_fetch_errors") or []
        if any(cls._fetch_error_is_transient(error) for error in errors):
            return "transient"
        return "negative"

    def _should_bypass_negative_cache(self, payload: dict) -> bool:
        """Retry cached misses that came from transient source failures."""
        if not isinstance(payload, dict) or not payload.get("_no_result"):
            return False
        return self._cache_entry_kind(payload) == "transient"

    def _extract_last_name(self, author: str) -> str:
        """Extract last name from author string."""
        author = self._strip_author_honorifics(author)
        if not author:
            return ""
        # Handle "Last, First" format
        if "," in author:
            return author.split(",")[0].strip()
        # Handle "First Last" format
        parts = author.strip().split()
        return parts[-1] if parts else ""

    def _author_matches(self, db_author: str, web_author: str) -> bool:
        """Check that web author contains the DB author's last name.

        When both sides have more than one word, also require that at least one
        non-last-name token (first name or initial) from the DB author appears
        in the web author string.  Falls back to last-name-only when either
        side is a single word (e.g. a pen-name or initials-only entry).
        """
        db_author = (db_author or "").strip()
        web_author = (web_author or "").strip()
        if not db_author or not web_author:
            return False
        last_name = self._extract_last_name(db_author)
        if not last_name:
            return False
        if last_name.lower() not in web_author.lower():
            return False

        # Additional check: first-name/initial overlap when both have >1 word
        web_lower = web_author.lower()
        if len(web_author.split()) > 1:
            if "," in db_author:
                given_parts = [
                    part.strip()
                    for part in db_author.split(",", 1)[1].split()
                    if part.strip()
                ]
            else:
                db_parts = db_author.split()
                given_parts = db_parts[:-1] if len(db_parts) > 1 else []
            if given_parts and not any(
                part.lower().rstrip(".") in web_lower for part in given_parts
            ):
                return False

        return True

    def _title_word_match_score(self, db_title: str, web_title: str) -> float:
        """Calculate percentage of DB title words found in web title.

        Applies a soft length penalty when the web title is more than twice as
        long (by meaningful words) as the DB title.  A penalty of 0.15 is
        subtracted so that a title like "Date Night Club" (3 words) still
        reaches the 0.5 threshold for "Date Night" (2 words) only when the
        overlap is 100 %, but more exotic expansions fail.
        """
        if not db_title or not web_title:
            return 0.0

        # Clean and split titles
        db_words = set(re.findall(r"\b\w+\b", db_title.lower())) - STOPWORDS
        web_words = set(re.findall(r"\b\w+\b", web_title.lower())) - STOPWORDS

        if not db_words:
            return 1.0  # No meaningful words to match

        matches = len(db_words & web_words)
        score = matches / len(db_words)

        # Soft penalty: web title has significantly more words than DB title
        if len(web_words) > len(db_words) * 2:
            score -= 0.15

        return score

    def _title_matches(
        self, db_title: str, web_title: str, db_author: str | None = None
    ) -> bool:
        """Check if at least 50% of DB title words appear in web title."""
        for candidate in self._db_title_match_candidates(db_title, db_author):
            if self._title_word_match_score(candidate, web_title) >= 0.5:
                return True
        return False

    def _best_title_word_match_score(
        self, db_title: str, web_title: str, db_author: str | None = None
    ) -> float:
        scores = [
            self._title_word_match_score(candidate, web_title)
            for candidate in self._db_title_match_candidates(db_title, db_author)
        ]
        return max(scores) if scores else 0.0

    def _metadata_matches_db(
        self,
        db_title: str,
        db_author: str,
        metadata: Optional[Dict],
        *,
        require_author_match: bool = True,
    ) -> bool:
        """Require title word match; optionally require DB last name in web author."""
        if not metadata:
            return False
        web_title = (metadata.get("title") or "").strip()
        if not web_title:
            return False
        if not self._title_matches(db_title, web_title, db_author):
            return False
        if not require_author_match:
            return True
        if not self._author_matches(db_author, metadata.get("author", "")):
            return False
        return True

    def _plot_identifier_matches_db(
        self, db_title: str, db_author: str, metadata: Optional[Dict]
    ) -> bool:
        """Require same-work title identity for plot text fetched by ISBN."""
        if not metadata:
            return False
        web_title = str(metadata.get("title") or "").strip()
        if not web_title:
            return False
        web_author = str(metadata.get("author") or "").strip()
        if db_author and web_author and not self._author_matches(db_author, web_author):
            return False

        title_candidates = self._db_title_match_candidates(db_title, db_author)
        series_prefix_match = re.match(
            r"^.+?\s+\d+(?:\.\d+)?\s*[-:]\s*(.+)$", db_title or ""
        )
        if series_prefix_match:
            title_candidates.append(series_prefix_match.group(1).strip())

        if any(web_titles_match(candidate, web_title) for candidate in title_candidates):
            return True

        aliases = {
            normalize_title("The Murder Stone"),
            normalize_title("A Rule Against Murder"),
        }
        return (
            normalize_title(web_title) in aliases
            and any(normalize_title(title) in aliases for title in title_candidates)
        )


    @staticmethod
    def _plot_is_adequate(plot: str) -> bool:
        return _PLOT_RESOLVER.is_adequate(plot)

    @staticmethod
    def _strip_html(text: str) -> str:
        return _PLOT_RESOLVER.normalize_text(text)

    def _clean_plot_text(self, plot: str) -> str:
        return self._strip_html((plot or "").strip())

    def _is_non_book_plot(self, plot: str) -> bool:
        """Return True when plot text clearly describes music, film, or TV—not a book."""
        return _PLOT_RESOLVER.is_non_book(plot)

    @staticmethod
    def _is_stub_plot(plot: str) -> bool:
        """Return True when plot looks like an API/error placeholder, not a synopsis."""
        return _PLOT_RESOLVER.is_stub(plot)

    def _apply_plot_to_metadata(
        self,
        metadata: Dict,
        plot: str,
        plot_source: str,
        db_title: str,
        db_author: str,
        *,
        query_type: str = "",
        elapsed_seconds: float = 0.0,
        cache_state: str = "network",
        source_url: str = "",
        license_id: str = "",
        match_confidence: str = "low",
        candidates: list[PlotCandidate] | None = None,
        identifiers: dict[str, str] | None = None,
    ) -> bool:
        """Set plot on metadata when text is long enough and book-related."""
        provenance = (
            candidate_provenance(metadata)
            if plot_source
            in {
                metadata.get("plot_source"),
                metadata.get("source"),
                metadata.get("_resolved_source"),
            }
            else {}
        )
        candidate = PlotCandidate(
            text=plot,
            source=plot_source,
            identifiers=candidate_identifiers(metadata),
            match_confidence=match_confidence,
            query_type=query_type,
            elapsed_seconds=elapsed_seconds,
            cache_state=cache_state,
            source_url=source_url or provenance.get("plot_source_url", ""),
            license_id=license_id
            or provenance.get("plot_license_id", ""),
        )
        if identifiers:
            candidate.identifiers.update(identifiers)
        _PLOT_RESOLVER.evaluate(
            candidate,
            db_author=db_author,
            author_matches=self._author_matches,
            redundant=self._is_redundant_plot(plot),
        )
        self._record_plot_candidate(candidate)
        if candidate.rejection_reason:
            return False
        if candidates is not None:
            candidates.append(candidate)
            selected = _PLOT_RESOLVER.choose(candidates)
            if selected is not None:
                self._select_plot_candidate(metadata, selected)
                diagnostics = getattr(self._plot_diagnostics_local, "active", None)
                if diagnostics is not None:
                    diagnostics.select(selected)
        else:
            self._select_plot_candidate(metadata, candidate)
        return True

    @staticmethod
    def _select_plot_candidate(metadata: Dict, candidate: PlotCandidate) -> None:
        metadata["plot"] = candidate.normalized_text
        metadata["plot_source"] = candidate.source
        metadata["plot_source_url"] = candidate.source_url
        metadata["plot_license_id"] = candidate.license_id
        metadata["plot_match_confidence"] = (
            "high" if candidate.auto_apply else "medium"
        )
        metadata["plot_auto_apply"] = candidate.auto_apply
        metadata["plot_provenance"] = {
            "source": candidate.source,
            "identifiers": dict(candidate.identifiers),
            "source_url": candidate.source_url,
            "fetched_at": candidate.fetched_at,
            "license_id": candidate.license_id,
            "modified": candidate.modified,
            "match_confidence": candidate.match_confidence,
        }

    def _enrich_metadata_plot(
        self,
        metadata: Dict,
        db_title: str,
        db_author: str,
        *,
        report_progress=None,
    ) -> None:
        """Fill plot after metadata match: Open Library work, Wikipedia, then Google text."""
        if not metadata:
            return

        def _progress(msg: str) -> None:
            if report_progress:
                try:
                    report_progress(msg)
                except Exception:
                    pass

        existing = self._clean_plot_text(metadata.get("plot", ""))
        if self._plot_is_adequate(existing):
            source = metadata.get("source") or metadata.get("_resolved_source", "")
            metadata["plot"] = existing
            metadata["plot_source"] = metadata.get("plot_source") or source
            metadata.setdefault("plot_match_confidence", "high")
            metadata.setdefault("plot_auto_apply", True)
            provenance = candidate_provenance(metadata)
            metadata.setdefault(
                "plot_provenance",
                {
                    "source": metadata["plot_source"],
                    "identifiers": candidate_identifiers(metadata),
                    "source_url": provenance.get("plot_source_url", ""),
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "license_id": provenance.get("plot_license_id", ""),
                    "modified": False,
                    "match_confidence": "title_author" if db_author else "title",
                },
            )
            self._record_existing_plot(
                metadata,
                cache_state="metadata_result",
                query_type="primary_metadata",
            )
            return

        candidates: list[PlotCandidate] = []
        work_key = metadata.get("open_library_work_key", "")
        identifier_isbn = self._normalize_isbn(str(metadata.get("isbn") or ""))
        wiki_title = db_title or metadata.get("title", "")
        wiki_author = db_author or metadata.get("author", "")
        rest_candidates: list[str] = []
        seen_rest: set[str] = set()
        for candidate in (
            f"{wiki_title} {wiki_author} novel" if wiki_author else "",
            f"{wiki_title} novel",
        ):
            text = candidate.strip()
            if text and text not in seen_rest:
                seen_rest.add(text)
                rest_candidates.append(text)
        if not rest_candidates and wiki_title:
            rest_candidates.append(wiki_title)

        _progress("Searching online book sources…")
        worker_cancel = threading.Event()

        def _capture_candidate(
            source: str,
            query_type: str,
            match_confidence: str,
            fetch: Callable[[], str],
        ) -> dict | None:
            if worker_cancel.is_set():
                return None
            started = time.monotonic()
            self._plot_diagnostics_local.source_url = ""
            try:
                text = fetch()
            except FetchAborted:
                return None
            except Exception:
                return None
            text = self._clean_plot_text(text or "")
            if not text:
                return None
            return {
                "text": text,
                "source": source,
                "query_type": query_type,
                "match_confidence": match_confidence,
                "elapsed_seconds": time.monotonic() - started,
                "source_url": getattr(
                    self._plot_diagnostics_local, "source_url", ""
                ),
            }

        def _open_library_job() -> list[dict]:
            found: list[dict] = []
            if work_key and self._plot_identifier_matches_db(
                db_title, db_author, metadata
            ):
                item = _capture_candidate(
                    "open_library",
                    "work_identifier",
                    "identifier",
                    lambda: self._get_open_library_work_fields(work_key).get(
                        "description", ""
                    ),
                )
                if item:
                    item["source_url"] = f"https://openlibrary.org{work_key}"
                    found.append(item)
            elif identifier_isbn:
                started = time.monotonic()
                detail = self._fetch_by_isbn(identifier_isbn)
                detail_work_key = (detail or {}).get("open_library_work_key", "")
                if detail_work_key and self._plot_identifier_matches_db(
                    db_title, db_author, detail
                ):
                    item = _capture_candidate(
                        "open_library",
                        "isbn_work_identifier",
                        "identifier",
                        lambda: self._get_open_library_work_fields(
                            detail_work_key
                        ).get("description", ""),
                    )
                    if item:
                        item["elapsed_seconds"] += time.monotonic() - started
                        item["source_url"] = (detail or {}).get(
                            "plot_source_url", ""
                        ) or f"https://openlibrary.org{detail_work_key}"
                        item["identifiers"] = {
                            "open_library_work_key": detail_work_key,
                            "isbn": identifier_isbn,
                        }
                        found.append(item)
            elif metadata.get("_resolved_source") != "open_library":
                item = _capture_candidate(
                    "open_library",
                    "title_author_search",
                    "title_author" if db_author else "title",
                    lambda: self._fetch_plot_from_open_library(
                        db_title or metadata.get("title", ""), db_author
                    ),
                )
                if item:
                    found.append(item)
            return found

        def _google_books_job() -> list[dict]:
            if not identifier_isbn:
                return []
            found: list[dict] = []
            started = time.monotonic()
            google_detail = self._fetch_google_by_isbn(identifier_isbn)
            if self._plot_identifier_matches_db(
                db_title, db_author, google_detail
            ):
                item = _capture_candidate(
                    "google_books",
                    "isbn_detail",
                    "identifier",
                    lambda: google_detail.get("plot", ""),
                )
                if item:
                    item["elapsed_seconds"] = time.monotonic() - started
                    item["source_url"] = google_detail.get("plot_source_url", "")
                    item["identifiers"] = {
                        "isbn": identifier_isbn,
                        "google_id": str(google_detail.get("google_id", "")),
                    }
                    found.append(item)
            return found

        def _wikipedia_job() -> list[dict]:
            found: list[dict] = []
            for rest_title in rest_candidates:
                item = _capture_candidate(
                    "wikipedia",
                    "rest_summary",
                    "title",
                    lambda rest_title=rest_title: self._fetch_wikipedia_rest_summary(
                        rest_title
                    ),
                )
                if item:
                    found.append(item)
            item = _capture_candidate(
                "wikipedia",
                "title_author_search",
                "title_author" if db_author else "title",
                lambda: self._fetch_plot_from_wikipedia(
                    wiki_title,
                    wiki_author,
                    db_title=db_title,
                    db_author=db_author,
                ),
            )
            if item:
                found.append(item)
            return found

        jobs: list[Callable[[], list[dict]]] = [_open_library_job, _wikipedia_job]
        if identifier_isbn:
            jobs.append(_google_books_job)

        def _run_job(job: Callable[[], list[dict]]) -> list[dict]:
            self._plot_worker_local.cancel_event = worker_cancel
            try:
                return job()
            finally:
                self._plot_worker_local.cancel_event = None

        executor = ThreadPoolExecutor(
            max_workers=min(PLOT_FETCH_MAX_WORKERS, len(jobs)),
            thread_name_prefix="AbCSPlotFetch",
        )
        futures: set[Future] = {
            executor.submit(_run_job, job) for job in jobs
        }
        candidate_grace_deadline: float | None = None
        stop_workers = False
        try:
            while futures:
                try:
                    self._check_abort()
                except FetchAborted as abort:
                    if abort.reason == "canceled":
                        worker_cancel.set()
                        for future in futures:
                            future.cancel()
                        raise
                    stop_workers = True
                    worker_cancel.set()
                    for future in futures:
                        future.cancel()
                    break

                timeout = (
                    self._active_budget.remaining_seconds()
                    if self._active_budget is not None
                    else 45.0
                )
                timeout = min(timeout, 0.05)
                if candidate_grace_deadline is not None:
                    timeout = min(
                        timeout,
                        max(0.0, candidate_grace_deadline - time.monotonic()),
                    )
                    if timeout <= 0:
                        stop_workers = True
                        worker_cancel.set()
                        for future in futures:
                            future.cancel()
                        break
                done, futures = wait(
                    futures,
                    timeout=timeout,
                    return_when=FIRST_COMPLETED,
                )
                if not done:
                    budget_expired = (
                        self._active_budget is not None
                        and self._active_budget.remaining_seconds() <= 0
                    )
                    grace_expired = (
                        candidate_grace_deadline is not None
                        and time.monotonic() >= candidate_grace_deadline
                    )
                    if budget_expired or grace_expired:
                        stop_workers = True
                        worker_cancel.set()
                        for future in futures:
                            future.cancel()
                        break
                    continue

                for future in done:
                    try:
                        fetched = future.result()
                    except FetchAborted:
                        continue
                    except Exception:
                        continue
                    for item in fetched:
                        self._apply_plot_to_metadata(
                            metadata,
                            item["text"],
                            item["source"],
                            db_title,
                            db_author,
                            query_type=item["query_type"],
                            elapsed_seconds=item["elapsed_seconds"],
                            source_url=item["source_url"],
                            match_confidence=item["match_confidence"],
                            candidates=candidates,
                            identifiers=item.get("identifiers"),
                        )
                    selected = _PLOT_RESOLVER.choose(candidates)
                    if (
                        selected is not None
                        and selected.auto_apply
                        and candidate_grace_deadline is None
                        and futures
                    ):
                        candidate_grace_deadline = (
                            time.monotonic() + PLOT_CANDIDATE_GRACE_SECONDS
                        )
        finally:
            if stop_workers:
                worker_cancel.set()
            executor.shutdown(wait=True, cancel_futures=True)

        self._check_abort()

        selected = _PLOT_RESOLVER.choose(candidates)
        ranked_candidates = _PLOT_RESOLVER.rank(candidates)
        diagnostics = getattr(self._plot_diagnostics_local, "active", None)
        if selected is not None:
            self._select_plot_candidate(metadata, selected)
            metadata["plot_candidates"] = [
                {
                    "text": candidate.normalized_text,
                    "source": candidate.source,
                    "identifiers": dict(candidate.identifiers),
                    "source_url": candidate.source_url,
                    "fetched_at": candidate.fetched_at,
                    "license_id": candidate.license_id,
                    "modified": candidate.modified,
                    "match_confidence": candidate.match_confidence,
                    "auto_apply": candidate.auto_apply,
                }
                for candidate in ranked_candidates
            ]
            if diagnostics is not None:
                diagnostics.select(selected)
        else:
            metadata.pop("plot", None)
            metadata.pop("plot_source", None)
            metadata.pop("plot_source_url", None)
            metadata.pop("plot_license_id", None)
            metadata.pop("plot_match_confidence", None)
            metadata.pop("plot_auto_apply", None)
            metadata.pop("plot_provenance", None)
            metadata.pop("plot_candidates", None)

        # Never leave short/stub source text on metadata for the review UI or DB.
        final = self._clean_plot_text(metadata.get("plot", ""))
        if not self._plot_is_adequate(final) or self._is_stub_plot(final):
            metadata.pop("plot", None)
            metadata.pop("plot_source", None)

    @staticmethod
    def _normalize_person_name(value: str) -> str:
        return re.sub(r"\s+", " ", (value or "").strip().lower())

    def _names_likely_same(self, left: str, right: str) -> bool:
        """True when two person names likely refer to the same individual."""
        left_norm = self._normalize_person_name(left)
        right_norm = self._normalize_person_name(right)
        if not left_norm or not right_norm:
            return False
        if left_norm == right_norm:
            return True
        left_last = self._extract_last_name(left).lower()
        right_last = self._extract_last_name(right).lower()
        return bool(left_last and left_last == right_last)

    @staticmethod
    def _likely_librivox_source(
        path: str | None = None,
        source: str | None = None,
        comments: str | None = None,
    ) -> bool:
        blob = " ".join([path or "", source or "", comments or ""]).lower()
        return "librivox" in blob

    def _should_use_title_only_fallback(
        self,
        author: str | None,
        *,
        narrator: str | None = None,
        path: str | None = None,
        source: str | None = None,
        comments: str | None = None,
        search_without_author: bool = False,
    ) -> bool:
        """Heuristics for Librivox-style rows where DB author may be the narrator."""
        if search_without_author:
            return True
        if not (author or "").strip():
            return True
        if self._names_likely_same(author, narrator or ""):
            return True
        return self._likely_librivox_source(path, source, comments)

    def __init__(self):
        """Initialize the API client."""
        self.google_books_url = "https://www.googleapis.com/books/v1/volumes"
        self.open_library_url = "https://openlibrary.org/search.json"
        self.open_library_work_url = "https://openlibrary.org/works"
        self.open_library_isbn_url = "https://openlibrary.org/isbn"
        self.wikidata_api_url = "https://www.wikidata.org/w/api.php"
        self.wikidata_url = "https://query.wikidata.org/sparql"  # legacy alias
        self.wikipedia_url = "https://en.wikipedia.org/w/api.php"
        self._cache: dict = {}
        self.CACHE_DURATION = CACHE_DURATION
        self.NEGATIVE_CACHE_TTL = NEGATIVE_CACHE_TTL_SECONDS
        self._cache_dirty = False
        self._active_budget: FetchBudget | None = None
        self._should_cancel: Callable[[], bool] | None = None
        self._plot_diagnostics_local = threading.local()
        self._plot_worker_local = threading.local()
        _load_persisted_cooldowns()
        self._load_persistent_cache()

    def _start_plot_diagnostics(self, title: str, author: str) -> None:
        self._plot_diagnostics_local.active = PlotFetchDiagnostics(
            title=title or "", author=author or ""
        )
        self._plot_diagnostics_local.last = None

    def _record_plot_candidate(self, candidate: PlotCandidate) -> None:
        diagnostics = getattr(self._plot_diagnostics_local, "active", None)
        if diagnostics is not None:
            diagnostics.record(candidate)

    def _record_existing_plot(
        self,
        metadata: Dict,
        *,
        cache_state: str,
        query_type: str,
    ) -> None:
        plot = self._clean_plot_text(metadata.get("plot", ""))
        if not self._plot_is_adequate(plot):
            return
        source = metadata.get("plot_source") or metadata.get("source") or metadata.get(
            "_resolved_source", ""
        )
        candidate = PlotCandidate(
            text=plot,
            normalized_text=plot,
            source=source,
            identifiers=candidate_identifiers(metadata),
            match_confidence=(
                (metadata.get("plot_provenance") or {}).get("match_confidence")
                or ("title_author" if metadata.get("author") else "title")
            ),
            query_type=query_type,
            cache_state=cache_state,
            source_url=candidate_provenance(metadata).get("plot_source_url", ""),
            license_id=candidate_provenance(metadata).get("plot_license_id", ""),
        )
        self._record_plot_candidate(candidate)
        diagnostics = getattr(self._plot_diagnostics_local, "active", None)
        if diagnostics is not None:
            diagnostics.select(candidate)

    def _finish_plot_diagnostics(self) -> None:
        diagnostics = getattr(self._plot_diagnostics_local, "active", None)
        if diagnostics is None:
            return
        request_count = getattr(self._active_budget, "request_count", 0)
        diagnostics.finish(request_count=request_count)
        self._plot_diagnostics_local.last = diagnostics.snapshot()
        self._plot_diagnostics_local.active = None

    def get_last_plot_diagnostics(self) -> dict:
        """Return the current thread's latest plot trace without plot text."""
        snapshot = getattr(self._plot_diagnostics_local, "last", None)
        if not snapshot:
            return {}
        return {
            **snapshot,
            "candidates": [dict(item) for item in snapshot.get("candidates", [])],
        }

    def _check_abort(self, source: str | None = None) -> None:
        """Raise FetchAborted when canceled or budget exhausted."""
        worker_cancel = getattr(self._plot_worker_local, "cancel_event", None)
        if worker_cancel is not None and worker_cancel.is_set():
            raise FetchAborted("canceled")
        if self._should_cancel is not None:
            try:
                if self._should_cancel():
                    raise FetchAborted("canceled")
            except FetchAborted:
                raise
            except Exception:
                pass
        if self._active_budget is not None and not self._active_budget.can_continue(
            source
        ):
            raise FetchAborted("budget")

    @staticmethod
    def _google_books_params(params: dict) -> dict:
        """Copy params and append optional Google Books API key."""
        out = dict(params)
        api_key = get_google_books_api_key()
        if api_key:
            out["key"] = api_key
        return out

    def _load_persistent_cache(self) -> None:
        """Load the persistent cache from web_cache.json if it exists."""
        try:
            cache_path = os.path.normpath(WEB_CACHE_FILE)
            if not os.path.exists(cache_path):
                return
            with open(cache_path, encoding="utf-8") as f:
                raw = json.load(f)
            now = time.time()
            for key, entry in raw.items():
                if not (isinstance(entry, list) and len(entry) == 2):
                    continue
                stamp, payload = entry[0], entry[1]
                try:
                    stamp_f = float(stamp)
                except (TypeError, ValueError):
                    continue
                if (
                    isinstance(payload, dict)
                    and payload.get("_cache_schema_version") is not None
                    and payload.get("_cache_schema_version")
                    != WEB_CACHE_SCHEMA_VERSION
                ):
                    continue
                if now - stamp_f >= self._cache_ttl_for(payload):
                    continue
                self._cache[key] = (stamp_f, payload)
        except Exception:
            pass  # Corrupt or missing cache is non-fatal

    def _save_persistent_cache(self, *, force: bool = False) -> None:
        """Persist the in-memory cache when dirty (max WEB_CACHE_MAX_ENTRIES)."""
        global _cache_write_warned
        if not force and not self._cache_dirty:
            return
        try:
            cache_path = os.path.normpath(WEB_CACHE_FILE)
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            now = time.time()
            entries = []
            for key, value in self._cache.items():
                if not (isinstance(value, (list, tuple)) and len(value) == 2):
                    continue
                stamp = value[0]
                try:
                    stamp_f = float(stamp)
                except (TypeError, ValueError):
                    continue
                payload = value[1]
                if self._cache_entry_kind(payload) == "transient":
                    continue
                ttl = self._cache_ttl_for(payload)
                if now - stamp_f >= ttl:
                    continue
                entries.append((key, stamp_f, payload))
            if len(entries) > WEB_CACHE_MAX_ENTRIES:
                entries.sort(key=lambda x: x[1])
                entries = entries[-WEB_CACHE_MAX_ENTRIES:]
            serialisable = {k: [stamp, payload] for k, stamp, payload in entries}
            fd, tmp_path = tempfile.mkstemp(
                dir=os.path.dirname(cache_path), suffix=".tmp"
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(
                        serialisable, f, ensure_ascii=False, separators=(",", ":")
                    )
                os.replace(tmp_path, cache_path)
            except Exception:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise
            self._cache_dirty = False
        except Exception as exc:
            if not _cache_write_warned:
                print(
                    f"[AbCS] Warning: could not write web cache "
                    f"({WEB_CACHE_FILE}): {exc}",
                    file=sys.stderr,
                )
                _cache_write_warned = True

    def _store_cache_entry(self, cache_key: str, metadata: Dict) -> None:
        """Store a classified lookup and mark the disk cache dirty."""
        stored = dict(metadata)
        stored["_cache_schema_version"] = WEB_CACHE_SCHEMA_VERSION
        stored["_cache_kind"] = self._cache_entry_kind(stored)
        sources = set()
        for key in ("source", "plot_source", "_resolved_source"):
            if stored.get(key):
                sources.add(str(stored[key]))
        for error in stored.get("_fetch_errors", []) or []:
            source = str(error).split(":", 1)[0].strip()
            if source:
                sources.add(source)
        if sources:
            stored["_cache_sources"] = sorted(sources)
        self._cache[cache_key] = (time.time(), stored)
        self._cache_dirty = True
        self._save_persistent_cache()

    def _cache_ttl_for(self, payload) -> float:
        kind = self._cache_entry_kind(payload)
        if kind == "transient":
            return float(TRANSIENT_CACHE_TTL_SECONDS)
        if kind == "negative":
            return float(self.NEGATIVE_CACHE_TTL)
        return float(self.CACHE_DURATION)

    @staticmethod
    def _normalize_isbn(isbn: str) -> str:
        """Return a normalized ISBN-10/13 string, or empty when invalid."""
        if not isbn:
            return ""
        clean = re.sub(r"[^0-9X]", "", str(isbn).upper())
        if len(clean) in (10, 13):
            return clean
        return ""

    def _first_isbn_from_list(self, isbn_list) -> str:
        """Pick the first valid ISBN from an Open Library search doc list."""
        for raw in isbn_list or []:
            clean = self._normalize_isbn(str(raw))
            if clean:
                return clean
        return ""

    def _fetch_google_by_isbn(self, isbn: str) -> Optional[Dict]:
        """Fetch metadata from Google Books using an exact ISBN query."""
        clean_isbn = self._normalize_isbn(isbn)
        if not clean_isbn:
            return None
        if _is_source_cooling_down("google_books"):
            return None
        try:
            self._check_abort()
            params = {
                "q": f"isbn:{clean_isbn}",
                "maxResults": 1,
                "fields": (
                    "items(id,volumeInfo(title,subtitle,authors,publisher,"
                    "publishedDate,description,industryIdentifiers,categories,"
                    "averageRating,ratingsCount,seriesInfo))"
                ),
            }
            url = (
                f"{self.google_books_url}?"
                f"{urllib.parse.urlencode(self._google_books_params(params))}"
            )
            data = _http_get_json(
                url,
                timeout=TIMEOUT_DETAIL,
                source="google_books",
                budget=self._active_budget,
            )
            items = data.get("items") or []
            if not items:
                return None
            metadata = self._google_item_to_metadata(items[0])
            if metadata:
                metadata["isbn"] = clean_isbn
                google_id = str(items[0].get("id") or "").strip()
                if google_id:
                    metadata["google_id"] = google_id
                    metadata["plot_source_url"] = (
                        f"https://books.google.com/books?id={google_id}"
                    )
            return metadata
        except FetchAborted:
            raise
        except SourceCooldownError:
            return None
        except urllib.error.HTTPError as exc:
            if isinstance(exc, SourceCooldownError):
                return None
            if (
                exc.code in _FATAL_HTTP_CODES
                or _is_rate_limit_http_code("google_books", exc.code)
            ):
                _note_rate_limited("google_books", headers=getattr(exc, "headers", None))
            return None
        except Exception:
            return None

    def _fetch_metadata_by_isbn(self, isbn: str) -> Optional[Dict]:
        """Exact ISBN lookup: Google Books first, Open Library for gaps."""
        clean_isbn = self._normalize_isbn(isbn)
        if not clean_isbn:
            return None

        gb_meta = self._fetch_google_by_isbn(clean_isbn)
        need_ol = True
        if (
            gb_meta
            and gb_meta.get("title")
            and gb_meta.get("author")
            and gb_meta.get("year")
            and gb_meta.get("plot")
        ):
            need_ol = False

        ol_meta = self._fetch_by_isbn(clean_isbn) if need_ol else None
        if not gb_meta and not ol_meta:
            return None

        metadata: Dict = dict(ol_meta) if ol_meta else {}
        if gb_meta:
            if not metadata:
                metadata = dict(gb_meta)
            else:
                for key in (
                    "title",
                    "author",
                    "year",
                    "publisher",
                    "rating",
                    "ratings_count",
                ):
                    if gb_meta.get(key) and not metadata.get(key):
                        metadata[key] = gb_meta[key]
                if gb_meta.get("plot"):
                    metadata["plot"] = gb_meta["plot"]
                if gb_meta.get("genre") and not metadata.get("genre"):
                    metadata["genre"] = gb_meta["genre"]
            if ol_meta and ol_meta.get("open_library_work_key"):
                metadata["open_library_work_key"] = ol_meta["open_library_work_key"]
            metadata["_resolved_source"] = "google_books"
        else:
            metadata["_resolved_source"] = "open_library"

        metadata["isbn"] = clean_isbn
        return metadata

    def _fetch_by_isbn(self, isbn: str) -> Optional[Dict]:
        """Exact Open Library lookup by ISBN.

        Returns a metadata dict on success, or None.  ISBN lookups skip all
        title/author matching because the result is unambiguous.
        """
        if not isbn:
            return None
        try:
            self._check_abort()
            clean_isbn = self._normalize_isbn(isbn)
            if not clean_isbn:
                return None
            url = f"{self.open_library_isbn_url}/{clean_isbn}.json"
            data = _http_get_json(
                url,
                timeout=TIMEOUT_DETAIL,
                source="open_library",
                budget=self._active_budget,
            )

            if "error" in data:
                return None

            title = data.get("title", "")
            if not title:
                return None

            author = ""
            raw_authors = data.get("authors", [])
            if raw_authors:
                try:
                    author_key = raw_authors[0].get("key", "")
                    if author_key:
                        self._check_abort()
                        author_url = f"https://openlibrary.org{author_key}.json"
                        author_data = _http_get_json(
                            author_url,
                            timeout=TIMEOUT_DETAIL,
                            source="open_library",
                            budget=self._active_budget,
                        )
                        author = (
                            author_data.get("name", "")
                            or author_data.get("personal_name", "")
                        )
                except FetchAborted:
                    raise
                except Exception:
                    pass

            year = ""
            pub_date = str(data.get("publish_date", ""))
            year_match = re.search(r"\d{4}", pub_date)
            if year_match:
                year = year_match.group(0)

            work_key = ""
            works = data.get("works", [])
            if works:
                work_key = works[0].get("key", "")

            metadata: Dict = {
                "title": title,
                "author": author,
                "year": year,
                "isbn": clean_isbn,
                "open_library_work_key": work_key,
                "_resolved_source": "open_library",
            }
            if work_key:
                metadata["plot_source_url"] = f"https://openlibrary.org{work_key}"
            return metadata
        except FetchAborted:
            raise
        except Exception:
            return None

    def get_book_metadata(
        self,
        title: str,
        author: str = None,
        year: str = None,
        refresh: int = 0,
        append_series_to_title: bool = True,
        *,
        narrator: str | None = None,
        path: str | None = None,
        source: str | None = None,
        comments: str | None = None,
        search_without_author: bool = False,
        isbn: str | None = None,
        progress_callback: Callable[[str], None] | None = None,
        should_cancel: Callable[[], bool] | None = None,
        bypass_cache: bool = False,
    ) -> Optional[Dict]:
        """
        Fetch book metadata from multiple web sources.

        Args:
            title: Book title
            author: Author name (optional)
            year: Ignored for search (library years are often wrong); kept for API compatibility
            refresh: 0=Open Library then Google Books then WikiData;
                     1=Google Books then WikiData (skip Open Library);
                     2=WikiData only
            append_series_to_title: When True, append series number to title for display
            narrator: Reader/narrator when tagged separately from author
            path: Book folder path (Librivox detection)
            source: Book source field (Librivox detection)
            comments: Book comments (Librivox detection)
            search_without_author: Force title-only matching after author search fails
            isbn: ISBN-10 or ISBN-13 if available; tried first as an exact lookup
            progress_callback: Optional callable invoked with human-readable status text
            should_cancel: Optional callable; when True, abort between requests
            bypass_cache: When True (e.g. Re-fetch), skip the successful-lookup cache

        Returns:
            Dictionary with book metadata and source info, or None if not found.
            On cancel: ``{"_canceled": True}``. On total miss with errors:
            ``{"_no_result": True, "_fetch_errors": [...]}``.
        """
        cache_key = (
            f"{title}|{author}|{refresh}|{narrator}|{path}|{source}|"
            f"{search_without_author}|{isbn or ''}"
        )
        current_time = time.time()
        self._active_budget = FetchBudget()
        self._should_cancel = should_cancel
        self._start_plot_diagnostics(title or "", author or "")

        # Normalize title for search and comparison (do NOT append series number)
        search_title, series_number = self._strip_series_number(title)
        search_title = self._move_article_to_beginning(search_title)
        search_title = self._clean_text_field(search_title)

        search_author = self._strip_author_honorifics(
            self._apply_author_transformations(author)
        )

        def _report_progress(message: str) -> None:
            if not progress_callback:
                return
            try:
                progress_callback(message)
            except Exception:
                pass

        def _public_copy(metadata: Dict) -> Dict:
            """Return a UI-facing copy without internal cache-only keys."""
            out = dict(metadata)
            out.pop("open_library_work_key", None)
            for key in (
                "_cache_schema_version",
                "_cache_kind",
                "_cache_sources",
            ):
                out.pop(key, None)
            return out

        def _finish_metadata(
            metadata: Dict,
            resolved_source: str,
            first_attempt: bool,
        ) -> Dict:
            if append_series_to_title and series_number:
                title_text = metadata.get("title", "") or ""
                if not title_text.rstrip().endswith(f"- {series_number}"):
                    metadata["title"] = f"{title_text} - {series_number}".strip()
            metadata["source"] = resolved_source
            metadata["first_attempt"] = first_attempt
            try:
                self._enrich_metadata_plot(
                    metadata,
                    search_title,
                    search_author or "",
                    report_progress=_report_progress,
                )
            except FetchAborted as abort:
                if abort.reason == "canceled":
                    return {"_canceled": True}
            except Exception:
                pass
            if not self._plot_is_adequate(metadata.get("plot", "")) or self._is_stub_plot(
                metadata.get("plot", "")
            ):
                metadata.pop("plot", None)
                metadata.pop("plot_source", None)
                metadata.pop("plot_source_url", None)
                metadata.pop("plot_license_id", None)
                metadata.pop("plot_match_confidence", None)
                metadata.pop("plot_auto_apply", None)
                metadata.pop("plot_provenance", None)
            # True only when a usable plot was found — empty attempts must not
            # block later cache hits from retrying enrichment.
            metadata["_plot_enriched"] = self._plot_is_adequate(
                metadata.get("plot", "")
            )
            self._store_cache_entry(cache_key, dict(metadata))
            return _public_copy(metadata)

        try:
            # Cache successful lookups and short-TTL misses.
            if (
                not bypass_cache
                and hasattr(self, "_cache")
                and cache_key in self._cache
            ):
                cached_time, cached_result = self._cache[cache_key]
                if (
                    cached_result
                    and cached_time
                    and (current_time - cached_time) < self._cache_ttl_for(cached_result)
                ):
                    if isinstance(cached_result, dict) and cached_result.get(
                        "_no_result"
                    ):
                        if self._should_bypass_negative_cache(cached_result):
                            del self._cache[cache_key]
                            self._cache_dirty = True
                            cached_result = None
                        else:
                            return _public_copy(cached_result)
                    if cached_result is not None:
                        refreshed = dict(cached_result)
                        refreshed.pop("_series_enriched", None)
                        refreshed.pop("series", None)
                        refreshed.pop("series_number", None)
                        if self._plot_is_adequate(refreshed.get("plot", "")):
                            refreshed["_plot_enriched"] = True
                            self._record_existing_plot(
                                refreshed,
                                cache_state="cache_hit",
                                query_type="cached_result",
                            )
                            return _public_copy(refreshed)
                        # Match cached without plot: retry enrichment (e.g. WikiData
                        # hit that previously exhausted budget / hit Wikipedia limits).
                        try:
                            self._enrich_metadata_plot(
                                refreshed,
                                search_title,
                                search_author or "",
                                report_progress=_report_progress,
                            )
                        except FetchAborted as abort:
                            if abort.reason == "canceled":
                                return {"_canceled": True}
                        except Exception:
                            pass
                        refreshed["_plot_enriched"] = self._plot_is_adequate(
                            refreshed.get("plot", "")
                        )
                        self._store_cache_entry(cache_key, dict(refreshed))
                        return _public_copy(refreshed)
                if cached_time and (
                    current_time - cached_time
                ) >= self._cache_ttl_for(cached_result):
                    del self._cache[cache_key]
                    self._cache_dirty = True

            # ISBN pre-pass: exact lookup via Google Books and Open Library
            if isbn:
                self._check_abort()
                _report_progress("Looking up ISBN…")
                isbn_meta = self._fetch_metadata_by_isbn(isbn)
                if isbn_meta and not isbn_meta.get("_no_result"):
                    resolved = (
                        "open_library_isbn"
                        if isbn_meta.get("_resolved_source") == "open_library"
                        else "google_books_isbn"
                    )
                    return _finish_metadata(isbn_meta, resolved, first_attempt=True)

            metadata = self._search_metadata_sources(
                search_title,
                search_author,
                refresh,
                require_author_match=True,
                progress_callback=progress_callback,
            )
            if metadata and not metadata.get("_no_result"):
                return _finish_metadata(
                    metadata,
                    metadata.pop("_resolved_source", metadata.get("source", "")),
                    first_attempt=True,
                )
            _errors: list[str] = (metadata or {}).get("_fetch_errors", [])

            use_title_only = self._should_use_title_only_fallback(
                search_author,
                narrator=narrator,
                path=path,
                source=source,
                comments=comments,
                search_without_author=search_without_author,
            )
            if search_title and search_author and not use_title_only:
                self._check_abort()
                _report_progress("Trying broader title search…")
                metadata = self._search_metadata_sources(
                    search_title,
                    None,
                    refresh,
                    require_author_match=True,
                    match_author=search_author,
                    progress_callback=progress_callback,
                    search_phase="broadened",
                )
                if metadata and not metadata.get("_no_result"):
                    metadata["broadened_search"] = True
                    return _finish_metadata(
                        metadata,
                        metadata.pop("_resolved_source", metadata.get("source", "")),
                        first_attempt=True,
                    )
                if metadata:
                    _errors.extend(metadata.get("_fetch_errors", []))

            if search_title and use_title_only:
                self._check_abort()
                _report_progress("Trying title-only search…")
                metadata = self._search_metadata_sources(
                    search_title,
                    None,
                    refresh,
                    require_author_match=False,
                    progress_callback=progress_callback,
                    search_phase="title_only",
                )
                if metadata and not metadata.get("_no_result"):
                    metadata["title_only_search"] = True
                    return _finish_metadata(
                        metadata,
                        metadata.pop("_resolved_source", metadata.get("source", "")),
                        first_attempt=refresh >= 1,
                    )
                if metadata:
                    _errors.extend(metadata.get("_fetch_errors", []))

            if _errors:
                miss = {
                    "_fetch_errors": _dedupe_fetch_errors(_errors),
                    "_no_result": True,
                }
                self._store_cache_entry(cache_key, dict(miss))
                return miss
            miss = {"_no_result": True, "_fetch_errors": []}
            self._store_cache_entry(cache_key, dict(miss))
            return None
        except FetchAborted as abort:
            if abort.reason == "canceled":
                return {"_canceled": True}
            # Budget exhausted with no match yet
            return None
        finally:
            self._finish_plot_diagnostics()
            self._active_budget = None
            self._should_cancel = None
            self._save_persistent_cache(force=False)

    def _search_metadata_sources(
        self,
        search_title: str,
        query_author: str | None,
        refresh: int,
        *,
        require_author_match: bool,
        match_author: str | None = None,
        progress_callback: Callable[[str], None] | None = None,
        search_phase: str = "primary",
    ) -> Optional[Dict]:
        """Query Open Library, Google Books, and WikiData with shared match rules."""
        db_author = match_author if match_author is not None else query_author
        fetch_errors: list[str] = []

        def _report(message: str) -> None:
            if not progress_callback:
                return
            try:
                progress_callback(message)
            except Exception:
                pass

        if refresh == 0:
            self._check_abort()
            _report(_source_progress_message("open_library", phase=search_phase))
            try:
                metadata = self._fetch_from_open_library(
                    search_title,
                    query_author,
                    require_author_match=require_author_match,
                    match_author=db_author,
                )
                if metadata:
                    metadata["_resolved_source"] = "open_library"
                    return metadata
            except FetchAborted:
                raise
            except Exception as exc:
                fetch_errors.append(f"open_library: {exc}")

        if refresh <= 1:
            self._check_abort()
            if _is_source_cooling_down("google_books"):
                fetch_errors.append("google_books: paused")
            else:
                _report(_source_progress_message("google_books", phase=search_phase))
                try:
                    metadata = self._fetch_from_google_books(
                        search_title,
                        query_author,
                        require_author_match=require_author_match,
                        match_author=db_author,
                        propagate_fatal_errors=True,
                    )
                    if metadata:
                        metadata["_resolved_source"] = "google_books"
                        return metadata
                except FetchAborted:
                    raise
                except Exception as exc:
                    fetch_errors.append(f"google_books: {exc}")

        if refresh <= 2:
            self._check_abort()
            _report(_source_progress_message("wikidata", phase=search_phase))
            try:
                metadata = self._fetch_from_wikidata(
                    search_title,
                    query_author,
                    require_author_match=require_author_match,
                    match_author=db_author,
                    propagate_fatal_errors=True,
                )
                if metadata:
                    metadata["_resolved_source"] = "wikidata"
                    return metadata
            except FetchAborted:
                raise
            except Exception as exc:
                fetch_errors.append(f"wikidata: {exc}")

        if fetch_errors:
            return {"_fetch_errors": fetch_errors, "_no_result": True}
        return None

    def _google_item_to_metadata(self, item: dict) -> Optional[Dict]:
        """Build metadata dict from one Google Books API item."""
        volume_info = item.get("volumeInfo", {})
        if not volume_info.get("title"):
            return None

        metadata = {
            "title": volume_info.get("title", ""),
            "author": self._format_authors(volume_info.get("authors", [])),
            "year": self._extract_year(volume_info.get("publishedDate", "")),
            "publisher": volume_info.get("publisher", ""),
            "plot": self._strip_html(volume_info.get("description", "") or ""),
            "genre": self._format_categories(volume_info.get("categories", [])),
            "isbn": self._extract_isbn(volume_info.get("industryIdentifiers", [])),
            "rating": volume_info.get("averageRating", 0),
            "ratings_count": volume_info.get("ratingsCount", 0),
            "source": "Google Books",
            "confidence": 0.9,
        }
        google_id = str(item.get("id") or "").strip()
        if google_id:
            metadata["google_id"] = google_id
            metadata["plot_source_url"] = (
                f"https://books.google.com/books?id={google_id}"
            )
        return metadata

    def _pick_best_google_match(
        self,
        items: list,
        title: str,
        db_author: str | None,
        *,
        require_author_match: bool,
    ) -> Optional[Dict]:
        best_metadata = None
        best_title_score = -1.0
        for item in items:
            candidate = self._google_item_to_metadata(item)
            if not candidate:
                continue
            if not self._metadata_matches_db(
                title,
                db_author,
                candidate,
                require_author_match=require_author_match,
            ):
                continue
            title_score = self._best_title_word_match_score(
                title, candidate.get("title", ""), db_author
            )
            if title_score > best_title_score:
                best_title_score = title_score
                best_metadata = candidate
        return best_metadata

    def _fetch_from_google_books(
        self,
        title: str,
        author: str = None,
        *,
        require_author_match: bool = True,
        match_author: str | None = None,
        propagate_fatal_errors: bool = False,
    ) -> Optional[Dict]:
        """Fetch metadata from Google Books API."""
        db_author = match_author if match_author is not None else author
        if _is_source_cooling_down("google_books"):
            return None

        queries: list[str] = []
        for query_title in self._query_titles_for_metadata(title, db_author):
            if query_title and author:
                queries.append(f"intitle:{query_title} inauthor:{author}")
            if query_title and (author or require_author_match):
                queries.append(f"intitle:{query_title}")
            elif not require_author_match and query_title:
                queries.append(query_title)

        seen: set[str] = set()
        for q_idx, query in enumerate(queries):
            if not query or query in seen:
                continue
            seen.add(query)
            try:
                self._check_abort()
                max_results = 5 if q_idx > 0 else 10
                params = {
                    "q": query,
                    "maxResults": max_results,
                    "fields": (
                        "items(id,volumeInfo(title,subtitle,authors,publisher,"
                        "publishedDate,description,industryIdentifiers,categories,"
                        "averageRating,ratingsCount,seriesInfo))"
                    ),
                }
                url = (
                    f"{self.google_books_url}?"
                    f"{urllib.parse.urlencode(self._google_books_params(params))}"
                )
                search_timeout = TIMEOUT_SEARCH if q_idx == 0 else TIMEOUT_DETAIL
                data = _http_get_json(
                    url,
                    timeout=search_timeout,
                    source="google_books",
                    budget=self._active_budget,
                )
                if "items" in data and data["items"]:
                    best = self._pick_best_google_match(
                        data["items"],
                        title,
                        db_author,
                        require_author_match=require_author_match,
                    )
                    if best:
                        return best
            except FetchAborted:
                raise
            except SourceCooldownError:
                if propagate_fatal_errors:
                    raise
                break
            except urllib.error.HTTPError as exc:
                if isinstance(exc, SourceCooldownError):
                    if propagate_fatal_errors:
                        raise
                    break
                if (
                    exc.code in _FATAL_HTTP_CODES
                    or _is_rate_limit_http_code("google_books", exc.code)
                ):
                    _note_rate_limited(
                        "google_books", headers=getattr(exc, "headers", None)
                    )
                    if propagate_fatal_errors:
                        raise
                    break
                continue
            except Exception:
                continue
        return None

    def _fetch_from_open_library(
        self,
        title: str,
        author: str = None,
        *,
        require_author_match: bool = True,
        match_author: str | None = None,
    ) -> Optional[Dict]:
        """Fetch metadata from Open Library API (title and author only; no DB year filter)."""
        db_author = match_author if match_author is not None else author
        title_variants = self._query_titles_for_metadata(title, db_author)
        queries_to_try = []

        for variant_title in title_variants:
            if ORWELL_1984_TITLE_TOKEN in variant_title.lower():
                base_query = variant_title
                if author:
                    base_query += f" author:{author}"
                queries_to_try.append(base_query)

                if "nineteen eighty-four" not in variant_title.lower():
                    alt_query = "nineteen eighty-four"
                    if author:
                        alt_query += f" author:{author}"
                    queries_to_try.append(alt_query)
            else:
                if author:
                    queries_to_try.append(f"{variant_title} author:{author}")
                    stripped_author = self._strip_author_honorifics(author)
                    if stripped_author and stripped_author.lower() != author.lower():
                        queries_to_try.append(
                            f"{variant_title} author:{stripped_author}"
                        )
                queries_to_try.append(variant_title)

        fallback_metadata = None
        fallback_title_score = -1.0
        seen_queries = set()
        for query in queries_to_try:
            if query in seen_queries:
                continue
            seen_queries.add(query)
            if len(seen_queries) > 4:
                break
            try:
                self._check_abort()
                params = {
                    "q": query,
                    "limit": 10,
                    "fields": (
                        "key,title,author_name,first_publish_year,publisher,"
                        "subject,cover_i,isbn,ratings_average,ratings_count"
                    ),
                }

                url = f"{self.open_library_url}?{urllib.parse.urlencode(params)}"
                data = _http_get_json(
                    url,
                    timeout=TIMEOUT_SEARCH,
                    source="open_library",
                    budget=self._active_budget,
                )

                if data.get("docs"):
                    best_metadata = None
                    best_title_score = -1.0
                    best_exact_title = False
                    best_work_key = ""
                    best_isbn = ""
                    for doc in data["docs"]:
                        candidate = {
                            "title": doc.get("title", ""),
                            "author": ", ".join(doc.get("author_name", [])),
                            "year": str(doc.get("first_publish_year", "")),
                            "publisher": ", ".join(doc.get("publisher", [])),
                            "plot": "",
                            "genre": ", ".join(doc.get("subject", [])[:3]),
                            "rating": str(doc.get("ratings_average", "")),
                            "ratings_count": str(doc.get("ratings_count", "")),
                            "source": "open_library",
                        }
                        identity_match = self._plot_identifier_matches_db(
                            title, db_author, candidate
                        )
                        if not identity_match and not self._metadata_matches_db(
                            title,
                            db_author,
                            candidate,
                            require_author_match=require_author_match,
                        ):
                            continue
                        title_score = self._best_title_word_match_score(
                            title, candidate.get("title", ""), db_author
                        )
                        exact_title = identity_match
                        if (exact_title, title_score) > (
                            best_exact_title,
                            best_title_score,
                        ):
                            best_exact_title = exact_title
                            best_title_score = title_score
                            best_metadata = candidate
                            best_work_key = doc.get("key", "") or ""
                            best_isbn = self._first_isbn_from_list(doc.get("isbn"))
                    if best_metadata:
                        if best_isbn:
                            best_metadata["isbn"] = best_isbn
                        if best_work_key:
                            best_metadata["open_library_work_key"] = best_work_key
                        if best_exact_title:
                            if best_work_key:
                                work_fields = self._get_open_library_work_fields(
                                    best_work_key
                                )
                                best_metadata["plot"] = work_fields.get(
                                    "description", ""
                                )
                            return best_metadata
                        if best_title_score > fallback_title_score:
                            fallback_title_score = best_title_score
                            fallback_metadata = dict(best_metadata)

            except FetchAborted:
                raise
            except urllib.error.HTTPError as exc:
                _reraise_if_fatal_http_error(exc)
                continue
            except Exception:
                continue

        if fallback_metadata:
            fallback_work_key = fallback_metadata.get("open_library_work_key", "")
            if fallback_work_key:
                work_fields = self._get_open_library_work_fields(fallback_work_key)
                fallback_metadata["plot"] = work_fields.get("description", "")
            return fallback_metadata
        return None

    def _get_open_library_work_fields(self, work_key: str) -> Dict[str, str]:
        """Load description from an Open Library work record."""
        empty = {"description": ""}
        if not work_key:
            return empty
        try:
            self._check_abort()
            work_id = work_key.split("/")[-1] if "/" in work_key else work_key
            url = f"{self.open_library_work_url}/{work_id}.json"
            data = _http_get_json(
                url,
                timeout=TIMEOUT_DETAIL,
                source="open_library",
                budget=self._active_budget,
            )

            return {
                "description": self._extract_description(data.get("description", "")),
            }
        except FetchAborted:
            raise
        except Exception:
            return empty

    def _fetch_plot_from_open_library(self, title: str, author: str = None) -> str:
        """Search Open Library by title/author to find a work description.

        This is only called from _enrich_metadata_plot when no open_library_work_key
        is available on the metadata (e.g. after a Google Books or WikiData win).
        """
        try:
            if not title:
                return ""

            self._check_abort()
            query = title
            if author:
                query += f" author:{author}"

            params = {
                "q": query,
                "limit": 3,
                "fields": "key,title,author_name,description",
            }

            url = f"{self.open_library_url}?{urllib.parse.urlencode(params)}"
            data = _http_get_json(
                url,
                timeout=TIMEOUT_SEARCH,
                source="open_library",
                budget=self._active_budget,
            )

            if not data.get("docs"):
                return ""

            for doc in data["docs"]:
                candidate = {
                    "title": doc.get("title", ""),
                    "author": ", ".join(doc.get("author_name", [])),
                }
                if not self._metadata_matches_db(
                    title,
                    author or "",
                    candidate,
                    require_author_match=bool(author),
                ):
                    continue
                work_key = doc.get("key", "")
                if work_key:
                    plot = self._get_open_library_work_fields(work_key).get(
                        "description", ""
                    )
                    if plot and len(plot) > 20:
                        self._plot_diagnostics_local.source_url = (
                            f"https://openlibrary.org{work_key}"
                        )
                        return plot

            return ""
        except FetchAborted:
            raise
        except Exception:
            return ""

    def _fetch_wikipedia_rest_summary(self, title: str) -> str:
        """Fetch a plain-text extract from the Wikipedia REST summary endpoint."""
        if not title:
            return ""
        try:
            self._check_abort()
            encoded_title = urllib.parse.quote(title.replace(" ", "_"))
            request_url = (
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
            )
            data = _http_get_json(
                request_url,
                timeout=TIMEOUT_DETAIL,
                source="wikipedia",
                budget=self._active_budget,
            )
            extract = data.get("extract", "")
            if data.get("type") == "disambiguation":
                return ""
            page_url = (
                data.get("content_urls", {}).get("desktop", {}).get("page", "")
            )
            if not page_url:
                page_url = request_url
            self._plot_diagnostics_local.source_url = page_url
            return self._strip_html(extract)
        except FetchAborted:
            raise
        except Exception:
            return ""

    def _fetch_plot_from_wikipedia(
        self,
        title: str,
        author: str | None = None,
        *,
        db_title: str | None = None,
        db_author: str | None = None,
    ) -> str:
        """Search Wikipedia for a book and return its summary/extract."""
        match_title = db_title or title
        match_author = db_author or author
        try:
            if not title:
                return ""

            search_terms = [f"{title} novel", f"{title} book"]
            if author:
                search_terms.insert(0, f"{title} {author} novel")
                search_terms.insert(1, f"{title} {author} book")

            for search_query in search_terms:
                self._check_abort()
                search_params = {
                    "action": "query",
                    "list": "search",
                    "srsearch": search_query,
                    "srlimit": 5,
                    "format": "json",
                    "origin": "*",
                }

                search_url = (
                    f"{self.wikipedia_url}?{urllib.parse.urlencode(search_params)}"
                )
                search_data = _http_get_json(
                    search_url,
                    timeout=TIMEOUT_SEARCH,
                    source="wikipedia",
                    budget=self._active_budget,
                )

                if not search_data.get("query", {}).get("search"):
                    continue

                for result in search_data["query"]["search"][:3]:
                    page_title = result.get("title", "")
                    if not page_title:
                        continue

                    if match_title and not self._title_matches(match_title, page_title):
                        continue

                    if author:
                        author_parts = author.lower().split()
                        if all(part in page_title.lower() for part in author_parts):
                            if "(" in page_title or "author" in page_title.lower():
                                continue

                    self._check_abort()
                    extract_params = {
                        "action": "query",
                        "prop": "extracts",
                        "explaintext": True,
                        "exintro": True,
                        "exsentences": PLOT_MAX_WIKIPEDIA_SENTENCES,
                        "titles": page_title,
                        "format": "json",
                        "origin": "*",
                    }

                    extract_url = (
                        f"{self.wikipedia_url}?{urllib.parse.urlencode(extract_params)}"
                    )
                    extract_data = _http_get_json(
                        extract_url,
                        timeout=TIMEOUT_DETAIL,
                        source="wikipedia",
                        budget=self._active_budget,
                    )

                    pages = extract_data.get("query", {}).get("pages", {})
                    for _, page_data in pages.items():
                        extract = self._clean_plot_text(page_data.get("extract", ""))
                        if not self._plot_is_adequate(extract):
                            continue
                        if "may refer to" in extract.lower()[:120]:
                            continue
                        if "disambiguation" in page_data.get("title", "").lower():
                            continue
                        if match_author and not self._author_matches(
                            match_author, extract
                        ):
                            continue
                        self._plot_diagnostics_local.source_url = (
                            "https://en.wikipedia.org/wiki/"
                            + urllib.parse.quote(
                                page_data.get("title", page_title).replace(" ", "_")
                            )
                        )
                        return extract

            return ""
        except FetchAborted:
            raise
        except Exception:
            return ""

    def _format_authors(self, authors: List[str]) -> str:
        """Format author list as string."""
        if not authors:
            return ""
        elif len(authors) == 1:
            return authors[0]
        elif len(authors) <= 3:
            return ", ".join(authors)
        else:
            return f"{', '.join(authors[:2])} and {len(authors) - 2} others"

    def _format_categories(self, categories: List[str]) -> str:
        """Format category list as string."""
        if not categories:
            return ""
        elif len(categories) == 1:
            return categories[0]
        elif len(categories) <= 3:
            return " > ".join(categories[:3])
        else:
            return f"{' > '.join(categories[:2])} > {len(categories) - 2} more"

    def _extract_year(self, published_date: str) -> str:
        """Extract year from published date string."""
        if not published_date:
            return ""
        year_match = re.search(r"\b(19|20)\d{2}\b", published_date)
        return year_match.group(0) if year_match else ""

    def _extract_isbn(self, identifiers: List[Dict]) -> str:
        """Extract ISBN from industry identifiers."""
        if not identifiers:
            return ""

        # Prefer ISBN-13, fallback to ISBN-10
        for identifier in identifiers:
            if identifier.get("type") == "ISBN_13":
                return identifier.get("identifier", "")

        for identifier in identifiers:
            if identifier.get("type") == "ISBN_10":
                return identifier.get("identifier", "")

        return ""

    def _extract_description(self, description) -> str:
        """Extract description from various formats."""
        if isinstance(description, str):
            return description
        elif isinstance(description, dict):
            return description.get("value", "")
        else:
            return str(description) if description else ""

    def _fetch_from_wikidata(
        self,
        title: str,
        author: str = None,
        *,
        require_author_match: bool = True,
        match_author: str | None = None,
        propagate_fatal_errors: bool = False,
    ) -> Optional[Dict]:
        """Fetch metadata from WikiData via indexed entity search (not full SPARQL scan)."""
        db_author = match_author if match_author is not None else author
        if not title:
            return None
        if _is_source_cooling_down("wikidata"):
            if propagate_fatal_errors:
                _raise_cooldown_http_error("wikidata")
            return None
        try:
            self._check_abort("wikidata")
            search_terms: list[str] = []
            seen_terms: set[str] = set()

            def _add_search_term(term: str) -> None:
                if term and term not in seen_terms:
                    seen_terms.add(term)
                    search_terms.append(term)

            for query_title in self._query_titles_for_metadata(title, db_author):
                if ORWELL_1984_TITLE_TOKEN in query_title.lower():
                    _add_search_term(f"{query_title} {ORWELL_AUTHOR_LABEL}")
                if author:
                    _add_search_term(f"{query_title} {author}")
                _add_search_term(query_title)
            if not search_terms:
                return None

            candidate_ids: list[str] = []
            seen_ids: set[str] = set()
            for search_term in search_terms:
                if candidate_ids:
                    break
                params = {
                    "action": "wbsearchentities",
                    "search": search_term,
                    "language": "en",
                    "type": "item",
                    "limit": 8,
                    "format": "json",
                }
                url = (
                    f"{self.wikidata_api_url}?"
                    f"{urllib.parse.urlencode(params)}"
                )
                data = _http_get_json(
                    url,
                    timeout=TIMEOUT_SEARCH,
                    source="wikidata",
                    budget=self._active_budget,
                )
                for hit in data.get("search") or []:
                    qid = (hit.get("id") or "").strip()
                    if not qid or qid in seen_ids:
                        continue
                    label = hit.get("label") or ""
                    if label and not self._title_matches(title, label, db_author):
                        # Keep near-misses only when description mentions novel/book.
                        desc = (hit.get("description") or "").lower()
                        if not any(
                            token in desc
                            for token in ("novel", "book", "novella", "written work")
                        ):
                            continue
                    seen_ids.add(qid)
                    candidate_ids.append(qid)
                    if len(candidate_ids) >= 8:
                        break

            if not candidate_ids:
                return None

            self._check_abort("wikidata")
            get_params = {
                "action": "wbgetentities",
                "ids": "|".join(candidate_ids),
                "props": "labels|claims",
                "languages": "en",
                "format": "json",
            }
            get_url = (
                f"{self.wikidata_api_url}?"
                f"{urllib.parse.urlencode(get_params)}"
            )
            entities_data = _http_get_json(
                get_url,
                timeout=TIMEOUT_DETAIL,
                source="wikidata",
                budget=self._active_budget,
            )
            entities = entities_data.get("entities") or {}

            related_ids: list[str] = []
            seen_related: set[str] = set()
            for qid in candidate_ids:
                entity = entities.get(qid) or {}
                claims = entity.get("claims") or {}
                for prop in ("P50",):
                    for rid in self._wikidata_claim_ids(claims, prop):
                        if rid not in seen_related:
                            seen_related.add(rid)
                            related_ids.append(rid)

            label_map: dict[str, str] = {}
            if related_ids:
                self._check_abort("wikidata")
                label_params = {
                    "action": "wbgetentities",
                    "ids": "|".join(related_ids[:50]),
                    "props": "labels",
                    "languages": "en",
                    "format": "json",
                }
                label_url = (
                    f"{self.wikidata_api_url}?"
                    f"{urllib.parse.urlencode(label_params)}"
                )
                label_data = _http_get_json(
                    label_url,
                    timeout=TIMEOUT_DETAIL,
                    source="wikidata",
                    budget=self._active_budget,
                )
                for rid, ent in (label_data.get("entities") or {}).items():
                    labels = (ent or {}).get("labels") or {}
                    value = (labels.get("en") or {}).get("value") or ""
                    if value:
                        label_map[rid] = value

            best_metadata = None
            best_title_score = -1.0
            for qid in candidate_ids:
                entity = entities.get(qid) or {}
                if not entity or entity.get("missing") is not None:
                    continue
                labels = entity.get("labels") or {}
                book_label = (labels.get("en") or {}).get("value") or ""
                if not book_label:
                    continue
                claims = entity.get("claims") or {}
                author_ids = self._wikidata_claim_ids(claims, "P50")
                author_label = label_map.get(author_ids[0], "") if author_ids else ""
                metadata = {
                    "title": book_label,
                    "author": author_label,
                    "source": "WikiData",
                }
                if not self._metadata_matches_db(
                    title,
                    db_author,
                    metadata,
                    require_author_match=require_author_match,
                ):
                    continue
                title_score = self._best_title_word_match_score(
                    title, metadata.get("title", ""), db_author
                )
                if title_score > best_title_score:
                    best_title_score = title_score
                    best_metadata = metadata

            if best_metadata:
                return best_metadata
            return None
        except FetchAborted:
            raise
        except SourceCooldownError:
            if propagate_fatal_errors:
                raise
            return None
        except urllib.error.HTTPError as exc:
            if isinstance(exc, SourceCooldownError):
                if propagate_fatal_errors:
                    raise
                return None
            if propagate_fatal_errors and exc.code in _FATAL_HTTP_CODES:
                raise
            return None
        except Exception:
            return None

    def _wikidata_claim_ids(self, claims: dict, property_id: str) -> list[str]:
        """Return entity Q-ids from a Wikidata claim property."""
        ids: list[str] = []
        for statement in claims.get(property_id) or []:
            try:
                mainsnak = statement.get("mainsnak") or {}
                datavalue = mainsnak.get("datavalue") or {}
                value = datavalue.get("value") or {}
                qid = value.get("id")
                if qid:
                    ids.append(str(qid))
            except Exception:
                continue
        return ids

    def _strip_series_number(self, title: str) -> tuple[str, str]:
        """Strip series number from title and return (clean_title, series_number)."""
        return split_series_number(title)

    def _clean_text_field(self, text: str) -> str:
        """Clean text field: remove extra spaces, special chars, capitalize properly."""
        if not text:
            return ""

        # Convert multiple spaces to single space and trim
        text = re.sub(r"\s+", " ", text.strip())

        # Remove non-alphanumeric characters from start
        text = re.sub(r"^[^a-zA-Z0-9]+", "", text)

        # Remove special characters (keep basic punctuation)
        text = re.sub(r'[^\w\s\-\.,:;\'"!?()]', " ", text)

        # Clean up any extra spaces again
        text = re.sub(r"\s+", " ", text.strip())

        return text

    def _is_redundant_plot(self, plot: str) -> bool:
        """Formerly rejected series-label plots; always False now that series is unused."""
        return False

    def _apply_title_transformations(self, title: str) -> str:
        """Apply title transformations: strip series, clean (no article move)."""
        clean_title, series_number = self._strip_series_number(title)
        clean_title = self._clean_text_field(clean_title)
        if series_number:
            clean_title = f"{clean_title} - {series_number}"
        return clean_title

    def _apply_author_transformations(self, author: str) -> str:
        """Apply author transformations: clean only (no flipping)."""
        if not author:
            return ""
        return self._clean_text_field(author)

    def clean_web_data_for_storage(self, web_data: Dict) -> Dict:
        """Clean web data before storing in the database.

        Web fetch does not apply import title/author formatting preferences.
        """
        if not web_data:
            return web_data

        cleaned_data = web_data.copy()

        if "title" in cleaned_data:
            cleaned_data["title"] = self._apply_title_transformations(
                cleaned_data["title"]
            )

        if "author" in cleaned_data:
            cleaned_data["author"] = self._apply_author_transformations(
                cleaned_data["author"]
            )

        for field in ["publisher", "genre", "plot"]:
            if field in cleaned_data:
                cleaned_data[field] = self._clean_text_field(cleaned_data[field])

        plot = self._clean_plot_text(cleaned_data.get("plot", ""))
        if plot and (
            not self._plot_is_adequate(plot) or self._is_stub_plot(plot)
        ):
            cleaned_data.pop("plot", None)
            cleaned_data.pop("plot_source", None)

        cleaned_candidates = []
        for candidate in cleaned_data.get("plot_candidates") or []:
            if not isinstance(candidate, dict):
                continue
            candidate = dict(candidate)
            candidate_plot = self._clean_plot_text(candidate.get("text", ""))
            if (
                not self._plot_is_adequate(candidate_plot)
                or self._is_stub_plot(candidate_plot)
            ):
                continue
            candidate["text"] = candidate_plot
            cleaned_candidates.append(candidate)
        if cleaned_candidates:
            cleaned_data["plot_candidates"] = cleaned_candidates
        else:
            cleaned_data.pop("plot_candidates", None)

        # Drop series keys so legacy disk-cache entries cannot resurface in the UI.
        cleaned_data.pop("series", None)
        cleaned_data.pop("series_number", None)

        return cleaned_data


def clean_web_data(web_data: dict) -> dict:
    """Module-level convenience wrapper for WebBookAPI.clean_web_data_for_storage."""
    return get_web_api().clean_web_data_for_storage(web_data)


def normalize_title(title: str) -> str:
    """Normalize a title for search/comparison.

    Moves trailing articles ('Title, The' -> 'The Title'), trims, lowercases,
    and removes embedded spaces.  Shared between WebBookAPI matching logic
    and WebMetadataWindow field comparison.
    """
    if not title:
        return ""
    t = title.strip()
    match = re.match(r"^(.*?)[,\s]+(the|a|an)$", t, re.IGNORECASE)
    if match:
        base = match.group(1).strip()
        article = match.group(2).lower()
        t = f"{article} {base}"
    return "".join(t.lower().split())
