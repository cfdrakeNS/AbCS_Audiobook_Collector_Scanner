"""Scenario-aware import preference application for scanned book metadata."""

import re
import os
from typing import Dict, List


class ImportScanner:
    """Applies scenario, fallback, and reader parsing rules to scanned books."""

    AUTHOR_PLACEHOLDERS = {
        "",
        "unknown",
        "unknown author",
        "no author",
        "various",
        "various artists",
        "n/a",
        "na",
        "none",
        "null",
    }

    TITLE_PLACEHOLDERS = {
        "",
        "unknown",
        "unknown album",
        "no album",
        "untitled",
        "n/a",
        "na",
        "none",
        "null",
    }

    def __init__(self):
        self.scenario_mode = "mass_standard"
        self.author_fallback_mode = "folder"
        self.title_fallback_mode = "file"
        self.reader_keywords = ["reader", "read by", "narrator", "narrated by"]

    def configure(
        self,
        scenario_mode: str,
        author_fallback_mode: str = None,
        title_fallback_mode: str = None,
        reader_keywords: List[str] = None,
    ):
        self.scenario_mode = scenario_mode or "mass_standard"
        self.author_fallback_mode = (
            author_fallback_mode if author_fallback_mode else None
        )
        self.title_fallback_mode = title_fallback_mode if title_fallback_mode else None

        if reader_keywords:
            cleaned = [
                keyword.strip().lower()
                for keyword in reader_keywords
                if keyword and keyword.strip()
            ]
            if cleaned:
                self.reader_keywords = cleaned

    def apply_preferences(self, book: Dict):
        book.setdefault("series", "")
        book.setdefault("errors", [])
        folder = (book.get("folder") or "").strip()
        files = book.get("files") or []

        # Track which fields had fallback applied
        fallback_applied = set()

        narrator = (book.get("narrator") or "").strip()
        if not narrator:
            narrator = self._extract_reader_from_comment(book.get("comment", ""))
            if narrator:
                book["narrator"] = narrator

        title = (book.get("title") or "").strip()
        if self._is_placeholder_title(title) and self.title_fallback_mode == "file":
            # Fallback for all scenarios: use file stem only
            if files:
                fallback_title = os.path.splitext(os.path.basename(files[0]))[0]
                # Remove leading number and trim
                fallback_title = re.sub(r"^\d+\s*", "", fallback_title).strip()
                if fallback_title:
                    book["title"] = fallback_title
                    fallback_applied.add("Title")
                    from src.core.validator import ImportValidator

                    ImportValidator.append_flag_once(
                        book,
                        "F: Title fallback from file used",
                    )

        author = (book.get("author") or "").strip()
        if (
            self._is_placeholder_author(author)
            and self.author_fallback_mode == "folder"
            and folder
        ):
            fallback_author = self._fallback_author_from_path(
                folder=folder,
                files=files,
                title_hint=(book.get("title") or "").strip(),
            )
            if fallback_author:
                book["author"] = fallback_author
                fallback_applied.add("Author")
                from src.core.validator import ImportValidator

                ImportValidator.append_flag_once(
                    book,
                    "F: Author fallback from folder used",
                )

        author = (book.get("author") or "").strip()
        title = (book.get("title") or "").strip()
        if author and title and author.lower() == title.lower():
            parent_name = self._folder_parent_name(folder)
            if parent_name and parent_name.lower() != title.lower():
                book["author"] = parent_name

        if self.scenario_mode == "series_from_directory" and files:
            series_name, ambiguous_reason = self._derive_series_from_directory(
                book=book,
                folder=folder,
                files=files,
            )
            if series_name:
                book["series"] = series_name
            elif ambiguous_reason:
                from src.core.validator import ImportValidator

                ImportValidator.append_flag_once(
                    book,
                    f"W: Series from directory skipped ({ambiguous_reason})",
                )
        elif self.scenario_mode == "series_from_filename" and files:
            source_text = os.path.splitext(os.path.basename(files[0]))[0]

            parsed_series, parsed_number, _raw_block = (
                self._parse_series_from_filename_text(source_text)
            )
            if parsed_series:
                book["series"] = parsed_series

            if parsed_number:
                current_title = (book.get("title") or "").strip()
                if current_title:
                    suffix = f" - {parsed_number}"
                    if not current_title.endswith(suffix):
                        book["title"] = f"{current_title}{suffix}"

        field_corrections = self._apply_auto_corrections(book)
        # Only flag Title and Author corrections, but exclude fields that already have fallback flags
        for field in ["Title", "Author"]:
            if field in field_corrections and field not in fallback_applied:
                corrections = field_corrections[field]
                # Create specific message for each correction
                correction_text = ", ".join(corrections)
                from src.core.validator import ImportValidator

                ImportValidator.append_flag_once(
                    book,
                    f"C: {field} {correction_text}",
                )

    # Error/correction flagging now uses ImportValidator.append_flag_once

    def _extract_reader_from_comment(self, comment: str) -> str:
        if not comment:
            return ""

        lines = [line.strip() for line in comment.splitlines() if line.strip()]
        for line in lines:
            lowered = line.lower()
            for keyword in self.reader_keywords:
                match = re.search(
                    rf"\b{re.escape(keyword)}\b\s*[:\-]?\s*(.+)$", lowered
                )
                if match:
                    start_idx = match.start(1)
                    value = line[start_idx:].strip(" .:-")
                    if value:
                        return value
        return ""

    @staticmethod
    def _parse_series_from_filename_text(text: str):
        """Parse first parenthesized block from text into series name/number/raw block."""
        if not text:
            return (None, None, None)

        match = re.search(r"\(([^()]*)\)", str(text))
        if not match:
            return (None, None, None)

        raw_block = match.group(1).strip()
        if not raw_block:
            return (None, None, "")

        trailing_number_match = re.match(r"^(.*?)(?:\s+)(\d+)$", raw_block)
        if not trailing_number_match:
            return (raw_block, None, raw_block)

        series_name = trailing_number_match.group(1).strip()
        series_number = trailing_number_match.group(2).strip()
        if not series_name:
            return (raw_block, None, raw_block)

        return (series_name, series_number, raw_block)

    @staticmethod
    def _folder_parent_name(folder: str) -> str:
        if not folder:
            return ""
        parent = os.path.dirname(folder.rstrip("\\/"))
        return os.path.basename(parent.rstrip("\\/")) if parent else ""

    def _derive_series_from_directory(self, book: Dict, folder: str, files: List[str]):
        """Return (series_name, ambiguous_reason) for scenario series_from_directory."""
        candidate_folder = (folder or "").strip()
        if not candidate_folder and files:
            candidate_folder = os.path.dirname(files[0])

        candidate_folder = candidate_folder.rstrip("\\/")
        if not candidate_folder:
            return (None, "missing folder path")

        series_candidate = os.path.basename(candidate_folder)
        parent_folder = os.path.dirname(candidate_folder)
        author_candidate = (
            os.path.basename(parent_folder.rstrip("\\/")) if parent_folder else ""
        )

        if not series_candidate:
            return (None, "missing series folder name")
        if not author_candidate:
            return (None, "missing author folder name")

        author_text = (book.get("author") or "").strip()
        if author_text:
            if series_candidate.casefold() == author_text.casefold():
                return (None, "series folder matches author")
            if author_candidate.casefold() != author_text.casefold():
                return (None, "folder does not match author/series pattern")

        return (series_candidate, None)

    def _fallback_author_from_path(
        self, folder: str, files: List[str], title_hint: str
    ) -> str:
        folder_name = os.path.basename(folder.rstrip("\\/")) if folder else ""
        parent_name = self._folder_parent_name(folder)
        title_lower = title_hint.lower() if title_hint else ""

        if self._is_placeholder_author(folder_name) and parent_name:
            return parent_name

        if self.scenario_mode == "series_from_directory":
            if parent_name:
                return parent_name
            return folder_name

        if (
            title_lower
            and folder_name
            and folder_name.lower() == title_lower
            and parent_name
        ):
            return parent_name

        if folder_name:
            return folder_name

        if files:
            file_dir = os.path.dirname(files[0])
            file_dir_name = os.path.basename(file_dir.rstrip("\\/")) if file_dir else ""
            file_parent_name = self._folder_parent_name(file_dir)

            if self._is_placeholder_author(file_dir_name) and file_parent_name:
                return file_parent_name

            if (
                title_lower
                and file_dir_name
                and file_dir_name.lower() == title_lower
                and file_parent_name
            ):
                return file_parent_name
            if file_dir_name:
                return file_dir_name

        return ""

    @classmethod
    def _normalize_placeholder_text(cls, value: str) -> str:
        return " ".join(str(value or "").strip().lower().replace("_", " ").split())

    @classmethod
    def _is_placeholder_author(cls, value: str) -> bool:
        normalized = cls._normalize_placeholder_text(value)
        return normalized in cls.AUTHOR_PLACEHOLDERS

    @classmethod
    def _is_placeholder_title(cls, value: str) -> bool:
        normalized = cls._normalize_placeholder_text(value)
        return normalized in cls.TITLE_PLACEHOLDERS

    def _apply_auto_corrections(self, book: Dict) -> Dict[str, List[str]]:
        """Apply auto-corrections (always on) and return mapping of field -> list of corrections."""
        fields = ["author", "title", "series", "genre", "narrator"]
        field_corrections: Dict[str, List[str]] = {}

        for field in fields:
            value = book.get(field)
            if not isinstance(value, str) or not value:
                continue

            corrections_applied = []
            updated = value

            # Trim whitespace — always applied
            trimmed = " ".join(updated.split())
            if trimmed != updated:
                corrections_applied.append("trimmed")
                updated = trimmed

            # Strip leading punctuation — always applied
            stripped = re.sub(r"^[^A-Za-z0-9]+", "", updated)
            if stripped != updated:
                corrections_applied.append("punctuation removed")
                updated = stripped

            # Remove non-printable characters — always applied
            cleaned = "".join(c for c in updated if c.isprintable())
            if cleaned != updated:
                corrections_applied.append("non-printable characters removed")
                updated = cleaned

            # Proper case — always applied
            proper_cased = " ".join(
                word.capitalize() for word in updated.split(" ")
            )
            if proper_cased != updated:
                # Apply proper case but don't flag it
                updated = proper_cased

            normalized_updated = updated.strip()
            if corrections_applied:
                field_corrections[field.title()] = corrections_applied

            book[field] = normalized_updated

        return field_corrections
