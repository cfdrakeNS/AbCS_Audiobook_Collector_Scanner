"""Tests for name consistency clustering and author/genre merge."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.core.name_consistency import (
    find_similar_author_groups,
    find_similar_genre_groups,
)
from src.database.models import Book
from src.database.queries import AuthorQueries, BookQueries, GenreQueries


def test_find_similar_author_groups_clusters_near_spellings():
    authors = [
        SimpleNamespace(author_id=1, name="John Connelly"),
        SimpleNamespace(author_id=2, name="John Connely"),
        SimpleNamespace(author_id=3, name="Someone Else"),
    ]
    groups = find_similar_author_groups(
        authors, threshold=0.85, book_counts={1: 5, 2: 1, 3: 2}
    )
    assert len(groups) == 1
    ids = {item[0] for item in groups[0].items}
    assert ids == {1, 2}
    assert groups[0].suggested_id == 1
    assert groups[0].suggested_name == "John Connelly"


def test_find_similar_genre_groups_clusters_near_spellings():
    genres = [
        SimpleNamespace(genre_id=10, name="Mystery"),
        SimpleNamespace(genre_id=11, name="Mystrey"),
        SimpleNamespace(genre_id=12, name="Sci-Fi"),
    ]
    groups = find_similar_genre_groups(
        genres, threshold=0.8, book_counts={10: 3, 11: 1, 12: 4}
    )
    assert len(groups) == 1
    ids = {item[0] for item in groups[0].items}
    assert ids == {10, 11}
    assert groups[0].suggested_id == 10


@pytest.mark.skip(reason="Author/genre merge ships in version 3 Phase 8")
def test_author_merge_reassigns_books_and_deletes_source(temp_db):
    authors = AuthorQueries(temp_db)
    books = BookQueries(temp_db)
    source = authors.insert("Merge Source")
    target = authors.insert("Merge Target")
    books.insert(
        Book(
            title="Merge Book",
            author_id=source,
            year=2020,
            tracks=1,
            path="/tmp/merge",
        )
    )
    updated = authors.merge(source, target)
    assert updated == 1
    assert authors.get_by_id(source) is None
    remaining = books.get_all()
    assert any(b.author_id == target and b.title == "Merge Book" for b in remaining)


@pytest.mark.skip(reason="Author/genre merge ships in version 3 Phase 8")
def test_genre_merge_reassigns_books_and_deletes_source(temp_db):
    authors = AuthorQueries(temp_db)
    genres = GenreQueries(temp_db)
    books = BookQueries(temp_db)
    author_id = authors.insert("Genre Merge Author")
    source = genres.insert("Merge Genre Source")
    target = genres.insert("Merge Genre Target")
    books.insert(
        Book(
            title="Genre Merge Book",
            author_id=author_id,
            genre_id=source,
            year=2021,
            tracks=1,
            path="/tmp/genre-merge",
        )
    )
    updated = genres.merge(source, target)
    assert updated == 1
    assert genres.get_by_id(source) is None
    remaining = books.get_all()
    assert any(b.genre_id == target and b.title == "Genre Merge Book" for b in remaining)
