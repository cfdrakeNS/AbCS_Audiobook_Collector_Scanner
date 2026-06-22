"""Tests for book-list import title compare normalization."""

import pytest

from src.utils.text_utils import (
    compare_normalize_title,
    pre_normalize_title,
    strip_series_number,
)


@pytest.mark.parametrize(
    ("db_title", "sheet_title"),
    [
        ("Triptych - 01", "Triptych"),
        ("Broken - 04", "Broken"),
        ("Busted - 6.5", "Busted"),
        ("Snatched - 5.5", "Snatched"),
        ("The Last Widow - 09", "The Last Widow"),
        ("Girl, Forgotten", "Girl Forgotten"),
        ("Hobbit, The", "The Hobbit"),
        ("Bury Your Dead (Armand Gamache 6)", "Bury Your Dead"),
    ],
)
def test_compare_normalize_title_matches_db_to_sheet(db_title, sheet_title):
    assert compare_normalize_title(db_title) == compare_normalize_title(sheet_title)


def test_strip_series_number_leaves_bare_title_unchanged():
    assert strip_series_number("Triptych") == "Triptych"


def test_strip_series_number_does_not_strip_four_digit_year_suffix():
    assert strip_series_number("Some Title, 1999") == "Some Title, 1999"


def test_pre_normalize_title_order_series_before_article():
    assert pre_normalize_title("Sentinel, The - 02") == "The Sentinel"
