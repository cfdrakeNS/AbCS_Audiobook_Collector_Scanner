"""Pytest coverage for the Web Metadata dialog."""

import os
import sys
from pathlib import Path

# Ensure Qt can initialize in headless test environments.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.database.models import Book
from src.ui.web_metadata import WebMetadataWindow


@pytest.fixture(scope="session")
def qapp():
    """Provide a single QApplication instance for all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def sample_book():
    """Book fixture with realistic values for UI population checks."""
    return Book(
        book_id=1,
        title="The Great Gatsby",
        author_id=1,
        author_name="F. Scott Fitzgerald",
        year=1925,
        series_id=None,
        series_name="",
        genre_id=1,
        genre_name="Classic Fiction",
        collection_id=1,
        collection_name="Test Collection",
        comments="Original local comments",
        source="test",
    )


@pytest.fixture
def window(qapp, sample_book):
    """Construct the window without DB writes/network calls."""
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    dlg = WebMetadataWindow(
        db=None,
        book=sample_book,
        scaler=scaler,
        theme_manager=theme_manager,
        web_data=None,
    )
    yield dlg
    dlg.close()


def test_web_metadata_window_constructs(window):
    assert window.windowTitle() == "Web Metadata"
    assert hasattr(window, "setup_ui")
    assert hasattr(window, "load_book_data")
    assert hasattr(window, "update_fields_with_web_data")


def test_web_metadata_loads_book_values(window, sample_book):
    assert window.title_edit.text() == sample_book.title
    assert window.author_edit.text() == sample_book.author_name
    assert window.year_edit.text() == str(sample_book.year)
    assert window.genre_edit.text() == sample_book.genre_name
    assert window.plot_edit.toPlainText() == sample_book.comments


def test_update_fields_with_web_data_tracks_differences(window):
    web_data = {
        "title": "The Great Gatsby (Annotated)",
        "author": "Francis Scott Fitzgerald",
        "year": "1926",
        "series": "Modern Classics",
        "series_number": "2",
        "genre": "Literary Fiction",
        "plot": "A portrait of wealth, illusion, and longing in the Jazz Age.",
        "rating": "4.2",
        "ratings_count": "1203456",
    }

    window.update_fields_with_web_data(web_data)

    assert window.web_data == web_data
    assert "title" in window.field_differences
    assert "author" in window.field_differences
    assert "genre" in window.field_differences
    assert "plot" in window.field_differences
    assert window.title_web_edit.text() == "The Great Gatsby (Annotated)"
    assert window.author_web_edit.text() == "Francis Scott Fitzgerald"
    assert window.plot_edit.toPlainText().startswith("A portrait of wealth")
    assert window.rating_edit.text().startswith("4.2")


def test_set_status_updates_status_bar(window):
    msg = "Web data found - Difference - Title, Author"
    window.set_status(msg)
    assert window.status_bar.currentMessage() == msg


def test_series_row_hidden_when_db_and_web_empty(window):
    assert window.series_row.isHidden()


def test_series_row_visible_when_web_has_series(window):
    window.update_fields_with_web_data(
        {
            "title": window.book.title,
            "author": window.book.author_name,
            "series": "Modern Classics",
            "series_number": "2",
        }
    )
    assert not window.series_row.isHidden()
    assert not window.series_web_edit.isHidden()


def test_series_web_number_visible_when_name_matches_db(qapp):
    book = Book(
        book_id=3,
        title="Book Three",
        author_name="Author",
        series_name="Gamache",
        genre_name="Fiction",
    )
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    dlg = WebMetadataWindow(
        db=None,
        book=book,
        scaler=scaler,
        theme_manager=theme_manager,
        web_data=None,
    )
    try:
        dlg.update_fields_with_web_data(
            {
                "title": book.title,
                "author": book.author_name,
                "series": "Gamache",
                "series_number": "9",
            }
        )
        assert dlg.series_web_edit.isHidden()
        assert not dlg.series_number_web_edit.isHidden()
        assert dlg.series_number_web_edit.text() == "9"
        assert "series_number" in dlg.field_differences
    finally:
        dlg.close()


def test_series_web_number_hidden_when_only_orphan_number_returned(window):
    window.update_fields_with_web_data(
        {
            "title": window.book.title,
            "author": window.book.author_name,
            "series_number": "4",
        }
    )
    assert window.series_row.isHidden()
    assert window.series_number_web_edit.isHidden()
    assert "series_number" not in window.field_differences


def test_web_status_message_includes_plot_found(window):
    window.update_fields_with_web_data(
        {
            "title": window.book.title,
            "author": window.book.author_name,
            "plot": "A portrait of wealth, illusion, and longing in the Jazz Age.",
        }
    )
    msg = window._build_web_status_message("Web data found", window.web_data)
    assert "Plot found" in msg


def test_compute_field_differences_empty_when_data_matches(sample_book):
    web_data = {
        "title": sample_book.title,
        "author": sample_book.author_name,
        "year": str(sample_book.year),
        "genre": sample_book.genre_name,
        "plot": "",
    }
    assert WebMetadataWindow.compute_field_differences(sample_book, web_data) == {}


def test_web_data_offers_changes_false_for_matching_metadata(sample_book):
    web_data = {
        "title": sample_book.title,
        "author": sample_book.author_name,
        "year": str(sample_book.year),
        "genre": sample_book.genre_name,
    }
    assert not WebMetadataWindow.web_data_offers_changes(sample_book, web_data)


def test_plot_preserved_when_web_has_no_plot(window, sample_book):
    window.update_fields_with_web_data(
        {
            "title": sample_book.title,
            "author": sample_book.author_name,
        }
    )
    assert window.plot_edit.toPlainText() == sample_book.comments


def test_web_status_message_includes_no_plot(window):
    window.update_fields_with_web_data(
        {
            "title": window.book.title,
            "author": window.book.author_name,
        }
    )
    msg = window._build_web_status_message("Web data found", window.web_data)
    assert "No plot" in msg


def test_tab_order_web_series_fields_before_buttons(window):
    window.update_fields_with_web_data(
        {
            "title": window.book.title,
            "author": window.book.author_name,
            "year": "1926",
            "series": "Modern Classics",
            "series_number": "2",
            "genre": "Literary Fiction",
            "plot": "A portrait of wealth, illusion, and longing in the Jazz Age.",
        }
    )
    window.show()
    chain = window._iter_tab_widgets()
    assert window.series_web_edit in chain
    assert window.series_number_web_edit in chain
    assert chain.index(window.series_web_edit) < chain.index(window.refetch_button)
    assert chain.index(window.series_number_web_edit) < chain.index(window.save_button)


def _tab_focus_names(widget, qapp, *, start_widget, steps: int) -> list[str]:
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent

    start_widget.setFocus()
    qapp.processEvents()
    names: list[str] = []
    for _ in range(steps):
        fw = qapp.focusWidget()
        names.append(fw.accessibleName() if fw else "")
        target = qapp.focusWidget() or widget
        qapp.sendEvent(
            target,
            QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier),
        )
        qapp.processEvents()
    return names


def test_tab_order_genre_web_and_checkbox_after_show(qapp, sample_book):
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    dlg = WebMetadataWindow(
        db=None,
        book=sample_book,
        scaler=scaler,
        theme_manager=theme_manager,
        web_data={
            "title": sample_book.title,
            "author": sample_book.author_name,
            "year": "1926",
            "genre": "Literary Fiction",
            "plot": "A portrait of wealth, illusion, and longing in the Jazz Age.",
        },
    )
    try:
        dlg.show()
        qapp.processEvents()
        chain = _tab_focus_names(dlg, qapp, start_widget=dlg.genre_edit, steps=3)
        assert chain[0] == "Current Genre"
        assert chain[1] == "Web Genre"
        assert chain[2] == "Keep Web Genre"
    finally:
        dlg.close()


def test_series_row_visible_when_db_has_series(qapp):
    book = Book(
        book_id=2,
        title="Book Two",
        author_name="Author",
        series_name="Test Saga",
        genre_name="Fiction",
    )
    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    dlg = WebMetadataWindow(
        db=None,
        book=book,
        scaler=scaler,
        theme_manager=theme_manager,
        web_data=None,
    )
    try:
        assert not dlg.series_row.isHidden()
        assert dlg.series_edit.text() == "Test Saga"
    finally:
        dlg.close()
