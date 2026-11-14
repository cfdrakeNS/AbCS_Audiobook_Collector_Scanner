"""Book Details review fixes: read date prompts, year validation, stepping, paging."""

from __future__ import annotations

from datetime import datetime

import pytest
from PySide6.QtCore import QDate, QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QMessageBox, QSpinBox

from src.database.models import Book
from src.database.queries import AuthorQueries, BookQueries, CollectionQueries
from src.ui.book_details import BookDetailsWindow


@pytest.fixture
def classic_fields(monkeypatch):
    """Spin box / date edit fields (no screen reader)."""
    monkeypatch.setattr("src.ui.book_details.make_year_field", lambda *a, **k: None)
    monkeypatch.setattr("src.ui.book_details.make_date_combo_fields", lambda *a, **k: None)


@pytest.fixture
def date_combos(monkeypatch):
    """Read date as Year, Month, and Day boxes (screen reader running)."""
    from src.accessibility.date_combo_fields import DateComboFields

    monkeypatch.setattr("src.ui.book_details.make_year_field", lambda *a, **k: None)
    monkeypatch.setattr(
        "src.ui.book_details.make_date_combo_fields",
        lambda parent=None, **k: DateComboFields(parent, **k),
    )


@pytest.fixture
def prompts(monkeypatch):
    """Record styled message boxes in Book Details; answer with ``prompts.reply``."""

    class Recorder:
        reply = QMessageBox.Yes

        def __init__(self):
            self.calls = []

        def __call__(self, *args, **kwargs):
            self.calls.append(kwargs)
            return self.reply

    recorder = Recorder()
    monkeypatch.setattr("src.ui.book_details.exec_styled_message_box", recorder)
    return recorder


def _make_books(db, *, year=None, count=2) -> list[Book]:
    collection_id = CollectionQueries(db).get_all()[0].collection_id
    author_id = AuthorQueries(db).insert("Review Fix Author")
    ids = [
        BookQueries(db).insert(
            Book(
                title=f"Review Fix Book {index}",
                author_id=author_id,
                collection_id=collection_id,
                year=year,
            )
        )
        for index in range(count)
    ]
    return [BookQueries(db).get_by_id(book_id) for book_id in ids]


def _window(db, scaler, theme, books, index=0):
    return BookDetailsWindow(
        db,
        scaler,
        book=books[index],
        books_list=books,
        current_index=index,
        parent=None,
        theme_manager=theme,
    )


def _stored_read_date(db, book_id) -> str:
    value = BookQueries(db).get_by_id(book_id).read_date
    return str(value)[:10] if value else ""


def _key(key, modifiers=Qt.NoModifier):
    return QKeyEvent(QEvent.KeyPress, key, modifiers)


# 1. Year validation on focus out


