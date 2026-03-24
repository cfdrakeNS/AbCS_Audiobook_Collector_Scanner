

from enum import Enum
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QCheckBox, QGroupBox
from PySide6.QtGui import QKeySequence, QShortcut
from typing import Dict, Callable, Optional, List, Tuple


class ShortcutContext(Enum):
    """Shortcut context - where shortcuts are active."""
    COLLECTION_WINDOW = "collection_window"
    GLOBAL = "global"  # Active everywhere
    MAIN_WINDOW = "main_window"
    BOOK_DETAILS = "book_details"
    IMPORT_WINDOW = "import_window"
    IMPORT_PROGRESS_WINDOW = "import_progress_window"
    UPDATE_WINDOW = "update_window"
    PREFERENCES_WINDOW = "preferences_window"
    DUPLICATE_DIALOG = "duplicate_dialog"
    BACKUP_RESTORE_WINDOW = "backup_restore_window"
    NAMELIST_WINDOW = "namelist_window"
    READING_HISTORY_WINDOW = "reading_history_window"


class ShortcutManager(QObject):
    # Collection Window (dedicated context)
    COLLECTION_WINDOW_SHORTCUTS = {
        'B': ('Jump to list', 'table'),
        'S': ('Save', 'save_button'),
        'E': ('Edit selected row', 'edit_button'),
        'M': ('Name edit', 'name_edit'),
        'A': ('Active checkbox', 'active_check'),
        'L': ('Cancel edit/new', 'cancel_button'),
        'N': ('New', 'new_button'),
        'D': ('Delete', 'delete_button'),
    }
    # NameList Window
    NAMELIST_WINDOW_SHORTCUTS = {
        'B': ('Jump to list', 'table'),
        'S': ('Save', 'save_button'),
        'E': ('Edit selected row', 'edit_button'),
        'M': ('Name edit', 'name_edit'),
        'F': ('Find', 'find_edit'),
        'A': ('Active checkbox', 'active_check'),
        'L': ('Cancel edit/new', 'cancel_button'),
    }

    # Backup/Restore Window
    BACKUP_RESTORE_WINDOW_SHORTCUTS = {
        'B': ('Backup list', 'backup_list'),
        'W': ('Browse', 'browse_button'),
        'K': ('Create backup', 'backup_button'),
        'T': ('Focus restore file', 'restore_path_edit'),
        'R': ('Restore', 'restore_button'),
        'D': ('Delete', 'delete_button'),
        'F': ('Full reset', 'full_reset_button'),
    }
    # Reading History Window
    READING_HISTORY_WINDOW_SHORTCUTS = {
        'B': ('Jump to list', 'table'),
        'R': ('Refresh data', 'refresh_button'),
        'S': ('Search', 'refresh_button'),
        'F': ('From date', 'start_date_edit'),
    }

    """
    Manages keyboard shortcuts across the application.
    Provides centralized shortcut registration and documentation.
    """

    # Duplicate Check Dialog
    DUPLICATE_DIALOG_SHORTCUTS = {
        'R': ('Start duplicate check', 'start_button'),
        'L': ('Cancel duplicate check', 'cancel_button'),
        'M': ('Focus match type combo', 'mode_combo'),
    }

    # Alt+Key shortcuts (context-specific)
    # Main Window
    MAIN_WINDOW_SHORTCUTS = {
        'B': ('Book list focus', 'book_list'),
        'U': ('Update selected', 'update_button'),
        'D': ('Delete selected', 'delete_button'),
        'L': ('Cancel selection', 'cancel_button'),
    }

    # Book Details Window
    BOOK_DETAILS_SHORTCUTS = {
        'T': ('Title', 'title_edit'),
        'A': ('Author', 'author_combo'),
        'P': ('Plot', 'comments_edit'),    # Changed from Path/Comments to Plot
        'Y': ('Year', 'year_spin'),
        'M': ('Length', 'time_edit'),      # Changed from H to M for Length
        'R': ('Reader', 'reader_edit'),
        'E': ('Read date', 'read_date'),
        'I': ('Series', 'series_combo'),
        'G': ('Genre', 'genre_combo'),
        'C': ('Collection', 'collection_combo'),
        'F': ('Files', 'files_edit'),
        'B': ('Bitrate', 'bitrate_edit'),
        'Z': ('Size', 'size_edit'),
        'H': ('Path', 'path_edit'),        # Changed from P to H for Path
        'N': ('New', 'new_button'),
        'S': ('Save', 'save_button'),
        'D': ('Delete', 'delete_button'),
        'L': ('Cancel', 'cancel_button'),  # Alt+L now mapped to Cancel
        'F1': ('Show help', 'show_help'),
    }

    # Import Window
    IMPORT_WINDOW_SHORTCUTS = {
        'C': ('Collection field', 'collection_combo'),
        'F': ('Folder field', 'folder_field'),
        'E': ('Error filter', 'error_filter'),
        'W': ('Browse', 'browse_button'),
        'S': ('Import Selected', 'import_selected_button'),
        'V': ('Import All Valid', 'import_all_valid_button'),
        'B': ('Focus import list table', 'import_list_table'),
        'X': ('Export list to CSV', 'export_csv_button'),
    }

    # Update Window
    UPDATE_WINDOW_SHORTCUTS = {
        'S': ('Series', 'series_combo'),
        'G': ('Genre', 'genre_combo'),
        'C': ('Collection', 'collection_combo'),
        'B': ('Focus book list', 'book_list'),
    }

    # Preferences Window
    PREFERENCES_WINDOW_SHORTCUTS = {
        'D': ('Display section', 'theme_combo'),
        'P': ('Path & Scope section', 'import_dir_edit'),
        'O': ('Options section', 'auto_add_clean_books_check'),
        'F': ('Fallback section', 'author_fallback_checkbox'),
        'R': ('Validation Rules section', 'rules_section_text'),
        'A': ('Auto-Correction section', 'autocorrect_section_text'),
        'S': ('Save', 'save_button'),
        'L': ('Cancel', 'cancel_button'),
        '/': ('Status bar', 'status_bar'),
    }

    # Zoom shortcuts (Ctrl/Cmd)
    ZOOM_SHORTCUTS = {
        'Ctrl+Plus': 'Zoom in',
        'Ctrl+Minus': 'Zoom out',
        'Ctrl+0': 'Reset zoom',
    }

    def __init__(self):
        """Initialize shortcut manager."""
        super().__init__()
        self._shortcuts = {}

    def register_alt_shortcuts(self,
                               widget: QWidget,
                               context: ShortcutContext,
                               callback_map: Dict[str, Callable]):
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
            shortcuts = self.MAIN_WINDOW_SHORTCUTS
        elif context == ShortcutContext.BOOK_DETAILS:
            shortcuts = self.BOOK_DETAILS_SHORTCUTS
        elif context == ShortcutContext.IMPORT_WINDOW:
            shortcuts = self.IMPORT_WINDOW_SHORTCUTS
        elif context == ShortcutContext.UPDATE_WINDOW:
            shortcuts = self.UPDATE_WINDOW_SHORTCUTS
        elif context == ShortcutContext.PREFERENCES_WINDOW:
            shortcuts = self.PREFERENCES_WINDOW_SHORTCUTS
        elif context == ShortcutContext.DUPLICATE_DIALOG:
            shortcuts = self.DUPLICATE_DIALOG_SHORTCUTS
        elif context == ShortcutContext.BACKUP_RESTORE_WINDOW:
            shortcuts = self.BACKUP_RESTORE_WINDOW_SHORTCUTS
        elif context == ShortcutContext.NAMELIST_WINDOW:
            shortcuts = self.NAMELIST_WINDOW_SHORTCUTS
        elif context == ShortcutContext.COLLECTION_WINDOW:
            shortcuts = self.COLLECTION_WINDOW_SHORTCUTS
        elif context == ShortcutContext.READING_HISTORY_WINDOW:
            shortcuts = self.READING_HISTORY_WINDOW_SHORTCUTS
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
                else:
                    key_seq = QKeySequence(f"Alt+{key}")
                shortcut = QShortcut(key_seq, widget)
                shortcut.activated.connect(callback_map[widget_id])
                shortcut_id = f"{context.value}_{key}"
                self._shortcuts[shortcut_id] = shortcut

    def register_zoom_shortcuts(self, widget: QWidget, scaler):
        """
        Register zoom shortcuts (Ctrl +/-/0).

        Args:
            widget: Widget to register shortcuts on
            scaler: UIScaler instance
        """
        # Zoom in - use = key (same as + without shift)
        zoom_in = QShortcut(QKeySequence("Ctrl++"), widget)
        zoom_in.activated.connect(scaler.increase_scale)
        self._shortcuts['zoom_in'] = zoom_in

        # Zoom out
        zoom_out = QShortcut(QKeySequence("Ctrl+-"), widget)
        zoom_out.activated.connect(scaler.decrease_scale)
        self._shortcuts['zoom_out'] = zoom_out

        # Reset zoom
        zoom_reset = QShortcut(QKeySequence("Ctrl+0"), widget)
        zoom_reset.activated.connect(scaler.reset_scale)
        self._shortcuts['zoom_reset'] = zoom_reset

    def get_shortcut_help(self, context: ShortcutContext) -> list:
        """
        Get help text for shortcuts in a context.

        Args:
            context: Shortcut context

        Returns:
            List of (shortcut, description) tuples
        """
        help_text = []

        # Function keys
        # for key, desc in self.FUNCTION_KEYS.items():
        #     key_name = f"F{key - Qt.Key_F1 + 1}"
        #     help_text.append((key_name, desc))

        # Context-specific Alt shortcuts
        shortcuts = None
        if context == ShortcutContext.MAIN_WINDOW:
            shortcuts = self.MAIN_WINDOW_SHORTCUTS
        elif context == ShortcutContext.BOOK_DETAILS:
            shortcuts = self.BOOK_DETAILS_SHORTCUTS
        elif context == ShortcutContext.IMPORT_WINDOW:
            shortcuts = self.IMPORT_WINDOW_SHORTCUTS
        elif context == ShortcutContext.UPDATE_WINDOW:
            shortcuts = self.UPDATE_WINDOW_SHORTCUTS

        if shortcuts:
            for key, (desc, _) in shortcuts.items():
                help_text.append((f"Alt+{key}", desc))

        # Zoom shortcuts
        for shortcut, desc in self.ZOOM_SHORTCUTS.items():
            help_text.append((shortcut, desc))

        return help_text

    @staticmethod
    def set_widget_shortcut_hint(widget: QWidget, key: str):
        """
        Set visual hint for keyboard shortcut on widget.
        Underlines the shortcut key in the widget's text.

        Args:
            widget: Widget to set hint on
            key: Single character that's the shortcut key
        """
        if hasattr(widget, 'text'):
            text = widget.text()
            if key.upper() in text.upper():
                # Find first occurrence and underline it
                idx = text.upper().index(key.upper())
                new_text = text[:idx] + '&' + text[idx:]
                widget.setText(new_text)
        elif hasattr(widget, 'setTitle'):
            # For group boxes
            text = widget.title()
            if key.upper() in text.upper():
                idx = text.upper().index(key.upper())
                new_text = text[:idx] + '&' + text[idx:]
                widget.setTitle(new_text)


# Global shortcut manager
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
        if text[idx] == '&':
            nxt = text[idx + 1]
            if nxt == '&':
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
        owner = owner_name or shortcut.parent(
        ).__class__.__name__ if shortcut.parent() else "Unknown"
        shortcut_map.setdefault(key, []).append(owner)

    for key, owners in shortcut_map.items():
        if len(owners) > 1:
            conflicts.append(
                f"Duplicate QShortcut {key} ({', '.join(sorted(set(owners)))})")

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
                f"Duplicate mnemonic Alt+{mnemonic} ({', '.join(sorted(set(owners)))})")

    return conflicts
