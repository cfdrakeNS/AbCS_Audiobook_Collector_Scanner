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
