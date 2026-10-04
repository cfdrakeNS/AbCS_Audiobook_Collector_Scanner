from enum import Enum
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QCheckBox, QGroupBox
from PySide6.QtGui import QKeySequence, QShortcut
from typing import Dict, Callable, Optional, List, Tuple


class ShortcutContext(Enum):
    """Shortcut context - where shortcuts are active."""

    COLLECTION_WINDOW = "collection_window"
    MAIN_WINDOW = "main_window"
    BOOK_DETAILS = "book_details"
    WEB_METADATA = "web_metadata"
    IMPORT_WINDOW = "import_window"
    UPDATE_WINDOW = "update_window"
    PREFERENCES_WINDOW = "preferences_window"
    DUPLICATE_DIALOG = "duplicate_dialog"
    BACKUP_RESTORE_WINDOW = "backup_restore_window"
    NAMELIST_WINDOW = "namelist_window"
    READING_HISTORY_WINDOW = "reading_history_window"
    BOOK_LIST_IMPORT_WINDOW = "book_list_import_window"
    IMPORT_DETAIL_WINDOW = "import_detail_window"
    PATH_HEALTH_WINDOW = "path_health_window"
    PREVIEW_WINDOW = "preview_window"
    HELP_WINDOW = "help_window"
    BATCH_WEB_FETCH_SUMMARY = "batch_web_fetch_summary"


COLLECTION_WINDOW_SHORTCUTS = {
    "L": ("Jump to list", "table"),
    "E": ("Edit selected row", "edit_button"),
    "D": ("Delete", "delete_button"),
    "B": ("Browse collection folder", "browse_button"),
    "M": ("Name", "name_edit"),
    "F": ("Collection folder", "root_edit"),
    "A": ("Active", "active_check"),
}

NAMELIST_WINDOW_SHORTCUTS = {
    "L": ("Jump to list", "table"),
    "E": ("Edit selected row", "edit_button"),
    "S": ("Sort", "sort_combo"),
    "A": ("Active checkbox", "active_check"),
}

BACKUP_RESTORE_WINDOW_SHORTCUTS = {
    "L": ("Backup list", "backup_list"),
    "B": ("Browse", "browse_button"),
    "K": ("Create backup", "backup_button"),
    "T": ("Focus restore file", "restore_path_edit"),
    "R": ("Restore", "restore_button"),
    "D": ("Delete", "delete_button"),
    "F": ("Full reset", "full_reset_button"),
}

READING_HISTORY_WINDOW_SHORTCUTS = {
    "L": ("Jump to list", "table"),
    "S": ("Search", "refresh_button"),
    "F": ("From date", "start_date_edit"),
    "G": ("General tab", "general_tab"),
    "Y": ("Year tab", "year_tab"),
    "M": ("Month tab", "month_tab"),
    "R": ("Date Range tab", "range_tab"),
}

PREVIEW_WINDOW_SHORTCUTS = {
    "N": ("Next track", "next_button"),
    "P": ("Previous track", "previous_button"),
    "S": ("Speed", "speed_combo"),
}

HELP_WINDOW_SHORTCUTS = {
    "L": ("Jump to the left list (topics, sections, or results)", "nav_list"),
}

BATCH_WEB_FETCH_SUMMARY_SHORTCUTS = {
    "A": ("Apply all", "apply_button"),
    "R": ("Review each", "review_button"),
    "L": ("Book list", "book_list"),
}

DUPLICATE_DIALOG_SHORTCUTS = {
    "R": ("Start duplicate check", "start_button"),
    "M": ("Focus match type combo", "mode_combo"),
}

PATH_HEALTH_WINDOW_SHORTCUTS = {
    "C": ("Collection", "collection_combo"),
    "F": ("Filter", "filter_combo"),
    "I": ("Info instructions", "guide_label"),
    "S": ("Scan", "scan_button"),
    "L": ("Focus check book locations list", "path_list_table"),
    "X": ("Export list to CSV", "export_button"),
}

MAIN_WINDOW_SHORTCUTS = {
    "L": ("Jump to list", "book_list"),
    "U": ("Update selected", "update_button"),
    "D": ("Delete selected", "delete_button"),
    "X": ("Export duplicates", "export_button"),
    "P": ("Toggle plot filter", "plot_filter_toggle"),
    "R": ("Toggle read filter", "read_filter_toggle"),
    "T": ("Toggle want to read filter", "want_to_read_filter_toggle"),
    "A": ("Author filter", "author_filter_combo"),
    "W": ("Fetch web info (batch when two or more selected)", "get_web_info"),
    # Alt+1..7 handled in main_window.py for column jump
}

