"""Tests for ImportDetailWindow new-value checks on Author/Series/Genre combos."""

from __future__ import annotations

import os
import shutil
import sys

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMessageBox, QDialog, QStatusBar

from accessibility.scaling import UIScaler
from accessibility.theme_manager import ThemeManager
from database.connection import DatabaseManager
from database.queries import CollectionQueries
from ui.import_detail_window import ImportDetailWindow

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_ROOT = os.path.join(PROJECT_ROOT, "src")
if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)


@pytest.fixture
def isolated_qsettings(tmp_path):
    """Use temporary INI-backed QSettings to avoid user registry writes."""
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


def _ensure_reference_data(window: ImportDetailWindow):
    """Ensure test-safe reference values exist for all checked combos."""
    if not window.author_queries.get_by_name("Test Existing Author A"):
        window.author_queries.insert("Test Existing Author A")
    if not window.author_queries.get_by_name("Test Existing Author B"):
        window.author_queries.insert("Test Existing Author B")

    if not window.series_queries.get_by_name("Test Existing Series A"):
        window.series_queries.insert("Test Existing Series A")
    if not window.series_queries.get_by_name("Test Existing Series B"):
        window.series_queries.insert("Test Existing Series B")

    if not window.genre_queries.get_by_name("Test Existing Genre A"):
        window.genre_queries.insert("Test Existing Genre A")
    if not window.genre_queries.get_by_name("Test Existing Genre B"):
        window.genre_queries.insert("Test Existing Genre B")


def _make_import_detail_window(db: DatabaseManager, qapp):
    return _make_import_detail_window_with_parent(db, qapp, parent=None)


def _make_import_detail_window_with_parent(db: DatabaseManager, qapp, parent=None):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)

    collections = CollectionQueries(db).get_all(active_only=False)
    collection_name = collections[0].name if collections else "Default"

    book_data = {
        "title": "Combo Check Book",
        "author": "Test Existing Author A",
        "series": "Test Existing Series A",
        "genre": "Test Existing Genre A",
        "collection": collection_name,
    }
    return ImportDetailWindow(
        db,
        scaler,
        theme_manager,
        book_data=book_data,
        errors=[],
        parent=parent,
    )


@pytest.mark.parametrize(
    "field_name, combo_attr, original_attr, query_attr, new_value",
    [
        ("Author", "author_combo", "_original_author",
         "author_queries", "Test New Author X"),
        ("Series", "series_combo", "_original_series",
         "series_queries", "Test New Series X"),
        ("Genre", "genre_combo", "_original_genre",
         "genre_queries", "Test New Genre X"),
    ],
)
def test_import_detail_new_value_no_reverts_to_original(
    qapp, qtbot, temp_db, isolated_qsettings, monkeypatch,
    field_name, combo_attr, original_attr, query_attr, new_value,
):
    window = _make_import_detail_window(temp_db, qapp)
    qtbot.addWidget(window)
    _ensure_reference_data(window)
    window.load_combos()
    window.load_book_data()

    combo = getattr(window, combo_attr)
    original_value = getattr(window, original_attr)
    query_obj = getattr(window, query_attr)

    monkeypatch.setattr(
        "ui.import_detail_window.exec_styled_message_box",
        lambda *args, **kwargs: QMessageBox.No,
    )

    combo.setCurrentText(new_value)
    window._check_combo_change(field_name, combo, original_value, query_obj)

    assert combo.currentText().strip() == original_value
    assert getattr(window, original_attr) == original_value


@pytest.mark.parametrize(
    "field_name, combo_attr, original_attr, query_attr, new_value",
    [
        ("Author", "author_combo", "_original_author",
         "author_queries", "Test New Author Y"),
        ("Series", "series_combo", "_original_series",
         "series_queries", "Test New Series Y"),
        ("Genre", "genre_combo", "_original_genre",
         "genre_queries", "Test New Genre Y"),
    ],
)
def test_import_detail_new_value_yes_keeps_value_and_updates_snapshot(
    qapp, qtbot, temp_db, isolated_qsettings, monkeypatch,
    field_name, combo_attr, original_attr, query_attr, new_value,
):
    window = _make_import_detail_window(temp_db, qapp)
    qtbot.addWidget(window)
    _ensure_reference_data(window)
    window.load_combos()
    window.load_book_data()

    combo = getattr(window, combo_attr)
    original_value = getattr(window, original_attr)
    query_obj = getattr(window, query_attr)

    monkeypatch.setattr(
        "ui.import_detail_window.exec_styled_message_box",
        lambda *args, **kwargs: QMessageBox.Yes,
    )

    combo.setCurrentText(new_value)
    window._check_combo_change(field_name, combo, original_value, query_obj)

    assert combo.currentText().strip() == new_value
    assert getattr(window, original_attr) == new_value


