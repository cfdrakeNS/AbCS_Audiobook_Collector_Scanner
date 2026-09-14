"""Tests for web metadata title/author comparison helpers."""

from __future__ import annotations

from src.utils.text_utils import (
    fold_text,
    web_authors_match,
    web_compare_author_key,
    web_compare_title_key,
    web_titles_match,
)


def test_fold_text_strips_accents_and_rewrites_ampersand():
    assert fold_text("Émile Zola") == "Emile Zola"
    assert "and" in fold_text("Black & White").lower()


def test_web_titles_match_ignores_punctuation_and_filler():
    assert web_titles_match("Dr. No", "Dr No")
    assert web_titles_match("Gone Girl", "Gone Girl: A Novel")
    assert web_titles_match("The Hobbit", "Hobbit, The")
    assert web_titles_match("Triptych", "Triptych - 01")
    assert web_titles_match("Black & White", "Black and White")
    assert web_titles_match("Pride", "Pride (Unabridged)")


def test_web_titles_match_keeps_real_subtitle_difference():
    assert not web_titles_match("Gone Girl", "Gone Girl: A Novel of Suspense")
    assert web_compare_title_key("Gone Girl") != web_compare_title_key(
        "Gone Girl: A Novel of Suspense"
    )


def test_web_authors_match_punctuation_and_order():
    assert web_authors_match("J.R.R. Tolkien", "J R R Tolkien")
    assert web_authors_match("King, Stephen", "Stephen King")
    assert web_authors_match("F. Scott Fitzgerald", "F Scott Fitzgerald")
    assert web_compare_author_key("King, Stephen") == web_compare_author_key(
        "Stephen King"
    )


def test_web_authors_match_initials():
    assert web_authors_match("J.R.R. Tolkien", "John Ronald Reuel Tolkien")
    assert web_authors_match("J. Patterson", "James Patterson")


def test_web_authors_match_rejects_different_people():
    assert not web_authors_match("Stephen King", "Stephen Fry")
    assert not web_authors_match("James Patterson", "Richard Patterson")
