"""Unit and enrichment tests for web metadata series and ISBN handling."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from src.web.web_book_api import WebBookAPI


@pytest.fixture
def api(web_api):
    return web_api


def test_parse_open_library_series_string_with_hash(api):
    name, num = api._parse_open_library_series_string("Inspector Gamache #9")
    assert name == "Inspector Gamache"
    assert num == "9"

def test_parse_open_library_series_string_plain(api):
    name, num = api._parse_open_library_series_string("Oxford World's Classics")
    assert name == "Oxford World's Classics"
    assert num == ""

def test_apply_series_to_metadata_does_not_overwrite(api):
    metadata = {"series": "Existing Saga", "series_number": "1"}
    api._apply_series_to_metadata(metadata, "New Saga", "2")
    assert metadata["series"] == "Existing Saga"
    assert metadata["series_number"] == "1"

def test_apply_series_to_metadata_fills_empty(api):
    metadata = {"title": "A Book", "plot": "Long enough plot text here for testing."}
    api._apply_series_to_metadata(metadata, "Test Series", "3")
    assert metadata["series"] == "Test Series"
    assert metadata["series_number"] == "3"

def test_extract_google_series_from_series_info(api):
    volume_info = {
        "seriesInfo": {
            "bookDisplayNumber": "4",
            "volumeSeries": [{"seriesTitle": "Chief Inspector Gamache"}],
        },
        "subtitle": "",
        "description": "",
    }
    series, number = api._extract_google_series(volume_info)
    assert series == "Chief Inspector Gamache"
    assert number == "4"

def test_extract_google_series_from_subtitle_book_of(api):
    volume_info = {
        "subtitle": "(Book 3 of The Expanse)",
        "description": "",
    }
    series, number = api._extract_google_series(volume_info)
    assert series == "The Expanse"
    assert number == "3"

def test_get_open_library_work_fields_parses_series(api):
    work_json = {
        "description": {"value": "A mystery in Quebec."},
        "series": ["How the Light Gets In #9"],
    }
    mock_resp = MagicMock()
    mock_resp.read.return_value = __import__("json").dumps(work_json).encode()

    with patch("urllib.request.urlopen", return_value=MagicMock(__enter__=lambda s: mock_resp, __exit__=lambda *a: None)):
        fields = api._get_open_library_work_fields("/works/OL123W")

    assert "Quebec" in fields["description"]
    assert fields["series"] == "How the Light Gets In"
    assert fields["series_number"] == "9"

def test_wikidata_metadata_includes_series_from_bindings(api):
    sparql_payload = {
        "results": {
            "bindings": [
                {
                    "bookLabel": {"value": "How the Light Gets In"},
                    "authorLabel": {"value": "Louise Penny"},
                    "seriesLabel": {"value": "Chief Inspector Armand Gamache"},
                    "seriesOrdinal": {"value": "9"},
                }
            ]
        }
    }
    with patch(
        "src.web.web_book_api._http_get_json", return_value=sparql_payload
    ):
        result = api._fetch_from_wikidata(
            "How the Light Gets In", "Louise Penny"
        )
    assert result is not None
    assert result["series"] == "Chief Inspector Armand Gamache"
    assert result["series_number"] == "9"

def test_enrich_metadata_series_uses_open_library_work_key(api):
    metadata = {
        "title": "A Great Mystery",
        "author": "Louise Penny",
        "open_library_work_key": "/works/OL999W",
        "_resolved_source": "open_library",
    }
    with patch.object(
        api,
        "_get_open_library_work_fields",
        return_value={
            "description": "",
            "series": "Inspector Gamache",
            "series_number": "9",
        },
    ):
        with patch.object(api, "_fetch_series_from_google", return_value=None):
            with patch.object(api, "_fetch_series_from_wikidata", return_value=None):
                api._enrich_metadata_series(metadata, "A Great Mystery", "Louise Penny")

    assert metadata["series"] == "Inspector Gamache"
    assert metadata["series_number"] == "9"

def test_strip_series_number_rejects_year_suffix(api):
    clean, number = api._strip_series_number("The Great War - 1914")
    assert clean == "The Great War - 1914"
    assert number == ""

def test_strip_series_number_handles_zero_padded_suffix(api):
    clean, number = api._strip_series_number("The Moon - 02")
    assert clean == "The Moon"
    assert number == "02"

def test_strip_series_number_handles_decimal_suffix(api):
    clean, number = api._strip_series_number("Busted - 6.5")
    assert clean == "Busted"
    assert number == "6.5"

def test_seed_series_from_db_title_preserves_decimal(api):
    metadata = {
        "title": "Busted - 6.5",
        "author": "Lee Child",
        "plot": "A Jack Reacher story with enough plot text for testing.",
        "series": "Jack Reacher",
    }
    assert api._seed_series_from_db_title(metadata, "6.5", "Lee Child")
    assert metadata["series_number"] == "6.5"

def test_seed_series_from_db_title_skips_orphan_number(api):
    metadata = {
        "title": "Murder Mystery - 2",
        "author": "Jane Author",
        "plot": "A standalone mystery with enough plot text for testing.",
    }
    changed = api._seed_series_from_db_title(metadata, "2", "Jane Author")
    assert not changed
    assert metadata.get("series") is None
    assert metadata.get("series_number") is None

def test_seed_series_from_db_title_lee_child_blue_moon(api):
    metadata = {
        "title": "Blue Moon - 24",
        "author": "Lee Child",
        "plot": "Reacher helps an elderly couple.",
    }
    assert api._seed_series_from_db_title(metadata, "24", "Lee Child")
    assert metadata["series"] == "Jack Reacher"
    assert metadata["series_number"] == "24"

def test_fill_series_fields_announces_only_when_found(api):
    metadata = {"title": "Blue Moon", "author": "Lee Child", "plot": "Short plot."}
    messages: list[str] = []

    api._fill_series_fields(
        metadata,
        "Blue Moon",
        "Lee Child",
        "24",
        report_progress=messages.append,
    )

    assert metadata["series"] == "Jack Reacher"
    assert metadata["series_number"] == "24"
    assert len(messages) == 1
    assert messages[0].startswith("Series found:")

def test_enrich_metadata_series_skips_google_when_series_present(api):
    metadata = {
        "title": "Book",
        "series": "Already Set",
        "series_number": "2",
        "_resolved_source": "google_books",
    }
    with patch.object(api, "_fetch_series_from_google") as mock_google:
        api._enrich_metadata_series(metadata, "Book", "Author")
    mock_google.assert_not_called()


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

