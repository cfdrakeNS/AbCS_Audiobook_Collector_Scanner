"""Tests for NameListWindow screen reader accessibility helpers."""

import pytest

from src.ui.name_list_window import NameListWindow


@pytest.mark.parametrize(
    "name, count, active, expected",
    [
        ("Louise Penny", 5, None, "Louise Penny: 5 books"),
        ("Louise Penny", 1, None, "Louise Penny: 1 book"),
        ("Louise Penny", 0, None, "Louise Penny: 0 books"),
        ("My Collection", 3, "Yes", "My Collection: Active Yes: 3 books"),
        ("Old Collection", 1, "No", "Old Collection: Active No: 1 book"),
    ],
)
def test_row_accessible_text(name, count, active, expected):
    kwargs = {} if active is None else {"active": active}
    assert NameListWindow._row_accessible_text(name, count, **kwargs) == expected


@pytest.mark.parametrize(
    "matched, expected",
    [
        (True, None),
        (False, 0),
    ],
)
def test_initial_table_row(matched, expected):
    assert NameListWindow._initial_table_row(matched) == expected
