"""Pytest coverage for the Web Metadata dialog."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from src.accessibility.read_only_text import plot_text_equivalent
from src.database.models import Book
from src.ui.web_metadata import WebMetadataWindow


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
def window(ui_scaler, theme_manager, sample_book):
    """Construct the window without DB writes/network calls."""
    dlg = WebMetadataWindow(
        db=None,
        book=sample_book,
        scaler=ui_scaler,
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
    assert not hasattr(window, "series_edit")
    assert not hasattr(window, "series_row")


def test_web_metadata_loads_book_values(window, sample_book):
    assert window.title_edit.text() == sample_book.title
    assert window.author_edit.text() == sample_book.author_name
    assert window.year_edit.text() == str(sample_book.year)
    assert window.genre_edit.text() == sample_book.genre_name
    assert plot_text_equivalent(window.plot_edit.plot_text(), sample_book.comments)


def test_update_fields_with_web_data_tracks_differences(window):
    web_data = {
        "title": "The Great Gatsby (Annotated)",
        "author": "Francis Scott Key Fitzgerald",
        "year": "1926",
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
    assert "series" not in window.field_differences
    assert window.title_web_edit.text() == "The Great Gatsby (Annotated)"
    assert window.author_web_edit.text() == "Francis Scott Key Fitzgerald"
    assert window.plot_edit.plot_text().startswith("A portrait of wealth")
    assert window.rating_edit.text().startswith("4.2")


def test_set_status_updates_status_bar(window):
    msg = "Plot found - Difference - Title, Author"
    window.set_status(msg)
    assert window.status_bar.currentMessage() == msg


def test_web_status_message_lists_non_plot_differences_only(window):
    window.update_fields_with_web_data(
        {
            "title": "The Great Gatsby (Annotated)",
            "author": window.book.author_name,
            "year": "1926",
            "genre": window.book.genre_name,
            "plot": "A portrait of wealth, illusion, and longing in the Jazz Age.",
        }
    )
    msg = window._build_web_status_message(window.web_data)
    assert msg.startswith("Plot found")
    assert "Web data found" not in msg
    assert "Difference - Title, Year" in msg
    assert "Plot" not in msg.split("Difference -", 1)[-1]


def test_web_status_message_includes_plot_found(window):
    window.update_fields_with_web_data(
        {
            "title": window.book.title,
            "author": window.book.author_name,
            "plot": "A portrait of wealth, illusion, and longing in the Jazz Age.",
        }
    )
    msg = window._build_web_status_message(window.web_data)
    assert msg == "Plot found"
    assert "Web data found" not in msg


def test_web_status_message_includes_no_plot(window):
    window.update_fields_with_web_data(
        {
            "title": window.book.title,
            "author": window.book.author_name,
        }
    )
    msg = window._build_web_status_message(window.web_data)
    assert msg == "No plot"
    assert "Web data found" not in msg


def test_web_status_message_refetch_keeps_prefix(window):
    window.update_fields_with_web_data(
        {
            "title": "The Great Gatsby (Annotated)",
            "author": window.book.author_name,
            "plot": "A portrait of wealth, illusion, and longing in the Jazz Age.",
        }
    )
    msg = window._build_web_status_message(
        window.web_data, prefix="Re-fetch complete"
    )
    assert msg.startswith("Re-fetch complete - Plot found")
    assert "Difference - Title" in msg


def test_cosmetic_author_difference_not_flagged(sample_book):
    web_data = {
        "title": sample_book.title,
        "author": "F Scott Fitzgerald",  # missing periods
        "year": str(sample_book.year),
        "genre": sample_book.genre_name,
    }
    diffs = WebMetadataWindow.compute_field_differences(sample_book, web_data)
    assert "author" not in diffs
    assert not WebMetadataWindow.web_data_offers_changes(sample_book, web_data)


def test_cosmetic_title_difference_not_flagged(sample_book):
    web_data = {
        "title": "The Great Gatsby: A Novel",
        "author": sample_book.author_name,
        "year": str(sample_book.year),
        "genre": sample_book.genre_name,
    }
    diffs = WebMetadataWindow.compute_field_differences(sample_book, web_data)
    assert "title" not in diffs
    assert not WebMetadataWindow.web_data_offers_changes(sample_book, web_data)


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
    assert plot_text_equivalent(window.plot_edit.plot_text(), sample_book.comments)


def test_initial_focus_is_plot(qapp, ui_scaler, theme_manager, sample_book):
    dlg = WebMetadataWindow(
        db=None,
        book=sample_book,
        scaler=ui_scaler,
        theme_manager=theme_manager,
        web_data={
            "title": sample_book.title,
            "author": sample_book.author_name,
            "plot": "A long enough plot for the reviewer to read first.",
        },
    )
    try:
        dlg.show()
        qapp.processEvents()
        dlg.set_initial_focus()
        qapp.processEvents()
        assert qapp.focusWidget() is dlg.plot_edit
        assert not dlg.plot_alternatives.isVisible()
        assert dlg.plot_alternatives not in dlg._iter_tab_widgets()
    finally:
        dlg.close()


def test_has_form_scroll_area(window):
    assert hasattr(window, "form_scroll")
    assert window.form_scroll.widget() is window.form_widget


def test_tab_order_web_fields_before_buttons(window):
    window.update_fields_with_web_data(
        {
            "title": window.book.title,
            "author": window.book.author_name,
            "year": "1926",
            "genre": "Literary Fiction",
            "plot": "A portrait of wealth, illusion, and longing in the Jazz Age.",
        }
    )
    window.show()
    chain = window._iter_tab_widgets()
    assert window.year_web_edit in chain
    assert window.genre_web_edit in chain
    assert chain.index(window.year_web_edit) < chain.index(window.refetch_button)
    assert chain.index(window.genre_web_edit) < chain.index(window.save_button)


def test_other_plots_selector_updates_reviewed_plot_and_provenance(window, qapp):
    selected_text = "Best identity match. " + "A" * 100
    alternative_text = "Alternate accepted description. " + "B" * 100
    web_data = {
        "title": window.book.title,
        "author": window.book.author_name,
        "plot": selected_text,
        "plot_candidates": [
            {
                "text": selected_text,
                "source": "open_library",
                "source_url": "https://openlibrary.org/works/OL1W",
                "identifiers": {"open_library_work_key": "/works/OL1W"},
                "fetched_at": "2026-09-29T12:00:00+00:00",
                "license_id": "terms-review-required",
                "modified": False,
                "match_confidence": "identifier",
                "auto_apply": True,
            },
            {
                "text": alternative_text,
                "source": "wikipedia",
                "source_url": "https://en.wikipedia.org/wiki/Example",
                "identifiers": {},
                "fetched_at": "2026-09-29T12:00:01+00:00",
                "license_id": "CC-BY-SA-4.0",
                "modified": False,
                "match_confidence": "title_author",
                "auto_apply": True,
            },
        ],
    }

    window.show()
    qapp.processEvents()
    window.update_fields_with_web_data(web_data)
    qapp.processEvents()

    assert window.plot_alternatives.isVisible()
    assert window.plot_alternatives.accessibleName() == "Other plots"
    assert window.plot_alternatives in window._iter_tab_widgets()
    assert window.plot_alternatives.itemText(0) == "Best match"
    assert window.plot_alternatives.itemText(1) == "Other plot 1"

    window.plot_alternatives.setCurrentIndex(1)

    assert window.plot_edit.plot_text().startswith("Alternate accepted description.")
    assert window.web_data["plot_source"] == "wikipedia"
    assert window.web_data["plot_provenance"]["source_url"].endswith("Example")
    assert "plot" in window.field_differences


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


def test_tab_order_genre_web_and_checkbox_after_show(qapp, ui_scaler, theme_manager, sample_book):
    dlg = WebMetadataWindow(
        db=None,
        book=sample_book,
        scaler=ui_scaler,
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
