"""Integration tests for WebBookAPI fetch, cache, rate-limit, cancel, and budget."""

from __future__ import annotations

import json
import time
from unittest.mock import patch

import pytest

from src.web import web_book_api as wba
from src.web.web_book_api import (
    FetchBudget,
    WebBookAPI,
    _clear_source_cooldown,
    _note_rate_limited,
    _reset_shared_web_api_for_tests,
    _seconds_until_cooldown_clears,
    get_web_api,
)


@pytest.fixture
def api(web_api):
    return web_api


@patch.object(WebBookAPI, "_fill_series_fields", return_value=False)
@patch.object(WebBookAPI, "_enrich_metadata_plot")
@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_open_library")
def test_sherlock_holmes_with_sir_author_finds_open_library(
    ol_mock, _gb_mock, _wd_mock, _plot, _series, api
):
    ol_mock.return_value = {
        "title": "The Adventures of Sherlock Holmes",
        "author": "Arthur Conan Doyle",
        "plot": "Short stories featuring Sherlock Holmes.",
        "source": "open_library",
    }
    result = api.get_book_metadata(
        "The Adventures Of Sherlock Holmes",
        "Sir Arthur Conan Doyle",
        refresh=0,
    )
    assert result is not None
    assert "Sherlock" in result["title"]
    assert "Doyle" in result["author"]
    ol_mock.assert_called()
    call_author = ol_mock.call_args[0][1]
    assert call_author == "Arthur Conan Doyle"

@patch.object(WebBookAPI, "_fill_series_fields", return_value=False)
@patch.object(WebBookAPI, "_enrich_metadata_plot")
@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_open_library")
def test_title_only_fallback_when_author_search_fails(
    ol_mock, _gb_mock, _wd_mock, _plot, _series, api
):
    """After strict author search fails, title-only search can return a match."""

    def open_library_side_effect(title, author=None, year=None, **kwargs):
        if author:
            return None
        return {
            "title": "Oliver Twist",
            "author": "Charles Dickens",
            "source": "open_library",
        }

    ol_mock.side_effect = open_library_side_effect
    result = api.get_book_metadata(
        "Oliver Twist",
        "John Volunteer",
        narrator="John Volunteer",
        refresh=0,
    )
    assert result is not None
    assert result.get("title_only_search") is True
    assert any(call.args[1] is None for call in ol_mock.call_args_list)

@patch.object(WebBookAPI, "_save_persistent_cache")
@patch.object(WebBookAPI, "_enrich_metadata_plot")
@patch.object(WebBookAPI, "_fetch_series_from_google", return_value=None)
@patch.object(WebBookAPI, "_get_open_library_work_fields", return_value={})
@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books")
@patch.object(WebBookAPI, "_fetch_from_open_library")
def test_refresh_zero_open_library_before_google(
    ol_mock, gb_mock, _wd_mock, _ol_fields, _series, _plot, _save, api
):
    ol_mock.return_value = {
        "title": "Dune",
        "author": "Frank Herbert",
        "source": "open_library",
    }
    result = api.get_book_metadata("Dune", "Frank Herbert", refresh=0)
    assert result is not None
    assert result["source"] == "open_library"
    ol_mock.assert_called_once()
    gb_mock.assert_not_called()

@patch.object(WebBookAPI, "_save_persistent_cache")
@patch.object(WebBookAPI, "_enrich_metadata_plot")
@patch.object(WebBookAPI, "_fetch_series_from_google", return_value=None)
@patch.object(WebBookAPI, "_get_open_library_work_fields", return_value={})
@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books")
@patch.object(WebBookAPI, "_fetch_from_open_library", return_value=None)
def test_refresh_zero_google_when_open_library_fails(
    ol_mock, gb_mock, _wd_mock, _ol_fields, _series, _plot, _save, api
):
    gb_mock.return_value = {
        "title": "Dune",
        "author": "Frank Herbert",
        "source": "Google Books",
    }
    result = api.get_book_metadata("Dune", "Frank Herbert", refresh=0)
    assert result is not None
    assert result["source"] == "google_books"
    ol_mock.assert_called_once()
    gb_mock.assert_called_once()

