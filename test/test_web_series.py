"""Unit tests for web metadata series extraction and enrichment."""

from unittest.mock import MagicMock, patch

import pytest

from src.web.web_book_api import WebBookAPI


@pytest.fixture
def api():
    return WebBookAPI()


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
    bindings = [
        {
            "bookLabel": {"value": "How the Light Gets In"},
            "authorLabel": {"value": "Louise Penny"},
            "seriesLabel": {"value": "Chief Inspector Armand Gamache"},
            "seriesOrdinal": {"value": "9"},
        }
    ]
    result = bindings[0]
    series_label = api._get_sparql_value(result, "seriesLabel")
    series_ordinal = api._get_sparql_value(result, "seriesOrdinal")
    metadata = {
        "title": api._get_sparql_value(result, "bookLabel"),
        "author": api._get_sparql_value(result, "authorLabel"),
        "series": series_label,
        "series_number": series_ordinal,
    }
    assert metadata["series"] == "Chief Inspector Armand Gamache"
    assert metadata["series_number"] == "9"


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
