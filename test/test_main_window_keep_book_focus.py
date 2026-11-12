"""Keep the focused book as current after sort and filter."""

from __future__ import annotations

from datetime import date

import pytest
from PySide6.QtWidgets import QMessageBox

from src.database.models import Book, Collection
from src.database.queries import AuthorQueries, BookQueries, CollectionQueries


def _current_book_id(window):
    row = window.table.currentRow()
    if 0 <= row < len(window.books):
        return window.books[row].book_id
    return None


def _insert_focus_books(window):
    authors = AuthorQueries(window.db)
    books = BookQueries(window.db)
    collection_id = window.current_filter.collection_id
    zebra = authors.insert("Zebra Author")
    alpha = authors.insert("Alpha Author")
    middle = authors.insert("Middle Author")
    id_middle = books.insert(
        Book(
            title="Middle Book",
            author_id=zebra,
            year=2000,
            tracks=1,
            path="/m",
            collection_id=collection_id,
        )
    )
    id_alpha = books.insert(
        Book(
            title="Alpha Book",
            author_id=alpha,
            year=1990,
            tracks=1,
            path="/a",
            read_date=date(2020, 1, 1),
            collection_id=collection_id,
        )
    )
    id_zulu = books.insert(
        Book(
            title="Zulu Book",
            author_id=middle,
            year=2010,
            tracks=1,
            path="/z",
            collection_id=collection_id,
        )
    )
    window.refresh_books()
    window.on_order_changed("Title")
    return id_middle, id_alpha, id_zulu


def test_rows_to_selection_merges_consecutive_rows(qapp):
    from PySide6.QtGui import QStandardItemModel

    from src.ui.table_selection import rows_to_selection

    model = QStandardItemModel(10, 3)
    selection = rows_to_selection(model, [5, 1, 2, 3, 7], 3)
    ranges = [(r.top(), r.bottom(), r.left(), r.right()) for r in selection]
    assert ranges == [(1, 3, 0, 2), (5, 5, 0, 2), (7, 7, 0, 2)]


def test_shift_down_selects_whole_rows(main_window, monkeypatch):
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent

    window = main_window
    _insert_focus_books(window)
    monkeypatch.setattr(window, "announce_selection", lambda: None)
    window.table.setCurrentCell(0, 1)
    down = QKeyEvent(QEvent.KeyPress, Qt.Key_Down, Qt.ShiftModifier)
    window.table_key_press(down)
    window.table_key_press(down)
    assert len(window.selected_book_ids) == 2
    selected = window.table.selectionModel().selectedIndexes()
    assert {i.row() for i in selected} == {0, 1}
    assert len(selected) == 2 * window.table.columnCount()
    assert window.table.currentRow() == 1

    # Rows that are not next to each other: one range per run of rows.
    ids = {window.books[0].book_id, window.books[2].book_id}
    window._apply_row_selection_by_book_ids(ids)
    selected = window.table.selectionModel().selectedIndexes()
    assert {i.row() for i in selected} == {0, 2}
    assert len(selected) == 2 * window.table.columnCount()


def test_column_jump_moves_highlight_with_focus(main_window):
    """Alt+1..7 move the current cell and its highlight, like Left/Right."""
    window = main_window
    id_middle, _id_alpha, _id_zulu = _insert_focus_books(window)
    window.focus_book_by_id(id_middle, 1)
    row = window.table.currentRow()
    for column in range(7):
        assert not window.table.isColumnHidden(column)
        window.jump_to_column(column)
        assert window.table.currentRow() == row
        assert window.table.currentColumn() == column
        selected = window.table.selectionModel().selectedIndexes()
        assert [(i.row(), i.column()) for i in selected] == [(row, column)]


def test_tab_stays_in_table_when_no_footer_buttons(main_window, monkeypatch):
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent

    window = main_window
    id_middle, _id_alpha, _id_zulu = _insert_focus_books(window)
    window.focus_book_by_id(id_middle, 1)
    moves = []
    monkeypatch.setattr(window, "focusNextChild", lambda: moves.append("next") or True)
    monkeypatch.setattr(
        window, "focusPreviousChild", lambda: moves.append("previous") or True
    )
    assert window._footer_buttons_visible() is False

    for key, modifiers in ((Qt.Key_Tab, Qt.NoModifier), (Qt.Key_Backtab, Qt.ShiftModifier)):
        event = QKeyEvent(QEvent.KeyPress, key, modifiers)
        window.accessible_table_key_press(event)
        assert event.isAccepted()
    assert moves == []

    monkeypatch.setattr(window, "_footer_buttons_visible", lambda: True)
    window.accessible_table_key_press(QKeyEvent(QEvent.KeyPress, Qt.Key_Tab, Qt.NoModifier))
    window.accessible_table_key_press(
        QKeyEvent(QEvent.KeyPress, Qt.Key_Backtab, Qt.ShiftModifier)
    )
    assert moves == ["next", "previous"]


