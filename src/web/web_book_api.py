"""
Web Book API - Audio Book Collection
Fetches book metadata from Open Library, Google Books, and WikiData APIs (in that order).
"""

import json
import os
import urllib.request
import urllib.parse
import re
import time
from typing import Callable, Optional, Dict, List

# Common stopwords to ignore in title matching
STOPWORDS = {"the", "a", "an", "and", "or", "of", "in", "on", "to", "for"}

# Plot enrichment: treat shorter text as needing a better source
PLOT_MIN_LENGTH = 80
PLOT_MAX_WIKIPEDIA_SENTENCES = 20
HTML_TAG_RE = re.compile(r"<[^>]+>")

# Persistent cache file (JSON) in the app data folder
WEB_CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "web_cache.json")
WEB_CACHE_MAX_ENTRIES = 200

# Network timeout constants (seconds)
TIMEOUT_SEARCH = 10    # primary title/author searches
TIMEOUT_DETAIL = 6     # secondary calls (work description, extract)

# Leading honorifics to strip from author search (Sir Arthur Conan Doyle -> Arthur Conan Doyle)
AUTHOR_HONORIFIC_PREFIX = re.compile(
    r"^(?:sir|dame|dr\.?|prof\.?|mr\.?|mrs\.?|ms\.?|lord|lady)\s+",
    re.IGNORECASE,
)

# Fixed display order for fetch-progress messages (1=OL, 2=Google, 3=WikiData).
_SOURCE_PROGRESS_LABELS = {
    "open_library": (1, "Open Library"),
    "google_books": (2, "Google Books"),
    "wikidata": (3, "WikiData"),
}


