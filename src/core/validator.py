"""
Validator for audiobook import data.
Detects errors and issues in imported audiobook metadata.
"""

from .import_rules import ImportRulesEngine
from PySide6.QtCore import QSettings
from typing import List, Dict, Any
from difflib import SequenceMatcher
import re


class ImportValidator:
    """
    Validates imported audiobook data and identifies errors.
    Matches the error detection from MS Access version.
    """

    @staticmethod
    def normalize_title_for_compare(title: str) -> str:
        """Normalize title for comparison: lowercase, strip (Articles no longer moved)."""
        if not isinstance(title, str):
            return ""
        return title.strip().lower()

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

    @staticmethod
    def _similarity_ratio(left: str, right: str) -> float:
        """Return a normalized text similarity score from 0.0 to 1.0."""
        if not left or not right:
            return 0.0
        return SequenceMatcher(None, left, right).ratio()

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
        title = self.normalize_title_for_compare(book.get("title", ""))
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
            existing_title = self.normalize_title_for_compare(existing.get("title", ""))
            existing_author = existing.get("author", "").strip().lower()

            same_title = existing_title == title
            same_author = existing_author == author
            exact_match = same_title and same_author

            if not exact_match:
                if not fuzzy_enabled:
                    continue

                title_similarity = self._similarity_ratio(existing_title, title)
                author_similarity = self._similarity_ratio(existing_author, author)
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
                cleaned = cleaned.title()
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

        warning_errors = [
            "author name in title",
            "title in author name",
            "author contains unknown or various",
            "title below minimum length",
            "folder path does not match expected structure",
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
