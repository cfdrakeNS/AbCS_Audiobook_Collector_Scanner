"""Consolidated MainWindow menu and shortcut tests."""

from __future__ import annotations

from src.accessibility.shortcuts import ShortcutManager
from src.database.models import Collection
from src.database.queries import CollectionQueries


def test_main_window_shortcut_registry_includes_filter_toggles():
    """Main window shortcut map should include plot/read toggles and related keys."""
    keys = set(ShortcutManager.MAIN_WINDOW_SHORTCUTS.keys())
    assert {"P", "R", "W", "L", "U"}.issubset(keys)
    assert "B" not in keys
    assert "O" not in keys


def test_backup_restore_shortcut_registry_browse_and_backup_keys():
    """Backup/restore shortcuts should expose Alt+B browse and Alt+K backup."""
    shortcuts = ShortcutManager.BACKUP_RESTORE_WINDOW_SHORTCUTS
    assert "B" in shortcuts
    assert "K" in shortcuts
    assert "W" not in shortcuts


def test_reading_history_shortcut_registry_keys():
    """Reading history window registry exposes expected Alt keys."""
    shortcuts = ShortcutManager.READING_HISTORY_WINDOW_SHORTCUTS
    assert "S" in shortcuts
    assert "L" in shortcuts
    assert "B" not in shortcuts


def test_view_find_action_uses_ctrl_f(main_window):
    """View menu should expose Find with the standard Ctrl+F shortcut."""
    window = main_window

    find_action = None
    for action in window.view_menu.actions():
        if "Find" in action.text():
            find_action = action
            break

    assert find_action is not None
    action_shortcuts = {seq.toString() for seq in find_action.shortcuts()}
    assert "Ctrl+F" in action_shortcuts


def test_view_menu_reading_history_action(main_window):
    """View menu Reading History action is present, enabled, and visible."""
    window = main_window
    assert hasattr(window, "view_menu")
    view_menu = window.view_menu
    assert view_menu is not None

    reading_history_action = None
    for action in view_menu.actions():
        if action and "Reading &History" in action.text():
            reading_history_action = action
            break

    assert reading_history_action is not None, "Reading History menu item not found"
    assert reading_history_action.isEnabled()
    assert reading_history_action.isVisible()


def test_view_read_menu_entries_match_expected(main_window):
    """Read filter options should be driven by the View > Read menu."""
    window = main_window
    labels = [action.text() for action in window.view_read_menu.actions()]
    assert labels == ["All", "Read", "Unread"]


def test_collection_menu_selection_updates_filter_state(temp_db, main_window):
    """Choosing a collection from View > Collections should update current_filter."""
    collection_queries = CollectionQueries(temp_db)
    collection_id = collection_queries.insert(
        Collection(name="Menu Filter Test", active=True)
    )

    window = main_window
    window.refresh_collections()

    target_action = None
    for action in window.collection_filter_group.actions():
        if action.data() == collection_id:
            target_action = action
            break

    assert target_action is not None
    target_action.trigger()
    assert window.current_filter.collection_id == collection_id


def test_read_menu_selection_updates_filter_and_checked_action(main_window):
    """Selecting View > Read option should update filter state and checked menu item."""
    window = main_window

    target_action = None
    for action in window.read_filter_group.actions():
        if action.data() == "Unread":
            target_action = action
            break

    assert target_action is not None
    target_action.trigger()

    assert window.current_filter.read_filter == "Unread"
    checked = [
        action.data()
        for action in window.read_filter_group.actions()
        if action.isChecked()
    ]
    assert checked == ["Unread"]


def test_sort_menu_primary_action_updates_order_by(main_window):
    """Selecting primary sort action should set order_by and keep sort menu in sync."""
    window = main_window

    genre_action = window._sort_actions_by_key["Genre"]
    genre_action.trigger()

    assert window.current_filter.order_by == "Genre"
    assert window._active_sort_key == "Genre"
    assert "Sort: Genre, Title" in window.filter_summary_label.text()
    assert "(Ascending)" not in window.filter_summary_label.text()
    assert genre_action.isChecked()