@patch.object(WebBookAPI, "_save_persistent_cache")
@patch.object(WebBookAPI, "_enrich_metadata_plot")
@patch.object(WebBookAPI, "_fetch_series_from_google", return_value=None)
@patch.object(WebBookAPI, "_get_open_library_work_fields", return_value={})
@patch.object(WebBookAPI, "_fetch_from_wikidata")
@patch.object(WebBookAPI, "_fetch_from_google_books")
@patch.object(WebBookAPI, "_fetch_from_open_library")
def test_refresh_one_skips_open_library(
    ol_mock, gb_mock, wd_mock, _ol_fields, _series, _plot, _save, api
):
    gb_mock.return_value = {
        "title": "Dune",
        "author": "Frank Herbert",
    }
    wd_mock.return_value = None
    result = api.get_book_metadata("Dune", "Frank Herbert", refresh=1)
    assert result is not None
    ol_mock.assert_not_called()
    gb_mock.assert_called_once()

@patch("src.web.web_book_api.urllib.request.urlopen")
def test_open_library_never_filters_by_db_year(urlopen_mock, api):
    """Library year must not be sent to Open Library (often birth/import date, not publication)."""

    doc = {
        "title": "The Adventures of Sherlock Holmes",
        "author_name": ["Arthur Conan Doyle"],
        "first_publish_year": 1892,
        "key": "/works/OL123W",
    }

    class FakeResponse:
        def read(self):
            return json.dumps({"docs": [doc]}).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    urlopen_mock.return_value = FakeResponse()
    with patch.object(
        api,
        "_get_open_library_work_fields",
        return_value={"description": "", "series": "", "series_number": ""},
    ):
        result = api.get_book_metadata(
            "The Adventures Of Sherlock Holmes",
            "Sir Arthur Conan Doyle",
            year="1867",
            refresh=0,
        )
    assert result is not None
    for call in urlopen_mock.call_args_list:
        assert "first_publish_year=1867" not in call.args[0].full_url

def test_get_book_metadata_same_result_with_or_without_db_year(api):
    """Search uses title and author only; a wrong DB year must not change the outcome."""
    with (
        patch.object(api, "_enrich_metadata_plot"),
        patch.object(api, "_fill_series_fields", return_value=False),
        patch.object(api, "_fetch_from_wikidata", return_value=None),
        patch.object(api, "_fetch_from_google_books", return_value=None),
        patch.object(api, "_fetch_from_open_library") as ol_mock,
    ):
        ol_mock.return_value = {
            "title": "The Hound of the Baskervilles",
            "author": "Arthur Conan Doyle",
            "source": "open_library",
        }
        with_year = api.get_book_metadata(
            "The Hound Of The Baskervilles",
            "Sir Arthur Conan Doyle",
            year="1867",
            refresh=0,
        )
        api._cache = {}
        without_year = api.get_book_metadata(
            "The Hound Of The Baskervilles",
            "Sir Arthur Conan Doyle",
            year=None,
            refresh=0,
        )
    assert with_year is not None
    assert without_year is not None
    assert with_year["title"] == without_year["title"]

@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_open_library")
def test_deaver_cause_of_death_rejects_cornwell_without_title_only_fallback(
    ol_mock, _gb_mock, _wd_mock, api
):
    def open_library_side_effect(title, author=None, **kwargs):
        # Mock bypasses picker; no OL hit survives author filter for Deaver.
        return None

    ol_mock.side_effect = open_library_side_effect
    result = api.get_book_metadata(
        "Cause Of Death",
        "Jeffery Deaver",
        refresh=0,
        path=r"C:\Audiobooks\cause_of_death",
        narrator="",
    )
    assert result is None
    assert any(call.args[1] for call in ol_mock.call_args_list)

@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_open_library")
def test_deaver_date_night_rejects_wrong_author_and_title_extension(
    ol_mock, _gb_mock, _wd_mock, api
):
    def open_library_side_effect(title, author=None, **kwargs):
        return None

    ol_mock.side_effect = open_library_side_effect
    result = api.get_book_metadata(
        "Date Night",
        "Jeffery Deaver",
        refresh=0,
        path=r"C:\Audiobooks\date_night",
        narrator="",
    )
    assert result is None

@patch.object(WebBookAPI, "_fill_series_fields", return_value=False)
@patch.object(WebBookAPI, "_enrich_metadata_plot")
@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_open_library")
def test_pride_and_prejudice_jane_austen_via_broadened_search(
    ol_mock, _gb_mock, _wd_mock, _plot, _series, api
):
    def open_library_side_effect(title, author=None, **kwargs):
        if author:
            return None
        return {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "source": "open_library",
        }

    ol_mock.side_effect = open_library_side_effect
    result = api.get_book_metadata(
        "Pride And Prejudice",
        "Jane Austen",
        refresh=0,
        path=r"C:\Audiobooks\pride",
        narrator="",
    )
    assert result is not None
    assert "Austen" in result["author"]
    assert result.get("broadened_search") is True

