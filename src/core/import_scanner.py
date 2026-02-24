"""Scenario-aware import preference application for scanned book metadata."""

import os
import re
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
        self.trim_whitespace = False
        self.strip_leading_punctuation = False
        self.remove_non_alphanumeric = False
        self.proper_case_fields = False
        self.move_leading_the_title = False

    def configure(
        self,
        scenario_mode: str,
        author_fallback_mode: str,
        title_fallback_mode: str,
        reader_keywords: List[str],
        trim_whitespace: bool = False,
        strip_leading_punctuation: bool = False,
        remove_non_alphanumeric: bool = False,
        proper_case_fields: bool = False,
        move_leading_the_title: bool = False,
    ):
        self.scenario_mode = scenario_mode or "mass_standard"
        self.author_fallback_mode = author_fallback_mode or "folder"
        self.title_fallback_mode = title_fallback_mode or "file"
        self.trim_whitespace = bool(trim_whitespace)
        self.strip_leading_punctuation = bool(strip_leading_punctuation)
        self.remove_non_alphanumeric = bool(remove_non_alphanumeric)
        self.proper_case_fields = bool(proper_case_fields)
        self.move_leading_the_title = bool(move_leading_the_title)

        cleaned = [keyword.strip().lower()
                   for keyword in reader_keywords if keyword and keyword.strip()]
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
            narrator = self._extract_reader_from_comment(
                book.get("comment", ""))
            if narrator:
                book["narrator"] = narrator

        title = (book.get("title") or "").strip()
        if self._is_placeholder_title(title):
            if self.title_fallback_mode == "folder" and folder:
                fallback_title = os.path.basename(folder.rstrip("\\/"))
                if fallback_title:
                    book["title"] = fallback_title
                    fallback_applied.add("Title")
                    self._append_flag_once(
                        book,
                        "F: Title fallback from folder used",
                    )
            elif self.title_fallback_mode == "file" and files:
                fallback_title = os.path.splitext(
                    os.path.basename(files[0]))[0]
                if fallback_title:
                    book["title"] = fallback_title
                    fallback_applied.add("Title")
                    self._append_flag_once(
                        book,
                        "F: Title fallback from file used",
                    )

        author = (book.get("author") or "").strip()
        if self._is_placeholder_author(author) and self.author_fallback_mode == "folder" and folder:
            fallback_author = self._fallback_author_from_path(
                folder=folder,
                files=files,
                title_hint=(book.get("title") or "").strip(),
            )
            if fallback_author:
                book["author"] = fallback_author
                fallback_applied.add("Author")
                self._append_flag_once(
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
            series_name = os.path.basename(
                os.path.dirname(files[0]).rstrip("\\/"))
            book_folder_name = os.path.basename(
                folder.rstrip("\\/")) if folder else ""
            if series_name and series_name.lower() != book_folder_name.lower():
                book["series"] = series_name
        elif self.scenario_mode == "series_from_filename" and files:
            series_name = self._series_from_filename(files[0])
            if series_name:
                book["series"] = series_name

        field_corrections = self._apply_auto_corrections(book)
        # Only flag Title and Author corrections, but exclude fields that already have fallback flags
        for field in ["Title", "Author"]:
            if field in field_corrections and field not in fallback_applied:
                corrections = field_corrections[field]
                # Create specific message for each correction
                correction_text = ", ".join(corrections)
                self._append_flag_once(
                    book,
                    f"C: {field} {correction_text}",
                )

    @staticmethod
    def _append_flag_once(book: Dict, message: str):
        """Append a flag message to book errors exactly once (case-insensitive)."""
        if not message:
            return
        errors = book.setdefault("errors", [])
        existing = {
            str(err).strip().lower() for err in errors if str(err).strip()
        }
        normalized = message.strip().lower()
        if normalized not in existing:
            errors.append(message)

    def _extract_reader_from_comment(self, comment: str) -> str:
        if not comment:
            return ""

        lines = [line.strip() for line in comment.splitlines() if line.strip()]
        for line in lines:
            lowered = line.lower()
            for keyword in self.reader_keywords:
                match = re.search(
                    rf"\b{re.escape(keyword)}\b\s*[:\-]?\s*(.+)$", lowered)
                if match:
                    start_idx = match.start(1)
                    value = line[start_idx:].strip(" .:-")
                    if value:
                        return value
        return ""

    @staticmethod
    def _series_from_filename(file_path: str) -> str:
        if not file_path:
            return ""
        stem = os.path.splitext(os.path.basename(file_path))[0]
        match = re.search(r"\(([^()]+)\)", stem)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _folder_parent_name(folder: str) -> str:
        if not folder:
            return ""
        parent = os.path.dirname(folder.rstrip("\\/"))
        return os.path.basename(parent.rstrip("\\/")) if parent else ""

    def _fallback_author_from_path(self, folder: str, files: List[str], title_hint: str) -> str:
        folder_name = os.path.basename(folder.rstrip("\\/")) if folder else ""
        parent_name = self._folder_parent_name(folder)
        title_lower = title_hint.lower() if title_hint else ""

        if self._is_placeholder_author(folder_name) and parent_name:
            return parent_name

        if self.scenario_mode == "series_from_directory":
            if parent_name:
                return parent_name
            return folder_name

        if title_lower and folder_name and folder_name.lower() == title_lower and parent_name:
            return parent_name

        if folder_name:
            return folder_name

        if files:
            file_dir = os.path.dirname(files[0])
            file_dir_name = os.path.basename(
                file_dir.rstrip("\\/")) if file_dir else ""
            file_parent_name = self._folder_parent_name(file_dir)

            if self._is_placeholder_author(file_dir_name) and file_parent_name:
                return file_parent_name

            if title_lower and file_dir_name and file_dir_name.lower() == title_lower and file_parent_name:
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
        """Apply auto-corrections and return mapping of field -> list of corrections."""
        fields = ["author", "title", "series", "genre", "narrator"]
        field_corrections: Dict[str, List[str]] = {}

        for field in fields:
            value = book.get(field)
            if not isinstance(value, str) or not value:
                continue

            corrections_applied = []
            updated = value

            if self.trim_whitespace:
                trimmed = " ".join(updated.split())
                if trimmed != updated:
                    corrections_applied.append("trimmed")
                    updated = trimmed

            if self.strip_leading_punctuation:
                stripped = re.sub(r"^[^A-Za-z0-9]+", "", updated)
                if stripped != updated:
                    corrections_applied.append("punctuation removed")
                    updated = stripped

            if self.remove_non_alphanumeric:
                cleaned = re.sub(r"[^A-Za-z0-9\s\.,!?&:;()\-'/]", "", updated)
                cleaned = re.sub(r"\s{2,}", " ", cleaned)
                if cleaned != updated:
                    corrections_applied.append("special characters removed")
                    updated = cleaned

            if self.proper_case_fields:
                proper_cased = " ".join(word.capitalize()
                                        for word in updated.split(" "))
                if proper_cased != updated:
                    # Apply proper case but don't flag it
                    updated = proper_cased

            normalized_updated = updated.strip()
            if corrections_applied:
                field_corrections[field.title()] = corrections_applied

            book[field] = normalized_updated

        if self.move_leading_the_title:
            title = (book.get("title") or "").strip()
            if title.lower().startswith("the ") and len(title) > 4:
                title_core = title[4:].strip()
                if title_core and not title_core.lower().endswith(", the"):
                    # Move "The" to end but don't flag it
                    book["title"] = f"{title_core}, The"

        return field_corrections