def test_sort_menu_non_primary_year_updates_active_sort_and_label(main_window):
    """Selecting non-primary Year sort should set active sort key and ascending status label."""
    window = main_window

    year_action = window._sort_actions_by_key["Year"]
    year_action.trigger()

    assert window._active_sort_key == "Year"
    assert year_action.isChecked()
    assert "Sort: Year (Ascending)" in window.filter_summary_label.text()


def test_refresh_preserves_in_memory_time_sort(main_window):
    """refresh_books should keep Year/Time in-memory sort order and direction."""
    window = main_window

    time_action = window._sort_actions_by_key["Time"]
    time_action.trigger()
    time_action.trigger()

    assert window._active_sort_key == "Time"
    assert window._active_sort_direction == "Descending"
    first_id = window.books[0].book_id if window.books else None

    window.refresh_books()

    assert window._active_sort_key == "Time"
    assert window._active_sort_direction == "Descending"
    assert "Sort: Time (Descending)" in window.filter_summary_label.text()
    if window.books and first_id is not None:
        assert window.books[0].book_id == first_id


def test_escape_clears_active_find_filter_state(main_window, qtbot):
    """ESC from main window should clear active find filter state."""
    window = main_window

    window.current_filter.search_text = "king"
    window.current_filter.is_keyword_search = True
    window.on_escape_pressed()
    qtbot.wait(200)

    assert window.current_filter.search_text == ""
    assert window.current_filter.is_keyword_search is False


def test_invalid_collection_selection_falls_back_to_all(main_window):
    """Invalid View > Collections selection should fall back to All Collections."""
    window = main_window

    window.on_collection_menu_selected(-99999)

    assert window.current_filter.collection_id is None
    checked = [
        action.data()
        for action in window.collection_filter_group.actions()
        if action.isChecked()
    ]
    assert checked == [None]


def _insert_two_books(window):
    from src.database.models import Book
    from src.database.queries import AuthorQueries, BookQueries

    authors = AuthorQueries(window.db)
    books = BookQueries(window.db)
    author_id = authors.insert("Selection Author")
    id1 = books.insert(
        Book(title="Select One", author_id=author_id, year=2000, tracks=1, path="/s1")
    )
    id2 = books.insert(
        Book(title="Select Two", author_id=author_id, year=2001, tracks=1, path="/s2")
    )
    window.refresh_books()
    return id1, id2


def test_selection_disables_navigation_keeps_search_web(main_window):
    window = main_window
    id1, id2 = _insert_two_books(window)
    window.selected_book_ids = {id1, id2}
    window.update_selection_ui()
    assert not window.find_action.isEnabled()
    assert not window.new_book_action.isEnabled()
    assert not window.import_action.isEnabled()
    search = next(a for a, r in window._toolbar_actions if r == "search_web")
    assert search.isEnabled()
    assert window.web_fetch_button.isVisible()
    assert window.web_fetch_button.isEnabled()
    window.selected_book_ids.clear()
    window.update_selection_ui()
    assert window.find_action.isEnabled()
    assert window.new_book_action.isEnabled()


def test_alt_w_with_two_selected_runs_batch(main_window, monkeypatch):
    window = main_window
    id1, id2 = _insert_two_books(window)
    window.selected_book_ids = {id1, id2}
    window.update_selection_ui()
    called = {"n": 0}
    monkeypatch.setattr(
        window, "on_batch_web_fetch_clicked", lambda: called.__setitem__("n", called["n"] + 1)
    )
    window.on_get_web_info_clicked()
    assert called["n"] == 1