def test_year_focus_out_skips_view_mode(
    temp_db, ui_scaler, theme_manager, classic_fields, monkeypatch
):
    books = _make_books(temp_db, year=1750, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    calls = []
    monkeypatch.setattr(
        "src.ui.book_details.validate_year_spin", lambda *a, **k: calls.append(a)
    )
    try:
        window._validate_year_on_focus_out()
        assert calls == []
    finally:
        window.close()


def test_year_focus_out_skips_unchanged_value_in_edit_mode(
    temp_db, ui_scaler, theme_manager, classic_fields, monkeypatch
):
    books = _make_books(temp_db, year=1750, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    calls = []
    monkeypatch.setattr(
        "src.ui.book_details.validate_year_spin", lambda *a, **k: calls.append(a)
    )
    try:
        window.on_edit_mode()
        # Leave the year field (and clear any leftover focus from earlier tests).
        window.title_edit.setFocus()
        window._validate_year_on_focus_out()
        assert calls == []
        window.year_spin.setValue(1600)
        window.title_edit.setFocus()
        window._validate_year_on_focus_out()
        assert len(calls) == 1
    finally:
        window.close()


def test_year_focus_out_skips_while_a_message_box_has_focus(
    temp_db, ui_scaler, theme_manager, classic_fields, monkeypatch
):
    """Save or Escape already warned; the year leaving focus must not add a second box."""
    books = _make_books(temp_db, year=1750, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    calls = []
    monkeypatch.setattr(
        "src.ui.book_details.validate_year_spin", lambda *a, **k: calls.append(a)
    )
    box = QMessageBox()
    try:
        window.on_edit_mode()
        window.year_spin.setValue(1600)
        monkeypatch.setattr(
            "src.ui.book_details.QApplication.activeModalWidget", lambda: box
        )
        window._validate_year_on_focus_out()
        assert calls == []
        monkeypatch.setattr(
            "src.ui.book_details.QApplication.activeModalWidget", lambda: None
        )
        monkeypatch.setattr("src.ui.book_details.QApplication.focusWidget", lambda: box)
        window._validate_year_on_focus_out()
        assert calls == []
    finally:
        box.deleteLater()
        window.close()


def test_escape_yes_with_invalid_year_keeps_book_details_open(
    temp_db, ui_scaler, theme_manager, classic_fields, prompts, monkeypatch
):
    books = _make_books(temp_db, year=1750, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    closed = []
    monkeypatch.setattr(window, "reject", lambda: closed.append(True))
    monkeypatch.setattr(
        "src.accessibility.masked_date_fields.warn_masked_field_error",
        lambda *a, **k: None,
    )
    try:
        window.on_edit_mode()
        window.year_spin.setValue(1600)
        window._mark_dirty(window.year_spin)
        prompts.reply = QMessageBox.Yes
        window.on_cancel_edit()
        assert closed == []
        assert window._dirty is True
    finally:
        window.close()


def test_unsaved_prompt_hides_cancel_and_escape_discards(
    temp_db, ui_scaler, theme_manager, classic_fields, prompts
):
    books = _make_books(temp_db, year=1999, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    try:
        window.on_edit_mode()
        window.title_edit.setText("Changed title")
        prompts.reply = QMessageBox.No
        window.on_cancel_edit()
        asked = prompts.calls[-1]
        assert "Press Escape to cancel" in asked["text"]
        assert "Cancel =" not in asked["text"]
        assert QMessageBox.Cancel not in asked["button_texts"]
        assert asked["escape_only_button"] == QMessageBox.Cancel
        assert asked["default_button"] == QMessageBox.No
    finally:
        window.close()


def test_escape_no_returns_focus_to_last_changed_field(
    temp_db, ui_scaler, theme_manager, classic_fields, prompts, monkeypatch
):
    books = _make_books(temp_db, year=1999, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    focused = []
    monkeypatch.setattr(
        "src.ui.book_details.QTimer.singleShot",
        lambda ms, fn: fn() if ms == 0 else None,
    )
    monkeypatch.setattr(window, "_focus_after_prompt", lambda w: focused.append(w))
    monkeypatch.setattr(window, "reject", lambda: None)
    try:
        window.show()
        window.on_edit_mode()
        window.title_edit.setText("Changed title")
        window.reader_edit.setText("Changed narrator")
        prompts.reply = QMessageBox.No
        window.on_cancel_edit()
        assert focused == [window.reader_edit]
        assert window._dirty is True
    finally:
        window.close()


def test_typing_in_typed_year_marks_book_details_changed(
    temp_db, ui_scaler, theme_manager, monkeypatch
):
    from src.accessibility.masked_date_fields import MaskedYearEdit

    monkeypatch.setattr(
        "src.ui.book_details.make_year_field", lambda parent=None: MaskedYearEdit(parent)
    )
    books = _make_books(temp_db, year=1999, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    try:
        assert window._year_is_masked is True
        window.on_edit_mode()
        assert window._dirty is False
        window.year_spin.textEdited.emit("20")
        assert window._dirty is True
    finally:
        window.close()


def test_year_restore_never_uses_invalid_stored_value(qapp, monkeypatch):
    from src.accessibility import masked_date_fields as mdf

    monkeypatch.setattr(mdf, "warn_masked_field_error", lambda *a, **k: None)
    spin = QSpinBox()
    mdf.apply_preferred_year_spin_range(spin)
    spin.setValue(1500)
    assert mdf.validate_year_spin(spin, None, restore_to=1700) is False
    assert spin.value() == spin.minimum()

    min_year, _max_year = mdf.preferred_year_range()
    spin.setValue(1500)
    mdf.validate_year_spin(spin, None, restore_to=min_year + 1)
    assert spin.value() == min_year + 1


# 2. Plain Up/Down on Year / Read date


def test_plain_down_on_read_date_guards_commit_and_starts_at_today(
    temp_db, ui_scaler, theme_manager, classic_fields, prompts, monkeypatch
):
    books = _make_books(temp_db, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    monkeypatch.setattr(
        "src.ui.book_details.QTimer.singleShot",
        lambda ms, fn: fn() if ms == 0 else None,
    )
    monkeypatch.setattr(window.read_date, "hasFocus", lambda: True)
    try:
        consumed = window.eventFilter(window.read_date, _key(Qt.Key_Down))
        assert consumed is True
        assert window.read_date.date() == QDate.currentDate()
        assert window._suppress_read_date_commit is True
        window._commit_read_date_if_focus_left()
        assert prompts.calls == []
        assert _stored_read_date(temp_db, books[0].book_id) == ""
    finally:
        window.close()


def test_read_date_guard_end_commits_when_focus_already_left(
    temp_db, ui_scaler, theme_manager, classic_fields, prompts, monkeypatch
):
    books = _make_books(temp_db, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    monkeypatch.setattr("src.ui.book_details.QTimer.singleShot", lambda ms, fn: None)
    try:
        window.show()
        window._finish_read_date_step()
        window.read_date.setDate(QDate(2024, 1, 2))
        window.title_edit.setFocus()
        window._end_read_date_announce_guard(window._read_date_step_token)
        assert len(prompts.calls) == 1
        assert prompts.calls[0]["title"] == "Confirm Read Date"
        assert _stored_read_date(temp_db, books[0].book_id) == "2024-01-02"
    finally:
        window.close()


def test_plain_up_on_blank_year_lands_in_range(
    temp_db, ui_scaler, theme_manager, classic_fields, monkeypatch
):
    from src.accessibility.masked_date_fields import preferred_year_range

    books = _make_books(temp_db, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    monkeypatch.setattr(
        "src.ui.book_details.QTimer.singleShot",
        lambda ms, fn: fn() if ms == 0 else None,
    )
    try:
        window.on_edit_mode()
        consumed = window.eventFilter(window.year_spin, _key(Qt.Key_Up))
        assert consumed is True
        min_year, max_year = preferred_year_range()
        assert min_year <= window.year_spin.value() <= max_year
        assert window.year_spin.value() == min(datetime.now().year, max_year)
        assert window._suppress_year_validation is True

        window.year_spin.setValue(min_year)
        window.eventFilter(window.year_spin, _key(Qt.Key_Down))
        assert window.year_spin.value() == window.year_spin.minimum()
    finally:
        window.close()


# 3. Page Up / Page Down commit a typed read date first


def test_page_down_confirms_typed_read_date_before_loading_next_book(
    temp_db, ui_scaler, theme_manager, classic_fields, prompts
):
    books = _make_books(temp_db, count=2)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    try:
        window.read_date.setDate(QDate(2024, 1, 2))
        window.on_next()
        assert len(prompts.calls) == 1
        assert "as read on 2024-01-02" in prompts.calls[0]["text"]
        assert _stored_read_date(temp_db, books[0].book_id) == "2024-01-02"
        assert window.title_edit.text() == books[1].title
    finally:
        window.close()


def test_page_down_declined_read_date_is_not_saved(
    temp_db, ui_scaler, theme_manager, classic_fields, prompts
):
    books = _make_books(temp_db, count=2)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    prompts.reply = QMessageBox.No
    try:
        window.read_date.setDate(QDate(2024, 1, 2))
        window.on_next()
        assert len(prompts.calls) == 1
        assert _stored_read_date(temp_db, books[0].book_id) == ""
        assert window.title_edit.text() == books[1].title
    finally:
        window.close()


# A. Edit mode Save confirms the read date like the main window


def test_edit_mode_save_confirms_read_date(
    temp_db, ui_scaler, theme_manager, classic_fields, prompts
):
    books = _make_books(temp_db, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    try:
        window.on_edit_mode()
        window.read_date.setDate(QDate(2024, 3, 4))
        window._mark_dirty(window.title_edit)
        prompts.reply = QMessageBox.No
        window.on_save()
        assert [c["title"] for c in prompts.calls] == ["Confirm Read Date"]
        assert _stored_read_date(temp_db, books[0].book_id) == ""
        assert "Read date not changed" in window.status_bar.currentMessage()

        prompts.calls.clear()
        prompts.reply = QMessageBox.Yes
        window.on_edit_mode()
        window.read_date.setDate(QDate(2024, 3, 4))
        window._mark_dirty(window.title_edit)
        window.on_save()
        assert [c["title"] for c in prompts.calls] == ["Confirm Read Date"]
        assert _stored_read_date(temp_db, books[0].book_id) == "2024-03-04"
    finally:
        window.close()


# B. Read date as Year, Month, and Day boxes with a screen reader


def _run_zero_timers(monkeypatch):
    monkeypatch.setattr(
        "src.ui.book_details.QTimer.singleShot",
        lambda ms, fn: fn() if ms == 0 else None,
    )


def test_read_date_boxes_blank_book_and_tab_order(
    temp_db, ui_scaler, theme_manager, date_combos
):
    from PySide6.QtWidgets import QComboBox

    from src.accessibility.date_combo_fields import BLANK_TEXT, DateComboFields

    books = _make_books(temp_db, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    try:
        assert isinstance(window.read_date, DateComboFields)
        parts = window.read_date.parts()
        assert [p.accessibleName() for p in parts] == ["Read year", "Read month", "Read day"]
        assert all(isinstance(p, QComboBox) and not p.isEditable() for p in parts)
        assert [p.currentText() for p in parts] == [BLANK_TEXT] * 3
        assert window.read_date.text() == ""
        assert window.clear_read_date_button is not None

        chain = [*parts, window.clear_read_date_button, window.want_to_read_checkbox]
        for first, second in zip(chain, chain[1:]):
            widget = first.nextInFocusChain()
            while not (widget.focusPolicy() & Qt.TabFocus) or not widget.isVisibleTo(window):
                widget = widget.nextInFocusChain()
            assert widget is second
    finally:
        window.close()


def _screen_reader_running(monkeypatch, running: bool) -> None:
    monkeypatch.setattr(
        "src.accessibility.screen_reader.is_screen_reader_active_cached", lambda: running
    )


def test_read_date_boxes_step_with_plain_arrows(
    temp_db, ui_scaler, theme_manager, date_combos, monkeypatch
):
    _screen_reader_running(monkeypatch, True)
    books = _make_books(temp_db, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    try:
        for part in window.read_date.parts():
            assert window.eventFilter(part, _key(Qt.Key_Down)) is False
        assert window.eventFilter(window.collection_combo, _key(Qt.Key_Down)) is True
    finally:
        window.close()


def test_combo_arrows_blocked_without_alt(
    temp_db, ui_scaler, theme_manager, classic_fields, monkeypatch
):
    beeps = []
    monkeypatch.setattr("src.ui.book_details.QApplication.beep", lambda: beeps.append(1))
    books = _make_books(temp_db, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    try:
        window.on_edit_mode()
        for combo in (
            window.author_combo,
            window.series_combo,
            window.genre_combo,
            window.collection_combo,
        ):
            for key in (Qt.Key_Down, Qt.Key_Up):
                assert window.eventFilter(combo, _key(key)) is True
        assert len(beeps) == 8
        assert window.eventFilter(window.collection_combo, _key(Qt.Key_Down, Qt.AltModifier)) is False
    finally:
        window.close()


def test_format_combo_ignores_arrows_in_view_mode_without_screen_reader(
    temp_db, ui_scaler, theme_manager, classic_fields, monkeypatch
):
    _screen_reader_running(monkeypatch, False)
    books = _make_books(temp_db, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    try:
        assert window.eventFilter(window.format_combo, _key(Qt.Key_Down)) is True
    finally:
        window.close()


def test_read_date_boxes_save_only_after_focus_leaves_all_three(
    temp_db, ui_scaler, theme_manager, date_combos, prompts, monkeypatch
):
    books = _make_books(temp_db, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    _run_zero_timers(monkeypatch)
    focus = {"widget": None}
    monkeypatch.setattr(
        "src.ui.book_details.QApplication.focusWidget", lambda: focus["widget"]
    )
    year, month, day = window.read_date.parts()
    try:
        window.read_date.setDate(QDate(2024, 1, 2))
        focus["widget"] = month
        window.eventFilter(year, QEvent(QEvent.FocusOut))
        assert prompts.calls == []

        focus["widget"] = window.title_edit
        window.eventFilter(day, QEvent(QEvent.FocusOut))
        assert [c["title"] for c in prompts.calls] == ["Confirm Read Date"]
        assert _stored_read_date(temp_db, books[0].book_id) == "2024-01-02"
    finally:
        window.close()


def test_read_date_boxes_refuse_future_date(
    temp_db, ui_scaler, theme_manager, date_combos, prompts, monkeypatch
):
    warnings = []
    monkeypatch.setattr(
        "src.accessibility.masked_date_fields.warn_masked_field_error",
        lambda parent, message, **kw: warnings.append(message),
    )
    books = _make_books(temp_db, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    _run_zero_timers(monkeypatch)
    monkeypatch.setattr(
        "src.ui.book_details.QApplication.focusWidget", lambda: window.title_edit
    )
    last_day = QDate(QDate.currentDate().year(), 12, 31)
    if last_day <= QDate.currentDate():
        pytest.skip("No later day left this year")
    try:
        window.read_date.setDate(last_day)
        window.eventFilter(window.read_date.year, QEvent(QEvent.FocusOut))
        assert len(warnings) == 1
        assert "in the future" in warnings[0]
        assert prompts.calls == []
        assert _stored_read_date(temp_db, books[0].book_id) == ""
    finally:
        window.close()


def test_read_date_boxes_clear_and_page_down(
    temp_db, ui_scaler, theme_manager, date_combos, prompts
):
    from datetime import date

    from src.accessibility.date_combo_fields import BLANK_TEXT

    books = _make_books(temp_db, count=2)
    BookQueries(temp_db).update_many([(books[0].book_id, date(2023, 5, 6))])
    books = [BookQueries(temp_db).get_by_id(b.book_id) for b in books]
    window = _window(temp_db, ui_scaler, theme_manager, books)
    try:
        assert window.read_date.text() == "2023-05-06"
        window._on_clear_read_date_clicked()
        assert [c["title"] for c in prompts.calls] == ["Confirm Clear Read Date"]
        assert _stored_read_date(temp_db, books[0].book_id) == ""
        assert window.read_date.year.currentText() == BLANK_TEXT

        prompts.calls.clear()
        window.read_date.setDate(QDate(2024, 1, 2))
        window.on_next()
        assert len(prompts.calls) == 1
        assert "as read on 2024-01-02" in prompts.calls[0]["text"]
        assert _stored_read_date(temp_db, books[0].book_id) == "2024-01-02"
        assert window.title_edit.text() == books[1].title
        assert window.read_date.year.currentText() == BLANK_TEXT
    finally:
        window.close()


def test_date_combo_fields_blank_rules(qapp):
    from src.accessibility.date_combo_fields import BLANK_TEXT, DateComboFields

    fields = DateComboFields(allow_blank=True)
    fields.setNullDate(QDate(2000, 1, 1))
    assert fields.is_blank()
    assert fields.date() == QDate(2000, 1, 1)
    assert fields.validated_date() is None

    fields.year.setCurrentText("2019")
    today = QDate.currentDate()
    assert fields.month.currentIndex() == today.month() - 1
    assert fields.date().year() == 2019
    assert fields.text().startswith("2019-")

    fields.month.setCurrentText(BLANK_TEXT)
    assert [p.currentText() for p in fields.parts()] == [BLANK_TEXT] * 3
    assert fields.text() == ""

    fields.setDisallowFuture(True)
    fields.setDate(QDate(today.year(), 12, 31))
    if QDate(today.year(), 12, 31) > today:
        with pytest.raises(ValueError, match="future"):
            fields.validated_date()


# 5 / 6. Alt+B in view mode, F1 rows from the central map


def test_alt_b_in_view_mode_announces_edit_hint(
    temp_db, ui_scaler, theme_manager, monkeypatch
):
    books = _make_books(temp_db, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    statuses = []
    monkeypatch.setattr(
        window, "set_status", lambda msg, announce=False: statuses.append((msg, announce))
    )
    try:
        window._on_browse_path_shortcut()
        assert statuses == [
            ("Browse is available in Edit mode.", True)
        ]
    finally:
        window.close()


def test_f1_rows_follow_book_details_shortcut_map(temp_db, ui_scaler, theme_manager):
    from src.accessibility.shortcuts import BOOK_DETAILS_SHORTCUTS

    books = _make_books(temp_db, count=1)
    window = _window(temp_db, ui_scaler, theme_manager, books)
    try:
        rows = window._shortcut_help_rows()
        keys = [key for key, _desc in rows]
        for letter, (desc, _widget) in BOOK_DETAILS_SHORTCUTS.items():
            if len(letter) == 1:
                assert (f"Alt+{letter}", desc) in rows
        for extra in ("Ctrl+S", "Ctrl+L", "Ctrl+N", "Alt+E", "Alt+D", "Page Up", "Page Down"):
            assert extra in keys
        assert keys[:3] == ["Alt+T", "Alt+A", "Alt+S"]
        assert keys.index("Alt+D") < keys.index("Alt+W") < keys.index("Ctrl+L")
    finally:
        window.close()
