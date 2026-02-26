"""Automated checks for Import Window collection selection rules and duplicate scope."""

from __future__ import annotations
from ui.import_window import ImportWindow
from database.queries import CollectionQueries
from database.models import Collection
from database.connection import DatabaseManager
from core.validator import ImportValidator
from accessibility.theme_manager import ThemeManager
from accessibility.scaling import UIScaler
from ui.import_progress_window import ImportProgressWindow

import os
import shutil
import sys
from pathlib import Path

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_ROOT = os.path.join(PROJECT_ROOT, "src")
if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)


@pytest.fixture
def isolated_qsettings(tmp_path):
    """Use temporary INI-based QSettings to avoid touching user registry settings."""
    original_format = QSettings.defaultFormat()
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path))
    try:
        yield
    finally:
        QSettings.setDefaultFormat(original_format)


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


def _set_single_active_collection(cq: CollectionQueries):
    all_collections = cq.get_all(active_only=False)
    if not all_collections:
        inserted_id = cq.insert(Collection(name="Default", active=True))
        all_collections = [
            Collection(collection_id=inserted_id, name="Default", active=True)
        ]

    keep_id = all_collections[0].collection_id
    for collection in all_collections:
        should_be_active = collection.collection_id == keep_id
        if collection.active != should_be_active:
            cq.update(
                Collection(
                    collection_id=collection.collection_id,
                    name=collection.name,
                    active=should_be_active,
                )
            )


def _make_import_window(db: DatabaseManager, qapp):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    return ImportWindow(db, scaler, theme_manager)


def test_import_window_requires_selection_when_multiple_collections(
    qapp, qtbot, temp_db, isolated_qsettings
):
    cq = CollectionQueries(temp_db)
    _set_single_active_collection(cq)
    cq.insert(Collection(name="Second Collection", active=True))

    window = _make_import_window(temp_db, qapp)
    qtbot.addWidget(window)

    root_layout = window.layout()
    header_layout = root_layout.itemAt(0).layout()
    first_header_widget = header_layout.itemAt(0).widget()
    assert isinstance(first_header_widget, QLabel)
    assert first_header_widget.text() == "&Collection:"

    assert window.collection_combo.itemText(0) == "None"
    assert window.collection_combo.itemData(0) is None
    assert window.collection_combo.currentData() is None
    assert window.scan_button.isEnabled() is False

    window.collection_combo.setCurrentIndex(1)
    assert window.collection_combo.currentData() is not None
    assert window.scan_button.isEnabled() is True


def test_import_window_allows_scan_when_single_collection(
    qapp, qtbot, temp_db, isolated_qsettings
):
    cq = CollectionQueries(temp_db)
    _set_single_active_collection(cq)

    window = _make_import_window(temp_db, qapp)
    qtbot.addWidget(window)

    assert window.collection_combo.count() == 1
    assert window.collection_combo.currentData() is not None
    assert window.scan_button.isEnabled() is True


def test_duplicate_check_is_collection_scoped():
    validator = ImportValidator()
    book = {"title": "Dune", "author": "Frank Herbert", "year": 1965}
    existing_books = [
        {
            "title": "Dune",
            "author": "Frank Herbert",
            "year": 1965,
            "collection_id": 1,
        },
        {
            "title": "Dune",
            "author": "Frank Herbert",
            "year": 1965,
            "collection_id": 2,
        },
    ]

    assert validator.is_duplicate(book, existing_books, target_collection_id=1)
    assert validator.is_duplicate(book, existing_books, target_collection_id=2)
    assert not validator.is_duplicate(
        book, existing_books, target_collection_id=3)


def test_scan_progress_updates_status_message_for_alt_slash(
    qapp, qtbot, temp_db, isolated_qsettings, tmp_path, monkeypatch
):
    window = _make_import_window(temp_db, qapp)
    qtbot.addWidget(window)

    if window.collection_combo.currentData() is None and window.collection_combo.count() > 1:
        window.collection_combo.setCurrentIndex(1)

    window.folder_edit.setText(str(tmp_path))

    def fake_scan_folder(
        folder_path,
        include_subfolders,
        allowed_extensions,
        progress_callback,
        cancel_check,
    ):
        progress_callback(1, 2, os.path.join(folder_path, "sample_book.mp3"))
        assert window._default_status_message.startswith("Scan started")
        assert window.status_bar.currentMessage().startswith("Scan started")
        return []

    monkeypatch.setattr(window.scanner, "scan_folder", fake_scan_folder)

    window.on_scan()