def test_alt_w_with_one_selected_does_not_batch(main_window, monkeypatch):
    from src.web.web_fetch_service import WebFetchResult

    window = main_window
    id1, _id2 = _insert_two_books(window)
    window.selected_book_ids = {id1}
    window.update_selection_ui()
    called = {"n": 0}
    monkeypatch.setattr(
        window, "on_batch_web_fetch_clicked", lambda: called.__setitem__("n", 1)
    )
    monkeypatch.setattr(
        "src.web.web_fetch_service.fetch_web_metadata_for_book",
        lambda *a, **k: WebFetchResult(
            canceled=True,
            status_message="canceled",
            dialog_text="canceled",
        ),
    )
    window.on_get_web_info_clicked()
    assert called["n"] == 0


def test_announce_selection_requests_status_speech(main_window, monkeypatch):
    window = main_window
    id1, _id2 = _insert_two_books(window)
    window.table.setCurrentCell(0, 1)
    window.selected_book_ids = {id1}
    calls = []

    def capture(message, timeout_ms=0, announce=False):
        calls.append((message, announce))

    monkeypatch.setattr(window, "set_status", capture)
    window.announce_selection()
    assert calls
    message, announce = calls[-1]
    assert announce is True
    assert "Escape to cancel selection" in message


def test_preview_menu_enabled_for_focused_book(main_window, tmp_path, monkeypatch):
    from src.database.models import Book
    from src.database.queries import AuthorQueries, BookQueries

    window = main_window
    assert hasattr(window, "preview_action")
    audio = tmp_path / "menu_preview.m4b"
    audio.write_bytes(b"x")
    missing = tmp_path / "gone"
    author_id = AuthorQueries(window.db).insert("Preview Menu Author")
    books = BookQueries(window.db)
    good_id = books.insert(
        Book(title="Preview Menu Good", author_id=author_id, path=str(audio))
    )
    bad_id = books.insert(
        Book(title="Preview Menu Bad", author_id=author_id, path=str(missing))
    )
    window.refresh_books()
    monkeypatch.setattr(
        "src.ui.main_window.exec_styled_message_box",
        lambda *args, **kwargs: 0,
    )
    statuses = []
    monkeypatch.setattr(
        window,
        "set_status",
        lambda message, announce=False, timeout_ms=0: statuses.append(message),
    )

    for row, book in enumerate(window.books):
        if book.book_id == good_id:
            window.table.setCurrentCell(row, 1)
            window._update_preview_action_enabled()
            assert window.preview_action.isEnabled() is True
        if book.book_id == bad_id:
            window.table.setCurrentCell(row, 1)
            window._update_preview_action_enabled()
            assert window.preview_action.isEnabled() is True
            window.on_preview_clicked()
            assert any(
                message == f"Book not found in - {missing}" for message in statuses
            )


def test_preview_blocked_while_selecting(main_window, tmp_path, monkeypatch):
    from src.database.models import Book
    from src.database.queries import AuthorQueries, BookQueries

    window = main_window
    audio = tmp_path / "select_preview.mp3"
    audio.write_bytes(b"x")
    author_id = AuthorQueries(window.db).insert("Select Preview Author")
    book_id = BookQueries(window.db).insert(
        Book(title="Select Preview Book", author_id=author_id, path=str(audio))
    )
    window.refresh_books()
    window.selected_book_ids = {book_id}
    window.update_selection_ui()
    opened = []
    monkeypatch.setattr(
        "src.ui.preview_window.show_preview",
        lambda *args, **kwargs: opened.append(True) or (True, "Playing"),
    )
    assert window.preview_action.isEnabled() is False
    window.on_preview_clicked()
    assert opened == []
    assert "Escape to cancel selection" in (window.statusBar().currentMessage() or "")


def test_new_book_blocked_while_selecting(main_window):
    window = main_window
    id1, id2 = _insert_two_books(window)
    window.selected_book_ids = {id1, id2}
    window.update_selection_ui()
    window.on_new_book()
    assert "Escape to cancel selection" in (window.statusBar().currentMessage() or "")