@pytest.mark.parametrize(
    "field_name, combo_attr, original_attr, query_attr, first_value, second_value",
    [
        (
            "Author", "author_combo", "_original_author", "author_queries",
            "Test Existing Author A", "Test Existing Author B",
        ),
        (
            "Series", "series_combo", "_original_series", "series_queries",
            "Test Existing Series A", "Test Existing Series B",
        ),
        (
            "Genre", "genre_combo", "_original_genre", "genre_queries",
            "Test Existing Genre A", "Test Existing Genre B",
        ),
    ],
)
def test_import_detail_existing_value_does_not_prompt(
    qapp, qtbot, temp_db, isolated_qsettings, monkeypatch,
    field_name, combo_attr, original_attr, query_attr, first_value, second_value,
):
    window = _make_import_detail_window(temp_db, qapp)
    qtbot.addWidget(window)
    _ensure_reference_data(window)
    window.load_combos()
    window.load_book_data()

    combo = getattr(window, combo_attr)
    query_obj = getattr(window, query_attr)

    combo.setCurrentText(first_value)
    setattr(window, original_attr, first_value)

    called = {"count": 0}

    def _spy(*args, **kwargs):
        called["count"] += 1
        return QMessageBox.Yes

    monkeypatch.setattr(
        "ui.import_detail_window.exec_styled_message_box", _spy)

    combo.setCurrentText(second_value)
    window._check_combo_change(field_name, combo, first_value, query_obj)

    assert called["count"] == 0
    assert getattr(window, original_attr) == second_value


def test_import_detail_locks_non_allowed_fields(
    qapp, qtbot, temp_db, isolated_qsettings
):
    window = _make_import_detail_window(temp_db, qapp)
    qtbot.addWidget(window)

    assert not window.title_edit.isReadOnly()
    assert window.author_combo.isEnabled()
    assert window.author_combo.isEditable()
    assert not window.comments_edit.isReadOnly()
    assert window.series_combo.isEnabled()
    assert window.series_combo.isEditable()
    assert window.genre_combo.isEnabled()
    assert window.genre_combo.isEditable()
    assert not window.reader_edit.isReadOnly()

    assert window.year_spin.isEnabled()
    assert window.year_spin.isReadOnly()
    assert window.time_edit.isReadOnly()
    assert not window.collection_combo.isEnabled()


def test_import_detail_applies_proper_case_except_comments(
    qapp, qtbot, temp_db, isolated_qsettings
):
    settings = QSettings("AbCS", "AbCS")
    settings.setValue("import/autocorrect/proper_case", True)
    settings.sync()

    window = _make_import_detail_window(temp_db, qapp)
    qtbot.addWidget(window)

    window.title_edit.setText("  tHe hOBbiT  ")
    window.author_combo.setCurrentText("  stephen kING  ")
    window.comments_edit.setPlainText("  tHis is A noTE  ")
    window.series_combo.setCurrentText("  tHe dark tOwer  ")
    window.genre_combo.setCurrentText("  science fIction  ")
    window.reader_edit.setText("  fRANK muller  ")

    window._collect_form_data()

    assert window.book_data["title"] == "The Hobbit"
    assert window.book_data["author"] == "Stephen King"
    assert window.book_data["comment"] == "tHis is A noTE"
    assert window.book_data["series"] == "The Dark Tower"
    assert window.book_data["genre"] == "Science Fiction"
    assert window.book_data["narrator"] == "Frank Muller"


def test_import_detail_exit_prompt_includes_valid_count_and_current_message(
    qapp, qtbot, temp_db, isolated_qsettings
):
    parent = QDialog()
    parent.status_bar = QStatusBar(parent)
    parent.status_bar.showMessage("Scanned: 12 | Valid: 9 | Errors: 1")
    parent._default_status_message = "Scanned: 12 | Valid: 9 | Errors: 1"
    parent._summary_counts = {}
    parent.scanned_items = [
        {"status": "OK"},
        {"status": "Warning"},
        {"status": "Error"},
        {"status": "Duplicate"},
    ]

    window = _make_import_detail_window_with_parent(
        temp_db, qapp, parent=parent)
    qtbot.addWidget(window)

    prompt_text = window._build_exit_prompt_text()

    assert "Valid books in Import list: 2" in prompt_text
    assert "Current message: Scanned: 12 | Valid: 9 | Errors: 1" in prompt_text
