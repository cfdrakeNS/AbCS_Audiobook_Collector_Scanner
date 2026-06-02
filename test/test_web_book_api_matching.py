"""Tests for WebBookAPI match gate and source lookup order."""

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


def test_metadata_matches_db_rejects_empty_db_author(api):
    meta = {"title": "Dune", "author": "Frank Herbert"}
    assert not api._metadata_matches_db("Dune", "", meta)
    assert not api._metadata_matches_db("Dune", "Frank Herbert", {"title": "Dune", "author": ""})


@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books")
@patch.object(WebBookAPI, "_fetch_from_open_library")
def test_refresh_zero_open_library_before_google(ol_mock, gb_mock, _wd_mock, api):
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


@patch.object(WebBookAPI, "_fetch_from_wikidata", return_value=None)
@patch.object(WebBookAPI, "_fetch_from_google_books")
@patch.object(WebBookAPI, "_fetch_from_open_library", return_value=None)
def test_refresh_zero_google_when_open_library_fails(ol_mock, gb_mock, _wd_mock, api):
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


@patch.object(WebBookAPI, "_fetch_from_wikidata")
@patch.object(WebBookAPI, "_fetch_from_google_books")
@patch.object(WebBookAPI, "_fetch_from_open_library")
def test_refresh_one_skips_open_library(ol_mock, gb_mock, wd_mock, api):
    gb_mock.return_value = {
        "title": "Dune",
        "author": "Frank Herbert",
    }
    wd_mock.return_value = None
    result = api.get_book_metadata("Dune", "Frank Herbert", refresh=1)
    assert result is not None
    ol_mock.assert_not_called()
    gb_mock.assert_called_once()


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