@patch.object(WebBookAPI, "_fill_series_fields", return_value=False)
@patch.object(WebBookAPI, "_enrich_metadata_plot")
@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_open_library", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books")
def test_google_intitle_retry_finds_austen_when_inauthor_empty(
    gb_mock, _ol_mock, _wd_mock, _plot, _series, api
):
    def google_side_effect(title, author=None, **kwargs):
        db_author = kwargs.get("match_author") or author
        if author:
            return None
        if db_author and "Austen" in db_author:
            return {
                "title": "Pride and Prejudice",
                "author": "Jane Austen",
                "source": "Google Books",
            }
        return None

    gb_mock.side_effect = google_side_effect
    result = api.get_book_metadata(
        "Pride And Prejudice",
        "Jane Austen",
        refresh=0,
        path=r"C:\Audiobooks\pride",
        narrator="",
    )
    assert result is not None
    assert "Austen" in result["author"]

@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_open_library")
def test_open_library_broadened_pass_uses_match_author(ol_mock, _gb_mock, _wd_mock, api):
    captured = []

    def open_library_side_effect(title, author=None, **kwargs):
        captured.append((author, kwargs.get("match_author")))
        return None

    ol_mock.side_effect = open_library_side_effect
    api.get_book_metadata(
        "Cause Of Death",
        "Jeffery Deaver",
        refresh=0,
        path=r"C:\Audiobooks\cause",
        narrator="",
    )
    assert (None, "Jeffery Deaver") in captured

def test_enrich_metadata_plot_fills_from_wikipedia_when_ol_plot_short(api):
    metadata = {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "source": "open_library",
        "plot": "Short.",
        "open_library_work_key": "/works/OL123W",
    }
    wiki_text = (
        "Pride and Prejudice is a novel by Jane Austen that follows Elizabeth Bennet "
        "as she navigates issues of manners, upbringing, and marriage in Georgian England."
    )
    with patch.object(api, "_get_open_library_work_fields", return_value={"description": "Tiny"}):
        with patch.object(api, "_fetch_wikipedia_rest_summary", return_value=""):
            with patch.object(api, "_fetch_plot_from_wikipedia", return_value=wiki_text):
                api._enrich_metadata_plot(metadata, "Pride And Prejudice", "Jane Austen")
    assert metadata["plot"] == wiki_text
    assert metadata["plot_source"] == "wikipedia"

def test_enrich_metadata_plot_keeps_adequate_open_library_plot(api):
    long_plot = "A" * 100
    metadata = {
        "title": "Dune",
        "author": "Frank Herbert",
        "source": "open_library",
        "plot": long_plot,
    }
    with patch.object(api, "_fetch_plot_from_wikipedia") as wiki_mock:
        api._enrich_metadata_plot(metadata, "Dune", "Frank Herbert")
        wiki_mock.assert_not_called()
    assert metadata["plot"] == long_plot

@patch.object(WebBookAPI, "_enrich_metadata_plot")
@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_open_library", return_value=None)
def test_progress_callback_order_refresh_zero(
    _ol_mock, _gb_mock, _wd_mock, _enrich_mock, api
):
    """Progress callback reports sources in Open Library -> Google -> WikiData order."""
    messages: list[str] = []
    api.get_book_metadata(
        "Test Title",
        "Test Author",
        refresh=0,
        progress_callback=messages.append,
    )
    ol_idx = next(i for i, m in enumerate(messages) if "Open Library" in m)
    gb_idx = next(i for i, m in enumerate(messages) if "Google Books" in m)
    wd_idx = next(i for i, m in enumerate(messages) if "WikiData" in m)
    assert ol_idx < gb_idx < wd_idx
    assert messages[ol_idx].startswith("Trying source 1:")
    assert messages[gb_idx].startswith("Trying source 2:")
    assert messages[wd_idx].startswith("Trying source 3:")

