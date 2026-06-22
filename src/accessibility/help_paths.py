"""Resolve help documentation paths for dev and installed builds."""

from __future__ import annotations

import sys
from pathlib import Path

from src.accessibility.graphics_paths import bundle_base, project_root

OVERVIEW_DOC = "01_overview.md"

HELP_TOPICS: list[tuple[str, str]] = [
    ("Overview", "01_overview.md"),
    ("Import (Folder Scan)", "02_import_process.md"),
    ("Find and Filters", "03_find_filters_process.md"),
    ("Book Details", "04_book_details_process.md"),
    ("Update", "05_update_process.md"),
    ("Collections", "06_collections_process.md"),
    ("Web Metadata Fetch", "07_web_metadata_process.md"),
    ("Duplicate Mode", "08_duplicate_mode_process.md"),
    ("Backup and Restore", "09_backup_restore_process.md"),
    ("Preferences", "10_preferences_process.md"),
    ("Import Book List", "11_import_book_list_process.md"),
    ("Import Detail", "12_import_detail_process.md"),
    ("Reading History", "13_reading_history_process.md"),
    ("Statistics", "14_statistics_process.md"),
    ("Name List", "15_name_list_process.md"),
    ("Keyboard Shortcuts", "16_shortcuts_list.md"),
    ("Default Preferences", "17_default_preference.md"),
    ("Import Preferences", "18_import_preferences.md"),
]


def _search_bases() -> list[Path]:
    """Directories to search for help_docs (dev, frozen, and installed app)."""
    bases: list[Path] = []
    seen: set[Path] = set()

    def add_base(path: Path) -> None:
        resolved = path.resolve()
        if resolved in seen:
            return
        seen.add(resolved)
        bases.append(resolved)

    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            add_base(Path(meipass))
        if getattr(sys, "executable", None):
            add_base(Path(sys.executable).resolve().parent)

    add_base(bundle_base())
    root = project_root()
    if root.resolve() not in seen:
        add_base(root)

    return bases


def resolve_help_docs_dir() -> Path:
    """Return the directory containing markdown help files."""
    for base in _search_bases():
        candidate = base / "help_docs"
        if candidate.is_dir():
            return candidate.resolve()
    return (project_root() / "help_docs").resolve()


def resolve_help_doc_path(filename: str) -> Path:
    """Return the path to a help markdown file, or a predictable fallback."""
    safe_name = Path(filename).name
    docs_dir = resolve_help_docs_dir()
    return docs_dir / safe_name


def help_doc_exists(filename: str) -> bool:
    """True when the requested help file is present on disk."""
    return resolve_help_doc_path(filename).is_file()