@pytest.mark.parametrize("masked", [True, False])
def test_read_date_dialog_has_ok_and_clear_buttons(main_window, monkeypatch, masked):
    """The screen reader (typed) version has the same buttons as the calendar version."""
    from PySide6.QtWidgets import QDialog

    from src.accessibility.masked_date_fields import MaskedDateEdit
    from src.ui.accessible_dialog import AccessibleDialog

    window = main_window
    _insert_focus_books(window)
    if masked:
        monkeypatch.setattr(
            "src.accessibility.masked_date_fields.make_date_field",
            lambda parent=None, **kw: MaskedDateEdit(parent),
        )
    else:
        monkeypatch.setattr(
            "src.accessibility.masked_date_fields.make_date_field",
            lambda parent=None, **kw: None,
        )
    captured = {}

    def fake_exec(dialog):
        captured["dialog"] = dialog
        return QDialog.Rejected

    monkeypatch.setattr(AccessibleDialog, "exec", fake_exec)
    window.show_read_date_dialog(0)

    dlg = captured["dialog"]
    assert dlg.use_masked is masked
    assert dlg.ok_button.text() == "OK"
    assert dlg.clear_button.text() == "Clear"
    # Spoken names match the visible labels.
    assert dlg.ok_button.accessibleName() == "OK"
    assert dlg.clear_button.accessibleName() == "Clear"
    # Focus starts in the date field, so its description carries the instructions.
    description = dlg.date_field.accessibleDescription()
    assert window.books[0].title in description
    assert "OK saves the date. Clear removes it." in description


def test_author_sort_keeps_focused_book(main_window, qapp, qtbot):
    window = main_window
    id_middle, _id_alpha, _id_zulu = _insert_focus_books(window)
    window.focus_book_by_id(id_middle, 1)
    assert _current_book_id(window) == id_middle

    window.on_order_changed("Author")
    qapp.processEvents()
    qtbot.wait(20)

    assert _current_book_id(window) == id_middle
    assert window.books[window.table.currentRow()].title == "Middle Book"


def test_year_sort_keeps_focused_book(main_window, qapp, qtbot):
    window = main_window
    _id_middle, _id_alpha, id_zulu = _insert_focus_books(window)
    window.focus_book_by_id(id_zulu, 1)
    assert _current_book_id(window) == id_zulu

    window._sort_actions_by_key["Year"].trigger()
    qapp.processEvents()
    qtbot.wait(20)

    assert _current_book_id(window) == id_zulu
    year_keys = [(book.year is None, book.year or 0) for book in window.books]
    assert year_keys == sorted(year_keys)


def test_unread_filter_keeps_unread_book(main_window, qapp, qtbot):
    window = main_window
    id_middle, _id_alpha, _id_zulu = _insert_focus_books(window)
    window.focus_book_by_id(id_middle, 1)
    window.on_read_filter_changed("Unread")
    qapp.processEvents()
    qtbot.wait(20)

    assert _current_book_id(window) == id_middle


def test_read_filter_moves_when_book_excluded(main_window, qapp, qtbot):
    window = main_window
    id_middle, id_alpha, _id_zulu = _insert_focus_books(window)
    window.focus_book_by_id(id_middle, 1)
    window.on_read_filter_changed("Read")
    qapp.processEvents()
    qtbot.wait(20)

    remaining_ids = {book.book_id for book in window.books}
    assert id_middle not in remaining_ids
    assert id_alpha in remaining_ids
    current_id = _current_book_id(window)
    assert current_id in remaining_ids
    current = next(book for book in window.books if book.book_id == current_id)
    assert current.read_date


def test_update_returns_focus_to_first_selected_book(
    main_window, qapp, qtbot, monkeypatch
):
    window = main_window
    _insert_focus_books(window)
    assert len(window.books) >= 2
    first_id = window.books[0].book_id
    second_id = window.books[1].book_id
    window.focus_book_by_id(second_id, 1)
    window.selected_book_ids = {first_id, second_id}
    window.update_selection_ui()
    assert _current_book_id(window) == second_id

    class _FakeUpdate:
        def __init__(self, *args, **kwargs):
            self.changes_applied = True
            self.selected_book_ids = {first_id, second_id}

        def exec(self):
            return 1

    monkeypatch.setattr("src.ui.main_window.UpdateWindow", _FakeUpdate)
    window.on_update_clicked()
    qapp.processEvents()
    qtbot.wait(20)

    assert _current_book_id(window) == first_id
    assert window.selected_book_ids == set()
    assert window.table.hasFocus()


def _confirm_delete(monkeypatch):
    monkeypatch.setattr(
        "src.ui.main_window.exec_styled_message_box",
        lambda *args, **kwargs: QMessageBox.Yes,
    )


def _show_collection(window, collection_id: int) -> None:
    window.refresh_collections()
    for action in window.collection_filter_group.actions():
        if action.data() == collection_id:
            action.trigger()
            return
    raise AssertionError("collection filter action missing")


def test_delete_moves_focus_to_next_or_previous_book(
    main_window, qapp, qtbot, monkeypatch
):
    """Deleting books leaves focus on the next book, or the previous one at the end."""
    _confirm_delete(monkeypatch)
    window = main_window

    def run_case(name: str, delete_titles: list[str], expected: str) -> None:
        titles = [
            f"{name} A",
            f"{name} B",
            f"{name} C",
            f"{name} D",
        ]
        collection_id = CollectionQueries(window.db).insert(
            Collection(name=name, active=True)
        )
        books = BookQueries(window.db)
        ids = {
            title: books.insert(Book(title=title, collection_id=collection_id))
            for title in titles
        }
        _show_collection(window, collection_id)
        window.on_order_changed("Title")
        assert [book.title for book in window.books] == titles

        window.focus_book_by_id(ids[f"{name} {delete_titles[0]}"], 1)
        window.selected_book_ids = {ids[f"{name} {title}"] for title in delete_titles}
        window.on_delete_clicked()
        qapp.processEvents()
        qtbot.wait(20)

        current = window.books[window.table.currentRow()]
        assert current.title == f"{name} {expected}"
        assert window.table.hasFocus()
        assert window.selected_book_ids == set()

    run_case("Delete Next", ["B"], "C")
    run_case("Delete End", ["D"], "C")
    run_case("Delete Block", ["B", "C"], "D")
    run_case("Delete Tail", ["C", "D"], "B")
    run_case("Delete First", ["A"], "B")