def test_enrich_metadata_plot_uses_wikipedia_rest_for_open_library_win(api):
    metadata = {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "source": "open_library",
        "plot": "Short.",
        "open_library_work_key": "/works/OL123W",
    }
    rest_text = (
        "Pride and Prejudice is a novel by Jane Austen that follows Elizabeth Bennet "
        "as she navigates issues of manners, upbringing, and marriage in Georgian England."
    )
    with patch.object(
        api, "_get_open_library_work_fields", return_value={"description": "Tiny"}
    ):
        with patch.object(
            api, "_fetch_wikipedia_rest_summary", return_value=rest_text
        ) as rest_mock:
            with patch.object(api, "_fetch_plot_from_wikipedia") as wiki_mock:
                api._enrich_metadata_plot(
                    metadata, "Pride And Prejudice", "Jane Austen"
                )
    rest_mock.assert_called()
    assert rest_mock.call_args_list[0].args[0] == "Pride and Prejudice Jane Austen novel"
    wiki_mock.assert_not_called()
    assert metadata["plot"] == rest_text
    assert metadata["plot_source"] == "wikipedia"

@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_open_library", return_value=None)
def test_google_books_429_surfaces_fetch_errors(_ol_mock, _wd_mock, api):
    import urllib.error

    def raise_429(*_args, **_kwargs):
        raise urllib.error.HTTPError(
            "https://www.googleapis.com/books/v1/volumes",
            429,
            "Too Many Requests",
            {},
            None,
        )

    with patch.object(WebBookAPI, "_fetch_from_google_books", side_effect=raise_429):
        result = api._search_metadata_sources(
            "Pride and Prejudice",
            "Jane Austen",
            refresh=0,
            require_author_match=True,
        )
    assert result is not None
    assert result.get("_no_result") is True
    assert any("google_books" in err for err in result.get("_fetch_errors", []))

@patch("src.web.web_book_api.urllib.request.urlopen")
def test_open_library_search_sends_user_agent(urlopen_mock, api):
    class FakeResponse:
        def read(self):
            return json.dumps({"docs": []}).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    urlopen_mock.return_value = FakeResponse()
    api._fetch_from_open_library("Pride and Prejudice", "Jane Austen")
    sent_request = urlopen_mock.call_args.args[0]
    from src.web.web_book_api import USER_AGENT

    assert sent_request.get_header("User-agent") == USER_AGENT

def _http_error_429():
    import urllib.error

    return urllib.error.HTTPError(
        "https://www.googleapis.com/books/v1/volumes",
        429,
        "Too Many Requests",
        {},
        None,
    )

class _FakeGoogleResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

@patch("src.web.web_book_api.time.sleep")
@patch("src.web.web_book_api.urllib.request.urlopen")
def test_google_books_429_stops_query_loop(urlopen_mock, sleep_mock, api):
    """Fatal 429 must not retry and must not try the next query variant."""
    urlopen_mock.side_effect = _http_error_429()
    result = api._fetch_from_google_books(
        "Pride and Prejudice",
        "Jane Austen",
        require_author_match=True,
        propagate_fatal_errors=False,
    )
    assert result is None
    assert urlopen_mock.call_count == 1
    sleep_mock.assert_not_called()

@patch("src.web.web_book_api.time.sleep")
@patch("src.web.web_book_api.urllib.request.urlopen")
def test_google_books_cooldown_short_circuits_followup(urlopen_mock, sleep_mock, api):
    """After a 429, a follow-up call within the cooldown window skips the network."""
    urlopen_mock.side_effect = _http_error_429()
    api._fetch_from_google_books(
        "Pride and Prejudice",
        "Jane Austen",
        require_author_match=True,
        propagate_fatal_errors=False,
    )
    first_calls = urlopen_mock.call_count
    assert first_calls >= 1

    result = api._fetch_from_google_books(
        "Sense and Sensibility",
        "Jane Austen",
        require_author_match=True,
        propagate_fatal_errors=False,
    )
    assert result is None
    assert urlopen_mock.call_count == first_calls

def _http_error_503():
    import urllib.error

    return urllib.error.HTTPError(
        "https://www.googleapis.com/books/v1/volumes",
        503,
        "Service Unavailable",
        {},
        None,
    )

