"""Scenario-aware import preference application for scanned book metadata."""

import os
import re
from typing import Dict, List


class ImportScanner:
    """Applies scenario, fallback, and reader parsing rules to scanned books."""

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
        folder = (book.get("folder") or "").strip()
        files = book.get("files") or []

        narrator = (book.get("narrator") or "").strip()
        if not narrator:
            narrator = self._extract_reader_from_comment(
                book.get("comment", ""))
            if narrator:
                book["narrator"] = narrator

        title = (book.get("title") or "").strip()
        if not title:
            if self.title_fallback_mode == "folder" and folder:
                fallback_title = os.path.basename(folder.rstrip("\\/"))
                if fallback_title:
                    book["title"] = fallback_title
            elif self.title_fallback_mode == "file" and files:
                fallback_title = os.path.splitext(
                    os.path.basename(files[0]))[0]
                if fallback_title:
                    book["title"] = fallback_title

        author = (book.get("author") or "").strip()
        if not author and self.author_fallback_mode == "folder" and folder:
            fallback_author = self._fallback_author_from_path(
                folder=folder,
                files=files,
                title_hint=(book.get("title") or "").strip(),
            )
            if fallback_author:
                book["author"] = fallback_author

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

        self._apply_auto_corrections(book)

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

            if title_lower and file_dir_name and file_dir_name.lower() == title_lower and file_parent_name:
                return file_parent_name
            if file_dir_name:
                return file_dir_name

        return ""

    def _apply_auto_corrections(self, book: Dict):
        fields = ["author", "title", "series", "genre", "narrator"]

        for field in fields:
            value = book.get(field)
            if not isinstance(value, str) or not value:
                continue

            updated = value
            if self.trim_whitespace:
                updated = " ".join(updated.split())
            if self.strip_leading_punctuation:
                updated = re.sub(r"^[^A-Za-z0-9]+", "", updated)
            if self.remove_non_alphanumeric:
                updated = re.sub(r"[^A-Za-z0-9\s\.,!?&:;()\-'/]", "", updated)
                updated = re.sub(r"\s{2,}", " ", updated)
            if self.proper_case_fields:
                updated = " ".join(word.capitalize()
                                   for word in updated.split(" "))

            book[field] = updated.strip()

        if self.move_leading_the_title:
            title = (book.get("title") or "").strip()
            if title.lower().startswith("the ") and len(title) > 4:
                title_core = title[4:].strip()
                if title_core and not title_core.lower().endswith(", the"):
                    book["title"] = f"{title_core}, The"