def test_close_prompt_uses_valid_count_message(
    qapp, qtbot, temp_db, isolated_qsettings, monkeypatch
):
    window = _make_import_window(temp_db, qapp)
    qtbot.addWidget(window)
    window.table.setRowCount(1)
    window.scanned_items = [
        {"status": "OK"},
        {"status": "Warning"},
        {"status": "Error"},
    ]

    captured = {}

    def fake_message_box(*args, **kwargs):
        captured["text"] = kwargs.get("text")
        return False

    monkeypatch.setattr(
        "ui.import_window.exec_styled_message_box", fake_message_box)

    window._confirm_close_window()
    assert captured["text"].startswith("There are 2 books not added!")
    assert "Current scan results in this window will be discarded." in captured["text"]


def test_close_prompt_hides_valid_count_when_zero(
    qapp, qtbot, temp_db, isolated_qsettings, monkeypatch
):
    window = _make_import_window(temp_db, qapp)
    qtbot.addWidget(window)
    window.table.setRowCount(1)
    window.scanned_items = [
        {"status": "Error"},
    ]

    captured = {}

    def fake_message_box(*args, **kwargs):
        captured["text"] = kwargs.get("text")
        return False

    monkeypatch.setattr(
        "ui.import_window.exec_styled_message_box", fake_message_box)

    window._confirm_close_window()
    assert captured["text"] == (
        "Current scan results in this window will be discarded."
    )


def test_mixed_dataset_routes_to_expected_outcomes(
    qapp, qtbot, temp_db, isolated_qsettings, tmp_path, monkeypatch
):
    """Mixed scan dataset should route to Added/Duplicate/Warning/Error outcomes."""
    window = _make_import_window(temp_db, qapp)
    qtbot.addWidget(window)

    if window.collection_combo.currentData() is None and window.collection_combo.count() > 1:
        window.collection_combo.setCurrentIndex(1)

    window.folder_edit.setText(str(tmp_path))

    books = [
        {
            "title": "Valid Auto Added",
            "author": "Frank Herbert",
            "year": 1965,
            "genre": "Science Fiction",
            "narrator": "",
            "comment": "",
            "files": [str(tmp_path / "valid.mp3")],
            "folder": str(tmp_path),
            "errors": [],
            "time_hours": 1,
            "time_minutes": 0,
            "tracks": 1,
            "size_mb": 1.0,
            "bitrate": 128,
            "format": "MP3",
        },
        {
            "title": "Duplicate Routed",
            "author": "Frank Herbert",
            "year": 1965,
            "genre": "Science Fiction",
            "narrator": "",
            "comment": "",
            "files": [str(tmp_path / "dup.mp3")],
            "folder": str(tmp_path),
            "errors": [],
            "time_hours": 1,
            "time_minutes": 0,
            "tracks": 1,
            "size_mb": 1.0,
            "bitrate": 128,
            "format": "MP3",
        },
        {
            "title": "Warning Routed",
            "author": "Frank Herbert",
            "year": 1965,
            "genre": "Science Fiction",
            "narrator": "",
            "comment": "",
            "files": [str(tmp_path / "warn.mp3")],
            "folder": str(tmp_path),
            "errors": ["W: Simulated warning"],
            "time_hours": 1,
            "time_minutes": 0,
            "tracks": 1,
            "size_mb": 1.0,
            "bitrate": 128,
            "format": "MP3",
        },
        {
            "title": "Error Routed",
            "author": "",
            "year": 1965,
            "genre": "Science Fiction",
            "narrator": "",
            "comment": "",
            "files": [str(tmp_path / "error.mp3")],
            "folder": str(tmp_path),
            "errors": ["E: Simulated parse error"],
            "time_hours": 1,
            "time_minutes": 0,
            "tracks": 1,
            "size_mb": 1.0,
            "bitrate": 128,
            "format": "MP3",
        },
    ]

    def fake_scan_folder(
        folder_path,
        include_subfolders,
        allowed_extensions,
        progress_callback,
        cancel_check,
    ):
        total = len(books)
        for index, _ in enumerate(books, start=1):
            progress_callback(index, total, os.path.join(
                folder_path, f"item_{index}.mp3"))
        return books

    monkeypatch.setattr(window.scanner, "scan_folder", fake_scan_folder)

    original_is_duplicate = window.validator.is_duplicate

    def fake_is_duplicate(book, existing_books, target_collection_id=None):
        if book.get("title") == "Duplicate Routed":
            return True
        return original_is_duplicate(
            book,
            existing_books,
            target_collection_id=target_collection_id,
        )

    monkeypatch.setattr(window.validator, "is_duplicate", fake_is_duplicate)

    window.on_scan()

    assert len(window.scan_outcomes) == 4

    by_title = {
        item.get("book", {}).get("title"): item
        for item in window.scan_outcomes
    }

    assert by_title["Valid Auto Added"]["status"] == "Added"
    assert "added" in by_title["Valid Auto Added"].get("outcomes", [])

    assert by_title["Duplicate Routed"]["status"] == "Duplicate"
    assert "duplicate" in by_title["Duplicate Routed"].get("outcomes", [])

    assert by_title["Warning Routed"]["status"] == "Warning"
    assert "warning" in by_title["Warning Routed"].get(
        "outcomes", [])

    assert by_title["Error Routed"]["status"] == "Error"
    assert "error" in by_title["Error Routed"].get("outcomes", [])

    # Auto-added valid item should not remain in review list; others should.
    review_titles = {
        item.get("book", {}).get("title")
        for item in window.scanned_items
    }
    assert "Valid Auto Added" not in review_titles
    assert {"Duplicate Routed", "Warning Routed",
            "Error Routed"}.issubset(review_titles)


