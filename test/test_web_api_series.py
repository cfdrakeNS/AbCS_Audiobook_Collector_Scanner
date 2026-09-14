"""Assert web fetch no longer emits or enriches series fields."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from src.web.web_book_api import WebBookAPI, clean_web_data


@pytest.fixture
def api(web_api):
    return web_api


def test_google_item_to_metadata_omits_series(api):
    item = {
        "volumeInfo": {
            "title": "How the Light Gets In",
            "authors": ["Louise Penny"],
            "publishedDate": "2013",
            "description": "A Gamache mystery.",
            "seriesInfo": {
                "bookDisplayNumber": "9",
                "volumeSeries": [{"seriesTitle": "Chief Inspector Gamache"}],
            },
        }
    }
    meta = api._google_item_to_metadata(item)
    assert meta is not None
    assert "series" not in meta
    assert "series_number" not in meta


def test_get_open_library_work_fields_description_only(api):
    work_json = {
        "description": {"value": "A mystery in Quebec."},
        "series": ["How the Light Gets In #9"],
    }
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(work_json).encode()

    with patch(
        "urllib.request.urlopen",
        return_value=MagicMock(
            __enter__=lambda s: mock_resp, __exit__=lambda *a: None
        ),
    ):
        fields = api._get_open_library_work_fields("/works/OL123W")

    assert "Quebec" in fields["description"]
    assert "series" not in fields
    assert "series_number" not in fields


def test_wikidata_metadata_omits_series(api):
    search_payload = {
        "search": [
            {
                "id": "Q123",
                "label": "How the Light Gets In",
                "description": "novel by Louise Penny",
            }
        ]
    }
    entities_payload = {
        "entities": {
            "Q123": {
                "labels": {"en": {"value": "How the Light Gets In"}},
                "claims": {
                    "P50": [
                        {
                            "mainsnak": {
                                "datavalue": {
                                    "value": {"id": "Q999"},
                                }
                            }
                        }
                    ],
                    "P179": [
                        {
                            "mainsnak": {
                                "datavalue": {
                                    "value": {"id": "Q888"},
                                }
                            }
                        }
                    ],
                    "P1545": [
                        {
                            "mainsnak": {
                                "datavalue": {"value": "9"},
                            }
                        }
                    ],
                },
            }
        }
    }
    labels_payload = {
        "entities": {
            "Q999": {"labels": {"en": {"value": "Louise Penny"}}},
            "Q888": {"labels": {"en": {"value": "Chief Inspector Gamache"}}},
        }
    }

    responses = [search_payload, entities_payload, labels_payload]
    call_idx = {"n": 0}

    def fake_http_get_json(url, **kwargs):
        i = call_idx["n"]
        call_idx["n"] += 1
        return responses[min(i, len(responses) - 1)]

    with patch("src.web.web_book_api._http_get_json", side_effect=fake_http_get_json):
        meta = api._fetch_from_wikidata(
            "How the Light Gets In",
            "Louise Penny",
            require_author_match=True,
        )

    assert meta is not None
    assert meta["title"] == "How the Light Gets In"
    assert "series" not in meta
    assert "series_number" not in meta


def test_clean_web_data_strips_legacy_series_keys(api):
    cleaned = clean_web_data(
        {
            "title": "A Book",
            "author": "An Author",
            "series": "Legacy Saga",
            "series_number": "3",
            "plot": "A long enough plot description for storage.",
        }
    )
    assert "series" not in cleaned
    assert "series_number" not in cleaned


def test_no_series_enrichment_methods_on_api(api):
    for name in (
        "_fill_series_fields",
        "_enrich_metadata_series",
        "_extract_google_series",
        "_fetch_series_from_google",
        "_parse_open_library_series_string",
    ):
        assert not hasattr(api, name)