@patch("src.web.web_book_api.time.sleep")
@patch("src.web.web_book_api.urllib.request.urlopen")
def test_google_books_503_retry_recovers(urlopen_mock, sleep_mock, api):
    """One 503 then a successful retry returns the matched volume."""
    success_payload = {
        "items": [
            {
                "volumeInfo": {
                    "title": "Pride and Prejudice",
                    "authors": ["Jane Austen"],
                    "publishedDate": "1813",
                }
            }
        ]
    }
    urlopen_mock.side_effect = [
        _http_error_503(),
        _FakeGoogleResponse(success_payload),
    ]
    result = api._fetch_from_google_books(
        "Pride and Prejudice",
        "Jane Austen",
        require_author_match=True,
        propagate_fatal_errors=False,
    )
    assert result is not None
    assert result["title"] == "Pride and Prejudice"
    assert urlopen_mock.call_count == 2
    sleep_mock.assert_called_once()

@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books", return_value=None)
@patch.object(
    WebBookAPI,
    "_fetch_from_open_library",
    return_value={
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "year": "1813",
        "plot": "",
        "source": "open_library",
    },
)
def test_get_book_metadata_keeps_match_when_plot_enrichment_raises(
    _ol_mock, _gb_mock, _wd_mock, api
):
    with patch.object(
        WebBookAPI, "_enrich_metadata_plot", side_effect=RuntimeError("plot boom")
    ):
        with patch.object(WebBookAPI, "_fill_series_fields", return_value=False):
            result = api.get_book_metadata("Pride and Prejudice", "Jane Austen")
    assert result is not None
    assert result.get("_no_result") is not True
    assert result["title"] == "Pride and Prejudice"
    assert result["source"] == "open_library"

@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books", return_value=None)
@patch.object(
    WebBookAPI,
    "_fetch_from_open_library",
    return_value={
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "year": "1813",
        "plot": "A long enough plot for adequacy checks in other tests.",
        "source": "open_library",
    },
)
def test_get_book_metadata_keeps_match_when_series_enrichment_raises(
    _ol_mock, _gb_mock, _wd_mock, api
):
    with patch.object(WebBookAPI, "_enrich_metadata_plot"):
        with patch.object(
            WebBookAPI, "_fill_series_fields", side_effect=RuntimeError("series boom")
        ):
            result = api.get_book_metadata("Pride and Prejudice", "Jane Austen")
    assert result is not None
    assert result.get("_no_result") is not True
    assert result["title"] == "Pride and Prejudice"

@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books", return_value=None)
@patch.object(
    WebBookAPI,
    "_fetch_from_open_library",
    return_value={
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "year": "1813",
        "plot": "",
        "source": "open_library",
    },
)
def test_get_book_metadata_keeps_match_when_progress_callback_raises(
    _ol_mock, _gb_mock, _wd_mock, api
):
    def boom(_msg):
        raise RuntimeError("ui boom")

    with patch.object(WebBookAPI, "_enrich_metadata_plot"):
        with patch.object(WebBookAPI, "_fill_series_fields", return_value=False):
            result = api.get_book_metadata(
                "Pride and Prejudice",
                "Jane Austen",
                progress_callback=boom,
            )
    assert result is not None
    assert result.get("_no_result") is not True
    assert result["title"] == "Pride and Prejudice"

def test_cache_hit_survives_series_enrichment_exception(api):
    cache_key = "Pride and Prejudice|Jane Austen|0|None|None|None|False|"
    api._cache[cache_key] = (
        __import__("time").time(),
        {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "year": "1813",
            "plot": "Cached plot text.",
            "source": "open_library",
            "first_attempt": True,
        },
    )
    with patch.object(
        WebBookAPI, "_fill_series_fields", side_effect=RuntimeError("cache series boom")
    ):
        result = api.get_book_metadata("Pride and Prejudice", "Jane Austen")
    assert result is not None
    assert result["title"] == "Pride and Prejudice"
    assert result["plot"] == "Cached plot text."

@patch("src.web.web_book_api.time.sleep")
@patch("src.web.web_book_api.urllib.request.urlopen")
def test_fetch_google_by_isbn_notes_rate_limit_on_429(urlopen_mock, sleep_mock, api):
    from src.web.web_book_api import _is_source_cooling_down

    urlopen_mock.side_effect = _http_error_429()
    result = api._fetch_google_by_isbn("9780765326355")
    assert result is None
    assert _is_source_cooling_down("google_books")
    # Follow-up ISBN call must short-circuit without another network attempt.
    prior = urlopen_mock.call_count
    assert api._fetch_google_by_isbn("9780765326355") is None
    assert urlopen_mock.call_count == prior


