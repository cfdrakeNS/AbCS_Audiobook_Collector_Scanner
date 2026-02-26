"""Regression tests for chunked bulk book operations in BookQueries."""

from __future__ import annotations

from database.queries import BookQueries


class _FakeConnection:
    def __init__(self):
        self.commit_calls = 0

    def commit(self):
        self.commit_calls += 1


class _FakeDb:
    def __init__(self):
        self.calls = []
        self._conn = _FakeConnection()

    def execute(self, query, params=None):
        self.calls.append(
            (query, tuple(params) if params is not None else None))

    def connect(self):
        return self._conn


def test_delete_many_chunks_large_id_list():
    db = _FakeDb()
    queries = BookQueries(db)
    book_ids = list(range(1, 2501))

    queries.delete_many(book_ids)

    assert len(db.calls) == 3
    assert db._conn.commit_calls == 1

    chunk_sizes = [len(params) for _query, params in db.calls]
    assert chunk_sizes == [900, 900, 700]


def test_bulk_update_genre_chunks_and_includes_target_param():
    db = _FakeDb()
    queries = BookQueries(db)
    book_ids = list(range(1, 2501))

    queries.bulk_update_genre(book_ids, genre_id=12)

    assert len(db.calls) == 3
    assert db._conn.commit_calls == 1

    # params = [genre_id] + chunk_ids
    param_lengths = [len(params) for _query, params in db.calls]
    assert param_lengths == [901, 901, 701]

    for _query, params in db.calls:
        assert params[0] == 12
