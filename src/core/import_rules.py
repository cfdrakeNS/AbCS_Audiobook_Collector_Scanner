"""Rule engine for import validation."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List
from PySide6.QtCore import QSettings


RuleFunc = Callable[[Dict[str, Any]], List[str]]


@dataclass(frozen=True)
class RuleSetting:
    enabled: bool
    severity: str


@dataclass
class ValidationRule:
    name: str
    evaluator: RuleFunc
    settings_key: str
    default_enabled: bool = True
    default_severity: str = "error"


class ImportRulesEngine:
    """Evaluates import validation rules against scanned book metadata."""

    def __init__(self):
        self.settings = QSettings('AbCS', 'AudioBookCollector')
        self.rules: List[ValidationRule] = [
            ValidationRule(
                "title_blank",
                self._rule_title_blank,
                settings_key="title_blank",
                default_enabled=True,
                default_severity="error",
            ),
            ValidationRule(
                "author_blank",
                self._rule_author_blank,
                settings_key="author_blank",
                default_enabled=True,
                default_severity="error",
            ),
            ValidationRule(
                "author_non_alpha_start",
                self._rule_author_non_alpha_start,
                settings_key="author_non_alpha_start",
                default_enabled=True,
                default_severity="error",
            ),
            ValidationRule(
                "author_name_in_title",
                self._rule_author_name_in_title,
                settings_key="author_name_in_title",
                default_enabled=True,
                default_severity="warning",
            ),
            ValidationRule(
                "title_in_author_name",
                self._rule_title_in_author_name,
                settings_key="title_in_author_name",
                default_enabled=True,
                default_severity="warning",
            ),
            ValidationRule(
                "unknown_or_various_author",
                self._rule_unknown_or_various_author,
                settings_key="unknown_or_various_author",
                default_enabled=True,
                default_severity="warning",
            ),
            ValidationRule(
                "minimum_title_length",
                self._rule_minimum_title_length,
                settings_key="minimum_title_length",
                default_enabled=False,
                default_severity="warning",
            ),
            ValidationRule(
                "file_structure",
                self._rule_file_structure,
                settings_key="file_structure",
                default_enabled=False,
                default_severity="warning",
            ),
            ValidationRule(
                "year_out_of_range",
                self._rule_year_out_of_range,
                settings_key="year_out_of_range",
                default_enabled=False,
                default_severity="warning",
            ),
            ValidationRule(
                "genre_missing",
                self._rule_genre_missing,
                settings_key="genre_missing",
                default_enabled=False,
                default_severity="warning",
            ),
            ValidationRule(
                "bitrate_below_minimum",
                self._rule_bitrate_below_minimum,
                settings_key="bitrate_below_minimum",
                default_enabled=False,
                default_severity="warning",
            ),
        ]
        self._rule_settings: Dict[str, RuleSetting] = {}
        self.min_title_length = 3
        self.file_structure_pattern = "author_title"
        self.min_year = 1900
        self.max_year = 2100
        self.min_bitrate = 0
        self.reload_settings()

    def reload_settings(self):
        """Reload rule settings from QSettings."""
        settings_map: Dict[str, RuleSetting] = {}
        for rule in self.rules:
            enabled = self.settings.value(
                f"import/rules/{rule.settings_key}/enabled",
                rule.default_enabled,
                type=bool,
            )
            severity = self.settings.value(
                f"import/rules/{rule.settings_key}/severity",
                rule.default_severity,
                type=str,
            )
            normalized_severity = "warning" if str(
                severity).lower() == "warning" else "error"
            settings_map[rule.name] = RuleSetting(
                enabled=enabled,
                severity=normalized_severity,
            )

        self._rule_settings = settings_map
        self.min_title_length = self.settings.value(
            "import/rules/minimum_title_length/value",
            3,
            type=int,
        )
        self.file_structure_pattern = self.settings.value(
            "import/rules/file_structure/pattern",
            "author_title",
            type=str,
        )
        self.min_year = self.settings.value(
            "import/rules/year_out_of_range/min_year",
            1900,
            type=int,
        )
        self.max_year = self.settings.value(
            "import/rules/year_out_of_range/max_year",
            2100,
            type=int,
        )
        if self.max_year < self.min_year:
            self.min_year, self.max_year = self.max_year, self.min_year
        self.min_bitrate = max(
            0,
            self.settings.value(
                "import/rules/bitrate_below_minimum/min_kbps",
                0,
                type=int,
            ),
        )

    def validate(self, book: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        for rule in self.rules:
            rule_setting = self._rule_settings.get(
                rule.name,
                RuleSetting(
                    enabled=rule.default_enabled,
                    severity=rule.default_severity,
                ),
            )
            if not rule_setting.enabled:
                continue
            rule_errors = rule.evaluator(book)
            if rule_setting.severity == "warning":
                rule_errors = [
                    f"Warning: {message}" for message in rule_errors
                ]
            errors.extend(rule_errors)
        return errors

    @staticmethod
    def _rule_title_blank(book: Dict[str, Any]) -> List[str]:
        title = (book.get("title") or "").strip()
        if not title:
            return ["Title Blank"]
        return []

    @staticmethod
    def _rule_author_blank(book: Dict[str, Any]) -> List[str]:
        author = (book.get("author") or "").strip()
        if not author:
            return ["Author Blank"]
        return []

    @staticmethod
    def _rule_author_non_alpha_start(book: Dict[str, Any]) -> List[str]:
        author = (book.get("author") or "").strip()
        if author and not author[0].isalpha():
            return ["Author Name Starts with non-alphabetic character"]
        return []

    @staticmethod
    def _rule_author_name_in_title(book: Dict[str, Any]) -> List[str]:
        author = (book.get("author") or "").strip().lower()
        title = (book.get("title") or "").strip().lower()
        if author and title and author in title:
            return ["Author name in Title"]
        return []

    @staticmethod
    def _rule_title_in_author_name(book: Dict[str, Any]) -> List[str]:
        author = (book.get("author") or "").strip().lower()
        title = (book.get("title") or "").strip().lower()
        if author and title and title in author:
            return ["Title in Author name"]
        return []

    def _rule_unknown_or_various_author(self, book: Dict[str, Any]) -> List[str]:
        author = (book.get("author") or "").strip().lower()
        if not author:
            return []
        if "unknown" in author or "various" in author:
            return ["Author contains Unknown or Various"]
        return []

    def _rule_minimum_title_length(self, book: Dict[str, Any]) -> List[str]:
        title = (book.get("title") or "").strip()
        if not title:
            return []
        if len(title) < max(1, int(self.min_title_length)):
            return [
                f"Title below minimum length ({self.min_title_length})"
            ]
        return []

    def _rule_file_structure(self, book: Dict[str, Any]) -> List[str]:
        folder = (book.get("folder") or "").strip()
        if not folder:
            return []

        parts = [part for part in folder.replace("\\", "/").split("/") if part]
        if not parts:
            return []

        def is_author_title_path() -> bool:
            return len(parts) >= 2

        def is_year_author_title_path() -> bool:
            if len(parts) < 3:
                return False
            return parts[-3].isdigit() and len(parts[-3]) == 4

        pattern = (self.file_structure_pattern or "author_title").lower()
        valid = False

        if pattern == "year_author_title":
            valid = is_year_author_title_path()
            expected_label = "Year/Author/Title"
        elif pattern == "either":
            valid = is_author_title_path() or is_year_author_title_path()
            expected_label = "Author/Title or Year/Author/Title"
        else:
            valid = is_author_title_path()
            expected_label = "Author/Title"

        if valid:
            return []
        return [f"Folder path does not match expected structure ({expected_label})"]

    def _rule_year_out_of_range(self, book: Dict[str, Any]) -> List[str]:
        year = book.get("year")
        if year in (None, ""):
            return []

        try:
            year_value = int(year)
        except (TypeError, ValueError):
            return ["Year is not a valid number"]

        if year_value < self.min_year or year_value > self.max_year:
            return [
                f"Year outside allowed range ({self.min_year}-{self.max_year})"
            ]
        return []

    @staticmethod
    def _rule_genre_missing(book: Dict[str, Any]) -> List[str]:
        genre = (book.get("genre") or "").strip()
        if not genre:
            return ["Genre is missing"]
        return []

    def _rule_bitrate_below_minimum(self, book: Dict[str, Any]) -> List[str]:
        if self.min_bitrate <= 0:
            return []

        bitrate = book.get("bitrate")
        if bitrate in (None, ""):
            return []

        try:
            bitrate_value = int(bitrate)
        except (TypeError, ValueError):
            return ["Bitrate is not a valid number"]

        if bitrate_value < self.min_bitrate:
            return [f"Bitrate below minimum ({self.min_bitrate} kbps)"]
        return []
