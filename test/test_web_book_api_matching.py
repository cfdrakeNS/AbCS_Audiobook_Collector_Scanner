"""Tests for WebBookAPI match gate and source lookup order."""

import json
from unittest.mock import patch

import pytest

from src.web.web_book_api import WebBookAPI


@pytest.fixture
def api():
    client = WebBookAPI()
    client._cache = {}
    return client


def test_metadata_matches_db_requires_title_and_author(api):
    meta = {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald"}
    assert api._metadata_matches_db("The Great Gatsby", "F. Scott Fitzgerald", meta)

    assert not api._metadata_matches_db(
        "The Great Gatsby", "F. Scott Fitzgerald", {"title": "", "author": "X"}
    )
    assert not api._metadata_matches_db(
        "The Great Gatsby",
        "F. Scott Fitzgerald",
        {"title": "The Great Gatsby", "author": "Stephen King"},
    )


def test_metadata_matches_db_rejects_title_only_bypass(api):
    """Results with plot/rating but wrong author must not pass when DB author is set."""
    meta = {
        "title": "The Great Gatsby",
        "author": "Stephen King",
        "plot": "Long description here.",
        "rating": 4.5,
        "genre": "Fiction",
    }
    assert not api._metadata_matches_db(
        "The Great Gatsby", "F. Scott Fitzgerald", meta
    )
    assert api._metadata_matches_db(
        "The Great Gatsby",
        "F. Scott Fitzgerald",
        meta,
        require_author_match=False,
    )


def test_strip_author_honorifics_for_search(api):
    assert api._strip_author_honorifics("Sir Arthur Conan Doyle") == "Arthur Conan Doyle"
    assert api._extract_last_name("Sir Arthur Conan Doyle") == "Doyle"


@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_open_library")
def test_sherlock_holmes_with_sir_author_finds_open_library(ol_mock, _gb_mock, _wd_mock, api):
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


def test_should_use_title_only_for_librivox_and_narrator(api):
    assert api._likely_librivox_source(path=r"C:\Audio\librivox\book")
    assert api._should_use_title_only_fallback(
        "Charles Dickens",
        narrator="Charles Dickens",
    )
    assert api._should_use_title_only_fallback(
        "Jane Reader",
        path=r"D:\LibriVox\pride_and_prejudice",
    )


@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_open_library")
def test_title_only_fallback_when_author_search_fails(ol_mock, _gb_mock, _wd_mock, api):
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



def test_metadata_matches_db_rejects_deaver_issue_cases(api):
    assert not api._metadata_matches_db(
        "Cause Of Death",
        "Jeffery Deaver",
        {"title": "Cause Of Death", "author": "Patricia Cornwell"},
    )
    assert not api._metadata_matches_db(
        "Date Night",
        "Jeffery Deaver",
        {"title": "Date Night Club", "author": "Saxon Bennett"},
    )


def test_metadata_matches_db_rejects_empty_db_author(api):
    meta = {"title": "Dune", "author": "Frank Herbert"}
    assert not api._metadata_matches_db("Dune", "", meta)
    assert not api._metadata_matches_db("Dune", "Frank Herbert", {"title": "Dune", "author": ""})


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
    with patch.object(api, "_get_open_library_description", return_value=""):
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




@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_open_library")
def test_pride_and_prejudice_jane_austen_via_broadened_search(
    ol_mock, _gb_mock, _wd_mock, api
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


@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_open_library", return_value=None)
def test_google_intitle_retry_finds_austen_when_inauthor_empty(gb_mock, _ol_mock, api):
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
    with patch.object(api, "_fetch_plot_from_open_library", return_value=""):
        with patch.object(api, "_fetch_plot_from_wikipedia", return_value=""):
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




def test_plot_is_adequate_threshold(api):
    assert not api._plot_is_adequate("short")
    assert api._plot_is_adequate("x" * 80)


def test_rejects_non_book_song_plot(api):
    song_plot = (
        '"Blue on Black" is a song by American blues rock group Kenny Wayne Shepherd Band. '
        "Written by Shepherd with Mark Selby and Tia Sillers, it was originally released on "
        "their second studio album, Trouble Is... (1997). In 1998, the song was released as a "
        "single and reached the top position on the US Billboard Mainstream Rock Tracks chart."
    )
    assert api._is_non_book_plot(song_plot)
    metadata = {"title": "Blue On Black", "author": "Michael Connelly"}
    assert not api._apply_plot_to_metadata(
        metadata,
        song_plot,
        "wikipedia",
        "Blue On Black",
        "Michael Connelly",
    )
    assert "plot" not in metadata or not metadata.get("plot")


def test_wikipedia_plot_requires_author_or_book_context(api):
    metadata = {"title": "Blue On Black", "author": "Michael Connelly"}
    unrelated = "A" * 120
    assert not api._apply_plot_to_metadata(
        metadata,
        unrelated,
        "wikipedia",
        "Blue On Black",
        "Michael Connelly",
    )
    metadata = {"title": "Blue On Black", "author": "Michael Connelly"}
    book_plot = (
        "Blue On Black is a novella by Michael Connelly featuring detective Harry Bosch "
        "in a case involving a mysterious death tied to a jazz club."
    )
    assert api._apply_plot_to_metadata(
        metadata,
        book_plot,
        "wikipedia",
        "Blue On Black",
        "Michael Connelly",
    )
    assert metadata["plot"] == book_plot


def test_strip_html_removes_tags(api):
    raw = "<p>Hello <b>world</b> &amp; friends</p>"
    assert "<" not in api._strip_html(raw)
    assert "Hello" in api._strip_html(raw)


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

def test_google_item_picker_rejects_wrong_author(api):
    items = [
        {
            "volumeInfo": {
                "title": "Dune",
                "authors": ["Stephen King"],
                "publishedDate": "1965",
            }
        },
        {
            "volumeInfo": {
                "title": "Dune",
                "authors": ["Frank Herbert"],
                "publishedDate": "1965",
            }
        },
    ]
    with patch.object(api, "_google_item_to_metadata", side_effect=lambda item: {
        "title": item["volumeInfo"]["title"],
        "author": ", ".join(item["volumeInfo"].get("authors", [])),
    }):
        best = None
        best_score = -1.0
        for item in items:
            candidate = api._google_item_to_metadata(item)
            if not api._metadata_matches_db("Dune", "Frank Herbert", candidate):
                continue
            score = api._title_word_match_score("Dune", candidate["title"])
            if score > best_score:
                best_score = score
                best = candidate
    assert best is not None
    assert "Herbert" in best["author"]


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


def test_discovered_isbn_used_for_google_series_enrichment(api):
    metadata = {
        "title": "The Way of Kings",
        "author": "Brandon Sanderson",
        "isbn": "9780765326355",
        "_resolved_source": "open_library",
    }
    with patch.object(api, "_get_open_library_work_fields", return_value={}):
        with patch.object(
            api,
            "_fetch_series_from_google_by_isbn",
            return_value={"series": "The Stormlight Archive", "series_number": "1"},
        ) as isbn_mock:
            with patch.object(api, "_fetch_series_from_google") as title_mock:
                with patch.object(api, "_fetch_series_from_wikidata", return_value=None):
                    api._enrich_metadata_series(
                        metadata, "The Way of Kings", "Brandon Sanderson"
                    )
    isbn_mock.assert_called_once_with("9780765326355")
    title_mock.assert_not_called()
    assert metadata["series"] == "The Stormlight Archive"


def test_series_enrichment_wikidata_before_google_title(api):
    metadata = {
        "title": "How the Light Gets In",
        "author": "Louise Penny",
        "_resolved_source": "open_library",
    }
    call_order: list[str] = []

    def wikidata_side_effect(*args, **kwargs):
        call_order.append("wikidata")
        return {"series": "Chief Inspector Gamache", "series_number": "9"}

    def google_side_effect(*args, **kwargs):
        call_order.append("google_title")
        return None

    with patch.object(api, "_get_open_library_work_fields", return_value={}):
        with patch.object(
            api, "_fetch_series_from_wikidata", side_effect=wikidata_side_effect
        ):
            with patch.object(
                api, "_fetch_series_from_google", side_effect=google_side_effect
            ):
                with patch.object(api, "_fetch_series_from_google_by_isbn", return_value=None):
                    api._enrich_metadata_series(
                        metadata, "How the Light Gets In", "Louise Penny"
                    )
    assert call_order == ["wikidata"]
    assert metadata["series"] == "Chief Inspector Gamache"


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


def test_cache_key_includes_isbn_param(api):
    with patch.object(api, "_fetch_metadata_by_isbn") as isbn_fetch:
        isbn_fetch.return_value = {
            "title": "Dune",
            "author": "Frank Herbert",
            "_resolved_source": "open_library",
        }
        with patch.object(api, "_enrich_metadata_plot"):
            with patch.object(api, "_fill_series_fields"):
                with patch.object(api, "_save_persistent_cache"):
                    api.get_book_metadata(
                        "Dune", "Frank Herbert", isbn="9780441172719"
                    )
    assert any("9780441172719" in key for key in api._cache)


@patch("src.web.web_book_api.urllib.request.urlopen")
def test_open_library_search_stores_discovered_isbn(urlopen_mock, api):
    """OL search docs with isbn field should be kept for in-flight enrichment."""
    doc = {
        "title": "The Way of Kings",
        "author_name": ["Brandon Sanderson"],
        "first_publish_year": 2010,
        "key": "/works/OL123W",
        "isbn": ["9780765326355"],
    }

    class FakeResponse:
        def read(self):
            return json.dumps({"docs": [doc]}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    urlopen_mock.return_value = FakeResponse()
    with patch.object(api, "_get_open_library_work_fields", return_value={}):
        result = api._fetch_from_open_library(
            "The Way of Kings", "Brandon Sanderson"
        )
    assert result is not None
    assert result.get("isbn") == "9780765326355"


def test_google_isbn_lookup_returns_series_info(api):
    item = {
        "volumeInfo": {
            "title": "The Way of Kings",
            "authors": ["Brandon Sanderson"],
            "seriesInfo": {
                "bookDisplayNumber": "1",
                "volumeSeries": [{"seriesTitle": "The Stormlight Archive"}],
            },
        }
    }

    class FakeResponse:
        def read(self):
            return json.dumps({"items": [item]}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    with patch("urllib.request.urlopen", return_value=FakeResponse()):
        result = api._fetch_google_by_isbn("9780765326355")
    assert result is not None
    assert result["series"] == "The Stormlight Archive"
    assert result["series_number"] == "1"


def test_dedupe_fetch_errors_keeps_one_per_source():
    from src.web.web_book_api import _dedupe_fetch_errors

    errors = [
        "google_books: HTTP Error 429: Too Many Requests",
        "google_books: HTTP Error 429: Too Many Requests",
        "open_library: timed out",
    ]
    assert _dedupe_fetch_errors(errors) == [
        "google_books: HTTP Error 429: Too Many Requests",
        "open_library: timed out",
    ]


def test_format_web_fetch_status_message_rate_limit():
    from src.web.web_book_api import format_web_fetch_status_message

    msg = format_web_fetch_status_message(
        ["google_books: HTTP Error 429: Too Many Requests"]
    )
    assert "rate limited" in msg.lower()
    assert "re-fetch" in msg.lower()


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
    assert sent_request.get_header("User-agent") == "AbCS-Audiobook-Collector/1.0"
