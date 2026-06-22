"""Map AbCS windows to context-sensitive help documents."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget

from src.accessibility.help_paths import HELP_TOPICS, OVERVIEW_DOC, help_doc_exists
from src.ui.help_window import HelpWindow

FALLBACK_DOC = OVERVIEW_DOC

DUPLICATE_MODE_DOC = "08_duplicate_mode_process.md"

WINDOW_HELP_MAP: dict[str, str] = {
    "MainWindow": "03_find_filters_process.md",
    "ImportWindow": "02_import_process.md",
    "ImportProgressWindow": "02_import_process.md",
    "ImportDetailWindow": "12_import_detail_process.md",
    "BookDetailsWindow": "04_book_details_process.md",
    "UpdateWindow": "05_update_process.md",
    "CollectionWindow": "06_collections_process.md",
    "WebMetadataWindow": "07_web_metadata_process.md",
    "BackupRestoreWindow": "09_backup_restore_process.md",
    "PreferencesWindow": "10_preferences_process.md",
    "BookListImportWindow": "11_import_book_list_process.md",
    "ReadingHistoryWindow": "13_reading_history_process.md",
    "StatisticsDialog": "14_statistics_process.md",
    "NameListWindow": "15_name_list_process.md",
}

DUPLICATE_MODE_DOC = "08_duplicate_mode_process.md"


def get_help_doc_filename(widget: QWidget | None) -> str:
    """Return the help markdown filename for a window or dialog."""
    if widget is None:
        return FALLBACK_DOC
    class_name = widget.__class__.__name__
    if class_name == "MainWindow" and getattr(widget, "duplicate_mode_active", False):
        doc_name = DUPLICATE_MODE_DOC
    else:
        doc_name = WINDOW_HELP_MAP.get(class_name, FALLBACK_DOC)
    if not help_doc_exists(doc_name):
        return FALLBACK_DOC
    return doc_name


def show_context_help(parent: QWidget | None) -> None:
    """Open context-sensitive help for the given parent window."""
    doc_name = get_help_doc_filename(parent)
    show_help_doc(parent, doc_name)


def show_overview_help(parent: QWidget | None) -> None:
    """Open the AbCS overview help index."""
    show_help_doc(parent, OVERVIEW_DOC)


def show_help_doc(parent: QWidget | None, doc_filename: str) -> None:
    """Open help for a specific markdown filename."""
    scaler = getattr(parent, "scaler", None)
    dlg = HelpWindow(scaler, parent, doc_filename=doc_filename)
    dlg.exec()


def install_shift_f1_help(
    window: QWidget,
    *,
    shortcut_context: Qt.ShortcutContext | None = None,
) -> QShortcut:
    """Register Shift+F1 to open context-sensitive help for a window."""
    shortcut = QShortcut(QKeySequence("Shift+F1"), window)
    if shortcut_context is not None:
        shortcut.setContext(shortcut_context)
    shortcut.activated.connect(lambda: show_context_help(window))
    return shortcut
