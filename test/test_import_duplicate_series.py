"""Series-number tiebreaker for import duplicate detection."""

from src.core.validator import ImportValidator
from src.ui.book_list_import_window import BookListImportWindow


def _book_list_dup_check(
    title: str,
    preexisting: list,
    *,
    author: str = "Karin Slaughter",
    year: int | None = 2006,
    collection_id: int = 1,
    match_mode: str = "title_author_only",
    fuzzy_threshold: int = 0,
) -> bool:
    """Call BookListImportWindow._check_duplicate without constructing the UI."""
    return BookListImportWindow._check_duplicate(
        None,
        title,
        author,
        year,
        collection_id,
        preexisting,
        match_mode,
        fuzzy_threshold,
    )


def _preexisting_entry(title: str, author: str = "Karin Slaughter", **extra) -> dict:
    from src.utils.text_utils import (
        compare_normalize_title,
        normalize_author,
        series_number_key,
        split_series_number,
    )

    _, series_num = split_series_number(title)
    return {
        "title": title,
        "author": author,
        "norm_title": compare_normalize_title(title),
        "norm_author": normalize_author(author, aggressive=True),
        "series_key": series_number_key(series_num),
        "year": extra.get("year", 2006),
        "collection_id": extra.get("collection_id", 1),
    }


def test_book_list_different_series_numbers_not_duplicate():
    preexisting = [_preexisting_entry("Triptych - 01")]
    assert _book_list_dup_check("Triptych - 02", preexisting) is False


def test_book_list_bare_title_matches_series_suffix():
    preexisting = [_preexisting_entry("Triptych - 01")]
    assert _book_list_dup_check("Triptych", preexisting) is True


def test_book_list_same_series_number_is_duplicate():
    preexisting = [_preexisting_entry("Triptych - 01")]
    assert _book_list_dup_check("Triptych - 1", preexisting) is True


def _validator_for_series_tests() -> ImportValidator:
    validator = ImportValidator()
    validator.duplicate_match_mode = "title_author_only"
    validator.duplicate_fuzzy_threshold = 0
    return validator


def test_validator_different_series_numbers_not_duplicate():
    validator = _validator_for_series_tests()
    index = validator.build_duplicate_index(
        [{"title": "Triptych - 01", "author": "Karin Slaughter", "year": 2006}]
    )
    assert (
        validator.is_duplicate_fast(
            {"title": "Triptych - 02", "author": "Karin Slaughter", "year": 2006},
            index,
        )
        is False
    )


def test_validator_bare_title_matches_series_suffix():
    validator = _validator_for_series_tests()
    index = validator.build_duplicate_index(
        [{"title": "Triptych - 01", "author": "Karin Slaughter", "year": 2006}]
    )
    assert (
        validator.is_duplicate_fast(
            {"title": "Triptych", "author": "Karin Slaughter", "year": 2006},
            index,
        )
        is True
    )


def test_validator_live_index_sees_same_pass_add():
    """A book added mid-scan must be visible to a later identical check."""
    validator = _validator_for_series_tests()
    index = validator.build_duplicate_index([])
    first = {"title": "Triptych - 01", "author": "Karin Slaughter", "year": 2006}
    assert validator.is_duplicate_fast(first, index) is False

    validator.add_to_duplicate_index(index, first)
    assert validator.is_duplicate_fast(first, index) is True

    # Different series number in the same pass still imports
    second = {"title": "Triptych - 02", "author": "Karin Slaughter", "year": 2006}
    assert validator.is_duplicate_fast(second, index) is False
