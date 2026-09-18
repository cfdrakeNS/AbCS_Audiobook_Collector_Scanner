"""HTTP helpers, fetch budget, and rate-limit cooldowns for web metadata."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from src.build_config import APP_VERSION

TIMEOUT_SEARCH = 10
TIMEOUT_DETAIL = 6

FETCH_BUDGET_SECONDS = 45.0
FETCH_BUDGET_MAX_REQUESTS = 12
FETCH_BUDGET_MAX_GOOGLE = 2
FETCH_BUDGET_MAX_WIKIDATA = 4

_USER_AGENT_CONTACT = (
    "https://github.com/cfdrakeNS/AbCS_Audiobook_Collector_Scanner"
)
USER_AGENT = f"AbCS/{APP_VERSION} (+{_USER_AGENT_CONTACT})"

GOOGLE_BOOKS_API_KEY_ENV = "ABCS_GOOGLE_BOOKS_API_KEY"
GOOGLE_BOOKS_API_KEY_SETTING = "web/google_books_api_key"

_SOURCE_PROGRESS_LABELS = {
    "open_library": (1, "Open Library"),
    "google_books": (2, "Google Books"),
    "wikidata": (3, "WikiData"),
}

_FATAL_HTTP_CODES = frozenset({429, 500, 502, 503})
_RETRYABLE_HTTP_CODES = frozenset({503})

RATE_LIMIT_COOLDOWN_SECONDS = 45
RATE_LIMIT_COOLDOWN_DEFAULTS = {
    "google_books": 15 * 60,
    "wikidata": 5 * 60,
    "wikipedia": 5 * 60,
    "open_library": 60,
}
SERVICE_UNAVAILABLE_RETRY_DELAY_SECONDS = 2.0
RATE_LIMIT_RETRY_DELAY_SECONDS = SERVICE_UNAVAILABLE_RETRY_DELAY_SECONDS

_source_cooldown_until: dict[str, float] = {}
_cooldown_persist_warned = False


def _resolve_web_cache_file() -> str:
    """Writable cache path: user data dir when frozen, project data/ in dev."""
    if getattr(sys, "frozen", False):
        from src.app_paths import get_user_data_dir

        return str(get_user_data_dir() / "web_cache.json")
    project_root = Path(__file__).resolve().parents[2]
    return str(project_root / "data" / "web_cache.json")


WEB_CACHE_FILE = _resolve_web_cache_file()


def _cooldown_state_path() -> Path:
    return Path(WEB_CACHE_FILE).with_name("web_source_cooldowns.json")


def _default_cooldown_seconds(source: str) -> float:
    return float(
        RATE_LIMIT_COOLDOWN_DEFAULTS.get(source, RATE_LIMIT_COOLDOWN_SECONDS)
    )


def _load_persisted_cooldowns() -> None:
    path = _cooldown_state_path()
    try:
        if not path.exists():
            return
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return
        now = time.time()
        for source, until in raw.items():
            try:
                until_f = float(until)
            except (TypeError, ValueError):
                continue
            if until_f > now:
                previous = _source_cooldown_until.get(str(source), 0.0)
                if until_f > previous:
                    _source_cooldown_until[str(source)] = until_f
    except Exception:
        pass


def _save_persisted_cooldowns() -> None:
    global _cooldown_persist_warned
    path = _cooldown_state_path()
    try:
        now = time.time()
        active = {
            source: until
            for source, until in _source_cooldown_until.items()
            if until > now
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(active, handle, separators=(",", ":"))
            os.replace(tmp_path, path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
    except Exception as exc:
        if not _cooldown_persist_warned:
            print(
                f"[AbCS] Warning: could not persist web source cooldowns "
                f"({path}): {exc}",
                file=sys.stderr,
            )
            _cooldown_persist_warned = True


def get_google_books_api_key() -> str:
    env_key = (os.environ.get(GOOGLE_BOOKS_API_KEY_ENV) or "").strip()
    if env_key:
        return env_key
    try:
        from src.utils.settings_helpers import read_setting

        stored = read_setting(GOOGLE_BOOKS_API_KEY_SETTING, "", type=str)
        return (stored or "").strip()
    except Exception:
        return ""


class FetchBudget:
    """Wall-clock and request budget for one get_book_metadata call."""

    def __init__(
        self,
        *,
        seconds: float = FETCH_BUDGET_SECONDS,
        max_requests: int = FETCH_BUDGET_MAX_REQUESTS,
        max_google: int = FETCH_BUDGET_MAX_GOOGLE,
        max_wikidata: int = FETCH_BUDGET_MAX_WIKIDATA,
    ) -> None:
        self.deadline = time.time() + max(0.0, float(seconds))
        self.max_requests = max(0, int(max_requests))
        self.max_google = max(0, int(max_google))
        self.max_wikidata = max(0, int(max_wikidata))
        self.request_count = 0
        self.google_count = 0
        self.wikidata_count = 0
        self.exhausted = False

    def remaining_seconds(self) -> float:
        return max(0.0, self.deadline - time.time())

    def can_continue(self, source: str | None = None) -> bool:
        if self.exhausted:
            return False
        if self.request_count >= self.max_requests:
            self.exhausted = True
            return False
        if time.time() >= self.deadline:
            self.exhausted = True
            return False
        if source == "google_books" and self.google_count >= self.max_google:
            return False
        if source == "wikidata" and self.wikidata_count >= self.max_wikidata:
            return False
        return True

    def note_request(self, source: str | None = None) -> None:
        self.request_count += 1
        if source == "google_books":
            self.google_count += 1
        elif source == "wikidata":
            self.wikidata_count += 1
        if self.request_count >= self.max_requests or time.time() >= self.deadline:
            self.exhausted = True


class FetchAborted(Exception):
    """Raised when the user cancels or the fetch budget is exhausted mid-cascade."""

    def __init__(self, reason: str = "canceled") -> None:
        self.reason = reason
        super().__init__(reason)


class SourceCooldownError(urllib.error.HTTPError):
    """Synthetic 429 for a source still in cooldown — must not extend the cooldown."""

    def __init__(self, source: str, remaining: int, url: str) -> None:
        self.source = source
        self.remaining = remaining
        super().__init__(
            f"{url} (cooldown {remaining}s)",
            429,
            "Too Many Requests",
            {},
            None,
        )


def _parse_retry_after_seconds(
    headers, default: float = RATE_LIMIT_COOLDOWN_SECONDS
) -> float:
    if headers is None:
        return float(default)
    raw = None
    try:
        raw = headers.get("Retry-After") or headers.get("retry-after")
    except Exception:
        raw = None
    if not raw:
        return float(default)
    try:
        return max(1.0, float(str(raw).strip()))
    except (TypeError, ValueError):
        return float(default)


def _is_rate_limit_http_code(source: str, code: int) -> bool:
    if code == 429:
        return True
    if code == 403 and source == "google_books":
        return True
    return False


def _note_rate_limited(
    source: str,
    seconds: float | None = None,
    *,
    headers=None,
) -> None:
    default = _default_cooldown_seconds(source)
    if seconds is None:
        seconds = default
    if headers is not None:
        parsed = _parse_retry_after_seconds(headers, default=default)
        seconds = max(float(default), float(parsed))
    until = time.time() + max(0.0, float(seconds))
    previous = _source_cooldown_until.get(source, 0.0)
    if until > previous:
        _source_cooldown_until[source] = until
        _save_persisted_cooldowns()


def _seconds_until_cooldown_clears(source: str) -> float:
    until = _source_cooldown_until.get(source, 0.0)
    remaining = until - time.time()
    if remaining <= 0:
        if source in _source_cooldown_until:
            _source_cooldown_until.pop(source, None)
            _save_persisted_cooldowns()
        return 0.0
    return remaining


def _is_source_cooling_down(source: str) -> bool:
    return _seconds_until_cooldown_clears(source) > 0


def _clear_source_cooldown(source: str | None = None) -> None:
    if source is None:
        _source_cooldown_until.clear()
    else:
        _source_cooldown_until.pop(source, None)
    _save_persisted_cooldowns()


def _raise_cooldown_http_error(source: str = "google_books") -> None:
    remaining = max(1, int(round(_seconds_until_cooldown_clears(source))))
    urls = {
        "google_books": "https://www.googleapis.com/books/v1/volumes",
        "open_library": "https://openlibrary.org/search.json",
        "wikidata": "https://www.wikidata.org/w/api.php",
        "wikipedia": "https://en.wikipedia.org/w/api.php",
    }
    base = urls.get(source, urls["google_books"])
    raise SourceCooldownError(source, remaining, base)


def _urlopen_with_retry(req, timeout: float, *, source: str = "google_books"):
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as exc:
        if isinstance(exc, SourceCooldownError):
            raise
        if _is_rate_limit_http_code(source, exc.code):
            raise
        if exc.code not in _RETRYABLE_HTTP_CODES:
            raise
        _note_rate_limited(source, headers=getattr(exc, "headers", None))
        time.sleep(SERVICE_UNAVAILABLE_RETRY_DELAY_SECONDS)
        try:
            return urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.HTTPError as retry_exc:
            if isinstance(retry_exc, SourceCooldownError):
                raise
            if (
                retry_exc.code in _FATAL_HTTP_CODES
                or _is_rate_limit_http_code(source, retry_exc.code)
            ):
                _note_rate_limited(
                    source, headers=getattr(retry_exc, "headers", None)
                )
            raise


def _http_get_json(
    url: str,
    *,
    timeout: float,
    source: str,
    budget: FetchBudget | None = None,
    extra_headers: dict | None = None,
    accept: str | None = None,
) -> dict:
    """GET JSON with shared User-Agent, retry/cooldown, and optional budget count."""
    if budget is not None and not budget.can_continue(source):
        raise FetchAborted("budget")
    if _is_source_cooling_down(source):
        _raise_cooldown_http_error(source)

    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    if accept:
        req.add_header("Accept", accept)
    if extra_headers:
        for key, value in extra_headers.items():
            req.add_header(key, value)

    if budget is not None:
        budget.note_request(source)

    try:
        with _urlopen_with_retry(req, timeout, source=source) as response:
            raw = response.read().decode("utf-8")
    except SourceCooldownError:
        raise
    except urllib.error.HTTPError as exc:
        if (
            exc.code in _FATAL_HTTP_CODES
            or _is_rate_limit_http_code(source, exc.code)
        ):
            _note_rate_limited(source, headers=getattr(exc, "headers", None))
        raise

    if not raw.strip():
        return {}
    if not raw.strip().startswith(("{", "[")):
        return {}
    return json.loads(raw)


def _reraise_if_fatal_http_error(exc: urllib.error.HTTPError) -> None:
    if isinstance(exc, SourceCooldownError):
        raise exc
    if exc.code in _FATAL_HTTP_CODES:
        raise exc


def _dedupe_fetch_errors(errors: list[str]) -> list[str]:
    seen_sources: set[str] = set()
    unique: list[str] = []
    for err in errors:
        source_key = str(err).split(":", 1)[0].strip().lower()
        if source_key in seen_sources:
            continue
        seen_sources.add(source_key)
        unique.append(str(err))
    return unique


def format_web_fetch_status_message(fetch_errors: list) -> str:
    fetch_errors = _dedupe_fetch_errors(list(fetch_errors or []))
    if not fetch_errors:
        return "Web fetch failed: unable to reach web sources."
    first = str(fetch_errors[0])
    lowered = first.lower()
    if (
        "429" in first
        or "too many requests" in lowered
        or "403" in first
        or "rate limit" in lowered
        or "quota" in lowered
    ):
        remaining = _seconds_until_cooldown_clears("google_books")
        if remaining <= 0:
            for source in ("wikidata", "wikipedia", "open_library"):
                remaining = _seconds_until_cooldown_clears(source)
                if remaining > 0:
                    break
        if remaining > 0:
            if remaining >= 60:
                minutes = max(1, int(round(remaining / 60.0)))
                return (
                    f"Web source rate limited. Try again in about {minutes} "
                    f"minute{'s' if minutes != 1 else ''}."
                )
            seconds = max(1, int(round(remaining)))
            return f"Web source rate limited. Try again in about {seconds}s."
        return "Web source rate limited. Try again later."
    if "open_library" in lowered:
        return f"Open Library unavailable. {first.split(':', 1)[-1].strip()}"
    if "google_books" in lowered:
        return f"Google Books unavailable. {first.split(':', 1)[-1].strip()}"
    if "wikidata" in lowered:
        return f"WikiData unavailable. {first.split(':', 1)[-1].strip()}"
    return f"Web fetch failed: {first}"


def format_web_fetch_dialog_text(fetch_errors: list) -> str:
    fetch_errors = _dedupe_fetch_errors(list(fetch_errors or []))
    status = format_web_fetch_status_message(fetch_errors)
    lines = [status, ""]
    if fetch_errors:
        lines.append("Details:")
        for err in fetch_errors[:3]:
            lines.append(f"  • {err}")
        lines.append("")
    lines.append(
        "The web details window only opens when data is found. "
        "Wait for the cooldown, then press Alt+W again on this book."
    )
    return "\n".join(lines)


def _source_progress_message(source_key: str, *, phase: str = "primary") -> str:
    step, name = _SOURCE_PROGRESS_LABELS[source_key]
    if phase == "primary":
        return f"Trying source {step}: {name}…"
    if phase == "broadened":
        return f"Broadened search, {name}…"
    if phase == "title_only":
        return f"Title-only search, {name}…"
    return f"Trying {name}…"