def test_progress_window_keyboard_only_interaction(
    qapp, qtbot, temp_db, isolated_qsettings, monkeypatch
):
    """Progress window supports keyboard-only cancel/close workflow in compact mode."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportProgressWindow(scaler, theme_manager)
    qtbot.addWidget(window)

    window.set_compact_mode(True)
    window.update_scan_progress(processed=3, total=10, elapsed_text="00:04")
    window.update_counters(
        files_scanned=3,
        elapsed_text="00:04",
        books_added=1,
        read_errors=0,
    )
    window.show()

    assert not window.title_edit.isVisible()
    assert not window.author_edit.isVisible()
    assert window.files_edit.isVisible()

    monkeypatch.setattr(
        "ui.import_progress_window.exec_styled_message_box",
        lambda *args, **kwargs: 16384,  # QMessageBox.Yes
    )

    # Keyboard-only cancel during active scan.
    window.cancel_shortcut.activated.emit()
    assert window.cancel_requested is True

    # Complete then close via keyboard-only Alt+C.
    window.mark_complete(
        canceled=True,
        elapsed_text="00:08",
        files_scanned=10,
        books_added=1,
        read_errors=0,
        summary_text="Files scanned: 10 | Added: 1 | Warnings: 0 | Errors: 0 | Duplicates: 0 | Elapsed: 00:08",
    )
    assert window.close_button.isVisible()

    window.close_shortcut.activated.emit()
    qtbot.waitUntil(lambda: not window.isVisible(), timeout=2000)


def test_progress_window_alt_slash_announces_with_accessibility_active(
    qapp, qtbot, temp_db, isolated_qsettings, monkeypatch
):
    """Alt+/ should route status to accessibility announce path when active."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportProgressWindow(scaler, theme_manager)
    qtbot.addWidget(window)

    calls = []

    def announce_spy(widget, message, move_focus=False):
        calls.append((message, move_focus))

    popup_calls = {"count": 0}

    monkeypatch.setattr(
        "ui.import_progress_window.announce_status_message", announce_spy)
    monkeypatch.setattr(
        "ui.import_progress_window.QAccessible.isActive", lambda: True)
    monkeypatch.setattr(
        "ui.import_progress_window.exec_styled_message_box",
        lambda *args, **kwargs: popup_calls.__setitem__(
            "count", popup_calls["count"] + 1),
    )

    window.set_status("Scanning 3/10")
    window.on_read_status_bar()

    assert calls[-1] == ("Scanning 3/10", True)
    assert popup_calls["count"] == 0


def test_progress_window_mark_complete_announces_summary(
    qapp, qtbot, temp_db, isolated_qsettings, monkeypatch
):
    """Completion summary should be announced for screen readers."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = ImportProgressWindow(scaler, theme_manager)
    qtbot.addWidget(window)

    calls = []

    def announce_spy(widget, message, move_focus=False):
        calls.append((message, move_focus))

    monkeypatch.setattr(
        "ui.import_progress_window.announce_status_message", announce_spy)

    summary = "Files scanned: 10 | Added: 1 | Warnings: 0 | Errors: 0 | Duplicates: 0 | Elapsed: 00:08"
    window.mark_complete(
        canceled=False,
        elapsed_text="00:08",
        files_scanned=10,
        books_added=1,
        read_errors=0,
        summary_text=summary,
    )

    assert calls[-1] == (summary, True)
