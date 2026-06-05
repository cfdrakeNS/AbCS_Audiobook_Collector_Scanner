"""Regression tests to prevent accessibility and shortcut breakage."""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from src.database import get_db
from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.shortcuts import ShortcutManager
from src.ui.main_window import MainWindow
from src.ui.reading_history_window import ReadingHistoryWindow
from src.ui.name_list_window import NameListWindow
from src.ui.book_details import BookDetailsWindow


@pytest.fixture
def main_window(qapp):
    """Provide a main window for testing."""
    db = get_db()
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(db, scaler, theme_manager)
    yield window
    window.close()


@pytest.fixture
def reading_history_window(qapp):
    """Provide a reading history window for testing."""
    db = get_db()
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ReadingHistoryWindow(db, scaler, theme_manager)
    yield window
    window.close()


def test_accessibility_properties_regression(main_window, reading_history_window):
    """Regression test: Ensure all windows maintain accessibility properties."""
    
    windows_to_test = [
        ("Main Window", main_window),
        ("Reading History", reading_history_window),
    ]
    
    for window_name, window in windows_to_test:
        # Each window should have accessibility properties
        assert window.accessibleName() != "", f"{window_name} missing accessible name"
        assert window.isEnabled(), f"{window_name} should be enabled"
        
        # Window should be focusable
        assert window.focusPolicy() & Qt.TabFocus, f"{window_name} not tab focusable"


def test_shortcut_registry_regression():
    """Regression test: Ensure shortcut registry maintains expected structure."""
    
    # Check main window shortcuts haven't changed unexpectedly
    main_shortcuts = ShortcutManager.MAIN_WINDOW_SHORTCUTS
    
    # Critical shortcuts that must exist
    critical_shortcuts = {
        'L': ('Jump to list', 'book_list'),
        'U': ('Update selected', 'update_button'),
        'D': ('Delete selected', 'delete_button'),
    }
    
    for key, expected_value in critical_shortcuts.items():
        assert key in main_shortcuts, f"Critical shortcut {key} missing from main window"
        assert main_shortcuts[key] == expected_value, f"Shortcut {key} value changed"
    
    # Check reading history shortcuts
    reading_shortcuts = ShortcutManager.READING_HISTORY_WINDOW_SHORTCUTS
    
    reading_critical = {
        'S': ('Search', 'refresh_button'),
        'L': ('Jump to list', 'table'),
    }
    
    for key, expected_value in reading_critical.items():
        assert key in reading_shortcuts, f"Critical shortcut {key} missing from reading history"
        assert reading_shortcuts[key] == expected_value, f"Reading history shortcut {key} value changed"


def test_menu_structure_regression(main_window):
    """Regression test: Ensure menu structure hasn't broken."""
    
    # Check View menu exists (main window creates menus in setup_ui)
    assert hasattr(main_window, 'view_menu'), "View menu missing"
    view_menu = main_window.view_menu
    assert view_menu is not None
    
    # Check View menu has Reading History action
    reading_history_action = None
    for action in view_menu.actions():
        if action and "Reading &History" in action.text():
            reading_history_action = action
            break
    
    assert reading_history_action is not None, "Reading History menu item missing from View menu"
    assert reading_history_action.isEnabled(), "Reading History action should be enabled"


def test_table_accessibility_regression(reading_history_window):
    """Regression test: Ensure tables maintain accessibility features."""
    
    tables = [
        ("General", reading_history_window.general_table),
        ("Year", reading_history_window.year_table),
        ("Month", reading_history_window.month_table),
        ("Date Range", reading_history_window.range_table),
    ]
    
    for table_name, table in tables:
        assert table is not None, f"{table_name} table missing"
        assert table.accessibleName() != "", f"{table_name} table missing accessible name"
        
        # Should have proper selection behavior (tables use SelectItems by default)
        from PySide6.QtWidgets import QAbstractItemView
        assert table.selectionBehavior() == QAbstractItemView.SelectionBehavior.SelectItems, f"{table_name} table should select items"
        
        # Check vertical header is accessible (should not announce rows)
        vheader = table.verticalHeader()
        assert vheader.accessibleName() == "", f"{table_name} table vertical header should not announce"