def _source_progress_message(source_key: str, *, phase: str = "primary") -> str:
    """Human-readable progress text for the metadata source cascade."""
    step, name = _SOURCE_PROGRESS_LABELS[source_key]
    if phase == "primary":
        return f"Trying source {step}: {name}…"
    if phase == "broadened":
        return f"Broadened search, {name}…"
    if phase == "title_only":
        return f"Title-only search, {name}…"
    return f"Trying {name}…"


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

    def _title_matches(self, db_title: str, web_title: str) -> bool:
        """Check if at least 50% of DB title words appear in web title."""
        return self._title_word_match_score(db_title, web_title) >= 0.5

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
        if not self._title_matches(db_title, web_title):
            return False
        if not require_author_match:
            return True
        if not self._author_matches(db_author, metadata.get("author", "")):
            return False
        return True


    @staticmethod
    def _plot_is_adequate(plot: str) -> bool:
        return len((plot or "").strip()) >= PLOT_MIN_LENGTH

    @staticmethod
    def _strip_html(text: str) -> str:
        if not text:
            return ""
        cleaned = HTML_TAG_RE.sub(" ", text)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    def _clean_plot_text(self, plot: str) -> str:
        return self._strip_html((plot or "").strip())

    def _apply_plot_to_metadata(
        self,
        metadata: Dict,
        plot: str,
        plot_source: str,
        db_title: str,
        db_author: str,
    ) -> bool:
        """Set plot on metadata when text is long enough and not a series label."""
        plot = self._clean_plot_text(plot)
        if not self._plot_is_adequate(plot):
            return False
        if self._is_redundant_plot(plot, metadata.get("series", "")):
            return False
        metadata["plot"] = plot
        metadata["plot_source"] = plot_source
        return True

    def _enrich_metadata_plot(
        self,
        metadata: Dict,
        db_title: str,
        db_author: str,
    ) -> None:
        """Fill plot after metadata match: Open Library work, Wikipedia, then Google text."""
        if not metadata:
            return

        existing = self._clean_plot_text(metadata.get("plot", ""))
        if self._plot_is_adequate(existing):
            source = metadata.get("source") or metadata.get("_resolved_source", "")
            metadata["plot"] = existing
            metadata["plot_source"] = metadata.get("plot_source") or source
            return

        work_key = metadata.get("open_library_work_key", "")
        if work_key:
            ol_plot = self._clean_plot_text(
                self._get_open_library_work_fields(work_key).get("description", "")
            )
            if self._apply_plot_to_metadata(
                metadata, ol_plot, "open_library", db_title, db_author
            ):
                return
        elif metadata.get("_resolved_source") != "open_library":
            # No work key (Google/WikiData win): try a loose OL search for description
            fallback_plot = self._clean_plot_text(
                self._fetch_plot_from_open_library(
                    db_title or metadata.get("title", ""), db_author
                )
            )
            if self._apply_plot_to_metadata(
                metadata, fallback_plot, "open_library", db_title, db_author
            ):
                return

        wiki_title = metadata.get("title") or db_title
        wiki_author = db_author or metadata.get("author", "")

        if wiki_title:
            rest_plot = self._clean_plot_text(
                self._fetch_wikipedia_rest_summary(wiki_title)
            )
            if self._apply_plot_to_metadata(
                metadata, rest_plot, "wikipedia", db_title, db_author
            ):
                return

        wiki_plot = self._fetch_plot_from_wikipedia(
            wiki_title,
            wiki_author,
            db_title=db_title,
            db_author=db_author,
        )
        if self._apply_plot_to_metadata(
            metadata, wiki_plot, "wikipedia", db_title, db_author
        ):
            return

        discovered_isbn = metadata.get("isbn", "")
        if discovered_isbn and not self._plot_is_adequate(
            self._clean_plot_text(metadata.get("plot", ""))
        ):
            gb_hit = self._fetch_google_by_isbn(discovered_isbn)
            if gb_hit and self._apply_plot_to_metadata(
                metadata,
                gb_hit.get("plot", ""),
                "google_books",
                db_title,
                db_author,
            ):
                return

        google_plot = self._clean_plot_text(metadata.get("plot", ""))
        if self._plot_is_adequate(google_plot):
            self._apply_plot_to_metadata(
                metadata,
                google_plot,
                "google_books",
                db_title,
                db_author,
            )

    def _parse_open_library_series_string(self, raw: str) -> tuple[str, str]:
        """Split an Open Library series string into name and optional number."""
        if not raw:
            return "", ""
        text = re.sub(r"\s+", " ", str(raw).strip())
        patterns = [
            r"^(.+?)\s*#\s*(\d+)\s*$",
            r"^(.+?),\s*Book\s+(\d+)\s*$",
            r"^(.+?)\s+Book\s+(\d+)\s*$",
        ]
        for pattern in patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip(), match.group(2).strip()
        return text, ""

    def _apply_series_to_metadata(
        self,
        metadata: Dict,
        series: str,
        series_number: str = "",
        *,
        db_title: str = "",
        db_plot: str = "",
    ) -> bool:
        """Set series fields on metadata when values look valid. Does not overwrite."""
        if not metadata:
            return False
        changed = False
        plot_ref = db_plot or metadata.get("plot", "")
        title_ref = db_title or metadata.get("title", "")

        cleaned_series = self._clean_text_field(series or "")
        if cleaned_series and not metadata.get("series"):
            if not self._is_unlikely_series_name(
                cleaned_series, title=title_ref, plot=plot_ref
            ):
                metadata["series"] = cleaned_series
                changed = True

        sn = str(series_number or "").strip()
        if sn and not metadata.get("series_number"):
            sn_digits = re.sub(r"[^\d]", "", sn)
            if sn_digits:
                metadata["series_number"] = sn_digits
                changed = True
        return changed

    def _infer_series_name_from_author(self, author: str) -> str:
        """Best-effort series name when the DB title carries a volume number only."""
        norm = self._normalize_person_name(author)
        if not norm:
            return ""
        if "child" in norm and (
            "lee" in norm or "andrew" in norm or norm.startswith("child ")
        ):
            return "Jack Reacher"
        return ""

    def _seed_series_from_db_title(
        self,
        metadata: Dict,
        title_series_number: str,
        author: str,
    ) -> bool:
        """Apply series number (and known author heuristics) from the library title."""
        if not metadata:
            return False
        changed = False
        sn_digits = re.sub(r"[^\d]", "", str(title_series_number or ""))
        if sn_digits and not metadata.get("series_number"):
            metadata["series_number"] = sn_digits
            changed = True
        if not metadata.get("series") and sn_digits:
            inferred = self._infer_series_name_from_author(author)
            if inferred and not self._is_unlikely_series_name(
                inferred,
                title=metadata.get("title", ""),
                plot=metadata.get("plot", ""),
            ):
                metadata["series"] = inferred
                changed = True
        return changed

    @staticmethod
    def _format_series_found_message(metadata: Dict) -> str:
        """Short status text when series fields were resolved (for screen readers)."""
        parts: list[str] = []
        if metadata.get("series"):
            parts.append(str(metadata["series"]))
        if metadata.get("series_number"):
            parts.append(f"book {metadata['series_number']}")
        if not parts:
            return ""
        return f"Series found: {'; '.join(parts)}"

    def _fill_series_fields(
        self,
        metadata: Dict,
        db_title: str,
        db_author: str,
        title_series_number: str = "",
        *,
        report_progress=None,
    ) -> bool:
        """Resolve series name/number; only announce when something was found."""
        if not metadata:
            return False
        before = (metadata.get("series"), metadata.get("series_number"))
        self._seed_series_from_db_title(metadata, title_series_number, db_author)
        self._enrich_metadata_series(metadata, db_title, db_author)
        self._seed_series_from_db_title(metadata, title_series_number, db_author)
        after = (metadata.get("series"), metadata.get("series_number"))
        if after != before and (after[0] or after[1]) and report_progress:
            msg = self._format_series_found_message(metadata)
            if msg:
                report_progress(msg)
        return after != before

    def _enrich_metadata_series(
        self,
        metadata: Dict,
        db_title: str,
        db_author: str,
    ) -> bool:
        """Fill series after primary match: Open Library work, Google, then WikiData."""
        if not metadata:
            return False
        if metadata.get("series") and metadata.get("series_number"):
            return False

        changed = False
        work_key = metadata.get("open_library_work_key", "")
        if not metadata.get("series") and work_key:
            work_fields = self._get_open_library_work_fields(work_key)
            if self._apply_series_to_metadata(
                metadata,
                work_fields.get("series", ""),
                work_fields.get("series_number", ""),
                db_title=db_title,
                db_plot=metadata.get("plot", ""),
            ):
                changed = True

        if not metadata.get("series") and metadata.get("_resolved_source") != "wikidata":
            wiki_hit = self._fetch_series_from_wikidata(
                db_title or metadata.get("title", ""),
                db_author or metadata.get("author", ""),
            )
            if wiki_hit and self._apply_series_to_metadata(
                metadata,
                wiki_hit.get("series", ""),
                wiki_hit.get("series_number", ""),
                db_title=db_title,
                db_plot=metadata.get("plot", ""),
            ):
                changed = True

        discovered_isbn = metadata.get("isbn", "")
        if not metadata.get("series") and discovered_isbn:
            gb_isbn_hit = self._fetch_series_from_google_by_isbn(discovered_isbn)
            if gb_isbn_hit and self._apply_series_to_metadata(
                metadata,
                gb_isbn_hit.get("series", ""),
                gb_isbn_hit.get("series_number", ""),
                db_title=db_title,
                db_plot=metadata.get("plot", ""),
            ):
                changed = True

        if not metadata.get("series"):
            google_hit = self._fetch_series_from_google(
                db_title or metadata.get("title", ""),
                db_author or metadata.get("author", ""),
            )
            if google_hit and self._apply_series_to_metadata(
                metadata,
                google_hit.get("series", ""),
                google_hit.get("series_number", ""),
                db_title=db_title,
                db_plot=metadata.get("plot", ""),
            ):
                changed = True
        return changed

    def _fetch_series_from_google(
        self, title: str, author: str | None
    ) -> Optional[Dict]:
        """Return series fields from the best Google Books match, or None."""
        if not title:
            return None
        hit = self._fetch_from_google_books(
            title, author, require_author_match=bool(author)
        )
        if not hit:
            return None
        series = hit.get("series", "")
        series_number = hit.get("series_number", "")
        if series or series_number:
            return {"series": series, "series_number": series_number}
        return None

    def _fetch_series_from_google_by_isbn(self, isbn: str) -> Optional[Dict]:
        """Return series fields from a Google Books ISBN lookup, or None."""
        hit = self._fetch_google_by_isbn(isbn)
        if not hit:
            return None
        series = hit.get("series", "")
        series_number = hit.get("series_number", "")
        if series or series_number:
            return {"series": series, "series_number": series_number}
        return None

    def _fetch_series_from_wikidata(
        self, title: str, author: str | None
    ) -> Optional[Dict]:
        """Lightweight WikiData lookup for series name and ordinal only."""
        if not title:
            return None
        hit = self._fetch_from_wikidata(
            title, author, require_author_match=bool(author)
        )
        if not hit:
            return None
        series = hit.get("series", "")
        series_number = hit.get("series_number", "")
        if series or series_number:
            return {"series": series, "series_number": series_number}
        return None

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
        # WikiData SPARQL endpoint
        self.wikidata_url = "https://query.wikidata.org/sparql"
        # Wikipedia API for plot summaries
        self.wikipedia_url = "https://en.wikipedia.org/w/api.php"
        self._cache = {}
        self.CACHE_DURATION = 300  # seconds for in-memory TTL
        self._load_persistent_cache()

    def _load_persistent_cache(self) -> None:
        """Load the persistent cache from web_cache.json if it exists."""
        try:
            cache_path = os.path.normpath(WEB_CACHE_FILE)
            if not os.path.exists(cache_path):
                return
            with open(cache_path, encoding="utf-8") as f:
                raw = json.load(f)
            for key, entry in raw.items():
                if isinstance(entry, list) and len(entry) == 2:
                    self._cache[key] = (entry[0], entry[1])
        except Exception:
            pass  # Corrupt or missing cache is non-fatal

    def _save_persistent_cache(self) -> None:
        """Persist the in-memory cache to web_cache.json (max WEB_CACHE_MAX_ENTRIES)."""
        try:
            cache_path = os.path.normpath(WEB_CACHE_FILE)
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            entries = list(self._cache.items())
            if len(entries) > WEB_CACHE_MAX_ENTRIES:
                # Evict oldest entries by fetch timestamp
                entries.sort(key=lambda x: x[1][0] if isinstance(x[1], (list, tuple)) and len(x[1]) > 0 else 0)
                entries = entries[-WEB_CACHE_MAX_ENTRIES:]
            serialisable = {k: [v[0], v[1]] for k, v in entries}
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(serialisable, f, ensure_ascii=False, separators=(",", ":"))
        except Exception:
            pass  # Cache write failure is non-fatal

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
        try:
            params = {
                "q": f"isbn:{clean_isbn}",
                "maxResults": 1,
                "fields": (
                    "items(id,volumeInfo(title,subtitle,authors,publisher,"
                    "publishedDate,description,industryIdentifiers,categories,"
                    "averageRating,ratingsCount,seriesInfo))"
                ),
            }
            url = f"{self.google_books_url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "AudiobookCollectorScanner/1.0")
            with urllib.request.urlopen(req, timeout=TIMEOUT_DETAIL) as response:
                data = json.loads(response.read().decode("utf-8"))
            items = data.get("items") or []
            if not items:
                return None
            metadata = self._google_item_to_metadata(items[0])
            if metadata:
                metadata["isbn"] = clean_isbn
            return metadata
        except Exception:
            return None

    def _fetch_metadata_by_isbn(self, isbn: str) -> Optional[Dict]:
        """Exact ISBN lookup: Google Books first, Open Library for gaps."""
        clean_isbn = self._normalize_isbn(isbn)
        if not clean_isbn:
            return None

        gb_meta = self._fetch_google_by_isbn(clean_isbn)
        ol_meta = self._fetch_by_isbn(clean_isbn)
        if not gb_meta and not ol_meta:
            return None

        metadata: Dict = dict(ol_meta) if ol_meta else {}
        if gb_meta:
            if not metadata:
                metadata = dict(gb_meta)
            else:
                for key in ("title", "author", "year", "publisher", "rating", "ratings_count"):
                    if gb_meta.get(key) and not metadata.get(key):
                        metadata[key] = gb_meta[key]
                for key in ("plot", "series", "series_number"):
                    if gb_meta.get(key):
                        metadata[key] = gb_meta[key]
                if gb_meta.get("genre") and not metadata.get("genre"):
                    metadata["genre"] = gb_meta["genre"]
            if ol_meta and ol_meta.get("open_library_work_key"):
                metadata["open_library_work_key"] = ol_meta["open_library_work_key"]
            metadata["_resolved_source"] = "google_books"
        else:
            metadata["_resolved_source"] = "open_library"

        metadata["isbn"] = clean_isbn
        return metadata

    def _fetch_by_isbn(self, isbn: str) -> "Optional[Dict]":
        """Exact Open Library lookup by ISBN.

        Returns a metadata dict on success, or None.  ISBN lookups skip all
        title/author matching because the result is unambiguous.
        """
        if not isbn:
            return None
        try:
            clean_isbn = self._normalize_isbn(isbn)
            if not clean_isbn:
                return None
            url = f"{self.open_library_isbn_url}/{clean_isbn}.json"
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "AbCS-Audiobook-Collector/1.0")
            with urllib.request.urlopen(req, timeout=TIMEOUT_DETAIL) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            if "error" in data:
                return None

            title = data.get("title", "")
            if not title:
                return None

            # Authors are stored as keys like {"key": "/authors/OL1234A"}
            author = ""
            raw_authors = data.get("authors", [])
            if raw_authors:
                try:
                    author_key = raw_authors[0].get("key", "")
                    if author_key:
                        author_url = f"https://openlibrary.org{author_key}.json"
                        req_a = urllib.request.Request(author_url)
                        req_a.add_header("User-Agent", "AbCS-Audiobook-Collector/1.0")
                        with urllib.request.urlopen(req_a, timeout=TIMEOUT_DETAIL) as r_a:
                            author_data = json.loads(r_a.read().decode("utf-8"))
                        author = author_data.get("name", "") or author_data.get("personal_name", "")
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
            return metadata
        except Exception:
            return None

    def get_book_metadata(
        self,
        title: str,
        author: str = None,
        year: str = None,
        refresh: int = 0,
        move_articles: bool = False,
        flip_author: bool = False,
        append_series_to_title: bool = True,
        *,
        narrator: str | None = None,
        path: str | None = None,
        source: str | None = None,
        comments: str | None = None,
        search_without_author: bool = False,
        isbn: str | None = None,
        progress_callback: Callable[[str], None] | None = None,
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
            move_articles: Move 'The', 'A', 'An' to end of title for search
            flip_author: Flip author name format for search
            narrator: Reader/narrator when tagged separately from author
            path: Book folder path (Librivox detection)
            source: Book source field (Librivox detection)
            comments: Book comments (Librivox detection)
            search_without_author: Force title-only matching after author search fails
            isbn: ISBN-10 or ISBN-13 if available; tried first as an exact lookup
            progress_callback: Optional callable invoked with human-readable status text

        Returns:
            Dictionary with book metadata and source info, or None if not found
        """

        import time

        cache_key = (
            f"{title}|{author}|{refresh}|{narrator}|{path}|{source}|"
            f"{search_without_author}|{isbn or ''}"
        )
        current_time = time.time()

        # Normalize title for search and comparison (do NOT append series number)
        search_title, series_number = self._strip_series_number(title)
        search_title = self._move_article_to_beginning(search_title)
        # Move articles to end logic removed for accessibility compliance
        search_title = self._clean_text_field(search_title)

        # Author transformation: clean and strip honorifics for web search queries
        search_author = self._strip_author_honorifics(
            self._apply_author_transformations(author)
        )

        def _report_progress(message: str) -> None:
            if progress_callback:
                progress_callback(message)

        def _finish_metadata(
            metadata: Dict,
            source: str,
            first_attempt: bool,
        ) -> Dict:
            _report_progress("Enriching plot description…")
            if append_series_to_title and series_number:
                if not metadata["title"].rstrip().endswith(f"- {series_number}"):
                    metadata["title"] = (
                        f"{metadata['title']} - {series_number}".strip()
                    )
            metadata["source"] = source
            metadata["first_attempt"] = first_attempt
            self._enrich_metadata_plot(metadata, search_title, search_author or "")
            self._fill_series_fields(
                metadata,
                search_title,
                search_author or "",
                series_number,
                report_progress=_report_progress,
            )
            metadata.pop("open_library_work_key", None)
            self._cache[cache_key] = (current_time, metadata)
            self._save_persistent_cache()
            return metadata

        # Cache successful lookups only (do not cache failures).
        if hasattr(self, "_cache") and cache_key in self._cache:
            cached_time, cached_result = self._cache[cache_key]
            if (
                cached_result
                and cached_time
                and (current_time - cached_time) < self.CACHE_DURATION
            ):
                refreshed = dict(cached_result)
                if self._fill_series_fields(
                    refreshed,
                    search_title,
                    search_author or "",
                    series_number,
                    report_progress=_report_progress,
                ):
                    self._cache[cache_key] = (current_time, refreshed)
                    self._save_persistent_cache()
                return refreshed
            if cached_time and (current_time - cached_time) >= self.CACHE_DURATION:
                del self._cache[cache_key]

        # ISBN pre-pass: exact lookup via Google Books and Open Library
        if isbn:
            _report_progress("Looking up ISBN…")
            isbn_meta = self._fetch_metadata_by_isbn(isbn)
            if isbn_meta and not isbn_meta.get("_no_result"):
                return _finish_metadata(
                    isbn_meta,
                    "open_library_isbn" if isbn_meta.get("_resolved_source") == "open_library" else "google_books_isbn",
                    first_attempt=True,
                )

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
            return {"_fetch_errors": _errors, "_no_result": True}
        return None

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
            if progress_callback:
                progress_callback(message)

        if refresh == 0:
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
            except Exception as exc:
                fetch_errors.append(f"open_library: {exc}")

        if refresh <= 1:
            _report(_source_progress_message("google_books", phase=search_phase))
            try:
                metadata = self._fetch_from_google_books(
                    search_title,
                    query_author,
                    require_author_match=require_author_match,
                    match_author=db_author,
                )
                if metadata:
                    metadata["_resolved_source"] = "google_books"
                    return metadata
            except Exception as exc:
                fetch_errors.append(f"google_books: {exc}")

        if refresh <= 2:
            _report(_source_progress_message("wikidata", phase=search_phase))
            try:
                metadata = self._fetch_from_wikidata(
                    search_title,
                    query_author,
                    require_author_match=require_author_match,
                    match_author=db_author,
                )
                if metadata:
                    metadata["_resolved_source"] = "wikidata"
                    return metadata
            except Exception as exc:
                fetch_errors.append(f"wikidata: {exc}")

        if fetch_errors:
            return {"_fetch_errors": fetch_errors, "_no_result": True}
        return None

    def _extract_google_series(self, volume_info: dict) -> tuple[str, str]:
        """Parse series name and number from Google Books volumeInfo."""
        series = ""
        series_number = ""

        series_info = volume_info.get("seriesInfo", {})
        if series_info:
            series_number = str(series_info.get("bookDisplayNumber", "") or "").strip()
            volume_series = series_info.get("volumeSeries", [])
            if volume_series:
                vs = volume_series[0]
                for key in ("seriesTitle", "title", "name"):
                    val = (vs.get(key) or "").strip()
                    if val:
                        series = val
                        break
                if not series:
                    raw_id = (vs.get("seriesId") or "").strip()
                    if raw_id and not re.match(r"^[a-f0-9]{12,}$", raw_id, re.IGNORECASE):
                        series = raw_id.replace("_", " ").title()

        subtitle = volume_info.get("subtitle", "") or ""
        if subtitle:
            book_of = re.search(
                r"\(Book\s+(\d+)\s+of\s+([^)]+)\)",
                subtitle,
                re.IGNORECASE,
            )
            if book_of:
                if not series_number:
                    series_number = book_of.group(1).strip()
                if not series:
                    series = book_of.group(2).strip(" -")
            else:
                hash_match = re.search(
                    r"\(([^)#]+?)\s*#\s*(\d+)\)",
                    subtitle,
                    re.IGNORECASE,
                )
                if hash_match:
                    if not series:
                        series = hash_match.group(1).strip(" -")
                    if not series_number:
                        series_number = hash_match.group(2).strip()
                elif not series_number:
                    for pattern in [
                        r"(?:book|volume|#)\s*(\d+)",
                        r"(?:part|novel)\s*(\w+)",
                    ]:
                        match = re.search(pattern, subtitle, re.IGNORECASE)
                        if match:
                            series_number = match.group(1)
                            if not series:
                                series = re.sub(
                                    pattern, "", subtitle, flags=re.IGNORECASE
                                ).strip(" -()")
                            break

        description = volume_info.get("description", "") or ""
        if description and (not series or not series_number):
            patterns = [
                (
                    r"(?:book|volume|#)\s*(\d+)\s+(?:in\s+)?(?:the\s+)?(.+?)(?:\s+series|\s+trilogy|\s+quartet|$)",
                    True,
                ),
                (r"(.+?)\s+(?:book|volume|#)\s*(\d+)", False),
            ]
            for pattern, number_first in patterns:
                match = re.search(pattern, description, re.IGNORECASE)
                if match:
                    if number_first:
                        if not series_number:
                            series_number = match.group(1)
                        if not series:
                            series = match.group(2).strip()
                    else:
                        if not series:
                            series = match.group(1).strip()
                        if not series_number:
                            series_number = match.group(2)
                    break

        return series, series_number

    def _google_item_to_metadata(self, item: dict) -> Optional[Dict]:
        """Build metadata dict from one Google Books API item."""
        volume_info = item.get("volumeInfo", {})
        if not volume_info.get("title"):
            return None

        series, series_number = self._extract_google_series(volume_info)

        return {
            "title": volume_info.get("title", ""),
            "author": self._format_authors(volume_info.get("authors", [])),
            "year": self._extract_year(volume_info.get("publishedDate", "")),
            "publisher": volume_info.get("publisher", ""),
            "plot": self._strip_html(volume_info.get("description", "") or ""),
            "genre": self._format_categories(volume_info.get("categories", [])),
            "isbn": self._extract_isbn(volume_info.get("industryIdentifiers", [])),
            "rating": volume_info.get("averageRating", 0),
            "ratings_count": volume_info.get("ratingsCount", 0),
            "series": series,
            "series_number": series_number,
            "source": "Google Books",
            "confidence": 0.9,
        }

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
            title_score = self._title_word_match_score(
                title, candidate.get("title", "")
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
    ) -> Optional[Dict]:
        """Fetch metadata from Google Books API."""
        db_author = match_author if match_author is not None else author
        queries: list[str] = []
        if title and author:
            queries.append(f"intitle:{title} inauthor:{author}")
        if title and (author or require_author_match):
            queries.append(f"intitle:{title}")
        elif not require_author_match and title:
            queries.append(title)

        seen: set[str] = set()
        for q_idx, query in enumerate(queries):
            if not query or query in seen:
                continue
            seen.add(query)
            try:
                max_results = 5 if q_idx > 0 else 10
                params = {
                    "q": query,
                    "maxResults": max_results,
                    "fields": "items(id,volumeInfo(title,subtitle,authors,publisher,publishedDate,description,industryIdentifiers,categories,averageRating,ratingsCount,seriesInfo))",
                }
                url = f"{self.google_books_url}?{urllib.parse.urlencode(params)}"
                req = urllib.request.Request(url)
                req.add_header("User-Agent", "AudiobookCollectorScanner/1.0")
                with urllib.request.urlopen(req, timeout=TIMEOUT_DETAIL) as response:
                    data = json.loads(response.read().decode("utf-8"))
                if "items" in data and data["items"]:
                    best = self._pick_best_google_match(
                        data["items"],
                        title,
                        db_author,
                        require_author_match=require_author_match,
                    )
                    if best:
                        return best
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
        try:
            # Build search query - combine title and author properly
            queries_to_try = []

            # Special handling for "1984" - try exact title first
            if "1984" in title.lower():
                base_query = title
                if author:
                    base_query += f" author:{author}"
                queries_to_try.append(base_query)

                # Also try alternative title
                if "nineteen eighty-four" not in title.lower():
                    alt_query = "nineteen eighty-four"
                    if author:
                        alt_query += f" author:{author}"
                    queries_to_try.append(alt_query)
            else:
                if author:
                    queries_to_try.append(f"{title} author:{author}")
                    stripped_author = self._strip_author_honorifics(author)
                    if stripped_author and stripped_author.lower() != author.lower():
                        queries_to_try.append(f"{title} author:{stripped_author}")
                queries_to_try.append(title)

            seen_queries = set()
            for query in queries_to_try:
                if query in seen_queries:
                    continue
                seen_queries.add(query)
                if len(seen_queries) > 4:
                    break
                params = {
                    "q": query,
                    "limit": 10,
                    "fields": "key,title,author_name,first_publish_year,publisher,subject,cover_i,isbn,ratings_average,ratings_count",
                }

                url = f"{self.open_library_url}?{urllib.parse.urlencode(params)}"
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=TIMEOUT_SEARCH) as response:
                    data = json.loads(response.read().decode("utf-8"))

                if data.get("docs"):
                    best_metadata = None
                    best_title_score = -1.0
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
                        if not self._metadata_matches_db(
                            title,
                            db_author,
                            candidate,
                            require_author_match=require_author_match,
                        ):
                            continue
                        title_score = self._title_word_match_score(
                            title, candidate.get("title", "")
                        )
                        if title_score > best_title_score:
                            best_title_score = title_score
                            best_metadata = candidate
                            best_work_key = doc.get("key", "") or ""
                            best_isbn = self._first_isbn_from_list(doc.get("isbn"))
                    if best_metadata:
                        if best_isbn:
                            best_metadata["isbn"] = best_isbn
                        if best_work_key:
                            best_metadata["open_library_work_key"] = best_work_key
                            work_fields = self._get_open_library_work_fields(
                                best_work_key
                            )
                            best_metadata["plot"] = work_fields.get(
                                "description", ""
                            )
                            if work_fields.get("series"):
                                best_metadata["series"] = work_fields["series"]
                            if work_fields.get("series_number"):
                                best_metadata["series_number"] = work_fields[
                                    "series_number"
                                ]
                        return best_metadata

            return None
        except Exception as e:
            return None

    def _get_open_library_work_fields(self, work_key: str) -> Dict[str, str]:
        """Load description and series from an Open Library work record."""
        empty = {"description": "", "series": "", "series_number": ""}
        if not work_key:
            return empty
        try:
            work_id = work_key.split("/")[-1] if "/" in work_key else work_key
            url = f"{self.open_library_work_url}/{work_id}.json"
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "AbCS-Audiobook-Collector/1.0")
            with urllib.request.urlopen(req, timeout=TIMEOUT_DETAIL) as response:
                data = json.loads(response.read().decode("utf-8"))

            result = {
                "description": self._extract_description(
                    data.get("description", "")
                ),
                "series": "",
                "series_number": "",
            }
            series_list = data.get("series", [])
            if isinstance(series_list, list) and series_list:
                first = series_list[0]
                if isinstance(first, str):
                    name, number = self._parse_open_library_series_string(first)
                    result["series"] = self._clean_text_field(name)
                    result["series_number"] = number
            return result
        except Exception:
            return empty

    def _get_open_library_description(self, work_key: str) -> str:
        """Get description from Open Library work."""
        return self._get_open_library_work_fields(work_key).get("description", "")

    def _fetch_plot_from_open_library(self, title: str, author: str = None) -> str:
        """Search Open Library by title/author to find a work description.

        This is only called from _enrich_metadata_plot when no open_library_work_key
        is available on the metadata (e.g. after a Google Books or WikiData win).
        """
        try:
            if not title:
                return ""

            query = title
            if author:
                query += f" author:{author}"

            params = {
                "q": query,
                "limit": 3,
                "fields": "key,title,author_name,description",
            }

            url = f"{self.open_library_url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "AbCS-Audiobook-Collector/1.0")

            with urllib.request.urlopen(req, timeout=TIMEOUT_SEARCH) as response:
                data = json.loads(response.read().decode("utf-8"))

            if not data.get("docs"):
                return ""

            for doc in data["docs"]:
                work_key = doc.get("key", "")
                if work_key:
                    plot = self._get_open_library_description(work_key)
                    if plot and len(plot) > 20:
                        return plot

            return ""
        except Exception:
            return ""

    def _fetch_wikipedia_rest_summary(self, title: str) -> str:
        """Fetch a plain-text extract from the Wikipedia REST summary endpoint.

        A single call returns the introduction section as clean text without
        requiring a separate search step.
        """
        if not title:
            return ""
        try:
            encoded_title = urllib.parse.quote(title.replace(" ", "_"))
            url = (
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
            )
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "AbCS-Audiobook-Collector/1.0")
            with urllib.request.urlopen(req, timeout=TIMEOUT_DETAIL) as response:
                data = json.loads(response.read().decode("utf-8"))
            extract = data.get("extract", "")
            if data.get("type") in ("disambiguation", "standard"):
                if data.get("type") == "disambiguation":
                    return ""
                return self._strip_html(extract)
            return self._strip_html(extract)
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
                req = urllib.request.Request(search_url)
                req.add_header("User-Agent", "AbCS-Audiobook-Collector/1.0")

                with urllib.request.urlopen(req, timeout=TIMEOUT_SEARCH) as response:
                    search_data = json.loads(response.read().decode("utf-8"))

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
                    req2 = urllib.request.Request(extract_url)
                    req2.add_header("User-Agent", "AbCS-Audiobook-Collector/1.0")

                    with urllib.request.urlopen(req2, timeout=TIMEOUT_DETAIL) as response2:
                        extract_data = json.loads(response2.read().decode("utf-8"))

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
                        return extract

            return ""
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

        # Try to extract 4-digit year
        import re

        year_match = re.search(r"\b(19|20)\d{2}\b", published_date)
        return year_match.group(0) if year_match else published_date

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
    ) -> Optional[Dict]:
        """Fetch metadata from WikiData SPARQL endpoint."""
        db_author = match_author if match_author is not None else author
        try:
            # Build a very simple SPARQL query that should work
            # Use basic title search without complex conditions
            safe_title = title.replace('"', '\\"') if title else ""
            safe_author = author.replace('"', '\\"') if author else ""

            # Simple SPARQL query - more flexible matching
            # Try multiple search strategies including exact matches
            search_terms = [
                safe_title,
                safe_title.replace(" ", ""),
                safe_title.replace(" and ", " & ").replace(" And ", " & "),
            ]

            # Create a more flexible query with multiple title options
            title_conditions = []
            for term in search_terms:
                title_conditions.append(f'CONTAINS(LCASE(?bookLabel), LCASE("{term}"))')

            title_filter = " || ".join(title_conditions)

            # Add author filter if available
            author_filter = ""
            if author:
                safe_author = author.replace('"', '\\"')
                author_filter = f"""
                ?book wdt:P50 ?author.
                ?author rdfs:label ?authorLabel.
                FILTER(LANG(?authorLabel) = "en")
                FILTER(CONTAINS(LCASE(?authorLabel), LCASE("{safe_author}")))
                """

            # Special case for "1984" - try to find the correct Wikidata item for Orwell's 1984
            if "1984" in safe_title.lower():
                # Claude AI's expert fix - search both label and altLabel, remove restrictive class filter
                safe_title_escaped = safe_title.replace('"', '\\"')
                sparql_query = f"""
                SELECT DISTINCT ?book ?bookLabel ?bookDescription WHERE {{
                  ?author rdfs:label "George Orwell"@en.
                  ?book wdt:P50 ?author.
                  {{ ?book rdfs:label ?label. }}
                  UNION
                  {{ ?book skos:altLabel ?label. }}
                  FILTER(CONTAINS(LCASE(?label), LCASE("{safe_title_escaped}")))
                  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                }}
                LIMIT 10
                """
            else:
                sparql_query = f"""
                SELECT ?book ?bookLabel ?authorLabel ?seriesLabel ?seriesOrdinal WHERE {{
                    ?book wdt:P31 wd:Q571.
                    ?book rdfs:label ?bookLabel.
                    FILTER(LANG(?bookLabel) = "en")
                    FILTER({title_filter})
                    
                    {author_filter}
                    
                    OPTIONAL {{
                        ?book wdt:P179 ?series.
                        ?series rdfs:label ?seriesLabel.
                        FILTER(LANG(?seriesLabel) = "en")
                    }}
                    OPTIONAL {{
                        ?book wdt:P1545 ?seriesOrdinal.
                    }}
                }}
                LIMIT 10
                """

            # Properly URL encode the query
            from urllib.parse import quote_plus

            encoded_query = quote_plus(sparql_query.strip())

            # Build URL with encoded query
            url = f"{self.wikidata_url}?query={encoded_query}&format=json"

            req = urllib.request.Request(url)
            req.add_header(
                "User-Agent",
                "AbCS-Audiobook-Collector/1.0 (Educational audiobook metadata tool)",
            )
            req.add_header("Accept", "application/sparql-results+json")

            with urllib.request.urlopen(req, timeout=TIMEOUT_DETAIL) as response:
                response_text = response.read().decode("utf-8")

                # Check if we got JSON
                if not response_text.strip().startswith("{"):
                    return None

                data = json.loads(response_text)

            # Parse results
            results = data.get("results", {}).get("bindings", [])

            best_metadata = None
            best_title_score = -1.0
            for result in results:
                series_label = self._get_sparql_value(result, "seriesLabel")
                series_ordinal = self._get_sparql_value(result, "seriesOrdinal")
                metadata = {
                    "title": self._get_sparql_value(result, "bookLabel"),
                    "author": self._get_sparql_value(result, "authorLabel"),
                    "series": series_label,
                    "series_number": series_ordinal,
                    "source": "WikiData",
                }
                if not metadata.get("title"):
                    continue
                if not self._metadata_matches_db(
                    title,
                    db_author,
                    metadata,
                    require_author_match=require_author_match,
                ):
                    continue
                title_score = self._title_word_match_score(
                    title, metadata.get("title", "")
                )
                if title_score > best_title_score:
                    best_title_score = title_score
                    best_metadata = metadata

            if best_metadata:
                if best_metadata.get("series"):
                    best_metadata["series"] = self._clean_text_field(
                        best_metadata["series"]
                    )
                    if self._is_unlikely_series_name(
                        best_metadata["series"],
                        title=best_metadata.get("title", ""),
                    ):
                        best_metadata["series"] = ""
                if best_metadata.get("series_number"):
                    ordinal = re.sub(
                        r"[^\d]", "", str(best_metadata["series_number"])
                    )
                    best_metadata["series_number"] = ordinal or ""
                return best_metadata
        except Exception as e:
            return None

    def _get_sparql_value(self, result: dict, field: str) -> str:
        """Extract value from SPARQL result binding."""
        try:
            if field in result and result[field]:
                return result[field].get("value", "").strip()
        except Exception:
            pass
        return ""

    def _strip_series_number(self, title: str) -> tuple[str, str]:
        """Strip series number from title and return (clean_title, series_number)."""
        if not title:
            return "", ""

        # Patterns to match series numbers (only if clearly separated)
        patterns = [
            r"^(.*?)\s*-\s*(\d+)$",  # "Title - 09"
            r"^(.*?)\s*#\s*(\d+)$",  # "Title #09"
            r"^(.*?)\s+Book\s*(\d+)$",  # "Title Book 09"
            r"^(.*?)\s+Volume\s*(\d+)$",  # "Title Volume 09"
            r"^(.*?)\s*,\s*(\d+)$",  # "Title, 09"
        ]

        for pattern in patterns:
            match = re.match(pattern, title.strip(), re.IGNORECASE)
            if match:
                clean_title = match.group(1).strip()
                series_number = match.group(2)
                if clean_title:
                    return clean_title, series_number

        # No series number found
        return title.strip(), ""

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

    def _is_redundant_plot(self, plot: str, series: str) -> bool:
        """Return True when the plot appears to be just a series label rather than a real description."""
        if not plot or not series:
            return False

        normalized_plot = re.sub(r"\s+", " ", plot.strip().lower())
        normalized_series = re.sub(r"\s+", " ", series.strip().lower())

        if normalized_plot == normalized_series:
            return True

        redundant_variants = [
            f"{normalized_series} series",
            f"{normalized_series} book",
            f"{normalized_series} books",
            f"book in the {normalized_series} series",
            f"series: {normalized_series}",
        ]
        if normalized_plot in redundant_variants:
            return True

        return False

    def _is_unlikely_series_name(
        self, series: str, title: str = "", plot: str = ""
    ) -> bool:
        """Return True when the series value is too long or looks like plot/article text."""
        if not series:
            return False

        normalized_series = re.sub(r"\s+", " ", series.strip())
        if len(normalized_series) > 90:
            return True
        if len(normalized_series.split()) > 12:
            return True
        if len(re.findall(r"[\.\?!]", normalized_series)) > 1:
            return True

        series_lower = normalized_series.lower()
        if "new york times" in series_lower or "bestselling author" in series_lower:
            return True
        if "novel" in series_lower and "chief inspector" in series_lower:
            return True

        if plot:
            normalized_plot = re.sub(r"\s+", " ", plot.strip().lower())
            if series_lower in normalized_plot and len(normalized_plot) > len(series_lower) + 20:
                return True

        if title:
            title_lower = title.strip().lower()
            if title_lower and title_lower in series_lower and len(series_lower) > len(title_lower) + 20:
                return True

        return False

    def _apply_title_transformations(
        self, title: str, move_articles: bool = False
    ) -> str:
        """Apply title transformations: strip series, move articles, clean."""
        # Strip series number first
        clean_title, series_number = self._strip_series_number(title)

        # Move articles to end logic removed for accessibility compliance

        # Clean the title
        clean_title = self._clean_text_field(clean_title)

        # Re-add series number if it existed
        if series_number:
            clean_title = f"{clean_title} - {series_number}"

        return clean_title

    def _apply_author_transformations(self, author: str) -> str:
        """Apply author transformations: clean only (no flipping)."""
        if not author:
            return ""

        # Clean the author name only
        author = self._clean_text_field(author)
        return author

    def clean_web_data_for_storage(
        self, web_data: Dict, move_articles: bool = False, flip_author: bool = False
    ) -> Dict:
        """Clean web data according to user preferences before storing in database."""
        if not web_data:
            return web_data

        cleaned_data = web_data.copy()

        # Clean title
        if "title" in cleaned_data:
            cleaned_data["title"] = self._apply_title_transformations(
                cleaned_data["title"], False
            )

        # Clean author
        if "author" in cleaned_data:
            cleaned_data["author"] = self._apply_author_transformations(
                cleaned_data["author"]
            )

        # Clean other text fields
        for field in ["publisher", "genre", "plot"]:
            if field in cleaned_data:
                cleaned_data[field] = self._clean_text_field(cleaned_data[field])

        # Clean series
        if "series" in cleaned_data:
            cleaned_data["series"] = self._clean_text_field(cleaned_data["series"])
            if self._is_unlikely_series_name(
                cleaned_data["series"],
                title=cleaned_data.get("title", ""),
                plot=cleaned_data.get("plot", ""),
            ):
                cleaned_data["series"] = ""

        # Remove plot text that is just the series name or a series-only label
        if "plot" in cleaned_data and cleaned_data.get("plot"):
            if self._is_redundant_plot(cleaned_data["plot"], cleaned_data.get("series", "")):
                cleaned_data["plot"] = ""

        return cleaned_data


def clean_web_data(
    web_data: dict,
    move_articles: bool = False,
    flip_author: bool = False,
) -> dict:
    """Module-level convenience wrapper for WebBookAPI.clean_web_data_for_storage.

    Allows callers (e.g. web_metadata.py) to clean web data without constructing
    a full WebBookAPI instance purely for that purpose.
    """
    return WebBookAPI().clean_web_data_for_storage(web_data, move_articles, flip_author)


def normalize_title(title: str) -> str:
    """Normalize a title for search/comparison.

    Moves trailing articles ('Title, The' -> 'The Title'), trims, lowercases,
    and removes embedded spaces.  Shared between WebBookAPI matching logic
    and WebMetadataWindow field comparison.
    """
    import re as _re
    if not title:
        return ""
    t = title.strip()
    match = _re.match(r"^(.*?)[,\s]+(the|a|an)$", t, _re.IGNORECASE)
    if match:
        base = match.group(1).strip()
        article = match.group(2).lower()
        t = f"{article} {base}"
    return "".join(t.lower().split())
