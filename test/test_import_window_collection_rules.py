"""Automated checks for Import Window collection selection rules and duplicate scope."""

from __future__ import annotations
from ui.import_window import ImportWindow
from database.queries import CollectionQueries
from database.models import Collection
from database.connection import DatabaseManager
from core.validator import ImportValidator
from accessibility.theme_manager import ThemeManager
from accessibility.scaling import UIScaler

import os
import shutil
import sys

import pytest
from PySide6.QtCore import QSettings
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
    source_db = os.path.join(PROJECT_ROOT, "data", "abcs.db")
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
    assert first_header_widget.text() == "Co&llection:"

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
        assert window._default_status_message.startswith("Scanning 1/2:")
        assert window.status_bar.currentMessage().startswith("Scanning 1/2:")
        return []

    monkeypatch.setattr(window.scanner, "scan_folder", fake_scan_folder)

    window.on_scan()


def test_close_prompt_uses_valid_count_message(
    qapp, qtbot, temp_db, isolated_qsettings, monkeypatch
):
    window = _make_import_window(temp_db, qapp)
    qtbot.addWidget(window)
    window.table.setRowCount(1)
    window._summary_counts = {
        "total": 3,
        "valid": 2,
        "warnings": 0,
        "errors": 1,
    }

    captured = {}

    def fake_message_box(*args, **kwargs):
        captured["text"] = kwargs.get("text")
        return False

    monkeypatch.setattr(
        "ui.import_window.exec_styled_message_box", fake_message_box)

    window._confirm_close_window()
    assert captured["text"].startswith("There are 2 valid books not added!")
    assert "Current scan results in this window will be discarded." in captured["text"]


def test_close_prompt_hides_valid_count_when_zero(
    qapp, qtbot, temp_db, isolated_qsettings, monkeypatch
):
    window = _make_import_window(temp_db, qapp)
    qtbot.addWidget(window)
    window.table.setRowCount(1)
    window._summary_counts = {
        "total": 1,
        "valid": 0,
        "warnings": 0,
        "errors": 1,
    }

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
