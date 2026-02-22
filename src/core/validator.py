"""
Validator for audiobook import data.
Detects errors and issues in imported audiobook metadata.
"""

from typing import List, Dict, Any
from difflib import SequenceMatcher
import re
from PySide6.QtCore import QSettings
from .import_rules import ImportRulesEngine


class ImportValidator:
    """
    Validates imported audiobook data and identifies errors.
    Matches the error detection from MS Access version.
    """

    def __init__(self):
        """Initialize validator."""
        self.settings = QSettings('AbCS', 'AudioBookCollector')
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
        title = book.get('title', '').strip().lower()
        author = book.get('author', '').strip().lower()
        year = book.get('year')
        collection_id = book.get('collection_id', target_collection_id)
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
            existing_title = existing.get('title', '').strip().lower()
            existing_author = existing.get('author', '').strip().lower()

            same_title = existing_title == title
            same_author = existing_author == author
            exact_match = same_title and same_author

            if not exact_match:
                if not fuzzy_enabled:
                    continue

                title_similarity = self._similarity_ratio(
                    existing_title, title)
                author_similarity = self._similarity_ratio(
                    existing_author, author)
                if (
                    title_similarity < fuzzy_ratio_threshold
                    or author_similarity < fuzzy_ratio_threshold
                ):
                    continue

            if include_year and existing.get('year') != year:
                continue

            if include_collection:
                if existing.get('collection_id') == collection_id:
                    return True
            else:
                return True

        return False

    def flip_author_name(self, name: str) -> str:
        """
        Flip author name from "First Last" to "Last, First".

        Args:
            name: Author name

        Returns:
            Flipped name
        """
        if not name or ',' in name:
            # Already in Last, First format or empty
            return name

        parts = name.strip().split()
        if len(parts) < 2:
            return name

        # Simple flip: last word is last name
        last_name = parts[-1]
        first_names = ' '.join(parts[:-1])
        return f"{last_name}, {first_names}"

    def normalize_title(self, title: str) -> str:
        """
        Normalize title by removing extra whitespace and special characters.

        Args:
            title: Book title

        Returns:
            Normalized title
        """
        # Remove extra whitespace
        title = ' '.join(title.split())

        # Remove common problematic patterns
        title = re.sub(r'\s*\(unabridged\)\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\[unabridged\]\s*', '', title, flags=re.IGNORECASE)

        return title.strip()

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

        if normalized_lower == 'duplicate':
            return 'duplicate'

        read_errors = ['error reading file', 'file not found', 'corrupted']
        if any(re_err in normalized_lower for re_err in read_errors):
            return 'read'

        error_text = str(error or '').strip()
        if error_text.upper().startswith('W:'):
            return 'warning'
        if error_text.upper().startswith('E:'):
            return 'parse'

        configured_severity = self.rules_engine.message_severity(
            normalized_error)
        if configured_severity == 'warning':
            return 'warning'

        warning_errors = [
            'author name in title',
            'title in author name',
            'author contains unknown or various',
            'title below minimum length',
            'folder path does not match expected structure',
            'year outside allowed range',
            'year is not a valid number',
        ]
        if any(warn in normalized_lower for warn in warning_errors):
            return 'warning'

        return 'parse'

    @staticmethod
    def normalize_error_message(error: str) -> str:
        """Normalize a raw error string for display and severity checks."""
        text = str(error or '').strip()
        if not text:
            return ''

        upper_text = text.upper()
        if upper_text.startswith('E:') or upper_text.startswith('W:'):
            text = text[2:].strip()
            upper_text = text.upper()

        if upper_text.startswith('WARNING:'):
            text = text[8:].strip()

        return text

    def format_error_message(self, error: str) -> str:
        """Format a single error for display with compact prefixes."""
        normalized = self.normalize_error_message(error)
        if not normalized:
            return ''

        if normalized.lower() == 'duplicate':
            return 'Duplicate'

        severity = self.categorize_error(error)
        prefix = 'W: ' if severity == 'warning' else 'E: '
        return f"{prefix}{normalized}"

    def format_error_summary(self, errors: List[str]) -> str:
        """Format a list of errors as compact display text."""
        formatted_errors: List[str] = []
        for err in errors:
            formatted = self.format_error_message(str(err))
            if not formatted:
                continue
            formatted_errors.append(formatted)

        return '; '.join(formatted_errors)
