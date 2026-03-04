"""Targeted MainWindow tests for menu-driven shortcuts and filters."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from accessibility.scaling import UIScaler
from accessibility.shortcuts import ShortcutManager
from accessibility.theme_manager import ThemeManager
from database.connection import DatabaseManager
from database.models import Collection
from database.queries import CollectionQueries
from ui.main_window import MainWindow


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def temp_db(tmp_path):
    """Provide a writable temporary copy of the project database."""
    data_dir = Path(PROJECT_ROOT) / "data"
    candidates = [
        data_dir / "abcs.db",
        data_dir / "wh abcs.db",
    ]
    backup_candidates = sorted(
        data_dir.glob("abcs.db.backup.*"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    candidates.extend(backup_candidates)

    source_db = next((path for path in candidates if path.exists()), None)
    if source_db is None:
        raise FileNotFoundError(
            f"No testable database found in {data_dir}. Expected one of: abcs.db, wh abcs.db, or abcs.db.backup.*"
        )

    target_db = tmp_path / "abcs_test.db"
    shutil.copy2(source_db, target_db)

    db = DatabaseManager(str(target_db))
    try:
        yield db
    finally:
        db.close()


def test_main_window_shortcut_registry_removes_legacy_alt_keys():
    """Main window shortcut map should not contain deprecated Alt+R/Alt+O entries."""
    keys = set(ShortcutManager.MAIN_WINDOW_SHORTCUTS.keys())

    assert "R" not in keys
    assert "O" not in keys
    assert "B" in keys
    assert "U" in keys


def test_view_find_action_uses_ctrl_f(qapp, qtbot, temp_db):
    """View menu should expose Find with the standard Ctrl+F shortcut."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    find_action = None
    for action in window.view_menu.actions():
        if "Find" in action.text():
            find_action = action
            break

    assert find_action is not None
    action_shortcuts = {seq.toString() for seq in find_action.shortcuts()}
    assert "Ctrl+F" in action_shortcuts

    window.close()


def test_view_read_menu_entries_match_expected(qapp, qtbot, temp_db):
    """Read filter options should be driven by the View > Read menu."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    labels = [action.text() for action in window.view_read_menu.actions()]
    assert labels == ["All", "Read", "Unread"]

    window.close()


def test_collection_menu_selection_updates_filter_state(qapp, qtbot, temp_db):
    """Choosing a collection from View > Collections should update current_filter."""
    collection_queries = CollectionQueries(temp_db)
    collection_id = collection_queries.insert(
        Collection(name="Menu Filter Test", active=True)
    )

    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    window.refresh_collections()

    target_action = None
    for action in window.collection_filter_group.actions():
        if action.data() == collection_id:
            target_action = action
            break

    assert target_action is not None
    target_action.trigger()

    assert window.current_filter.collection_id == collection_id

    window.close()


def test_read_menu_selection_updates_filter_and_checked_action(qapp, qtbot, temp_db):
    """Selecting View > Read option should update filter state and checked menu item."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    target_action = None
    for action in window.read_filter_group.actions():
        if action.data() == "Unread":
            target_action = action
            break

    assert target_action is not None
    target_action.trigger()

    assert window.current_filter.read_filter == "Unread"
    checked = [action.data()
               for action in window.read_filter_group.actions() if action.isChecked()]
    assert checked == ["Unread"]

    window.close()


def test_sort_menu_primary_action_updates_order_by(qapp, qtbot, temp_db):
    """Selecting primary sort action should set order_by and keep sort menu in sync."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    genre_action = window._sort_actions_by_key["Genre"]
    genre_action.trigger()

    assert window.current_filter.order_by == "Genre"
    assert window._active_sort_key == "Genre"
    assert "Genre" in window.sort_label.text()
    assert genre_action.isChecked()

    window.close()


def test_sort_menu_non_primary_year_updates_active_sort_and_label(qapp, qtbot, temp_db):
    """Selecting non-primary Year sort should set active sort key and ascending status label."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    year_action = window._sort_actions_by_key["Year"]
    year_action.trigger()

    assert window._active_sort_key == "Year"
    assert year_action.isChecked()
    assert window.sort_label.text() == "Sorted by: Year (Ascending)"

    window.close()


def test_escape_clears_active_find_filter_state(qapp, qtbot, temp_db):
    """ESC from main window should clear active find filter state."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    window.current_filter.search_text = "king"
    window.current_filter.is_keyword_search = True
    window.on_escape_pressed()
    qtbot.wait(200)

    assert window.current_filter.search_text == ""
    assert window.current_filter.is_keyword_search is False

    window.close()


def test_invalid_collection_selection_falls_back_to_all(qapp, qtbot, temp_db):
    """Invalid View > Collections selection should fall back to All Collections."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    window.on_collection_menu_selected(-99999)

    assert window.current_filter.collection_id is None
    checked = [action.data() for action in window.collection_filter_group.actions(
    ) if action.isChecked()]
    assert checked == [None]

    window.close()