BOOK_DETAILS_SHORTCUTS = {
    "T": ("Title", "title_edit"),
    "A": ("Author", "author_label_display"),  # View label (QLineEdit) - always accessible
    "P": ("Plot", "comments_edit"),  # From Pl&ot label
    "Y": ("Year", "year_spin"),
    "M": ("Time", "time_edit"),  # From &Time label
    "N": ("Narrator", "reader_edit"),
    "R": ("Read date", "read_date"),
    "S": ("Series", "series_label_display"),  # View label (QLineEdit) - always accessible
    "G": ("Genre", "genre_label_display"),  # View label (QLineEdit) - always accessible
    "C": ("Collection", "collection_label_display"),  # View label (QLineEdit) - always accessible
    "K": ("Want to read", "want_to_read_checkbox"),
    "H": ("Path", "path_edit"),  # From Pat&h label
    "B": ("Browse path", "browse_path_button"),
    "W": ("Get web info", "get_web_details_button"),
    # "E" (Edit) handled locally in book_details.py to trigger action
    "F1": ("Show help", "show_help"),
}

IMPORT_DETAIL_WINDOW_SHORTCUTS = {
    "T": ("Title", "title_edit"),
    "A": ("Author", "author_combo"),
    "P": ("Plot", "comments_edit"),
    "Y": ("Year", "year_spin"),
    "M": ("Time", "time_edit"),
    "N": ("Narrator", "reader_edit"),
    "I": ("Series", "series_combo"),
    "G": ("Genre", "genre_combo"),
    "C": ("Collection", "collection_combo"),
    "E": ("Errors", "errors_edit"),
    "H": ("Path", "path_edit"),
    "K": ("Keep", "keep_button"),
    "D": ("Discard", "skip_button"),
}

WEB_METADATA_SHORTCUTS = {
    "T": ("Title", "title_edit"),
    "A": ("Author", "author_edit"),
    "P": ("Plot", "plot_edit"),
    "Y": ("Year", "year_edit"),
    "G": ("Genre", "genre_edit"),
    "R": ("Rating", "rating_edit"),
    "F": ("Re-fetch web data", "refetch_button"),
    "K": ("Skip this book", "skip_button"),
}

# Import Window
IMPORT_WINDOW_SHORTCUTS = {
    "C": ("Collection field", "collection_combo"),
    "F": ("Folder field", "folder_field"),
    "B": ("Browse", "browse_button"),
    "E": ("Error filter", "error_filter"),
    "I": ("Import", "scan_button"),
    "S": ("Import Selected", "import_selected_button"),
    "L": ("Focus import list table", "import_list_table"),
    "X": ("Export list to CSV", "export_button"),
}

# Book List Import Window
BOOK_LIST_IMPORT_WINDOW_SHORTCUTS = {
    "C": ("Collection", "collection_combo"),
    "B": ("Browse for file", "browse_button"),
    "O": ("Options group", "options_group"),
    "T": ("Title field mapping", "title_mapping"),
    "A": ("Author field mapping", "author_mapping"),
    "Y": ("Year field mapping", "year_mapping"),
    "P": ("Plot field mapping", "plot_mapping"),
    "S": ("Series field mapping", "series_mapping"),
    "N": ("Series number field mapping", "series_number_mapping"),
    "G": ("Genre field mapping", "genre_mapping"),
    "R": ("Narrator field mapping", "reader_mapping"),
    "E": ("Read Date field mapping", "read_date_mapping"),
    "M": ("Time field mapping", "time_mapping"),
    "F": ("Files field mapping", "tracks_mapping"),
    "I": ("Import books", "import_button"),
    "X": ("Export errors to CSV", "export_button"),
}

UPDATE_WINDOW_SHORTCUTS = {
    "S": ("Series", "series_combo"),
    "G": ("Genre", "genre_combo"),
    "C": ("Collection", "collection_combo"),
    "L": ("Focus book list", "book_list"),
}


PREFERENCES_WINDOW_SHORTCUTS = {
    "D": ("Display Settings tab", "theme_picker"),
    "P": ("Import Settings tab", "import_dir_edit"),
    "B": ("Browse", "browse_button"),
    "F": ("Fallback & Auto Correct tab", "author_fallback_checkbox"),
    "V": ("Validation Rules tab", "rules_section_text"),
    "R": ("Restore Defaults", "restore_defaults_button"),
    "/": ("Status bar", "status_bar"),
}


