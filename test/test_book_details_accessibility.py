"""Book details accessibility: status readback and idle status text."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

from src.database.connection import DatabaseManager
from src.database.models import Book, Collection
from src.database.queries import AuthorQueries, BookQueries, CollectionQueries
from src.ui.book_details import BookDetailsWindow

def _ensure_sample_books(db: DatabaseManager, count: int = 2) -> list[Book]:
    books = BookQueries(db).get_all()
    while len(books) < count:
        index = len(books)
        author_id = AuthorQueries(db).insert(f"Accessibility Author {index}")
        BookQueries(db).insert(
            Book(title=f"Accessibility Book {index}", author_id=author_id)
        )
        books = BookQueries(db).get_all()
    return books

def test_idle_status_includes_title_and_author(temp_db, ui_scaler, theme_manager):
    books = _ensure_sample_books(temp_db, count=1)

    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books[0],
        parent=None,
        theme_manager=theme_manager,
    )
    message = window._idle_status_message()
    assert message.endswith(".")
    assert " by " in message
    assert window.status_bar.currentMessage() == message
    window.close()

def test_status_bar_has_no_sighted_tooltip(temp_db, ui_scaler, theme_manager):
    books = _ensure_sample_books(temp_db, count=1)

    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books[0],
        parent=None,
        theme_manager=theme_manager,
    )
    assert window.status_bar.toolTip() == ""
    window.close()

def test_display_leaves_blank_series_number_when_title_has_suffix(
    temp_db, ui_scaler, theme_manager
):
    author_id = AuthorQueries(temp_db).insert("Series Display Author")
    books = BookQueries(temp_db)
    blank_id = books.insert(
        Book(title="Busted - 6.5", author_id=author_id, series_number=None)
    )
    kept_id = books.insert(
        Book(title="Other - 9", author_id=author_id, series_number=2)
    )
    year_id = books.insert(
        Book(title="Some Title, 1999", author_id=author_id, series_number=None)
    )

    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books.get_by_id(blank_id),
        parent=None,
        theme_manager=theme_manager,
    )
    assert window.series_number_edit.text() == ""
    assert window.book.series_number is None
    assert window.book.title == "Busted - 6.5"
    assert window._dirty is False
    assert books.get_by_id(blank_id).series_number is None
    window.close()

    kept = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books.get_by_id(kept_id),
        parent=None,
        theme_manager=theme_manager,
    )
    assert kept.series_number_edit.text() == "2"
    assert books.get_by_id(kept_id).series_number == 2
    assert books.get_by_id(kept_id).title == "Other - 9"
    kept.close()

    year = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books.get_by_id(year_id),
        parent=None,
        theme_manager=theme_manager,
    )
    assert year.series_number_edit.text() == ""
    assert books.get_by_id(year_id).series_number is None
    assert books.get_by_id(year_id).title == "Some Title, 1999"
    year.close()


def test_save_stores_series_number_without_changing_title(
    temp_db, ui_scaler, theme_manager
):
    author_id = AuthorQueries(temp_db).insert("Suffix Save Author")
    collections = CollectionQueries(temp_db).get_all()
    if collections:
        collection_id = collections[0].collection_id
    else:
        collection_id = CollectionQueries(temp_db).insert(
            Collection(name="Suffix Save Collection", active=True)
        )
    books = BookQueries(temp_db)
    added_id = books.insert(
        Book(
            title="Rules of Prey",
            author_id=author_id,
            collection_id=collection_id,
            series_number=None,
        )
    )
    changed_id = books.insert(
        Book(
            title="Winter - 03",
            author_id=author_id,
            collection_id=collection_id,
            series_number=3,
        )
    )
    unchanged_id = books.insert(
        Book(
            title="Other - 9",
            author_id=author_id,
            collection_id=collection_id,
            series_number=9,
        )
    )

    added = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books.get_by_id(added_id),
        parent=None,
        theme_manager=theme_manager,
    )
    added.on_edit_mode()
    added.series_number_edit.setText("3")
    added.on_save()
    saved_added = books.get_by_id(added_id)
    assert saved_added.series_number == 3
    assert saved_added.title == "Rules Of Prey"
    added.close()

    changed = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books.get_by_id(changed_id),
        parent=None,
        theme_manager=theme_manager,
    )
    changed.on_edit_mode()
    changed.series_number_edit.setText("6.5")
    changed.on_save()
    saved_changed = books.get_by_id(changed_id)
    assert saved_changed.series_number == 6.5
    assert saved_changed.title == "Winter - 03"
    changed.close()

    unchanged = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books.get_by_id(unchanged_id),
        parent=None,
        theme_manager=theme_manager,
    )
    unchanged.on_edit_mode()
    unchanged.on_save()
    saved_unchanged = books.get_by_id(unchanged_id)
    assert saved_unchanged.series_number == 9
    assert saved_unchanged.title == "Other - 9"
    unchanged.close()


def test_page_navigation_focuses_title(temp_db, ui_scaler, theme_manager, monkeypatch):
    books = _ensure_sample_books(temp_db, count=2)

    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books[0],
        books_list=books,
        current_index=0,
        parent=None,
        theme_manager=theme_manager,
    )
    focus_calls = []

    def track_focus(reason=Qt.OtherFocusReason):
        focus_calls.append(reason)

    monkeypatch.setattr(window.title_edit, "setFocus", track_focus)
    monkeypatch.setattr(
        "src.ui.book_details.QTimer.singleShot",
        lambda _ms, fn: fn(),
    )

    window.on_next()
    assert focus_calls
    assert window.title_edit.text() == books[1].title
    window.close()


def test_preview_disabled_when_path_empty(temp_db, ui_scaler, theme_manager):
    books = _ensure_sample_books(temp_db, count=1)
    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books[0],
        parent=None,
        theme_manager=theme_manager,
    )
    window.path_edit.setText("")
    assert window.preview_button.isEnabled() is False
    assert "unavailable" in window.preview_button.accessibleDescription()
    window.close()


def test_preview_enabled_and_launches_for_audio_file(
    temp_db, ui_scaler, theme_manager, tmp_path, monkeypatch
):
    audio = tmp_path / "listen.mp3"
    audio.write_bytes(b"x")
    author_id = AuthorQueries(temp_db).insert("Preview Author")
    book_id = BookQueries(temp_db).insert(
        Book(title="Preview Book", author_id=author_id, path=str(audio))
    )
    book = BookQueries(temp_db).get_by_id(book_id)
    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=book,
        parent=None,
        theme_manager=theme_manager,
    )
    assert window.preview_button.isEnabled() is True
    called = []

    def fake_show(parent, stored_path, scaler, theme_manager=None, **kwargs):
        called.append((stored_path, kwargs.get("book_title", "")))
        return True, "Playing"

    monkeypatch.setattr("src.ui.preview_window.show_preview", fake_show)
    window.on_preview()
    assert called == [(str(audio), "Preview Book")]
    window.close()
