"""MainWindow filter UI, toolbar toggles, and status/summary sync."""

from __future__ import annotations

from datetime import date

import pytest

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


def test_default_startup_status_and_title_sort(main_window):
    """Startup status matches filter summary with Collection and Sort: Title."""
    window = main_window

    _assert_status_matches_summary(window)
    assert "Collection:" in window.status_bar.currentMessage()
    assert "Sort: Title" in window.status_bar.currentMessage()
    assert "Sort: Title" in window.filter_summary_label.text()
    assert window._active_sort_key == "Title"


def test_collection_filter_status_matches_filter_summary(temp_db, main_window):
    collection_queries = CollectionQueries(temp_db)
    collection_id = collection_queries.insert(
        Collection(name="Status Bar Test Collection", active=True)
    )

    window = main_window
    _trigger_collection_filter(window, collection_id)

    _assert_status_matches_summary(window)
    assert "Collection: Status Bar Test Collection" in window.status_bar.currentMessage()


def test_read_filter_status_matches_filter_summary(main_window):
    window = main_window
    _trigger_read_filter(window, "Unread")

    _assert_status_matches_summary(window)
    assert "Read: Unread" in window.status_bar.currentMessage()
    assert "Collection: All" in window.status_bar.currentMessage()


def test_read_and_collection_filters_both_show_in_status_bar(temp_db, main_window):
    collection_queries = CollectionQueries(temp_db)
    collection_id = collection_queries.insert(
        Collection(name="Combined Filter Collection", active=True)
    )

    window = main_window
    _trigger_collection_filter(window, collection_id)
    _trigger_read_filter(window, "Unread")

    _assert_status_matches_summary(window)
    status = window.status_bar.currentMessage()
    assert "Collection: Combined Filter Collection" in status
    assert "Read: Unread" in status


def test_plot_filter_status_matches_filter_summary(main_window):
    window = main_window
    _trigger_plot_filter(window, "With Plot")

    _assert_status_matches_summary(window)
    assert "Plot: With Plot" in window.status_bar.currentMessage()
    assert "Collection: All" in window.status_bar.currentMessage()


def test_sort_change_status_matches_filter_summary(main_window):
    window = main_window
    window.on_order_changed("Author")

    _assert_status_matches_summary(window)
    assert "Sort: Author, Year, Title" in window.status_bar.currentMessage()


def test_title_sort_shows_in_filter_summary(main_window):
    window = main_window

    window.on_order_changed("Author")
    assert "Sort: Author, Year, Title" in window.filter_summary_label.text()

    window.on_order_changed("Title")
    text = window.filter_summary_label.text()
    assert "Sort: Title" in text, text
    assert window._active_sort_key == "Title"


def test_title_sort_after_time_sort_shows_in_filter_summary(main_window):
    window = main_window

    window._sort_actions_by_key["Time"].trigger()
    assert window._active_sort_key == "Time"
    assert "Sort: Time" in window.filter_summary_label.text()

    window.on_order_changed("Title")
    text = window.filter_summary_label.text()
    assert "Sort: Time" not in text, text
    assert "Sort: Title" in text, text
    assert window._active_sort_key == "Title"


def test_active_find_status_matches_filter_summary(main_window):
    window = main_window
    window.current_filter.search_text = "Moby"
    window.refresh_books()

    _assert_status_matches_summary(window)
    assert "Find: Moby" in window.status_bar.currentMessage()


def test_date_added_filter_status_matches_filter_summary(main_window):
    window = main_window
    window.current_filter.date_added_since = date(2025, 1, 1)
    window.refresh_books()

    _assert_status_matches_summary(window)
    assert "Added since: 2025-01-01" in window.status_bar.currentMessage()
    assert "Collection: All" in window.status_bar.currentMessage()


def test_selection_status_differs_from_filter_summary(main_window):
    window = main_window
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


def test_plot_menu_selection_updates_filter(main_window):
    window = main_window

    target_action = None
    for action in window.plot_filter_group.actions():
        if action.data() == "With Plot":
            target_action = action
            break

    assert target_action is not None
    target_action.trigger()

    assert window.current_filter.plot_filter == "With Plot"
    assert window.plot_filter_action.isChecked()

    window.plot_filter_action.trigger()
    assert window.current_filter.plot_filter == "All"
    assert not window.plot_filter_action.isChecked()


def test_read_filter_toolbar_toggle(main_window):
    window = main_window

    window.read_filter_action.trigger()
    assert window.current_filter.read_filter == "Read"
    assert window.read_filter_action.isChecked()

    window.read_filter_action.trigger()
    assert window.current_filter.read_filter == "All"
    assert not window.read_filter_action.isChecked()


def test_want_to_read_view_menu_sets_filter(main_window):
    window = main_window
    action = None
    for item in window.view_want_to_read_menu.actions():
        if item.data() == "Want to Read":
            action = item
            break
    assert action is not None
    action.trigger()
    assert window.current_filter.want_to_read_filter == "Want to Read"
    assert window.want_to_read_filter_action.isChecked()


def test_want_to_read_filter_toolbar_toggle(main_window):
    window = main_window

    window.want_to_read_filter_action.trigger()
    assert window.current_filter.want_to_read_filter == "Want to Read"
    assert window.want_to_read_filter_action.isChecked()
    assert "Want to read" in window._filter_summary_text()

    window.want_to_read_filter_action.trigger()
    assert window.current_filter.want_to_read_filter == "All"
    assert not window.want_to_read_filter_action.isChecked()


def test_unread_menu_unchecks_read_toolbar_toggle(main_window):
    window = main_window

    unread_action = None
    for action in window.read_filter_group.actions():
        if action.data() == "Unread":
            unread_action = action
            break

    assert unread_action is not None
    unread_action.trigger()

    assert window.current_filter.read_filter == "Unread"
    assert not window.read_filter_action.isChecked()


def test_read_filter_shortcut_from_unread_sets_read(main_window):
    window = main_window

    window.current_filter.read_filter = "Unread"
    window._sync_read_menu_selection()
    window._sync_read_toolbar_toggle()

    window.on_read_filter_shortcut()

    assert window.current_filter.read_filter == "Read"
    assert window.read_filter_action.isChecked()
