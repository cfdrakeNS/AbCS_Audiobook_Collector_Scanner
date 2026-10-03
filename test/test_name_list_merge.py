"""Name-list merge when Save hits an existing author, series, or genre name."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMessageBox

from src.database.models import Book, Collection
from src.database.queries import (
    AuthorQueries,
    BookQueries,
    CollectionQueries,
    GenreQueries,
    SeriesQueries,
)
from src.ui.name_list_window import NameListWindow


def _select_row(window: NameListWindow, item_id: int) -> None:
    for row in range(window.table.rowCount()):
        name_item = window.table.item(row, window.COL_NAME)
        if name_item is not None and name_item.data(Qt.UserRole) == item_id:
            window.table.selectRow(row)
            window.table.setCurrentCell(row, window.COL_NAME)
            return
    raise AssertionError(f"Row for id {item_id} not found")


def _edit_name(window: NameListWindow, item_id: int, new_name: str) -> None:
    _select_row(window, item_id)
    window.on_edit()
    window.name_edit.setText(new_name)


def test_series_merge_yes_moves_books_and_deletes_source(
    temp_db, ui_scaler, theme_manager, qtbot, monkeypatch
):
    authors = AuthorQueries(temp_db)
    series = SeriesQueries(temp_db)
    books = BookQueries(temp_db)
    author_id = authors.insert("Nl Merge Series Author")
    source_id = series.insert("Merge 87 Precinct")
    target_id = series.insert("Merge 87th Precinct")
    books.insert(
        Book(
            title="Cop Book",
            author_id=author_id,
            series_id=source_id,
            series_number=3,
            year=1990,
            tracks=1,
            path="/nl/series-merge",
        )
    )

    replies = [QMessageBox.Yes, QMessageBox.Ok]
    prompts = []

    def fake_box(*_args, **kwargs):
        prompts.append(kwargs.get("text", ""))
        return replies.pop(0)

    monkeypatch.setattr("src.ui.name_list_window.exec_styled_message_box", fake_box)

    window = NameListWindow(temp_db, ui_scaler, theme_manager, "series")
    qtbot.addWidget(window)
    _edit_name(window, source_id, "Merge 87th Precinct")
    assert window.on_save() is True

    assert series.get_by_id(source_id) is None
    kept = series.get_by_id(target_id)
    assert kept is not None
    assert kept.name == "Merge 87th Precinct"
    remaining = [b for b in books.get_all() if b.title == "Cop Book"]
    assert len(remaining) == 1
    assert remaining[0].series_id == target_id
    assert remaining[0].series_number == 3
    assert any(
        "Update 1 books from Merge 87 Precinct to Merge 87th Precinct" in text
        for text in prompts
    )
    assert any(
        "1 books. Series changed from Merge 87 Precinct to Merge 87th Precinct."
        in text
        for text in prompts
    )
    window.close()


def test_series_merge_no_leaves_names_unchanged(
    temp_db, ui_scaler, theme_manager, qtbot, monkeypatch
):
    series = SeriesQueries(temp_db)
    source_id = series.insert("Nl Series Source No")
    target_id = series.insert("Nl Series Target No")

    replies = [QMessageBox.No]
    monkeypatch.setattr(
        "src.ui.name_list_window.exec_styled_message_box",
        lambda *_a, **_k: replies.pop(0),
    )

    window = NameListWindow(temp_db, ui_scaler, theme_manager, "series")
    qtbot.addWidget(window)
    _edit_name(window, source_id, "Nl Series Target No")
    assert window.on_save() is False

    assert series.get_by_id(source_id) is not None
    assert series.get_by_id(target_id) is not None
    assert series.get_by_id(source_id).name == "Nl Series Source No"
    window.close()


def test_same_row_case_change_does_not_ask_merge(
    temp_db, ui_scaler, theme_manager, qtbot, monkeypatch
):
    series = SeriesQueries(temp_db)
    series_id = series.insert("Nl Case Series Unique")
    calls = []

    def fake_box(*_args, **kwargs):
        calls.append(kwargs)
        return QMessageBox.Ok

    monkeypatch.setattr("src.ui.name_list_window.exec_styled_message_box", fake_box)

    window = NameListWindow(temp_db, ui_scaler, theme_manager, "series")
    qtbot.addWidget(window)
    _edit_name(window, series_id, "nl case series unique")
    assert window.on_save() is True
    assert series.get_by_id(series_id).name == "Nl Case Series Unique"
    assert calls == []
    window.close()


def test_author_merge_yes(
    temp_db, ui_scaler, theme_manager, qtbot, monkeypatch
):
    authors = AuthorQueries(temp_db)
    books = BookQueries(temp_db)
    source_id = authors.insert("Nl Author Source")
    target_id = authors.insert("Nl Author Target")
    books.insert(
        Book(
            title="Author Merge Book",
            author_id=source_id,
            year=2001,
            tracks=1,
            path="/nl/author-merge",
        )
    )

    replies = [QMessageBox.Yes, QMessageBox.Ok]
    monkeypatch.setattr(
        "src.ui.name_list_window.exec_styled_message_box",
        lambda *_a, **_k: replies.pop(0),
    )

    window = NameListWindow(temp_db, ui_scaler, theme_manager, "author")
    qtbot.addWidget(window)
    _edit_name(window, source_id, "Nl Author Target")
    assert window.on_save() is True
    assert authors.get_by_id(source_id) is None
    remaining = [b for b in books.get_all() if b.title == "Author Merge Book"]
    assert remaining[0].author_id == target_id
    window.close()


def test_genre_merge_yes(
    temp_db, ui_scaler, theme_manager, qtbot, monkeypatch
):
    authors = AuthorQueries(temp_db)
    genres = GenreQueries(temp_db)
    books = BookQueries(temp_db)
    author_id = authors.insert("Nl Genre Merge Author")
    source_id = genres.insert("Nl Genre Source")
    target_id = genres.insert("Nl Genre Target")
    books.insert(
        Book(
            title="Genre Merge Book",
            author_id=author_id,
            genre_id=source_id,
            year=2002,
            tracks=1,
            path="/nl/genre-merge",
        )
    )

    replies = [QMessageBox.Yes, QMessageBox.Ok]
    monkeypatch.setattr(
        "src.ui.name_list_window.exec_styled_message_box",
        lambda *_a, **_k: replies.pop(0),
    )

    window = NameListWindow(temp_db, ui_scaler, theme_manager, "genre")
    qtbot.addWidget(window)
    _edit_name(window, source_id, "Nl Genre Target")
    assert window.on_save() is True
    assert genres.get_by_id(source_id) is None
    remaining = [b for b in books.get_all() if b.title == "Genre Merge Book"]
    assert remaining[0].genre_id == target_id
    window.close()


def test_collection_duplicate_shows_warning_only(
    temp_db, ui_scaler, theme_manager, qtbot, monkeypatch
):
    collections = CollectionQueries(temp_db)
    source_id = collections.insert(
        Collection(name="Merge Collection Source", active=True)
    )
    collections.insert(Collection(name="Merge Collection Target", active=True))

    prompts = []

    def fake_box(*_args, **kwargs):
        prompts.append(kwargs.get("text", ""))
        return QMessageBox.Ok

    monkeypatch.setattr("src.ui.name_list_window.exec_styled_message_box", fake_box)

    window = NameListWindow(temp_db, ui_scaler, theme_manager, "collection")
    qtbot.addWidget(window)
    _edit_name(window, source_id, "Merge Collection Target")
    assert window.on_save() is False
    assert collections.get_by_id(source_id) is not None
    assert collections.get_by_id(source_id).name == "Merge Collection Source"
    assert any("already exists" in text.lower() for text in prompts)
    assert not any("Update" in text and "books from" in text for text in prompts)
    window.close()


def test_save_moves_focus_to_updated_row(
    temp_db, ui_scaler, theme_manager, qtbot, qapp
):
    series = SeriesQueries(temp_db)
    series_id = series.insert("Focus After Save Series")

    window = NameListWindow(temp_db, ui_scaler, theme_manager, "series")
    qtbot.addWidget(window)
    window.show()
    _edit_name(window, series_id, "Focus After Save Series Renamed")
    assert window.on_save() is True
    qapp.processEvents()
    qtbot.wait(20)

    assert window.table.hasFocus()
    assert window._selected_item_id() == series_id
    assert series.get_by_id(series_id).name == "Focus After Save Series Renamed"
    window.close()


def test_merge_yes_moves_focus_to_kept_row(
    temp_db, ui_scaler, theme_manager, qtbot, qapp, monkeypatch
):
    series = SeriesQueries(temp_db)
    source_id = series.insert("Focus Merge Source")
    target_id = series.insert("Focus Merge Target")

    replies = [QMessageBox.Yes, QMessageBox.Ok]
    monkeypatch.setattr(
        "src.ui.name_list_window.exec_styled_message_box",
        lambda *_a, **_k: replies.pop(0),
    )

    window = NameListWindow(temp_db, ui_scaler, theme_manager, "series")
    qtbot.addWidget(window)
    window.show()
    _edit_name(window, source_id, "Focus Merge Target")
    assert window.on_save() is True
    qapp.processEvents()
    qtbot.wait(20)

    assert window.table.hasFocus()
    assert window._selected_item_id() == target_id
    window.close()


def test_double_click_row_starts_edit(
    temp_db, ui_scaler, theme_manager, qtbot, qapp
):
    series_id = SeriesQueries(temp_db).insert("Double Click Series")
    window = NameListWindow(temp_db, ui_scaler, theme_manager, "series")
    qtbot.addWidget(window)
    window.show()
    window.focus_and_select_row(series_id)
    qapp.processEvents()

    assert window._collection_editor_locked
    window.table.cellDoubleClicked.emit(window.table.currentRow(), 0)
    qapp.processEvents()

    assert not window._collection_editor_locked
    assert window.name_edit.hasFocus()
    assert window.name_edit.text() == "Double Click Series"
    window.close()


def test_tab_order_includes_table_for_series(
    temp_db, ui_scaler, theme_manager, qtbot
):
    SeriesQueries(temp_db).insert("Tab Order Series")
    window = NameListWindow(temp_db, ui_scaler, theme_manager, "series")
    qtbot.addWidget(window)
    window.show()
    window._apply_tab_order()

    focusable = []
    widget = window.find_edit
    seen = {id(widget)}
    for _ in range(40):
        widget = widget.nextInFocusChain()
        if widget is None or id(widget) in seen:
            break
        seen.add(id(widget))
        if widget.window() is not window:
            continue
        if not widget.isVisible() or not widget.isEnabled():
            continue
        # Tab stops on TabFocus/StrongFocus (list included).
        if not (int(widget.focusPolicy()) & int(Qt.TabFocus)):
            continue
        focusable.append(widget)
        if widget is window.find_edit:
            break

    assert window.table in focusable
    assert window.edit_button in focusable
    window.close()


def test_escape_edit_without_changes_stays_in_window(
    temp_db, ui_scaler, theme_manager, qtbot
):
    series_id = SeriesQueries(temp_db).insert("Cancel Edit Series")
    window = NameListWindow(temp_db, ui_scaler, theme_manager, "series")
    qtbot.addWidget(window)
    window.show()
    _select_row(window, series_id)
    window.on_edit()
    assert not window._collection_editor_locked
    window.on_cancel_edit()
    assert window._collection_editor_locked
    assert window.isVisible()
    window.close()


def test_name_list_sort_by_name(temp_db, ui_scaler, theme_manager):
    series_queries = SeriesQueries(temp_db)
    zulu_id = series_queries.insert("Zulu")
    alpha_id = series_queries.insert("Alpha")
    window = NameListWindow(temp_db, ui_scaler, theme_manager, "series")
    window._sort_by = "name"
    window._sort_ascending = True
    all_items = {item.series_id: item for item in window.query.get_all()}
    items = window._sort_items_for_display(
        [all_items[zulu_id], all_items[alpha_id]]
    )
    assert [item.name for item in items] == ["Alpha", "Zulu"]
    window.close()


def test_escape_in_find_moves_focus_to_list(
    temp_db, ui_scaler, theme_manager, qtbot, qapp
):
    SeriesQueries(temp_db).insert("Escape Find Series")
    window = NameListWindow(temp_db, ui_scaler, theme_manager, "series")
    qtbot.addWidget(window)
    window.show()
    window.activateWindow()
    window.find_edit.setFocus(Qt.OtherFocusReason)
    qtbot.waitUntil(lambda: window.find_edit.hasFocus(), timeout=1000)
    window.find_edit.setText("Escape")
    window._apply_find_filter()
    assert window.table.focusPolicy() == Qt.StrongFocus

    window.on_cancel_edit()
    qapp.processEvents()

    assert window.isVisible()
    assert window.find_edit.text() == ""
    assert window.table.focusPolicy() == Qt.StrongFocus
    assert window.table.hasFocus()
    window.close()


def test_name_list_edit_label_uses_entity_and_has_no_alt_m(
    temp_db, ui_scaler, theme_manager, qtbot
):
    from PySide6.QtWidgets import QLabel

    from src.accessibility.shortcuts import ShortcutManager

    for list_type, expected in (
        ("author", "Author:"),
        ("series", "Series:"),
        ("genre", "Genre:"),
    ):
        window = NameListWindow(temp_db, ui_scaler, theme_manager, list_type)
        qtbot.addWidget(window)
        labels = [
            label
            for label in window.findChildren(QLabel)
            if label.buddy() is window.name_edit
        ]
        assert [label.text() for label in labels] == [expected]
        assert Qt.Key_M not in window._allowed_alt_letter_keys()
        window.close()
    assert "M" not in ShortcutManager.NAMELIST_WINDOW_SHORTCUTS


def test_name_list_alt_s_focuses_sort_and_rows_do_not_set_status(
    temp_db, ui_scaler, theme_manager, qtbot, monkeypatch
):
    queries = SeriesQueries(temp_db)
    first_id = queries.insert("Aaa Status Quiet Series")
    second_id = queries.insert("Bbb Status Quiet Series")
    window = NameListWindow(temp_db, ui_scaler, theme_manager, "series")
    qtbot.addWidget(window)

    focused = []
    monkeypatch.setattr(
        window.sort_combo, "setFocus", lambda *_args: focused.append(True)
    )
    shortcut = next(
        s
        for s in window.findChildren(QShortcut)
        if s.key() == QKeySequence("Alt+S")
    )
    shortcut.activated.emit()
    assert focused == [True]
    assert Qt.Key_S in window._allowed_alt_letter_keys()

    messages = []
    monkeypatch.setattr(window, "set_status", lambda msg, **_kw: messages.append(msg))
    window.focus_and_select_row(first_id)
    window.focus_and_select_row(second_id)
    window.table.selectRow(0)
    window.table.selectRow(1)
    window.focus_list()
    assert messages == []
    window.close()


def test_author_find_status_has_no_search_hint(
    temp_db, ui_scaler, theme_manager, qtbot, monkeypatch
):
    from src.database.queries import AuthorQueries

    AuthorQueries(temp_db).get_or_create("Zzhint, Quietly")
    window = NameListWindow(temp_db, ui_scaler, theme_manager, "author")
    qtbot.addWidget(window)
    messages = []
    monkeypatch.setattr(window, "set_status", lambda msg, **_kw: messages.append(msg))

    assert window.find_first_match("Zzhint") is True
    window.find_first_match("No Such Author Xyz")

    assert messages
    for msg in messages:
        assert "enter for next" not in msg.lower()
        assert "new search" not in msg.lower()
    window.close()


def test_name_list_sort_moves_current_row_to_first(
    temp_db, ui_scaler, theme_manager, qtbot
):
    queries = SeriesQueries(temp_db)
    queries.insert("Aaa Sort First Series")
    last_id = queries.insert("Zzz Sort Last Series")
    window = NameListWindow(temp_db, ui_scaler, theme_manager, "series")
    qtbot.addWidget(window)
    window.focus_and_select_row(last_id)
    assert window.table.currentRow() > 0

    window.sort_combo.setCurrentIndex(1)
    assert window.table.currentRow() == 0

    window._on_table_header_clicked(0)
    assert window.table.currentRow() == 0
    window.close()


def test_open_with_initial_series_focuses_table_on_match(
    temp_db, ui_scaler, theme_manager, qtbot
):
    series_id = SeriesQueries(temp_db).insert("Initial Focus Series")
    window = NameListWindow(
        temp_db,
        ui_scaler,
        theme_manager,
        "series",
        initial_name="Initial Focus Series",
    )
    qtbot.addWidget(window)
    window.show()
    window.activateWindow()
    qtbot.waitUntil(lambda: window.table.hasFocus(), timeout=1000)

    assert window._selected_item_id() == series_id
    assert window.find_edit.text() == ""
    window.close()


def test_open_with_unmatched_initial_series_focuses_full_table(
    temp_db, ui_scaler, theme_manager, qtbot
):
    SeriesQueries(temp_db).insert("Some Other Series")
    window = NameListWindow(
        temp_db,
        ui_scaler,
        theme_manager,
        "series",
        initial_name="Zzz No Such Series",
    )
    qtbot.addWidget(window)
    window.show()
    window.activateWindow()
    qtbot.waitUntil(lambda: window.table.hasFocus(), timeout=1000)

    assert window.find_edit.text() == ""
    assert window.table.currentRow() >= 0
    assert not window.table.isRowHidden(window.table.currentRow())
    window.close()
