"""Tests for NameListWindow screen reader accessibility helpers."""

from src.ui.name_list_window import NameListWindow


def test_row_accessible_text_plural_books():
    assert (
        NameListWindow._row_accessible_text("Louise Penny", 5)
        == "Louise Penny: 5 books"
    )


def test_row_accessible_text_singular_book():
    assert (
        NameListWindow._row_accessible_text("Louise Penny", 1)
        == "Louise Penny: 1 book"
    )


def test_row_accessible_text_zero_books():
    assert (
        NameListWindow._row_accessible_text("Louise Penny", 0)
        == "Louise Penny: 0 books"
    )


def test_row_accessible_text_collection_active():
    assert (
        NameListWindow._row_accessible_text(
            "My Collection", 3, active="Yes"
        )
        == "My Collection: Active Yes: 3 books"
    )


def test_row_accessible_text_collection_inactive():
    assert (
        NameListWindow._row_accessible_text(
            "Old Collection", 1, active="No"
        )
        == "Old Collection: Active No: 1 book"
    )


def test_initial_table_row_skips_reset_when_matched():
    assert NameListWindow._initial_table_row(True) is None


def test_initial_table_row_defaults_to_first_row():
    assert NameListWindow._initial_table_row(False) == 0
