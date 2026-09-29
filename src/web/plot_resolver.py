"""Internal plot candidates, validation, ranking, and fetch diagnostics."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
import time
from typing import Callable, Mapping


PLOT_MIN_LENGTH = 80
HTML_TAG_RE = re.compile(r"<[^>]+>")


@dataclass
class PlotCandidate:
    """One source-owned description considered for the selected book."""

    text: str
    source: str
    identifiers: dict[str, str] = field(default_factory=dict)
    match_confidence: str = "low"
    query_type: str = ""
    elapsed_seconds: float = 0.0
    cache_state: str = "network"
    source_url: str = ""
    fetched_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    license_id: str = ""
    modified: bool = False
    normalized_text: str = ""
    rejection_reason: str = ""

    @property
    def identity_rank(self) -> int:
        return {
            "identifier": 3,
            "title_author": 2,
            "title": 1,
            "low": 0,
            "existing": 2,
        }.get(self.match_confidence, 0)

    @property
    def auto_apply(self) -> bool:
        return self.identity_rank >= 2

    def diagnostic_record(self) -> dict:
        """Return trace data without duplicating the fetched description text."""
        return {
            "source": self.source,
            "identifiers": dict(self.identifiers),
            "match_confidence": self.match_confidence,
            "auto_apply": self.auto_apply,
            "query_type": self.query_type,
            "elapsed_seconds": round(max(0.0, self.elapsed_seconds), 4),
            "cache_state": self.cache_state,
            "source_url": self.source_url,
            "fetched_at": self.fetched_at,
            "license_id": self.license_id,
            "modified": self.modified,
            "text_length": len(self.normalized_text),
            "accepted": not bool(self.rejection_reason),
            "rejection_reason": self.rejection_reason,
        }


def candidate_provenance(metadata: Mapping | None) -> dict[str, str]:
    """Extract optional provenance fields carried by source adapters."""
    if not metadata:
        return {}
    provenance: dict[str, str] = {}
    for key in ("plot_source_url", "plot_license_id"):
        value = metadata.get(key)
        if value:
            provenance[key] = str(value)
    return provenance


@dataclass
class PlotFetchDiagnostics:
    """Per-fetch baseline measurements used by Phase 31 tests and tuning."""

    title: str
    author: str
    started_at: float = field(default_factory=time.monotonic)
    candidates: list[dict] = field(default_factory=list)
    selected_source: str = ""
    request_count: int = 0
    elapsed_seconds: float = 0.0

    def record(self, candidate: PlotCandidate) -> None:
        self.candidates.append(candidate.diagnostic_record())

    def select(self, candidate: PlotCandidate) -> None:
        self.selected_source = candidate.source

    def finish(self, request_count: int = 0) -> None:
        self.request_count = max(0, int(request_count))
        self.elapsed_seconds = round(max(0.0, time.monotonic() - self.started_at), 4)

    def snapshot(self) -> dict:
        return {
            "title": self.title,
            "author": self.author,
            "selected_source": self.selected_source,
            "request_count": self.request_count,
            "elapsed_seconds": self.elapsed_seconds,
            "candidates": [dict(item) for item in self.candidates],
        }


class PlotResolver:
    """Normalize, validate, and deterministically rank plot candidates."""

    _SOURCE_RANK = {
        "open_library": 3,
        "google_books": 2,
        "wikipedia": 1,
    }
    _SOURCE_ORDER = {
        "open_library": 0,
        "google_books": 1,
        "wikipedia": 2,
    }

    _NON_BOOK_PATTERNS = tuple(
        re.compile(pattern)
        for pattern in (
            r"\bis a song\b",
            r"\bis an album\b",
            r"\bstudio album\b",
            r"\breleased as a single\b",
            r"\bbillboard\b",
            r"\bmainstream rock\b",
            r"\brock band\b",
            r"\bhit single\b",
            r"\bgrammy\b",
            r"\btelevision series\b",
            r"\btv series\b",
            r"\b(episode|episodes) of\b",
            r"\bseason \d+\b",
            r"\bchart\b.{0,40}\b(position|successful|reached|peaked)\b",
        )
    )
    _STUB_PATTERNS = tuple(
        re.compile(pattern)
        for pattern in (
            r"^no metadata\b",
            r"\bno metadata\b.{0,40}\b(return|returned|available|found|provided)\b",
            r"\bmetadata (not |never )?(return|returned|available|found)\b",
            r"^no description\b",
            r"\bdescription not available\b",
            r"^no information (found|available|returned)\b",
            r"^not available\.?$",
            r"^n/?a\.?$",
        )
    )
    _BOOK_TERMS = re.compile(
        r"\b(novel|book|novella|short story|collection|memoir|thriller|mystery)\b",
        re.IGNORECASE,
    )

    def __init__(self, min_length: int = PLOT_MIN_LENGTH):
        self.min_length = max(0, int(min_length))

    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        cleaned = HTML_TAG_RE.sub(" ", text.strip())
        return re.sub(r"\s+", " ", cleaned).strip()

    def is_adequate(self, text: str) -> bool:
        return len((text or "").strip()) >= self.min_length

    def is_non_book(self, text: str) -> bool:
        lowered = (text or "").lower()
        return any(pattern.search(lowered) for pattern in self._NON_BOOK_PATTERNS)

    def is_stub(self, text: str) -> bool:
        normalized = re.sub(r"\s+", " ", (text or "").strip().lower())
        if not normalized:
            return True
        return any(pattern.search(normalized) for pattern in self._STUB_PATTERNS)

    def evaluate(
        self,
        candidate: PlotCandidate,
        *,
        db_author: str,
        author_matches: Callable[[str, str], bool],
        redundant: bool = False,
    ) -> PlotCandidate:
        """Apply existing acceptance rules and annotate the candidate in place."""
        candidate.normalized_text = self.normalize_text(candidate.text)
        candidate.modified = candidate.normalized_text != (candidate.text or "").strip()

        if not self.is_adequate(candidate.normalized_text):
            candidate.rejection_reason = "too_short"
        elif redundant:
            candidate.rejection_reason = "redundant"
        elif self.is_non_book(candidate.normalized_text):
            candidate.rejection_reason = "non_book"
        elif self.is_stub(candidate.normalized_text):
            candidate.rejection_reason = "stub"
        elif (
            db_author
            and candidate.source == "wikipedia"
            and not author_matches(db_author, candidate.normalized_text)
            and not self._BOOK_TERMS.search(candidate.normalized_text)
        ):
            candidate.rejection_reason = "unrelated"
        else:
            candidate.rejection_reason = ""
        return candidate

    def rank(self, candidates: list[PlotCandidate]) -> list[PlotCandidate]:
        """Return accepted candidates ordered by identity, source, and quality."""
        accepted = [candidate for candidate in candidates if not candidate.rejection_reason]
        return sorted(
            accepted,
            key=lambda candidate: (
                candidate.identity_rank,
                self._SOURCE_RANK.get(candidate.source, 0),
                min(len(candidate.normalized_text), 2000),
                -self._SOURCE_ORDER.get(candidate.source, len(self._SOURCE_ORDER)),
            ),
            reverse=True,
        )

    def choose(self, candidates: list[PlotCandidate]) -> PlotCandidate | None:
        """Choose the highest-ranked accepted candidate, if any."""
        ranked = self.rank(candidates)
        return ranked[0] if ranked else None


def candidate_identifiers(metadata: Mapping | None) -> dict[str, str]:
    """Extract stable identifiers from the current metadata representation."""
    if not metadata:
        return {}
    identifiers: dict[str, str] = {}
    nested = metadata.get("identifiers")
    if isinstance(nested, Mapping):
        for key, value in nested.items():
            if value:
                identifiers[str(key)] = str(value)
    for key in ("isbn", "google_id", "open_library_work_key", "wikidata_id"):
        value = metadata.get(key)
        if value:
            identifiers[key] = str(value)
    return identifiers


__all__ = [
    "PLOT_MIN_LENGTH",
    "PlotCandidate",
    "PlotFetchDiagnostics",
    "PlotResolver",
    "candidate_identifiers",
    "candidate_provenance",
]
