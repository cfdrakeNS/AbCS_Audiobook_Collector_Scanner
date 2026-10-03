"""MainWindow accessibility review fixes: Edit menu keys, Escape sync, Website."""

from __future__ import annotations


def _access_key(text: str):
    idx = 0
    while idx < len(text) - 1:
        if text[idx] == "&":
            if text[idx + 1] == "&":
                idx += 2
                continue
            return text[idx + 1].upper()
        idx += 1
    return None


def test_edit_menu_access_keys_are_unique(main_window):
    keys = [
        _access_key(action.text().split("\t")[0])
        for action in main_window.edit_menu.actions()
        if not action.isSeparator()
    ]
    keys = [key for key in keys if key]
    assert len(keys) == len(set(keys)), keys
    assert main_window.clear_listen_progress_action.text() == "Clear listening &position"


def test_escape_clears_want_to_read_and_syncs_view_menu(main_window):
    window = main_window
    menu_action = next(
        item
        for item in window.view_want_to_read_menu.actions()
        if item.data() == "Want to Read"
    )
    menu_action.trigger()
    assert window.current_filter.want_to_read_filter == "Want to Read"
    assert menu_action.isChecked()

    window.on_escape_pressed()

    assert window.current_filter.want_to_read_filter == "All"
    assert not window.want_to_read_filter_action.isChecked()
    checked = [
        item.data()
        for item in window.want_to_read_filter_group.actions()
        if item.isChecked()
    ]
    assert checked == ["All"]


def test_help_website_opens_website_url(main_window, monkeypatch):
    from src.app_urls import ABCS_WEBSITE_URL

    opened = []
    monkeypatch.setattr(
        "src.app_urls.open_public_url", lambda url: opened.append(url) or True
    )
    statuses = []
    monkeypatch.setattr(
        main_window,
        "set_status",
        lambda message, timeout_ms=0, announce=False: statuses.append(
            (message, announce)
        ),
    )

    main_window.on_open_website()

    assert opened == [ABCS_WEBSITE_URL]
    assert statuses == [("Opened the AbCS website in your browser.", True)]


def test_copy_cell_announces_status(main_window, monkeypatch):
    from src.database.models import Book
    from src.database.queries import AuthorQueries, BookQueries

    window = main_window
    author_id = AuthorQueries(window.db).insert("Copy Author")
    BookQueries(window.db).insert(Book(title="Copy Book", author_id=author_id))
    window.refresh_books()
    window.table.setCurrentCell(0, 1)
    monkeypatch.setattr("src.ui.main_window.copy_plain_text", lambda _text: True)
    statuses = []
    monkeypatch.setattr(
        window,
        "set_status",
        lambda message, timeout_ms=0, announce=False: statuses.append(
            (message, announce)
        ),
    )

    assert window._copy_current_table_cell() is True
    assert statuses == [("Copied.", True)]
