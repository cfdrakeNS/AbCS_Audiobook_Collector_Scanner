"""Consolidated ReadingHistoryWindow accessibility and behavior tests."""

from __future__ import annotations

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QAbstractItemView

MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


def test_window_initialization_and_accessible_names(reading_history_window):
    """Window title, accessible names, and required components are present."""
    window = reading_history_window

    assert window.windowTitle() == "Reading History"
    assert window.accessibleName() == "Reading History Window"
    assert window.accessibleDescription() != ""

    required_attrs = [
        "tab_widget",
        "general_table",
        "year_table",
        "month_table",
        "range_table",
        "start_date_edit",
        "end_date_edit",
        "refresh_button",
        "status_bar",
        "period_books_label",
        "_period_message",
        "_default_status_message",
    ]
    for attr in required_attrs:
        assert hasattr(window, attr), f"Missing required attribute: {attr}"

    assert window.tab_widget.accessibleName() != ""
    assert window.focusPolicy() & Qt.TabFocus


def test_tabs_labels_and_switching(reading_history_window):
    """General/Year/Month/Date Range tabs exist and can be selected."""
    window = reading_history_window
    tab_widget = window.tab_widget

    expected_tabs = ["General", "Year", "Month", "Date Range"]
    actual_tabs = [tab_widget.tabText(i) for i in range(tab_widget.count())]
    for expected_tab in expected_tabs:
        assert expected_tab in actual_tabs, f"Missing tab: {expected_tab}"

    for i in range(tab_widget.count()):
        tab_widget.setCurrentIndex(i)
        assert tab_widget.currentIndex() == i


def test_tables_accessibility(reading_history_window):
    """Tables expose accessible names, row selection, and labeled vheaders."""
    window = reading_history_window
    tables = [
        window.general_table,
        window.year_table,
        window.month_table,
        window.range_table,
    ]

    for table in tables:
        assert table.accessibleName() != ""
        assert table.accessibleDescription() != ""
        assert table.focusPolicy() & Qt.TabFocus
        assert table.focusPolicy() & Qt.StrongFocus
        assert table.selectionBehavior() == QAbstractItemView.SelectionBehavior.SelectRows
        assert table.verticalHeader().accessibleName() == "Table Row Headers"


def test_period_message_and_label_accessibility(reading_history_window):
    """Period message uses readable format; period label is SR-accessible."""
    window = reading_history_window

    assert isinstance(window._period_message, str)
    period_widget = window.period_books_label
    assert period_widget.accessibleName() != ""
    assert period_widget.focusPolicy() & Qt.StrongFocus
    assert period_widget.textInteractionFlags() & Qt.TextSelectableByKeyboard
    assert period_widget.height() <= 30

    # Default rolling range (if already loaded) should use Showing / month names.
    if window._period_message:
        assert "Showing" in window._period_message
        assert "books read between" in window._period_message
        assert "totaling" in window._period_message
        assert any(month in window._period_message for month in MONTH_NAMES)


def test_date_range_search_period_message_format(reading_history_window):
    """Date-range search produces Showing/.../totaling with month names, not ISO."""
    window = reading_history_window
    window.tab_widget.setCurrentIndex(3)

    start_date = QDate(2024, 3, 23)
    end_date = QDate(2024, 3, 23)
    window.start_date_edit.setDate(start_date)
    window.end_date_edit.setDate(end_date)
    assert window.start_date_edit.date() == start_date
    assert window.end_date_edit.date() == end_date

    window.load_date_range_data()

    assert isinstance(window._period_message, str)
    if window._period_message:
        assert "Showing" in window._period_message
        assert "books read between" in window._period_message
        assert "totaling" in window._period_message
        assert "March" in window._period_message
        assert "2024" in window._period_message
        assert "2024-03-23" not in window._period_message


def test_focus_after_date_range_search(reading_history_window):
    """After date-range search with rows, focus lands on title column."""
    window = reading_history_window
    window.tab_widget.setCurrentIndex(3)
    window.start_date_edit.setDate(QDate(2024, 1, 1))
    window.end_date_edit.setDate(QDate(2024, 12, 31))
    window.load_date_range_data()

    if window.range_table.rowCount() > 0 and window.range_table.currentRow() >= 0:
        assert window.range_table.currentColumn() == 1


def test_focus_current_table_across_tabs(reading_history_window):
    """focus_current_table works on each tab without raising."""
    window = reading_history_window
    assert hasattr(window, "focus_current_table")

    for tab_index in range(4):
        window.tab_widget.setCurrentIndex(tab_index)
        window.focus_current_table()


def test_refresh_button_alt_s_accessible_text(reading_history_window):
    """Search/refresh button advertises Alt+S and is enabled."""
    window = reading_history_window
    button = window.refresh_button
    assert button.isEnabled()
    assert "Alt+S" in button.accessibleDescription() or "Alt+S" in button.accessibleName()
    assert button.accessibleName() != ""
    assert button.accessibleDescription() != ""


def test_status_bar_empty_accessible_labels(reading_history_window):
    """Status bar has empty accessibleName/Description (bug 102) and a default message."""
    window = reading_history_window
    status_widget = window.status_bar
    assert status_widget.accessibleName() == ""
    assert status_widget.accessibleDescription() == ""
    assert (window._default_status_message or "").strip() != ""


def test_set_status_and_on_read_status_bar(reading_history_window):
    """set_status updates visible/default status; on_read_status_bar preserves it."""
    window = reading_history_window

    window.set_status("Test status message", announce=False)
    assert window._default_status_message == "Test status message"
    assert window.status_bar.currentMessage() == "Test status message"

    window.on_read_status_bar()
    assert window.status_bar.currentMessage() == "Test status message"
    assert window._default_status_message == "Test status message"