def test_focus_management_regression(main_window, reading_history_window):
    """Regression test: Ensure focus management hasn't broken."""
    
    # Test main window focus
    assert hasattr(main_window, 'book_list'), "Main window missing book list"
    book_list = main_window.book_list
    assert book_list.focusPolicy() & Qt.TabFocus, "Book list not focusable"
    
    # Test reading history focus management
    assert hasattr(reading_history_window, 'focus_current_table'), "Reading history missing focus management"
    
    # Test each table can receive focus
    tables = [
        reading_history_window.general_table,
        reading_history_window.year_table,
        reading_history_window.month_table,
        reading_history_window.range_table,
    ]
    
    for table in tables:
        assert table.focusPolicy() & Qt.StrongFocus, "Table not properly focusable"


def test_screen_reader_announcements_regression(reading_history_window):
    """Regression test: Ensure screen reader announcements work."""
    
    # Check period message widget exists and is accessible
    assert hasattr(reading_history_window, 'period_books_label'), "Period message widget missing"
    period_widget = reading_history_window.period_books_label
    
    # Should be accessible to screen readers
    assert period_widget.focusPolicy() & Qt.StrongFocus, "Period widget not focusable for screen readers"
    assert period_widget.textInteractionFlags() & Qt.TextSelectableByKeyboard, "Period text not selectable"
    
    # Should have accessibility properties
    assert period_widget.accessibleName() != "", "Period widget missing accessible name"


def test_status_announcement_system_regression(main_window, reading_history_window):
    """Regression test: Ensure status announcement system works."""
    
    # Both windows should have status announcement capability
    assert hasattr(main_window, 'set_status'), "Main window missing status announcement"
    assert hasattr(reading_history_window, 'set_status'), "Reading history missing status announcement"
    
    # Test status announcement doesn't crash
    try:
        main_window.set_status("Test status", announce=False)
        reading_history_window.set_status("Test status", announce=False)
        status_works = True
    except Exception as e:
        status_works = False
        assert False, f"Status announcement system broken: {e}"
    
    assert status_works, "Status announcement system not working"


def test_window_layout_regression(reading_history_window):
    """Regression test: Ensure window layouts haven't broken accessibility."""
    
    # Check reading history window has tab widget
    assert hasattr(reading_history_window, 'tab_widget'), "Reading history missing tab widget"
    tab_widget = reading_history_window.tab_widget
    
    # Should have expected tabs
    expected_tabs = ["General", "Year", "Month", "Date Range"]
    actual_tabs = [tab_widget.tabText(i) for i in range(tab_widget.count())]
    
    for expected_tab in expected_tabs:
        assert expected_tab in actual_tabs, f"Tab {expected_tab} missing from reading history window"


def test_shortcut_context_isolation_regression():
    """Regression test: Ensure shortcut contexts remain isolated."""
    
    # Check all shortcut contexts exist
    from src.accessibility.shortcuts import ShortcutContext
    
    expected_contexts = [
        'MAIN_WINDOW',
        'READING_HISTORY_WINDOW', 
        'BOOK_DETAILS',
        'IMPORT_WINDOW',
    ]
    
    for context_name in expected_contexts:
        assert hasattr(ShortcutContext, context_name), f"Shortcut context {context_name} missing"


def test_database_access_regression(qapp):
    """Regression test: Ensure database access hasn't broken reading history."""
    
    # Test reading history window can access database
    db = get_db()
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    
    try:
        window = ReadingHistoryWindow(db, scaler, theme_manager)
        
        # Should be able to load data without errors
        assert hasattr(window, 'load_general_stats'), "Reading history missing data loading"
        assert hasattr(window, 'load_date_range_data'), "Reading history missing date range loading"
        
        window.close()
        db_access_works = True
    except Exception as e:
        db_access_works = False
        assert False, f"Database access broken: {e}"
    
    assert db_access_works, "Database access not working properly"
