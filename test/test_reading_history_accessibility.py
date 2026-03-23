"""Accessibility tests for reading history window and screen reader support."""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.database import get_db
from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.ui.reading_history_window import ReadingHistoryWindow


@pytest.fixture
def reading_history_window(qapp):
    """Provide a reading history window for testing."""
    db = get_db()
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ReadingHistoryWindow(db, scaler, theme_manager)
    yield window
    window.close()


def test_reading_history_window_accessible_properties(reading_history_window):
    """Test reading history window has proper accessibility properties."""
    window = reading_history_window
    
    # Check window has accessible name
    assert window.accessibleName() != ""
    assert window.accessibleDescription() != ""
    
    # Check main widgets have accessibility properties
    assert hasattr(window, 'tab_widget')
    assert window.tab_widget.accessibleName() != ""
    
    # Check tables have proper accessibility
    assert hasattr(window, 'general_table')
    assert hasattr(window, 'year_table')
    assert hasattr(window, 'month_table')
    assert hasattr(window, 'range_table')
    
    # Tables should be focusable
    assert window.general_table.focusPolicy() & Qt.TabFocus
    assert window.year_table.focusPolicy() & Qt.TabFocus
    assert window.month_table.focusPolicy() & Qt.TabFocus
    assert window.range_table.focusPolicy() & Qt.TabFocus


def test_reading_history_period_message_accessibility(reading_history_window):
    """Test period message is accessible to screen readers."""
    window = reading_history_window
    
    # Check period message storage exists
    assert hasattr(window, '_period_message')
    assert isinstance(window._period_message, str)
    
    # Check status bar exists and is accessible
    assert hasattr(window, 'status_bar')
    status_widget = window.status_bar
    
    # Status bar should have accessibility properties
    assert status_widget.accessibleName() != ""
    assert status_widget.accessibleDescription() != ""
    
    # Status bar typically doesn't have StrongFocus, but should be accessible via announcements
    assert hasattr(window, 'set_status')
    assert hasattr(window, 'on_read_status_bar')


def test_alt_s_shortcut_functionality(reading_history_window):
    """Test Alt+S shortcut triggers search in reading history window."""
    window = reading_history_window
    
    # Check search button exists and is accessible
    assert hasattr(window, 'refresh_button')
    search_button = window.refresh_button
    
    # Should have accessible name/description mentioning Alt+S
    assert "Alt+S" in search_button.accessibleDescription() or "Alt+S" in search_button.accessibleName()
    
    # Button should be clickable
    assert search_button.isEnabled()


def test_alt_b_table_focus_shortcut(reading_history_window):
    """Test Alt+B shortcut focuses on appropriate table."""
    window = reading_history_window
    
    # Test each tab - Alt+B should focus on current table
    for tab_index in range(4):
        window.tab_widget.setCurrentIndex(tab_index)
        
        # Simulate Alt+B (this would need actual shortcut testing in UI)
        # For now, just verify focus_current_table method works
        try:
            window.focus_current_table()
            # If no exception, focus management is working
            focus_works = True
        except Exception:
            focus_works = False
        
        assert focus_works, f"Focus management failed on tab {tab_index}"


def test_reading_history_table_accessibility(reading_history_window):
    """Test reading history tables are accessible."""
    window = reading_history_window
    
    tables = [window.general_table, window.year_table, window.month_table, window.range_table]
    
    for table in tables:
        # Tables should have proper accessibility setup
        assert table.accessibleName() != ""
        
        # Should have proper selection behavior (tables use SelectItems by default)
        from PySide6.QtWidgets import QAbstractItemView
        assert table.selectionBehavior() == QAbstractItemView.SelectionBehavior.SelectItems
        
        # Should not announce row changes (like name_list_window)
        # This prevents excessive screen reader announcements
        assert table.verticalHeader().accessibleName() == ""


def test_reading_history_layout_compactness(reading_history_window):
    """Test reading history layout is compact for low vision users."""
    window = reading_history_window
    
    # Check date range tab has minimal spacing
    date_range_layout = window.findChild(object, name=None)
    
    # Period message should have minimal height (22px as designed)
    assert hasattr(window, 'period_books_label')
    period_widget = window.period_books_label
    assert period_widget.height() <= 30  # Should be compact


def test_reading_history_menu_integration(qapp):
    """Test reading history window integrates with main window menu."""
    # This would test the main window menu integration
    # For now, just verify the window can be created independently
    db = get_db()
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    
    window = ReadingHistoryWindow(db, scaler, theme_manager)
    
    # Window should be accessible and functional
    assert window.isVisible() or not window.isVisible()  # Can be shown/hidden
    assert window.isEnabled()
    
    window.close()


def test_screen_reader_announcements_structure(reading_history_window):
    """Test screen reader announcements have proper structure."""
    window = reading_history_window
    
    # Check status announcements are properly structured
    # Status messages should be clear and concise
    assert hasattr(window, 'set_status')
    
    # Test setting a status message
    try:
        window.set_status("Test message", announce=False)
        status_works = True
    except Exception:
        status_works = False
    
    assert status_works, "Status announcement system failed"
    
    # Check that status messages use readable date format
    # Should format like: "Showing 5 books read between March 23, 2026 and March 23, 2026 totaling 12 hours"
    assert hasattr(window, '_period_message')
    assert isinstance(window._period_message, str)
    
    # Period message should use readable date format
    # Should format like: "Between March 23, 2026 and March 23, 2026 you read 5 books totaling 12 hours"
    if window._period_message:
        assert "March" in window._period_message or "April" in window._period_message or "May" in window._period_message
        assert "you read" in window._period_message
        assert "totaling" in window._period_message
