"""Phase 11: collection library root checks and CRUD."""

from __future__ import annotations

from src.core.library_root import (
    folder_exists,
    folder_has_supported_audio,
    root_path_issue,
)
from src.database.connection import DatabaseManager
from src.database.models import Collection
from src.database.queries import CollectionQueries


def test_root_path_issue_blank_and_missing(tmp_path):
    assert root_path_issue("") == ""
    assert root_path_issue("   ") == ""
    assert folder_exists("") is False
    missing = tmp_path / "not_here"
    assert folder_exists(str(missing)) is False
    assert root_path_issue(str(missing)) == "missing"


def test_root_path_issue_empty_and_supported_audio(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    (empty / "notes.txt").write_text("no audio", encoding="utf-8")
    nested = empty / "author" / "title"
    nested.mkdir(parents=True)
    assert folder_has_supported_audio(str(empty)) is False
    assert root_path_issue(str(empty)) == "empty"

    good = tmp_path / "library"
    book_dir = good / "Author" / "Title"
    book_dir.mkdir(parents=True)
    (book_dir / "chapter.mp3").write_bytes(b"x")
    assert folder_exists(str(good)) is True
    assert folder_has_supported_audio(str(good)) is True
    assert root_path_issue(str(good)) == ""


def test_collection_root_path_crud(tmp_path):
    db = DatabaseManager(str(tmp_path / "abcs.db"))
    db.initialize_database()
    queries = CollectionQueries(db)

    cid = queries.insert(
        Collection(name="Root CRUD Unique", active=True, root_path=r"F:\audiobook")
    )
    loaded = queries.get_by_id(cid)
    assert loaded is not None
    assert loaded.root_path == r"F:\audiobook"

    loaded.root_path = r"D:\other"
    queries.update(loaded)
    changed = queries.get_by_id(cid)
    assert changed is not None
    assert changed.root_path == r"D:\other"

    changed.root_path = ""
    queries.update(changed)
    cleared = queries.get_by_id(cid)
    assert cleared is not None
    assert cleared.root_path == ""

    db.close()
