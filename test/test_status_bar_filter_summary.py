"""Verify main window status bar matches filter summary label."""

from __future__ import annotations

from datetime import date

import pytest

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.database.models import Collection
from src.database.queries import CollectionQueries
from src.ui.main_window import MainWindow

def _assert_status_matches_summary(window: MainWindow) -> None:
    assert window.status_bar.currentMessage() == window.filter_summary_label.text()


def _trigger_collection_filter(window: MainWindow, collection_id: int) -> None:
    window.refresh_collections()
    target_action = None
    for action in window.collection_filter_group.actions():
        if action.data() == collection_id:
            target_action = action
            break
    assert target_action is not None
    target_action.trigger()


def _trigger_read_filter(window: MainWindow, value: str) -> None:
    target_action = None
    for action in window.read_filter_group.actions():
        if action.data() == value:
            target_action = action
            break
    assert target_action is not None
    target_action.trigger()


def _trigger_plot_filter(window: MainWindow, value: str) -> None:
    target_action = None
    for action in window.plot_filter_group.actions():
        if action.data() == value:
            target_action = action
            break
    assert target_action is not None
    target_action.trigger()


def test_default_startup_status_matches_filter_summary(qapp, qtbot, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    _assert_status_matches_summary(window)
    assert "Collection:" in window.status_bar.currentMessage()
    assert "Sort: Title" in window.status_bar.currentMessage()

    window.close()


def test_collection_filter_status_matches_filter_summary(qapp, qtbot, temp_db):
    collection_queries = CollectionQueries(temp_db)
    collection_id = collection_queries.insert(
        Collection(name="Status Bar Test Collection", active=True)
    )

    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    _trigger_collection_filter(window, collection_id)

    _assert_status_matches_summary(window)
    assert "Collection: Status Bar Test Collection" in window.status_bar.currentMessage()

    window.close()


def test_read_filter_status_matches_filter_summary(qapp, qtbot, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    _trigger_read_filter(window, "Unread")

    _assert_status_matches_summary(window)
    assert "Read: Unread" in window.status_bar.currentMessage()
    assert "Collection: All" in window.status_bar.currentMessage()

    window.close()


def test_read_and_collection_filters_both_show_in_status_bar(qapp, qtbot, temp_db):
    collection_queries = CollectionQueries(temp_db)
    collection_id = collection_queries.insert(
        Collection(name="Combined Filter Collection", active=True)
    )

    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    _trigger_collection_filter(window, collection_id)
    _trigger_read_filter(window, "Unread")

    _assert_status_matches_summary(window)
    status = window.status_bar.currentMessage()
    assert "Collection: Combined Filter Collection" in status
    assert "Read: Unread" in status

    window.close()


def test_plot_filter_status_matches_filter_summary(qapp, qtbot, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    _trigger_plot_filter(window, "With Plot")

    _assert_status_matches_summary(window)
    assert "Plot: With Plot" in window.status_bar.currentMessage()
    assert "Collection: All" in window.status_bar.currentMessage()

    window.close()


def test_sort_change_status_matches_filter_summary(qapp, qtbot, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    window.on_order_changed("Author")

    _assert_status_matches_summary(window)
    assert "Sort: Author, Year, Title" in window.status_bar.currentMessage()

    window.close()


def test_active_find_status_matches_filter_summary(qapp, qtbot, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    window.current_filter.search_text = "Moby"
    window.refresh_books()

    _assert_status_matches_summary(window)
    assert "Find: Moby" in window.status_bar.currentMessage()

    window.close()


def test_date_added_filter_status_matches_filter_summary(qapp, qtbot, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    window.current_filter.date_added_since = date(2025, 1, 1)
    window.refresh_books()

    _assert_status_matches_summary(window)
    assert "Added since: 2025-01-01" in window.status_bar.currentMessage()
    assert "Collection: All" in window.status_bar.currentMessage()

    window.close()


def test_selection_status_differs_from_filter_summary(qapp, qtbot, temp_db):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    if not window.books:
        pytest.skip("No books available for selection test")

    book_id = window.books[0].book_id
    window.selected_book_ids.add(book_id)
    window.table.setCurrentCell(0, 1)
    window.set_default_status()

    status = window.status_bar.currentMessage()
    summary = window.filter_summary_label.text()
    assert status != summary
    assert "selected" in status

    window.close()
