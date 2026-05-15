"""
Validator for audiobook import data.
Detects errors and issues in imported audiobook metadata.
"""

import time
from .import_rules import ImportRulesEngine
from PySide6.QtCore import QSettings
from typing import List, Dict, Any, Set, Tuple
import re

from src.utils.text_utils import normalize_title, normalize_author, similarity_ratio


class ImportValidator:
    """
    Validates imported audiobook data and identifies errors.
    Matches the error detection from MS Access version.
    """

    @staticmethod
    def append_flag_once(book: dict, message: str):
        """Append a flag message to book errors exactly once (case-insensitive)."""
        if not message:
            return
        errors = book.setdefault("errors", [])
        existing = {str(err).strip().lower() for err in errors if str(err).strip()}
        normalized = message.strip().lower()
        if normalized not in existing:
            errors.append(message)

    def __init__(self):
        """Initialize validator."""
        self.settings = QSettings("AbCS", "AudioBookCollector")
        self.duplicate_match_mode = "with_collection"
        self.duplicate_fuzzy_threshold = 0
        self.rules_engine = ImportRulesEngine()
        self.reload_settings()

    def reload_settings(self):
        """Reload validator rule settings from QSettings."""
        self.rules_engine.reload_settings()
        duplicate_mode = self.settings.value(
            "import/rules/duplicate/match_mode",
            "title_author_year_collection",
            type=str,
        )
        if duplicate_mode == "with_collection":
            duplicate_mode = "title_author_year_collection"
        elif duplicate_mode == "ignore_collection":
            duplicate_mode = "title_author_year"
        elif duplicate_mode == "title_author_year_ignore_collection":
            duplicate_mode = "title_author_year"
        elif duplicate_mode == "title_author_ignore_collection":
            duplicate_mode = "title_author_year"
        self.duplicate_match_mode = duplicate_mode
        threshold = self.settings.value(
            "import/rules/duplicate/fuzzy_threshold",
            0,
            type=int,
        )
        self.duplicate_fuzzy_threshold = max(0, min(100, threshold))

    def build_duplicate_index(
        self,
        existing_books: List[Dict[str, Any]],
        target_collection_id: int | None = None,
    ) -> Dict[str, Any]:
        """
        PHASE 2 OPTIMIZATION: Build an optimized index for duplicate checking.

        Pre-computes normalized keys and signatures for all existing books,
        enabling O(1) exact lookups and filtered fuzzy checks.

        Args:
            existing_books: List of existing book dictionaries
            target_collection_id: Collection to scope duplicate checks to

        Returns:
            Dictionary containing:
            - 'exact_keys': Set of exact match keys
            - 'books_by_key': Dict mapping keys to list of books
            - 'normalized_books': List of pre-normalized book data for fuzzy checks
            - 'build_time': Time taken to build index
        """
        index_start = time.perf_counter()

        mode = self.duplicate_match_mode
        include_year = mode in ("title_author_year", "title_author_year_collection")
        include_collection = mode in ("title_author", "title_author_year_collection")

        exact_keys: Set[str] = set()
        books_by_key: Dict[str, List[Dict]] = {}
        normalized_books: List[Dict] = []

        for book in existing_books:
            # Pre-normalize all fields
            title = normalize_title(book.get("title", ""), aggressive=True)
            author = normalize_author(book.get("author", ""), aggressive=True)
            year = book.get("year")
            collection_id = book.get("collection_id", target_collection_id)

            # Build exact match key
            key_parts = [title, author]
            if include_year and year:
                key_parts.append(str(year))
            if include_collection:
                key_parts.append(str(collection_id or "none"))
            exact_key = "|".join(key_parts)

            exact_keys.add(exact_key)
            books_by_key.setdefault(exact_key, []).append(book)

            # Store normalized data for fuzzy matching
            normalized_books.append({
                "book": book,
                "title": title,
                "author": author,
                "year": year,
                "collection_id": collection_id,
                "exact_key": exact_key,
                "title_len": len(title),
                "author_len": len(author),
            })

        build_time = time.perf_counter() - index_start

        return {
            "exact_keys": exact_keys,
            "books_by_key": books_by_key,
            "normalized_books": normalized_books,
            "build_time": build_time,
            "include_year": include_year,
            "include_collection": include_collection,
        }

    def is_duplicate_fast(
        self,
        book: Dict[str, Any],
        index: Dict[str, Any],
        target_collection_id: int | None = None,
    ) -> bool:
        """
        PHASE 2 OPTIMIZATION: Fast duplicate check using pre-built index.

        O(1) exact lookup + O(k) fuzzy where k is small subset of candidates.

        Args:
            book: Book to check
            index: Pre-built index from build_duplicate_index()
            target_collection_id: Collection to scope duplicate checks to

        Returns:
            True if duplicate found
        """
        title = normalize_title(book.get("title", ""), aggressive=True)
        author = normalize_author(book.get("author", ""), aggressive=True)
        year = int(book.get("year")) if book.get("year") else None
        collection_id = book.get("collection_id", target_collection_id)

        include_year = index["include_year"]
        include_collection = index["include_collection"]
        fuzzy_ratio_threshold = self.duplicate_fuzzy_threshold / 100.0
        fuzzy_enabled = self.duplicate_fuzzy_threshold > 0

        # Build exact key for O(1) lookup
        key_parts = [title, author]
        if include_year and year:
            key_parts.append(str(year))
        if include_collection:
            key_parts.append(str(collection_id or "none"))
        exact_key = "|".join(key_parts)

        # O(1) exact match check
        if exact_key in index["exact_keys"]:
            return True

        if not fuzzy_enabled:
            return False

        # PHASE 2 OPTIMIZATION: Filtered fuzzy check
        # Only check books with similar title/author length (likely matches)
        # This reduces O(n) to O(k) where k << n
        title_len = len(title)
        author_len = len(author)
        len_tolerance = 5  # Characters difference allowed for fuzzy candidate

        for existing in index["normalized_books"]:
            # Quick length filter - skip obviously different books
            if abs(existing["title_len"] - title_len) > len_tolerance:
                continue
            if abs(existing["author_len"] - author_len) > len_tolerance:
                continue

            # Check year if required
            if include_year and existing["year"] != year:
                continue

            # Check collection if required
            if include_collection:
                if existing["collection_id"] != collection_id:
                    continue

            # Expensive fuzzy check only on filtered candidates
            title_sim = similarity_ratio(existing["title"], title)
            if title_sim < fuzzy_ratio_threshold:
                continue

            author_sim = similarity_ratio(existing["author"], author)
            if author_sim < fuzzy_ratio_threshold:
                continue

            # Both title and author match fuzzily
            return True

        return False

    def validate_book(self, book: Dict[str, Any]) -> List[str]:
        """
        Validate a book record and return list of errors.

        Args:
            book: Book dictionary from scanner

        Returns:
            List of error messages
        """
        return self.rules_engine.validate(book)

    def is_duplicate(
        self,
        book: Dict[str, Any],
        existing_books: List[Dict[str, Any]],
        target_collection_id: int | None = None,
    ) -> bool:
        """
        Check if book is a duplicate of an existing book.

        Args:
            book: Book to check
            existing_books: List of existing books
            target_collection_id: Collection to scope duplicate checks to

        Returns:
            True if duplicate found
        """
        title = normalize_title(book.get("title", ""))
        author = book.get("author", "").strip().lower()
        year = book.get("year")
        collection_id = book.get("collection_id", target_collection_id)
        mode = self.duplicate_match_mode

        include_year = mode in (
            "title_author_year",
            "title_author_year_collection",
        )
        include_collection = mode in (
            "title_author",
            "title_author_year_collection",
        )
        fuzzy_ratio_threshold = self.duplicate_fuzzy_threshold / 100.0
        fuzzy_enabled = self.duplicate_fuzzy_threshold > 0

        for existing in existing_books:
            existing_title = normalize_title(existing.get("title", ""))
            existing_author = existing.get("author", "").strip().lower()

            same_title = existing_title == title
            same_author = existing_author == author
            exact_match = same_title and same_author

            if not exact_match:
                if not fuzzy_enabled:
                    continue

                title_similarity = similarity_ratio(existing_title, title)
                author_similarity = similarity_ratio(existing_author, author)
                if (
                    title_similarity < fuzzy_ratio_threshold
                    or author_similarity < fuzzy_ratio_threshold
                ):
                    continue

            if include_year and existing.get("year") != year:
                continue

            if include_collection:
                if existing.get("collection_id") == collection_id:
                    return True
            else:
                return True

        return False

    def sanitize_metadata(self, book: Dict[str, Any]) -> List[str]:
        """
        Apply mandatory sanitization rules to all relevant fields.
        Only removes leading/trailing whitespace and leading punctuation (not internal punctuation).
        Applies proper case. Returns a list of 'C:' flags for any significant corrections.
        """
        import re

        flags = []
        # Fields to sanitize
        fields = ["title", "author", "genre", "series", "reader", "collection"]
        for field in fields:
            original = str(book.get(field, "") or "")
            if not original:
                continue
            # 1. Trim leading/trailing whitespace
            cleaned = original.strip()
            # 2. For author and reader only, remove all leading non-alphabetic characters (not internal)
            if field in ("author", "reader"):
                cleaned = re.sub(r"^[^A-Za-z]+", "", cleaned)
            # 3. Collapse multiple spaces to single space
            cleaned = re.sub(r"\s+", " ", cleaned)
            # 4. Proper Case (Mandatory)
            if cleaned:
                cleaned = cleaned.lower()

                def proper_case_word(match):
                    return match.group(1) + match.group(2).upper()

                # Capitalize first letters after whitespace or hyphen, but preserve apostrophe lowercase
                cleaned = re.sub(r"(^|[\s\-])([a-z])", proper_case_word, cleaned)
                # Handle names like O'Connor correctly
                cleaned = re.sub(
                    r"(\bO')([a-z])",
                    lambda m: m.group(1) + m.group(2).upper(),
                    cleaned,
                )
            # Detection logic for the C: flag
            significant_change = False
            if original.strip() != original:
                significant_change = True
            if field == "author":
                if field in ("author", "reader"):
                    if re.sub(r"^[^A-Za-z]+", "", original.strip()) != original.strip():
                        significant_change = True
            if re.sub(r"\s+", " ", original) != original:
                significant_change = True
            if significant_change:
                flags.append(f"C: Sanitized {field}")
            book[field] = cleaned
        return flags

    def categorize_error(self, error: str) -> str:
        """
        Categorize error for display.

        Args:
            error: Error message

        Returns:
            Error category: 'parse', 'read', or 'warning'
        """
        normalized_error = self.normalize_error_message(error)
        normalized_lower = normalized_error.lower()

        if normalized_lower == "duplicate":
            return "duplicate"

        read_errors = ["error reading file", "file not found", "corrupted"]
        if any(re_err in normalized_lower for re_err in read_errors):
            return "read"

        error_text = str(error or "").strip()
        if error_text.upper().startswith("W:"):
            return "warning"
        if error_text.upper().startswith("F:"):
            return "warning"
        if error_text.upper().startswith("C:"):
            return "warning"
        if error_text.upper().startswith("E:"):
            return "parse"

        configured_severity = self.rules_engine.message_severity(normalized_error)
        if configured_severity == "warning":
            return "warning"
        if configured_severity == "error":
            return "parse"

        warning_errors = [
            "author name in title",
            "title in author name",
            "author contains unknown or various",
            "title below minimum length",
            "folder path does not match expected structure",
            "book length below minimum",
            "book length above maximum",
        ]
        if any(warn in normalized_lower for warn in warning_errors):
            return "warning"

        return "parse"

    @staticmethod
    def normalize_error_message(error: str) -> str:
        """Normalize a raw error string for display and severity checks."""
        text = str(error or "").strip()
        if not text:
            return ""

        upper_text = text.upper()
        if (
            upper_text.startswith("E:")
            or upper_text.startswith("W:")
            or upper_text.startswith("F:")
            or upper_text.startswith("C:")
        ):
            text = text[2:].strip()
            upper_text = text.upper()

        if upper_text.startswith("WARNING:"):
            text = text[8:].strip()

        return text

    def format_error_message(self, error: str) -> str:
        """Format a single error for display with compact prefixes."""
        raw_error = str(error or "").strip()
        is_fallback_flag = raw_error.upper().startswith("F:")
        is_correction_flag = raw_error.upper().startswith("C:")
        normalized = self.normalize_error_message(error)
        if not normalized:
            return ""

        if normalized.lower() == "duplicate":
            return "Duplicate"

        if is_fallback_flag:
            return f"F: {normalized}"
        if is_correction_flag:
            return f"C: {normalized}"

        severity = self.categorize_error(error)
        prefix = "W: " if severity == "warning" else "E: "
        return f"{prefix}{normalized}"

    def format_error_summary(self, errors: List[str]) -> str:
        """Format a list of errors as compact display text."""
        return "; ".join(self.format_error_message(e) for e in errors if e)
