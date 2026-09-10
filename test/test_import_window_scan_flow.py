"""Import window scan-flow and browse shortcut tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication

from helpers.import_window_helpers import (
    _configure_mass_standard_scan,
    apply_suppress_import_confirmations,
    cleanup_window,
)

from src.database.models import Collection
from src.database.queries import CollectionQueries
from src.ui.import_window import ImportWindow


@pytest.fixture(autouse=True)
def suppress_import_confirmations(monkeypatch):
    apply_suppress_import_confirmations(monkeypatch)

def test_import_scan_reloads_fallback_preferences(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings):
    """Each scan should pick up current fallback checkbox values from settings."""
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    settings = QSettings("AbCS", "AudioBookCollector")
    settings.setValue("import/fallback/author_to_folder", True)
    settings.setValue("import/fallback/title_to_file", True)
    window._reload_scan_settings()
    assert window.author_fallback_to_folder is True
    assert window.import_scanner.author_fallback_mode == "folder"
    assert window.import_scanner.title_fallback_mode == "file"

    settings.setValue("import/fallback/author_to_folder", False)
    settings.setValue("import/fallback/title_to_file", False)
    window._reload_scan_settings()
    assert window.author_fallback_to_folder is False
    assert window.title_fallback_to_file is False
    assert window.import_scanner.author_fallback_mode is None
    assert window.import_scanner.title_fallback_mode is None

    cleanup_window(window)

def test_import_alt_browse_from_collection_combo(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings, monkeypatch):
    """Alt+B should open browse even when collection combo has focus."""
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    browse_called = {"count": 0}

    def fake_browse():
        browse_called["count"] += 1

    monkeypatch.setattr(window, "on_browse", fake_browse)
    window.collection_combo.setFocus()
    qtbot.keyClick(window.collection_combo, Qt.Key_B, Qt.AltModifier)

    assert browse_called["count"] == 1

    cleanup_window(window)

def test_scan_keeps_fixed_warning_rows_for_manual_add(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings, monkeypatch, tmp_path):
    """Fallback/autocorrect rows should stay in review list; clean rows may auto-add."""
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    # Ensure a selectable collection is active.
    cq = CollectionQueries(temp_db)
    if window.collection_combo.count() == 0:
        collection_id = cq.insert(Collection(name="Default", active=True))
        window._load_collection_options()
        target_index = window.collection_combo.findData(collection_id)
        if target_index >= 0:
            window.collection_combo.setCurrentIndex(target_index)
    elif window.collection_combo.currentData() is None:
        window.collection_combo.setCurrentIndex(1)

    scan_dir = Path(tmp_path)
    scan_dir.mkdir(parents=True, exist_ok=True)
    window.folder_edit.setText(str(scan_dir))
    _configure_mass_standard_scan(window)

    fixed_book = {
        "title": "Fixed Example",
        "author": "Author One",
        "year": 2022,
        "genre": "Fiction",
        "narrator": "",
        "comment": "",
        "folder": str(scan_dir),
        "files": [str(scan_dir / "fixed.mp3")],
        "errors": ["F: Author fallback from folder used"],
        "time_hours": 1,
        "time_minutes": 0,
        "tracks": 1,
        "size_mb": 1.0,
        "bitrate": 128,
        "format": "MP3",
    }
    clean_book = {
        "title": "Clean Example",
        "author": "Author Two",
        "year": 2021,
        "genre": "Fiction",
        "narrator": "",
        "comment": "",
        "folder": str(scan_dir),
        "files": [str(scan_dir / "clean.mp3")],
        "errors": [],
        "time_hours": 1,
        "time_minutes": 0,
        "tracks": 1,
        "size_mb": 1.0,
        "bitrate": 128,
        "format": "MP3",
    }

    monkeypatch.setattr(
        window.scanner,
        "scan_folder",
        lambda *args, **kwargs: [fixed_book, clean_book],
    )

    window.on_scan()

    # Wait a bit for the scan to complete and UI updates to process
    qtbot.wait(200)

    # Process any pending Qt events to ensure all UI updates have been processed
    from PySide6.QtWidgets import QApplication

    QApplication.processEvents()

    # Give the progress window time to update
    qtbot.wait(100)

    # Clean row auto-added, fixed row remains for review/manual add.
    assert any(
        (item.get("book", {}).get("title") == "Fixed Example")
        for item in window.scanned_items
    )
    assert not any(
        (item.get("book", {}).get("title") == "Clean Example")
        for item in window.scanned_items
    )
    assert window._summary_counts["fixed"] >= 1

    # Cleanup: use helper to close all windows properly
    cleanup_window(window)

def test_scan_keeps_author_title_corrected_rows_for_manual_add(qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings, monkeypatch, tmp_path):
    """Author/title corrected rows should stay in review list with C: flags."""
    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    cq = CollectionQueries(temp_db)
    if window.collection_combo.count() == 0:
        collection_id = cq.insert(Collection(name="Default", active=True))
        window._load_collection_options()
        target_index = window.collection_combo.findData(collection_id)
        if target_index >= 0:
            window.collection_combo.setCurrentIndex(target_index)
    elif window.collection_combo.currentData() is None:
        window.collection_combo.setCurrentIndex(1)

    scan_dir = Path(tmp_path)
    scan_dir.mkdir(parents=True, exist_ok=True)
    window.folder_edit.setText(str(scan_dir))
    _configure_mass_standard_scan(window, trim_whitespace=True)

    # on_scan() reloads from QSettings (often the Windows registry). Keep trim
    # reviewable so C: flags are not silently skipped by host preferences.
    original_reload = window._reload_scan_settings

    def _reload_with_reviewable_trim():
        original_reload()
        window.import_scanner.trim_whitespace = True
        window.import_scanner.trim_whitespace_skip_review = False

    monkeypatch.setattr(window, "_reload_scan_settings", _reload_with_reviewable_trim)

    corrected_book = {
        "title": "  Corrected Example  ",
        "author": "Author One",
        "year": 2022,
        "genre": "Fiction",
        "narrator": "",
        "comment": "",
        "folder": str(scan_dir),
        "files": [str(scan_dir / "corrected.mp3")],
        "errors": [],
        "time_hours": 1,
        "time_minutes": 0,
        "tracks": 1,
        "size_mb": 1.0,
        "bitrate": 128,
        "format": "MP3",
    }
    clean_book = {
        "title": "Clean Example",
        "author": "Author Two",
        "year": 2021,
        "genre": "Fiction",
        "narrator": "",
        "comment": "",
        "folder": str(scan_dir),
        "files": [str(scan_dir / "clean.mp3")],
        "errors": [],
        "time_hours": 1,
        "time_minutes": 0,
        "tracks": 1,
        "size_mb": 1.0,
        "bitrate": 128,
        "format": "MP3",
    }

    monkeypatch.setattr(
        window.scanner,
        "scan_folder",
        lambda *args, **kwargs: [corrected_book, clean_book],
    )

    window.on_scan()
    qtbot.wait(200)
    QApplication.processEvents()

    corrected_items = [
        item
        for item in window.scanned_items
        if (item.get("book", {}).get("title") or "").strip() == "Corrected Example"
    ]
    assert len(corrected_items) == 1
    assert corrected_items[0]["error_summary"].startswith("C:")
    assert not any(
        (item.get("book", {}).get("title") or "").strip() == "Clean Example"
        for item in window.scanned_items
    )
    assert window._summary_counts["fixed"] == 1
    assert window._summary_counts["added"] == 1
    assert window._summary_counts["errors"] == 0
    assert window._summary_counts["warnings"] == 0
    status_text = window.status_bar.currentMessage()
    assert "Added: 1" in status_text
    assert "Corrected: 1" in status_text
    assert "Errors: 0" in status_text
    assert "Warnings: 0" in status_text
    assert "Valid:" not in status_text

    cleanup_window(window)


def test_build_book_from_scan_uses_entity_cache(qtbot, temp_db, ui_scaler, theme_manager):
    """Prefetched entity caches should avoid repeated get_or_create SELECTs."""
    from unittest.mock import MagicMock

    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    if window.collection_combo.count() == 0:
        CollectionQueries(temp_db).insert(Collection(name="Cache Coll", active=True))
        window._load_collection_options()
    window.collection_combo.setCurrentIndex(0)

    books = [
        {"title": "Cache Book 1", "author": "Cache Author", "genre": "Cache Genre"},
        {"title": "Cache Book 2", "author": "Cache Author", "genre": "Cache Genre"},
    ]
    window._ensure_entity_caches(books, commit=False)
    assert "cache author" in window._author_id_cache
    assert "cache genre" in window._genre_id_cache

    get_or_create = MagicMock(wraps=window.author_queries.get_or_create)
    window.author_queries.get_or_create = get_or_create
    book = window._build_book_from_scan(books[0], defer_commits=True)
    assert book.author_id == window._author_id_cache["cache author"]
    get_or_create.assert_not_called()

    cleanup_window(window)


def test_import_rows_batches_with_insert_many(
    qtbot, temp_db, ui_scaler, theme_manager, monkeypatch
):
    """Manual add phase should call insert_many instead of per-row insert."""
    from unittest.mock import MagicMock

    window = ImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    if window.collection_combo.count() == 0:
        CollectionQueries(temp_db).insert(Collection(name="Add Coll", active=True))
        window._load_collection_options()
    window.collection_combo.setCurrentIndex(0)

    window.scanned_items = [
        {
            "book": {
                "title": "Batch Add One",
                "author": "Batch Add Author",
                "year": 2020,
            },
            "status": "OK",
            "errors": [],
        },
        {
            "book": {
                "title": "Batch Add Two",
                "author": "Batch Add Author",
                "year": 2021,
            },
            "status": "OK",
            "errors": [],
        },
    ]
    window.scan_outcomes = []
    window.table.setRowCount(2)

    insert_many = MagicMock(wraps=window.book_queries.insert_many)
    monkeypatch.setattr(window.book_queries, "insert_many", insert_many)
    monkeypatch.setattr(window, "progress_window", None)

    window._import_rows([0, 1])

    assert insert_many.call_count == 1
    assert insert_many.call_args.kwargs.get("commit") is False
    rows = temp_db.fetch_all(
        "SELECT title FROM books WHERE title LIKE 'Batch Add %' ORDER BY title"
    )
    assert [r[0] for r in rows] == ["Batch Add One", "Batch Add Two"]

    cleanup_window(window)

