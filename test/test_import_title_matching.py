"""Series-number tiebreaker and import title matching."""

from src.core.validator import ImportValidator


def _validator(
    *,
    match_mode: str = "title_author_only",
    fuzzy_threshold: int = 0,
) -> ImportValidator:
    validator = ImportValidator()
    validator.duplicate_match_mode = match_mode
    validator.duplicate_fuzzy_threshold = fuzzy_threshold
    return validator

def test_validator_different_series_numbers_not_duplicate():
    validator = _validator()
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
    validator = _validator()
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
    validator = _validator()
    index = validator.build_duplicate_index([])
    first = {"title": "Triptych - 01", "author": "Karin Slaughter", "year": 2006}
    assert validator.is_duplicate_fast(first, index) is False

    validator.add_to_duplicate_index(index, first)
    assert validator.is_duplicate_fast(first, index) is True

    # Different series number in the same pass still imports
    second = {"title": "Triptych - 02", "author": "Karin Slaughter", "year": 2006}
    assert validator.is_duplicate_fast(second, index) is False

def test_progress_throttle_skips_process_events_between_ticks():
    """Throttled progress updates must not pump the event loop every row."""
    from src.ui.book_list_import_window import BookListImportWindow

    calls = {"processEvents": 0}

    class _FakeProgress:
        title_edit = type("E", (), {"setText": staticmethod(lambda *_: None)})()
        author_edit = type("E", (), {"setText": staticmethod(lambda *_: None)})()

        def update_add_progress(self, **_kwargs):
            return None

    window = BookListImportWindow.__new__(BookListImportWindow)
    window.progress_window = _FakeProgress()
    window._progress_ui_next = float("inf")  # force throttle miss
    window._import_start_time = 0.0

    import src.ui.book_list_import_window as bli_mod

    original = bli_mod.QApplication.processEvents

    def _counting_process_events(*_a, **_k):
        calls["processEvents"] += 1

    bli_mod.QApplication.processEvents = staticmethod(_counting_process_events)
    try:
        window._update_import_progress(
            processed=1,
            total=100,
            added=0,
            duplicates=0,
            errors=0,
            current_title="x",
            current_author="y",
            force=False,
        )
        assert calls["processEvents"] == 0

        window._update_import_progress(
            processed=100,
            total=100,
            added=1,
            duplicates=0,
            errors=0,
            force=True,
        )
        assert calls["processEvents"] == 1
    finally:
        bli_mod.QApplication.processEvents = original

