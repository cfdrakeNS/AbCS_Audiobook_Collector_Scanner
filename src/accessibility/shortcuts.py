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


COLLECTION_WINDOW_SHORTCUTS = {
    "L": ("Jump to list", "table"),
    "S": ("Save", "save_button"),
    "E": ("Edit selected row", "edit_button"),
    "N": ("New", "new_button"),
    "D": ("Delete", "delete_button"),
}

NAMELIST_WINDOW_SHORTCUTS = {
    "L": ("Jump to list", "table"),
    "S": ("Save", "save_button"),
    "E": ("Edit selected row", "edit_button"),
    "M": ("Name edit", "name_edit"),
    "F": ("Clear find / new search", "find_edit"),
    "A": ("Active checkbox", "active_check"),
}

BACKUP_RESTORE_WINDOW_SHORTCUTS = {
    "L": ("Backup list", "backup_list"),
    "W": ("Browse", "browse_button"),
    "B": ("Create backup", "backup_button"),
    "T": ("Focus restore file", "restore_path_edit"),
    "R": ("Restore", "restore_button"),
    "D": ("Delete", "delete_button"),
    "F": ("Full reset", "full_reset_button"),
}

READING_HISTORY_WINDOW_SHORTCUTS = {
    "L": ("Jump to list", "table"),
    "R": ("Refresh data", "refresh_button"),
    "S": ("Search", "refresh_button"),
    "F": ("From date", "start_date_edit"),
}

DUPLICATE_DIALOG_SHORTCUTS = {
    "R": ("Start duplicate check", "start_button"),
    "L": ("Cancel duplicate check", "cancel_button"),
    "M": ("Focus match type combo", "mode_combo"),
}

MAIN_WINDOW_SHORTCUTS = {
    "U": ("Update selected", "update_button"),
    "D": ("Delete selected", "delete_button"),
    "A": ("Author filter", "author_filter_combo"),
    # Alt+1..7 handled in main_window.py for column jump
}

BOOK_DETAILS_SHORTCUTS = {
    "T": ("Title", "title_edit"),
    "A": ("Author", "author_combo"),
    "P": ("Plot", "comments_edit"),  # From Pl&ot label
    "Y": ("Year", "year_spin"),
    "M": ("Time", "time_edit"),  # From &Time label
    "R": ("Reader", "reader_edit"),
    "E": ("Read date", "read_date"),
    "I": ("Series", "series_combo"),
    "G": ("Genre", "genre_combo"),
    "C": ("Collection", "collection_combo"),
    "F": ("Files", "files_edit"),
    "B": ("Bitrate", "bitrate_edit"),
    "Z": ("Size", "size_edit"),
    "O": ("Format", "format_combo"),  # Alt+O for Format (ensured)
    "H": ("Path", "path_edit"),  # From Pat&h label
    "W": ("Get web info", "get_web_details_button"),
    "F1": ("Show help", "show_help"),
}

WEB_METADATA_SHORTCUTS = {
    "T": ("Title", "title_edit"),
    "A": ("Author", "author_edit"),
    "P": ("Plot", "plot_edit"),
    "Y": ("Year", "year_edit"),
    "I": ("Series", "series_edit"),
    "N": ("Series number", "series_number_edit"),
    "G": ("Genre", "genre_edit"),
    "R": ("Rating", "rating_edit"),
    "S": ("Save", "save_button"),
}

# Import Window
IMPORT_WINDOW_SHORTCUTS = {
    "C": ("Collection field", "collection_combo"),
    "F": ("Folder field", "folder_field"),
    "W": ("Browse", "browse_button"),
    "E": ("Error filter", "error_filter"),
    "S": ("Import Selected", "import_selected_button"),
    "L": ("Focus import list table", "import_list_table"),
    "X": ("Export list to CSV", "export_csv_button"),
}

# Book List Import Window
BOOK_LIST_IMPORT_WINDOW_SHORTCUTS = {
    "C": ("Collection", "collection_combo"),
    "W": ("Browse for file", "browse_button"),
    "O": ("Options group", "options_group"),
    "T": ("Title field mapping", "title_mapping"),
    "A": ("Author field mapping", "author_mapping"),
    "Y": ("Year field mapping", "year_mapping"),
    "P": ("Plot field mapping", "plot_mapping"),
    "S": ("Series field mapping", "series_mapping"),
    "N": ("Series number field mapping", "series_number_mapping"),
    "G": ("Genre field mapping", "genre_mapping"),
    "R": ("Reader field mapping", "reader_mapping"),
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
    "D": ("Display section", "theme_combo"),
    "P": ("Path & Scope section", "import_dir_edit"),
    "W": ("Browse", "browse_button"),
    "F": ("Fallback section", "author_fallback_checkbox"),
    "V": ("Validation Rules section", "rules_section_text"),
    "R": ("Restore Defaults", "restore_defaults_button"),
    "S": ("Save", "save_button"),
    "/": ("Status bar", "status_bar"),
    "C": ("Collection", "collection_combo"),
}


class ShortcutManager(QObject):
    """
    Manages keyboard shortcuts across the application.
    Provides centralized shortcut registration and documentation.
    """

    def __init__(self):
        """Initialize shortcut manager."""
        super().__init__()
        self._shortcuts = {}

    def register_alt_shortcuts(
        self,
        widget: QWidget,
        context: ShortcutContext,
        callback_map: Dict[str, Callable],
    ):
        """
        Register Alt+Key shortcuts for a widget.

        Args:
            widget: Widget to register shortcuts on
            context: Shortcut context
            callback_map: Map of widget_id to callback function
                         e.g., {'collection_combo': self.on_collection_focus}
        """
        # Get shortcuts for this context
        if context == ShortcutContext.MAIN_WINDOW:
            shortcuts = MAIN_WINDOW_SHORTCUTS
        elif context == ShortcutContext.BOOK_DETAILS:
            shortcuts = BOOK_DETAILS_SHORTCUTS
        elif context == ShortcutContext.WEB_METADATA:
            shortcuts = WEB_METADATA_SHORTCUTS
        elif context == ShortcutContext.IMPORT_WINDOW:
            shortcuts = IMPORT_WINDOW_SHORTCUTS
        elif context == ShortcutContext.UPDATE_WINDOW:
            shortcuts = UPDATE_WINDOW_SHORTCUTS
        elif context == ShortcutContext.PREFERENCES_WINDOW:
            shortcuts = PREFERENCES_WINDOW_SHORTCUTS
        elif context == ShortcutContext.DUPLICATE_DIALOG:
            shortcuts = DUPLICATE_DIALOG_SHORTCUTS
        elif context == ShortcutContext.BACKUP_RESTORE_WINDOW:
            shortcuts = BACKUP_RESTORE_WINDOW_SHORTCUTS
        elif context == ShortcutContext.NAMELIST_WINDOW:
            shortcuts = NAMELIST_WINDOW_SHORTCUTS
        elif context == ShortcutContext.COLLECTION_WINDOW:
            shortcuts = COLLECTION_WINDOW_SHORTCUTS
        elif context == ShortcutContext.READING_HISTORY_WINDOW:
            shortcuts = READING_HISTORY_WINDOW_SHORTCUTS
        elif context == ShortcutContext.BOOK_LIST_IMPORT_WINDOW:
            shortcuts = BOOK_LIST_IMPORT_WINDOW_SHORTCUTS
        else:
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
