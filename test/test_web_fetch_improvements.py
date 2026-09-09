"""Tests for web fetch budget, cancel, cache, Retry-After, and service."""

import json
import os
import time
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from src.web import web_book_api as wba
from src.web.web_book_api import (
    FetchBudget,
    WebBookAPI,
    _clear_source_cooldown,
    _http_get_json,
    _note_rate_limited,
    _reset_shared_web_api_for_tests,
    _seconds_until_cooldown_clears,
    get_web_api,
)
from src.web.web_fetch_service import fetch_web_metadata_for_book


@pytest.fixture
def api(tmp_path, monkeypatch):
    _clear_source_cooldown()
    _reset_shared_web_api_for_tests()
    monkeypatch.setattr(wba, "WEB_CACHE_FILE", str(tmp_path / "web_cache.json"))
    client = WebBookAPI()
    yield client
    _clear_source_cooldown()
    _reset_shared_web_api_for_tests()


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_extract_year_returns_empty_when_no_year(api):
    assert api._extract_year("unknown") == ""
    assert api._extract_year("2020-01-01") == "2020"
    assert api._extract_year("") == ""


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


def test_retry_after_sets_cooldown_from_header():
    _clear_source_cooldown()

    class Headers(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    headers = Headers({"Retry-After": "12"})
    _note_rate_limited("google_books", headers=headers)
    remaining = _seconds_until_cooldown_clears("google_books")
    assert 10 <= remaining <= 12
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


def test_fetch_service_canceled(qapp, api, monkeypatch):
    class Book:
        title = "Test"
        author_name = "Author"
        year = None
        reader = ""
        path = ""
        source = ""
        comments = ""

    def fake_get(*_a, **_k):
        return {"_canceled": True}

    monkeypatch.setattr("src.web.web_fetch_service.get_web_api", lambda: api)
    monkeypatch.setattr(api, "get_book_metadata", fake_get)
    result = fetch_web_metadata_for_book(Book(), show_progress=False)
    assert result.canceled
    assert "canceled" in result.status_message.lower()


def test_fetch_service_cleans_success(qapp, api, monkeypatch):
    class Book:
        title = "Pride and Prejudice"
        author_name = "Jane Austen"
        year = None
        reader = ""
        path = ""
        source = ""
        comments = ""

    raw = {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "plot": "A" * 100,
        "source": "open_library",
    }

    monkeypatch.setattr("src.web.web_fetch_service.get_web_api", lambda: api)
    monkeypatch.setattr(api, "get_book_metadata", lambda *a, **k: raw)
    result = fetch_web_metadata_for_book(Book(), show_progress=False)
    assert result.has_usable_data
    assert result.cleaned_data["title"] == "Pride and Prejudice"
