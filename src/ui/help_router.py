"""Map AbCS windows to context-sensitive help documents.

``WINDOW_HELP_MAP`` selects which markdown file Shift+F1 opens for each window
class. This is independent of the dynamic topic list in HelpWindow (see
``help_paths.discover_help_topics()``). When adding a window, add a map entry and
a matching ``help_docs/nn_topic.md`` file.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget

from src.accessibility.help_paths import OVERVIEW_DOC, help_doc_exists
from src.accessibility.help_scaling import resolve_initial_help_scale
from src.ui.help_window import HelpWindow

FALLBACK_DOC = OVERVIEW_DOC

DUPLICATE_MODE_DOC = "08_duplicate_mode.md"

WINDOW_HELP_MAP: dict[str, str] = {
    "MainWindow": "03_find_filters.md",
    "ImportWindow": "02_import.md",
    "ImportProgressWindow": "02_import.md",
    "ImportDetailWindow": "12_import_detail.md",
    "BookDetailsWindow": "04_book_details.md",
    "UpdateWindow": "05_update.md",
    "CollectionWindow": "06_collections.md",
    "WebMetadataWindow": "07_web_metadata.md",
    "BackupRestoreWindow": "09_backup_restore.md",
    "PreferencesWindow": "10_preferences.md",
    "BookListImportWindow": "11_import_book_list.md",
    "ReadingHistoryWindow": "13_reading_history.md",
    "StatisticsDialog": "14_statistics.md",
    "NameListWindow": "15_name_list.md",
}


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
    help_scale = resolve_initial_help_scale(scaler)
    dlg = HelpWindow(scaler, parent, doc_filename=doc_filename, help_scale=help_scale)
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