_CONTEXT_SHORTCUTS: Dict[ShortcutContext, Dict[str, Tuple[str, str]]] = {
    ShortcutContext.COLLECTION_WINDOW: COLLECTION_WINDOW_SHORTCUTS,
    ShortcutContext.MAIN_WINDOW: MAIN_WINDOW_SHORTCUTS,
    ShortcutContext.BOOK_DETAILS: BOOK_DETAILS_SHORTCUTS,
    ShortcutContext.WEB_METADATA: WEB_METADATA_SHORTCUTS,
    ShortcutContext.IMPORT_WINDOW: IMPORT_WINDOW_SHORTCUTS,
    ShortcutContext.UPDATE_WINDOW: UPDATE_WINDOW_SHORTCUTS,
    ShortcutContext.PREFERENCES_WINDOW: PREFERENCES_WINDOW_SHORTCUTS,
    ShortcutContext.DUPLICATE_DIALOG: DUPLICATE_DIALOG_SHORTCUTS,
    ShortcutContext.BACKUP_RESTORE_WINDOW: BACKUP_RESTORE_WINDOW_SHORTCUTS,
    ShortcutContext.NAMELIST_WINDOW: NAMELIST_WINDOW_SHORTCUTS,
    ShortcutContext.READING_HISTORY_WINDOW: READING_HISTORY_WINDOW_SHORTCUTS,
    ShortcutContext.BOOK_LIST_IMPORT_WINDOW: BOOK_LIST_IMPORT_WINDOW_SHORTCUTS,
    ShortcutContext.IMPORT_DETAIL_WINDOW: IMPORT_DETAIL_WINDOW_SHORTCUTS,
    ShortcutContext.PATH_HEALTH_WINDOW: PATH_HEALTH_WINDOW_SHORTCUTS,
    ShortcutContext.PREVIEW_WINDOW: PREVIEW_WINDOW_SHORTCUTS,
    ShortcutContext.HELP_WINDOW: HELP_WINDOW_SHORTCUTS,
    ShortcutContext.BATCH_WEB_FETCH_SUMMARY: BATCH_WEB_FETCH_SUMMARY_SHORTCUTS,
}


def shortcuts_for_context(context: ShortcutContext) -> Dict[str, Tuple[str, str]]:
    """Central Alt+key map for a window (empty when the window has none)."""
    return _CONTEXT_SHORTCUTS.get(context, {})


def allowed_alt_letters(context: ShortcutContext, *extra: str) -> set:
    """Alt letters a window maps, for ``is_unmapped_alt_letter`` allow-lists."""
    letters = {key.upper() for key in shortcuts_for_context(context) if len(key) == 1}
    return letters | {item.upper() for item in extra}


class ShortcutManager(QObject):
    """
    Manages keyboard shortcuts across the application.
    Provides centralized shortcut registration and documentation.
    """

    COLLECTION_WINDOW_SHORTCUTS = COLLECTION_WINDOW_SHORTCUTS
    NAMELIST_WINDOW_SHORTCUTS = NAMELIST_WINDOW_SHORTCUTS
    BACKUP_RESTORE_WINDOW_SHORTCUTS = BACKUP_RESTORE_WINDOW_SHORTCUTS
    READING_HISTORY_WINDOW_SHORTCUTS = READING_HISTORY_WINDOW_SHORTCUTS
    READING_HISTORY_SHORTCUTS = READING_HISTORY_WINDOW_SHORTCUTS
    DUPLICATE_DIALOG_SHORTCUTS = DUPLICATE_DIALOG_SHORTCUTS
    PATH_HEALTH_WINDOW_SHORTCUTS = PATH_HEALTH_WINDOW_SHORTCUTS
    MAIN_WINDOW_SHORTCUTS = MAIN_WINDOW_SHORTCUTS
    BOOK_DETAILS_SHORTCUTS = BOOK_DETAILS_SHORTCUTS
    IMPORT_DETAIL_WINDOW_SHORTCUTS = IMPORT_DETAIL_WINDOW_SHORTCUTS
    WEB_METADATA_SHORTCUTS = WEB_METADATA_SHORTCUTS
    IMPORT_WINDOW_SHORTCUTS = IMPORT_WINDOW_SHORTCUTS
    BOOK_LIST_IMPORT_WINDOW_SHORTCUTS = BOOK_LIST_IMPORT_WINDOW_SHORTCUTS
    UPDATE_WINDOW_SHORTCUTS = UPDATE_WINDOW_SHORTCUTS
    PREFERENCES_WINDOW_SHORTCUTS = PREFERENCES_WINDOW_SHORTCUTS
    PREVIEW_WINDOW_SHORTCUTS = PREVIEW_WINDOW_SHORTCUTS
    HELP_WINDOW_SHORTCUTS = HELP_WINDOW_SHORTCUTS
    BATCH_WEB_FETCH_SUMMARY_SHORTCUTS = BATCH_WEB_FETCH_SUMMARY_SHORTCUTS

    def __init__(self):
        """Initialize shortcut manager."""
        super().__init__()
        self._shortcuts = {}

    def register_alt_shortcuts(
        self,
        widget: QWidget,
        context: ShortcutContext,
        callback_map: Dict[str, Callable],
        *,
        shortcut_context: Qt.ShortcutContext = Qt.WindowShortcut,
    ):
        """
        Register Alt+Key shortcuts for a widget.

        Args:
            widget: Widget to register shortcuts on
            context: Shortcut context
            callback_map: Map of widget_id to callback function
                         e.g., {'collection_combo': self.on_collection_focus}
            shortcut_context: Qt shortcut context for the created QShortcuts
        """
        shortcuts = shortcuts_for_context(context)
        if not shortcuts:
            return

        # Register each shortcut
        for key, (description, widget_id) in shortcuts.items():
            if widget_id in callback_map:
                # Handle function keys (F1-F12) as true function keys, not Alt+F1
                if key.upper().startswith("F") and key[1:].isdigit():
                    qt_key = getattr(Qt, f"Key_{key.upper()}", None)
                    if qt_key is not None:
                        key_seq = QKeySequence(qt_key)
                    else:
                        key_seq = QKeySequence(key)
                elif key == "/":
                    key_seq = QKeySequence("Alt+/")
                elif key == "Escape":
                    key_seq = QKeySequence(Qt.Key_Escape)
                else:
                    key_seq = QKeySequence(f"Alt+{key}")
                shortcut = QShortcut(key_seq, widget)
                shortcut.setContext(shortcut_context)
                shortcut.activated.connect(callback_map[widget_id])
                shortcut_id = f"{context.value}_{key}"
                self._shortcuts[shortcut_id] = shortcut


