"""MainWindow-only accessibility and shortcut regressions."""

from __future__ import annotations

from PySide6.QtCore import Qt

from src.accessibility.shortcuts import ShortcutContext, ShortcutManager


def test_shortcut_registry_regression():
    """Thin key-presence check for critical shortcut registry entries."""
    main_shortcuts = ShortcutManager.MAIN_WINDOW_SHORTCUTS
    for key in ("L", "U", "D"):
        assert key in main_shortcuts, f"Critical shortcut {key} missing from main window"

    reading_shortcuts = ShortcutManager.READING_HISTORY_WINDOW_SHORTCUTS
    for key in ("S", "L"):
        assert key in reading_shortcuts, f"Critical shortcut {key} missing from reading history"


def test_menu_structure_regression(main_window):
    """View menu exposes an enabled Reading History action."""
    assert hasattr(main_window, "view_menu"), "View menu missing"
    view_menu = main_window.view_menu
    assert view_menu is not None

    reading_history_action = None
    for action in view_menu.actions():
        if action and "Reading &History" in action.text():
            reading_history_action = action
            break

    assert reading_history_action is not None, "Reading History menu item missing from View menu"
    assert reading_history_action.isEnabled(), "Reading History action should be enabled"


def test_book_list_accessibility_regression(main_window):
    """Main window book list remains tab-focusable with accessible properties."""
    assert main_window.accessibleName() != ""
    assert main_window.isEnabled()
    assert main_window.focusPolicy() & Qt.TabFocus

    assert hasattr(main_window, "book_list"), "Main window missing book list"
    book_list = main_window.book_list
    assert book_list.focusPolicy() & Qt.TabFocus


def test_status_announcement_system_regression(main_window):
    """Main window set_status updates the status bar message."""
    assert hasattr(main_window, "set_status"), "Main window missing status announcement"
    main_window.set_status("Test status", announce=False)
    assert main_window.status_bar.currentMessage() == "Test status"


def test_shortcut_context_isolation_regression():
    """ShortcutContext enum retains expected members."""
    expected_contexts = [
        "MAIN_WINDOW",
        "READING_HISTORY_WINDOW",
        "BOOK_DETAILS",
        "IMPORT_WINDOW",
    ]
    for context_name in expected_contexts:
        assert hasattr(ShortcutContext, context_name), f"Shortcut context {context_name} missing"
