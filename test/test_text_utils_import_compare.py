"""Tests for book-list import title compare normalization."""

import pytest

from src.utils.text_utils import (
    append_series_suffix,
    title_with_series_suffix,
    series_number_for_storage,
    title_without_matching_series_suffix,
    compare_normalize_title,
    format_series_suffix,
    pre_normalize_title,
    series_number_key,
    series_numbers_compatible,
    split_series_number,
    strip_series_number,
    titles_match,
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


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (2.0, "02"),
        (2, "02"),
        ("#2", "02"),
        ("6.5", "6.5"),
        (6.5, "6.5"),
        ("", ""),
        (None, ""),
    ],
)
def test_format_series_suffix(raw, expected):
    assert format_series_suffix(raw) == expected


def test_append_series_suffix_pads_whole_number():
    assert append_series_suffix("The Moon", 2.0) == "The Moon - 02"


def test_append_series_suffix_preserves_decimal():
    assert append_series_suffix("Busted", "6.5") == "Busted - 6.5"


def test_append_series_suffix_skips_when_already_present():
    assert append_series_suffix("The Moon - 02", 3) == "The Moon - 02"


def test_title_with_series_suffix_adds_and_replaces():
    assert title_with_series_suffix("Rules of Prey", 3) == "Rules of Prey - 03"
    assert title_with_series_suffix("Winter - 03", 6.5) == "Winter - 6.5"
    assert title_with_series_suffix("Other - 9", 9) == "Other - 9"
    assert title_with_series_suffix("Some Title, 1999", 3) == "Some Title, 1999 - 03"
    assert title_with_series_suffix("Winter - 03", None) == "Winter - 03"


def test_append_series_suffix_never_includes_series_name():
    result = append_series_suffix("The Moon", 2)
    assert "Sci Fi" not in result
    assert "(" not in result
    assert result == "The Moon - 02"


@pytest.mark.parametrize(
    ("title", "clean", "number"),
    [
        ("The Moon - 02", "The Moon", "02"),
        ("Busted - 6.5", "Busted", "6.5"),
        ("Triptych", "Triptych", ""),
    ],
)
def test_split_series_number(title, clean, number):
    assert split_series_number(title) == (clean, number)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("01", "1"),
        ("1", "1"),
        (1, "1"),
        ("1.0", "1"),
        (1.0, "1"),
        ("#01", "1"),
        ("6.5", "6.5"),
        (6.5, "6.5"),
        ("", ""),
        (None, ""),
    ],
)
def test_series_number_key(raw, expected):
    assert series_number_key(raw) == expected


def test_series_number_for_storage_keeps_decimals():
    assert series_number_for_storage("02") == 2
    assert series_number_for_storage("2.0") == 2
    assert series_number_for_storage("6.5") == 6.5
    assert series_number_for_storage("0.5") == 0.5
    assert series_number_for_storage("0") is None
    assert series_number_for_storage("") is None


def test_title_strip_only_when_suffix_matches_stored_number():
    assert title_without_matching_series_suffix("The Moon - 03", 3) == "The Moon"
    assert title_without_matching_series_suffix("The Moon - 02", 3) == "The Moon - 02"
    assert title_without_matching_series_suffix("The Moon", 3) == "The Moon"
    assert title_without_matching_series_suffix("Some Title, 1999", 1999) == "Some Title, 1999"
    assert title_without_matching_series_suffix("Winter - 6.5", 6.5) == "Winter"


@pytest.mark.parametrize(
    ("left", "right", "compatible"),
    [
        ("", "01", True),
        ("01", "", True),
        ("", "", True),
        ("01", "1", True),
        ("1.0", "01", True),
        ("01", "02", False),
        ("6.5", "6.5", True),
        ("6.5", "6", False),
    ],
)
def test_series_numbers_compatible(left, right, compatible):
    assert series_numbers_compatible(left, right) is compatible


def test_titles_match_bare_to_series_suffix():
    assert titles_match("Triptych - 01", "Triptych") is True


def test_titles_match_different_series_numbers_are_not_duplicates():
    assert titles_match("Triptych - 01", "Triptych - 02") is False


def test_titles_match_same_series_number_variants():
    assert titles_match("Triptych - 01", "Triptych - 1") is True
    assert titles_match("Triptych - 01", "Triptych - 1.0") is True
