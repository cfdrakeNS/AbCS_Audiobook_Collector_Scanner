"""Book details accessibility: status readback and idle status text."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication

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

def test_book_details_initial_size_within_screen(temp_db, qapp, ui_scaler, theme_manager):
    """High zoom must not size the dialog beyond the available screen (Linux VM)."""
    books = _ensure_sample_books(temp_db, count=1)
    ui_scaler.set_scale(200)
    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books[0],
        parent=None,
        theme_manager=theme_manager,
    )
    screen = QGuiApplication.primaryScreen()
    assert screen is not None
    avail = screen.availableGeometry()
    pad = 24
    assert window.width() <= avail.width() - pad
    assert window.height() <= avail.height() - pad
    assert window.maximumWidth() <= avail.width() - pad
    assert window.maximumHeight() <= avail.height() - pad
    assert window.form_scroll.maximumHeight() <= avail.height()
    clamp_w, clamp_h = window._clamp_dialog_size(5000, 5000)
    assert clamp_w == window.maximumWidth()
    assert clamp_h == window.maximumHeight()
    window.show()
    qapp.processEvents()
    window.close()


def test_idle_status_shows_filter_summary_not_title(temp_db, ui_scaler, theme_manager):
    books = _ensure_sample_books(temp_db, count=1)
    summary = "3 books  |  Collection: All  |  Sort: Title"

    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books[0],
        filter_summary=summary,
        parent=None,
        theme_manager=theme_manager,
    )
    message = window._idle_status_message()
    assert message == summary
    assert " by " not in message
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


def test_keep_edit_mode_stays_in_edit_after_paging(temp_db, ui_scaler, theme_manager):
    books = _ensure_sample_books(temp_db, count=2)

    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books[0],
        books_list=books,
        current_index=0,
        parent=None,
        theme_manager=theme_manager,
        keep_edit_mode=True,
    )
    window.on_edit_mode()
    window.on_next()
    assert window.title_edit.text() == books[1].title
    assert window._in_edit_mode
    assert not window.save_button.isHidden()
    assert window.edit_button.isHidden()
    window.on_prev()
    assert window.title_edit.text() == books[0].title
    assert window._in_edit_mode
    assert not window.save_button.isHidden()
    window.close()


def test_keep_edit_mode_save_announces_and_allows_listen(
    temp_db, ui_scaler, theme_manager, tmp_path, monkeypatch
):
    author_id = AuthorQueries(temp_db).insert("Keep Edit Listen Author")
    book_id = BookQueries(temp_db).insert(
        Book(
            title="Heat Lightning",
            author_id=author_id,
            collection_id=CollectionQueries(temp_db).get_all()[0].collection_id,
        )
    )
    books = [BookQueries(temp_db).get_by_id(book_id)]
    folder = tmp_path / "2 Heat Lighting"
    folder.mkdir()
    (folder / "01.mp3").write_bytes(b"x")

    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books[0],
        books_list=books,
        current_index=0,
        parent=None,
        theme_manager=theme_manager,
        keep_edit_mode=True,
    )
    window.on_edit_mode()
    statuses = []
    real_set_status = window.set_status

    def record(message, announce=False):
        statuses.append((message, announce))
        real_set_status(message, announce=False)

    monkeypatch.setattr(window, "set_status", record)
    monkeypatch.setattr(
        "src.ui.book_details.QTimer.singleShot", lambda _ms, fn: fn()
    )
    window.path_edit.setText(str(folder))
    window._mark_dirty(window.path_edit)
    assert window._listen_blocked_by_edit()

    window.on_save()

    assert BookQueries(temp_db).get_by_id(books[0].book_id).path == str(folder)
    assert window._in_edit_mode
    assert ("Book updated successfully", True) in statuses
    assert not window._listen_blocked_by_edit()
    played = []
    monkeypatch.setattr(
        "src.ui.preview_window.show_preview",
        lambda *args, **kwargs: played.append(args[1]) or (True, "Playing"),
    )
    window.on_preview()
    assert played == [str(folder)]
    window.close()


def test_paging_in_view_mode_stays_in_view_mode(temp_db, ui_scaler, theme_manager):
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
    window.on_next()
    assert window.title_edit.text() == books[1].title
    assert not window._in_edit_mode
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
    # No collection folder either, so Listen cannot find the book by author/title.
    window._preview_collection_root = lambda: ""
    window.path_edit.setText("")
    window._update_preview_button_state()
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
    assert window.preview_button.text() == "Listen"
    assert window.preview_button.accessibleName() == "Listen to audiobook"
    assert "Ctrl+L" in window.preview_button.accessibleDescription()
    assert window.preview_shortcut.key().toString() == "Ctrl+L"
    called = []

    def fake_show(parent, stored_path, scaler, theme_manager=None, **kwargs):
        called.append((stored_path, kwargs.get("book_title", "")))
        return True, "Playing"

    monkeypatch.setattr("src.ui.preview_window.show_preview", fake_show)
    window.on_preview()
    assert called == [(str(audio), "Preview Book")]
    window.close()


def _jpeg_bytes() -> bytes:
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QImage

    image = QImage(8, 8, QImage.Format.Format_RGB32)
    image.fill(0x336699)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "JPEG")
    return bytes(buffer.data())


def test_book_details_open_resolves_source_and_cover_once(
    temp_db, ui_scaler, theme_manager, tmp_path, monkeypatch
):
    from src.core.audio_launcher import PreviewTarget

    audio = tmp_path / "book.mp3"
    audio.write_bytes(b"x")
    book = _ensure_sample_books(temp_db, count=1)[0]
    book.path = str(audio)
    calls = {"resolve": 0, "cover": 0}

    def fake_resolve(path, collection_root="", import_dir="", **_lookup):
        calls["resolve"] += 1
        return PreviewTarget(path=audio)

    def fake_cover(path):
        calls["cover"] += 1
        return None

    monkeypatch.setattr("src.core.audio_launcher.resolve_preview_source", fake_resolve)
    monkeypatch.setattr("src.core.audio_launcher.read_embedded_cover", fake_cover)

    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=book,
        parent=None,
        theme_manager=theme_manager,
    )

    assert calls == {"resolve": 1, "cover": 1}
    window.close()

def test_book_details_cover_placeholder_without_art(temp_db, ui_scaler, theme_manager):
    author_id = AuthorQueries(temp_db).insert("Plain Author")
    book_id = BookQueries(temp_db).insert(
        Book(title="Plain Book", author_id=author_id, path="")
    )
    book = BookQueries(temp_db).get_by_id(book_id)
    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=book,
        parent=None,
        theme_manager=theme_manager,
    )
    assert window.cover_label.isHidden() is False
    assert window.cover_label.pixmap() is not None
    assert not window.cover_label.pixmap().isNull()
    assert window.cover_label.focusPolicy() == Qt.StrongFocus
    assert window.cover_label.accessibleName() == "No cover"
    assert window.cover_label.width() == window.cover_label.height()
    assert "cover" not in (window.status_bar.currentMessage() or "").lower()
    window.close()


def test_book_details_cover_shows_embedded_art(
    temp_db, ui_scaler, theme_manager, tmp_path
):
    from mutagen.id3 import APIC, ID3

    art = tmp_path / "with-art.mp3"
    art.write_bytes(b"")
    tags = ID3()
    tags.add(
        APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=_jpeg_bytes(),
        )
    )
    tags.save(art)

    author_id = AuthorQueries(temp_db).insert("Cover Art Test Author")
    book_id = BookQueries(temp_db).insert(
        Book(title="Cover Art Test Book", author_id=author_id)
    )
    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=BookQueries(temp_db).get_by_id(book_id),
        parent=None,
        theme_manager=theme_manager,
    )
    window.path_edit.setText(str(art))
    assert window.cover_label.isHidden() is False
    assert window.cover_label.pixmap() is not None
    assert window.cover_label.accessibleName() == "Book cover"
    assert window.cover_label.focusPolicy() == Qt.StrongFocus
    assert "cover" not in (window.status_bar.currentMessage() or "").lower()
    window.path_edit.clear()
    assert window.cover_label.isHidden() is False
    assert window.cover_label.accessibleName() == "No cover"
    assert window.cover_label.width() == ui_scaler.get_scaled_size(120)
    window.close()


def test_book_details_browse_path_edit_mode_only(temp_db, ui_scaler, theme_manager):
    books = _ensure_sample_books(temp_db, count=1)
    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books[0],
        parent=None,
        theme_manager=theme_manager,
    )
    assert window.browse_path_button.isHidden() is True
    assert window.browse_path_button.isEnabled() is False
    assert window.preview_button.isHidden() is False
    window.on_edit_mode()
    assert window.browse_path_button.isHidden() is False
    assert window.browse_path_button.isEnabled() is True
    assert window.browse_path_button.accessibleName() == "Browse book path"
    assert window.preview_button.isHidden() is True
    assert window.preview_button.isEnabled() is False
    window.close()


def test_book_details_tab_order_includes_cover(temp_db, ui_scaler, theme_manager):
    books = _ensure_sample_books(temp_db, count=1)
    window = BookDetailsWindow(
        temp_db,
        ui_scaler,
        book=books[0],
        parent=None,
        theme_manager=theme_manager,
    )
    expected = [
        window.title_edit,
        window.author_label_display,
        window.series_label_display,
        window.series_number_edit,
        window.genre_label_display,
        window.plot_stack,
        window.cover_label,
        window.year_spin,
        window.time_edit,
        window.listen_progress_edit,
        window.clear_listen_progress_button,
        window.files_edit,
        window.format_combo,
        window.bitrate_edit,
        window.reader_edit,
        window.collection_label_display,
        window.read_date,
        window.want_to_read_checkbox,
        window.size_edit,
        window.source_edit,
        window.added_edit,
        window.path_edit,
        window.new_button,
    ]
    found = []
    widget = window.title_edit
    for _ in range(200):
        widget = widget.nextInFocusChain()
        if widget is window.title_edit:
            break
        if (widget.focusPolicy() & Qt.TabFocus) and (
            widget in expected or widget is window.cover_label
        ):
            found.append(widget)
    assert window.cover_label in found
    names = [type(item).__name__ + ":" + (item.accessibleName() or item.objectName()) for item in found]
    expected_names = [type(item).__name__ + ":" + (item.accessibleName() or "") for item in expected[1:]]
    assert names == expected_names
    assert window.cover_label.focusPolicy() == Qt.StrongFocus
    assert window.cover_label.width() == window.cover_label.height()
    window.close()