# Global shortcut manager instance
_shortcut_manager: Optional[ShortcutManager] = None


def get_shortcut_manager() -> ShortcutManager:
    """
    Get global shortcut manager instance.

    Returns:
        ShortcutManager instance
    """
    global _shortcut_manager
    if _shortcut_manager is None:
        _shortcut_manager = ShortcutManager()
    return _shortcut_manager


def _extract_mnemonic(text: str) -> Optional[str]:
    """Extract Qt mnemonic letter from text with ampersand notation."""
    if not text:
        return None

    idx = 0
    while idx < len(text) - 1:
        if text[idx] == "&":
            nxt = text[idx + 1]
            if nxt == "&":
                idx += 2
                continue
            if nxt.isalpha():
                return nxt.upper()
        idx += 1
    return None


def find_shortcut_conflicts(widget: QWidget) -> List[str]:
    """Find duplicate keyboard shortcut declarations in a widget tree."""
    conflicts: List[str] = []

    shortcut_map: Dict[str, List[str]] = {}
    for shortcut in widget.findChildren(QShortcut):
        key_text = shortcut.key().toString(QKeySequence.NativeText)
        if not key_text:
            continue
        key = key_text.upper()
        owner_name = shortcut.parent().objectName() if shortcut.parent() else ""
        owner = (
            owner_name or shortcut.parent().__class__.__name__
            if shortcut.parent()
            else "Unknown"
        )
        shortcut_map.setdefault(key, []).append(owner)

    for key, owners in shortcut_map.items():
        if len(owners) > 1:
            conflicts.append(
                f"Duplicate QShortcut {key} ({', '.join(sorted(set(owners)))})"
            )

    mnemonic_map: Dict[str, List[str]] = {}
    controls: List[Tuple[QWidget, str]] = []
    controls.extend((w, w.text()) for w in widget.findChildren(QLabel))
    controls.extend((w, w.text()) for w in widget.findChildren(QPushButton))
    controls.extend((w, w.text()) for w in widget.findChildren(QCheckBox))
    controls.extend((w, w.title()) for w in widget.findChildren(QGroupBox))

    for control, text in controls:
        mnemonic = _extract_mnemonic(text)
        if not mnemonic:
            continue
        control_name = control.objectName() or control.__class__.__name__
        mnemonic_map.setdefault(mnemonic, []).append(control_name)

    for mnemonic, owners in mnemonic_map.items():
        if len(owners) > 1:
            conflicts.append(
                f"Duplicate mnemonic Alt+{mnemonic} ({', '.join(sorted(set(owners)))})"
            )

    return conflicts