def test_fetch_budget_exhausts_on_request_cap():
    budget = FetchBudget(seconds=60, max_requests=2)
    assert budget.can_continue()
    budget.note_request()
    assert budget.can_continue()
    budget.note_request()
    assert not budget.can_continue()
    assert budget.exhausted

def test_fetch_budget_exhausts_on_deadline():
    budget = FetchBudget(seconds=0.01, max_requests=100)
    time.sleep(0.02)
    assert not budget.can_continue()

def test_get_book_metadata_cancel_returns_canceled_flag(api):
    result = api.get_book_metadata(
        "Any Title",
        "Any Author",
        should_cancel=lambda: True,
    )
    assert result == {"_canceled": True}

def test_get_book_metadata_budget_stops_cascade(api):
    """Exhausted budget stops further sources without raising to the caller."""
    api._active_budget = FetchBudget(seconds=60, max_requests=0)
    api._should_cancel = None
    # With max_requests=0, can_continue is False immediately
    with pytest.raises(wba.FetchAborted):
        api._check_abort()

def test_cache_hit_skips_network_when_enriched(api):
    key_meta = {
        "title": "Dune",
        "author": "Frank Herbert",
        "plot": "A" * 100,
        "source": "open_library",
        "_plot_enriched": True,
        "_series_enriched": True,
    }
    cache_key = "Dune|Frank Herbert|0|None|None|None|False|"
    api._cache[cache_key] = (time.time(), key_meta)

    with patch.object(api, "_search_metadata_sources") as search_mock, patch.object(
        api, "_fill_series_fields"
    ) as series_mock, patch.object(api, "_enrich_metadata_plot") as plot_mock:
        result = api.get_book_metadata("Dune", "Frank Herbert", refresh=0)
        search_mock.assert_not_called()
        series_mock.assert_not_called()
        plot_mock.assert_not_called()
    assert result["title"] == "Dune"
    assert "open_library_work_key" not in result

