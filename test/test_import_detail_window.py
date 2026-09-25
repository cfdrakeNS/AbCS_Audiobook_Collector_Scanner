"""Import Detail window behavior tests."""

from __future__ import annotations

import pytest

from PySide6.QtCore import Qt

from helpers.import_window_helpers import (
    apply_suppress_import_confirmations,
    cleanup_window,
)

from src.accessibility.shortcuts import ShortcutManager
from src.database.models import Collection
from src.database.queries import CollectionQueries
from src.ui.import_detail_window import ImportDetailWindow
from src.ui.import_window import ImportWindow


@pytest.fixture(autouse=True)
def suppress_import_confirmations(monkeypatch):
    apply_suppress_import_confirmations(monkeypatch)

def test_import_detail_save_discard_shortcuts_are_explicit(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings):
    """Import Detail Save/Discard should not rely on Qt button mnemonics."""
    window = ImportDetailWindow(
        temp_db,
        ui_scaler,
        theme_manager,
        book_data={"title": "Example", "author": "Author"},
    )
    qtbot.addWidget(window)
    window.time_edit.setText("02:30")
    window._collect_form_data()
    assert window.book_data["time_hours"] == 2
    assert window.book_data["time_minutes"] == 30

    shortcuts = ShortcutManager.IMPORT_DETAIL_WINDOW_SHORTCUTS

    assert window.save_return_button.text() == "Save"
    assert window.skip_button.text() == "Discard"
    assert shortcuts["S"] == ("Save", "save_return_button")
    assert shortcuts["D"] == ("Discard", "skip_button")

    cleanup_window(window)

def test_import_detail_actions_return_focus_to_title(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings, monkeypatch):
    """Save, discard, and page navigation should return focus to Title."""
    window = ImportDetailWindow(
        temp_db,
        ui_scaler,
        theme_manager,
        book_data={"title": "Example", "author": "Author"},
    )
    qtbot.addWidget(window)

    focus_requests = []
    monkeypatch.setattr(window, "_focus_title_field", lambda: focus_requests.append(1))

    window.on_save()
    monkeypatch.setattr(window, "_navigate_without_close", lambda target_index: True)
    window.on_prev()
    window.on_next()

    class ParentStub:
        scanned_items = [{"book": {"title": "Next Example", "author": "Author"}}]

        def _discard_scanned_item(self, row):
            return 0

        def set_status(self, message, announce=False):
            pass

    window._owner_widget = ParentStub()
    window.on_skip_discard()

    assert len(focus_requests) == 4

    cleanup_window(window)

def test_import_detail_new_author_survives_focus_out_and_save(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings):
    """A typed author not yet in the database must not revert on focus-out or save."""
    import_window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(import_window)

    book = {
        "title": "A Good Title Here",
        "author": "",
        "year": 2020,
        "folder": "/tmp/book-missing-author",
        "errors": ["Author Blank"],
    }
    item = {
        "book": book,
        "status": "Error",
        "errors": list(book["errors"]),
        "is_duplicate": False,
        "error_summary": "",
        "author": book["author"],
        "title": book["title"],
        "year": book["year"],
        "folder": book["folder"],
    }
    import_window.scanned_items = [item]
    import_window.scan_outcomes = []

    detail = ImportDetailWindow(
        temp_db,
        ui_scaler,
        theme_manager,
        book_data=book.copy(),
        errors=list(item["errors"]),
        current_index=0,
        total_count=1,
        parent=import_window,
    )
    qtbot.addWidget(detail)

    detail.author_combo.setEditText("Brand New Author")
    detail.title_edit.setFocus()
    qtbot.wait(10)

    assert detail.author_combo.currentText().strip() == "Brand New Author"

    assert detail.on_save() is True
    assert book["author"] == "Brand New Author"
    assert item["author"] == "Brand New Author"
    assert item["status"] == "OK"
    assert not any("author blank" in str(err).lower() for err in item["errors"])

    cleanup_window(detail)
    cleanup_window(import_window)

def test_apply_detail_edits_persists_time_fields(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings, monkeypatch):
    """Import window should copy edited time fields from detail book_data."""
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    book = {
        "title": "Time Test Book",
        "author": "Author One",
        "year": 2020,
        "folder": "/tmp/time-test",
        "files": ["/tmp/time-test/part1.mp3"],
        "time_hours": 0,
        "time_minutes": 0,
        "tracks": 2,
        "errors": [],
    }
    window.scanned_items = [
        {
            "book": book,
            "status": "OK",
            "errors": [],
            "is_duplicate": False,
            "error_summary": "",
            "author": book["author"],
            "title": book["title"],
            "year": book["year"],
            "folder": book["folder"],
        }
    ]
    window.table.setRowCount(1)

    class DetailStub:
        book_data = {
            **book,
            "time_hours": 2,
            "time_minutes": 30,
        }

    monkeypatch.setattr(window, "_revalidate_scanned_item", lambda item: None)
    monkeypatch.setattr(window, "_refresh_summary_from_items", lambda: None)
    window._apply_detail_edits(0, DetailStub())

    assert book["time_hours"] == 2
    assert book["time_minutes"] == 30
    assert book["tracks"] == 2

    cleanup_window(window)

def test_build_book_from_scan_uses_scanned_time_and_tracks(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings):
    """Books added from scan should keep hours, minutes, and track count."""
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    cq = CollectionQueries(temp_db)
    if window.collection_combo.count() == 0:
        collection_id = cq.insert(Collection(name="Default", active=True))
        window._load_collection_options()
        idx = window.collection_combo.findData(collection_id)
        if idx >= 0:
            window.collection_combo.setCurrentIndex(idx)
    elif window.collection_combo.currentData() is None and window.collection_combo.count() > 1:
        window.collection_combo.setCurrentIndex(1)

    book = {
        "title": "Scan Length Book",
        "author": "Author Two",
        "year": 2019,
        "folder": "/tmp/scan",
        "files": ["/tmp/scan/a.mp3", "/tmp/scan/b.mp3", "/tmp/scan/c.mp3"],
        "time_hours": 5,
        "time_minutes": 15,
        "tracks": 3,
        "size_mb": 12.5,
        "bitrate": 128,
        "format": "MP3",
        "comment": "",
        "series_number": "6.5",
    }
    saved = window._build_book_from_scan(book)
    assert saved.time_hours == 5
    assert saved.time_minutes == 15
    assert saved.tracks == 3
    assert saved.series_number == 6.5

    cleanup_window(window)


def test_import_detail_tab_order_matches_book_details_columns(
    qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings
):
    """Tab follows Title through Path, then Errors, then the footer."""
    window = ImportDetailWindow(
        temp_db,
        ui_scaler,
        theme_manager,
        book_data={"title": "Example", "author": "Author"},
    )
    qtbot.addWidget(window)
    expected = [
        window.title_edit,
        window.author_combo,
        window.series_combo,
        window.genre_combo,
        window.comments_edit,
        window.year_spin,
        window.time_edit,
        window.files_edit,
        window.format_edit,
        window.bitrate_edit,
        window.reader_edit,
        window.collection_combo,
        window.size_edit,
        window.source_edit,
        window.path_edit,
        window.errors_edit,
        window.save_return_button,
        window.skip_button,
    ]
    found = []
    widget = window.title_edit
    for _ in range(200):
        widget = widget.nextInFocusChain()
        if widget is window.title_edit:
            break
        if (widget.focusPolicy() & Qt.TabFocus) and widget in expected:
            found.append(widget)
    assert found == expected[1:]
    cleanup_window(window)

