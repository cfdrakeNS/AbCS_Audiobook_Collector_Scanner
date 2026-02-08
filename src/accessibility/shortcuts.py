"""
Keyboard shortcut management for AbCS.
Centralizes all keyboard shortcuts for consistency and accessibility.
"""

from PySide6.QtCore import Qt, QObject
from PySide6.QtGui import QKeySequence, QShortcut, QAction
from PySide6.QtWidgets import QWidget
from typing import Dict, Callable, Optional
from enum import Enum


class ShortcutContext(Enum):
    """Shortcut context - where shortcuts are active."""
    GLOBAL = "global"  # Active everywhere
    MAIN_WINDOW = "main_window"
    BOOK_DETAILS = "book_details"
    IMPORT_WINDOW = "import_window"
    UPDATE_WINDOW = "update_window"


class ShortcutManager(QObject):
    """
    Manages keyboard shortcuts across the application.
    Provides centralized shortcut registration and documentation.
    """

    # Alt+Key shortcuts (context-specific)
    # Main Window
    MAIN_WINDOW_SHORTCUTS = {
        'C': ('Collection filter', 'collection_combo'),
        'R': ('Read filter', 'read_combo'),
        'O': ('Order by', 'order_combo'),
        'S': ('Search', 'search_box'),
        'B': ('Book list', 'book_list'),
        'E': ('Selected count', 'selected_label'),
        'U': ('Update selected', 'update_button'),
        'D': ('Delete selected', 'delete_button'),
        'L': ('Cancel selection', 'cancel_button'),
    }

    # Book Details Window
    BOOK_DETAILS_SHORTCUTS = {
        'T': ('Title', 'title_edit'),
        'A': ('Author', 'author_combo'),
        'Y': ('Year', 'year_edit'),
        'F': ('Files', 'files_edit'),
        'I': ('Series', 'series_combo'),
        'G': ('Genre', 'genre_combo'),
        'R': ('Reader', 'reader_edit'),
        'L': ('Collection', 'collection_combo'),
        'M': ('Time', 'time_edit'),
        'S': ('Size', 'size_edit'),
        'B': ('Bitrate', 'bitrate_edit'),
        'H': ('Path', 'path_edit'),
        'O': ('Comments', 'comments_edit'),
        'E': ('Date added', 'added_edit'),
        'W': ('New book', 'new_button'),
        'V': ('Save', 'save_button'),
        'D': ('Delete', 'delete_button'),
        'P': ('Previous', 'prev_button'),
        'N': ('Next', 'next_button'),
        'C': ('Close', 'close_button'),
    }

    # Import Window
    IMPORT_WINDOW_SHORTCUTS = {
        'L': ('Collection', 'collection_combo'),
        'F': ('Flip author name', 'flip_check'),
        'T': ('Elapsed time', 'time_label'),
        'S': ('Import list count', 'list_label'),
        'P': ('Parse errors', 'parse_label'),
        'R': ('Read errors', 'read_label'),
        'M': ('Menu', 'menu_combo'),
        'I': ('Import', 'import_button'),
        'X': ('Export', 'export_button'),
        'V': ('View', 'view_button'),
        'A': ('Add', 'add_button'),
        'C': ('Close', 'close_button'),
    }

    # Update Window
    UPDATE_WINDOW_SHORTCUTS = {
        'S': ('Series', 'series_combo'),
        'G': ('Genre', 'genre_combo'),
        'L': ('Collection', 'collection_combo'),
        'C': ('Close', 'close_button'),
    }

    # Zoom shortcuts (Ctrl/Cmd)
    ZOOM_SHORTCUTS = {
        'Ctrl+Plus': 'Zoom in',
        'Ctrl+Equal': 'Zoom in (alternative)',
        'Ctrl+Minus': 'Zoom out',
        'Ctrl+0': 'Reset zoom',
    }

    def __init__(self):
        """Initialize shortcut manager."""
        super().__init__()
        self._shortcuts: Dict[str, QShortcut] = {}

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
        else:
            return

        # Register each shortcut
        for key, (description, widget_id) in shortcuts.items():
            if widget_id in callback_map:
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
        zoom_in = QShortcut(QKeySequence("Ctrl+="), widget)
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