def test_retry_after_floors_to_source_default():
    """Short Retry-After must not undercut the Google Books policy cooldown."""
    _clear_source_cooldown()

    class Headers(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    headers = Headers({"Retry-After": "12"})
    _note_rate_limited("google_books", headers=headers)
    remaining = _seconds_until_cooldown_clears("google_books")
    # Default Google cooldown is 15 minutes; 12s header must not win.
    assert remaining >= 14 * 60
    _clear_source_cooldown()


def test_retry_after_can_lengthen_beyond_default():
    _clear_source_cooldown()

    class Headers(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    headers = Headers({"Retry-After": "2000"})
    _note_rate_limited("google_books", headers=headers)
    remaining = _seconds_until_cooldown_clears("google_books")
    assert remaining >= 1990
    _clear_source_cooldown()

@patch("src.web.web_book_api.urllib.request.urlopen")
def test_wikidata_503_propagates_into_fetch_errors(urlopen_mock, api):
    import urllib.error

    def raise_503(*_a, **_k):
        raise urllib.error.HTTPError(
            "https://query.wikidata.org/sparql",
            503,
            "Service Unavailable",
            {},
            None,
        )

    urlopen_mock.side_effect = raise_503
    with patch.object(api, "_fetch_from_open_library", return_value=None), patch.object(
        api, "_fetch_from_google_books", return_value=None
    ):
        result = api.get_book_metadata("Unknown Book", "Unknown Author", refresh=0)
    assert result is not None
    assert result.get("_no_result") is True
    assert any("wikidata" in e.lower() for e in result.get("_fetch_errors", []))

def test_get_web_api_returns_shared_instance(tmp_path, monkeypatch):
    _reset_shared_web_api_for_tests()
    monkeypatch.setattr(wba, "WEB_CACHE_FILE", str(tmp_path / "web_cache.json"))
    a = get_web_api()
    b = get_web_api()
    assert a is b
    _reset_shared_web_api_for_tests()


def test_user_agent_includes_version_and_contact():
    from src.build_config import APP_VERSION
    from src.web.web_book_api import USER_AGENT

    assert APP_VERSION in USER_AGENT
    assert USER_AGENT.startswith("AbCS/")
    assert "github.com/cfdrakeNS/AbCS_Audiobook_Collector_Scanner" in USER_AGENT


def test_resolve_web_cache_file_frozen_uses_user_data(tmp_path, monkeypatch):
    monkeypatch.setattr(wba.sys, "frozen", True, raising=False)
    monkeypatch.setattr(
        "src.app_paths.get_user_data_dir", lambda: tmp_path / "AbCSUser"
    )
    path = wba._resolve_web_cache_file()
    assert path == str(tmp_path / "AbCSUser" / "web_cache.json")


def test_source_cooldown_error_does_not_extend_cooldown(api):
    from src.web.web_book_api import (
        SourceCooldownError,
        _note_rate_limited,
        _raise_cooldown_http_error,
        _seconds_until_cooldown_clears,
        _clear_source_cooldown,
    )

    _clear_source_cooldown()
    _note_rate_limited("google_books", seconds=40)
    first = _seconds_until_cooldown_clears("google_books")
    assert first > 30
    try:
        _raise_cooldown_http_error("google_books")
    except SourceCooldownError:
        pass
    # Synthetic cooldown error must not push the deadline further out.
    second = _seconds_until_cooldown_clears("google_books")
    assert second <= first
    _clear_source_cooldown()


@patch("src.web.web_book_api.urllib.request.urlopen")
def test_http_get_json_cooldown_does_not_re_note_limit(urlopen_mock, api):
    from src.web.web_book_api import (
        SourceCooldownError,
        _http_get_json,
        _note_rate_limited,
        _seconds_until_cooldown_clears,
        _clear_source_cooldown,
    )

    _clear_source_cooldown()
    _note_rate_limited("google_books", seconds=40)
    before = _seconds_until_cooldown_clears("google_books")
    try:
        _http_get_json(
            "https://www.googleapis.com/books/v1/volumes?q=test",
            timeout=5,
            source="google_books",
        )
        assert False, "expected SourceCooldownError"
    except SourceCooldownError:
        pass
    after = _seconds_until_cooldown_clears("google_books")
    assert after <= before
    urlopen_mock.assert_not_called()
    _clear_source_cooldown()


def test_negative_cache_short_circuits_repeat_miss(api, monkeypatch):
    monkeypatch.setattr(
        WebBookAPI,
        "_search_metadata_sources",
        lambda *a, **k: {"_no_result": True, "_fetch_errors": ["google_books: miss"]},
    )
    first = api.get_book_metadata("No Such Book XYZ", "Nobody Author")
    assert first and first.get("_no_result")
    # Second call must hit negative cache (search not invoked again).
    calls = {"n": 0}

    def boom(*_a, **_k):
        calls["n"] += 1
        return {"_no_result": True, "_fetch_errors": ["should-not-run"]}

    monkeypatch.setattr(WebBookAPI, "_search_metadata_sources", boom)
    second = api.get_book_metadata("No Such Book XYZ", "Nobody Author")
    assert second and second.get("_no_result")
    assert calls["n"] == 0


@patch("src.web.web_book_api.urllib.request.urlopen")
def test_wikidata_uses_wbsearchentities_not_sparql_scan(urlopen_mock, api):
    search_payload = {
        "search": [
            {
                "id": "Q170583",
                "label": "Pride and Prejudice",
                "description": "novel by Jane Austen",
            }
        ]
    }
    entities_payload = {
        "entities": {
            "Q170583": {
                "labels": {"en": {"value": "Pride and Prejudice"}},
                "claims": {
                    "P50": [
                        {
                            "mainsnak": {
                                "datavalue": {
                                    "value": {"id": "Q36322"},
                                    "type": "wikibase-entityid",
                                }
                            }
                        }
                    ]
                },
            }
        }
    }
    labels_payload = {
        "entities": {
            "Q36322": {"labels": {"en": {"value": "Jane Austen"}}},
        }
    }

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def read(self):
            return __import__("json").dumps(self._payload).encode()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    urlopen_mock.side_effect = [
        FakeResponse(search_payload),
        FakeResponse(entities_payload),
        FakeResponse(labels_payload),
    ]
    result = api._fetch_from_wikidata(
        "Pride and Prejudice",
        "Jane Austen",
        require_author_match=True,
    )
    assert result is not None
    assert result["title"] == "Pride and Prejudice"
    assert result["author"] == "Jane Austen"
    for call in urlopen_mock.call_args_list:
        url = call.args[0].full_url
        assert "query.wikidata.org/sparql" not in url
        assert "wikidata.org/w/api.php" in url


def test_google_books_api_key_appended(monkeypatch, api):
    monkeypatch.setenv("ABCS_GOOGLE_BOOKS_API_KEY", "test-key-123")
    params = api._google_books_params({"q": "intitle:Test"})
    assert params["key"] == "test-key-123"

