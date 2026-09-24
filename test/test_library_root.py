"""Phase 11: collection library root checks and CRUD."""

from __future__ import annotations

from src.core.library_root import (
    IMPORT_DEFAULT_DIRECTORY_KEY,
    apply_collection_root,
    folder_exists,
    folder_has_supported_audio,
    root_path_issue,
    sync_single_collection_import_path,
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


def test_apply_collection_root_keeps_author_title_under_new_root(tmp_path):
    stored = tmp_path / "old_drive" / "import" / "Jeffery Deaver" / "A Maiden's Grave"
    new_root = tmp_path / "portable" / "import"
    remapped = apply_collection_root(str(stored), str(new_root))
    assert remapped == str(new_root / "Jeffery Deaver" / "A Maiden's Grave")


class _FakeSettings:
    def __init__(self, values=None):
        self._values = dict(values or {})

    def value(self, key, default="", type=str):
        return self._values.get(key, default)

    def setValue(self, key, value):
        self._values[key] = value


def test_sync_single_collection_fills_empty_root_from_prefs(tmp_path):
    db = DatabaseManager(str(tmp_path / "abcs.db"))
    db.initialize_database()
    queries = CollectionQueries(db)
    collections = queries.get_all(active_only=False)
    assert len(collections) == 1
    assert collections[0].root_path == ""
    prefs = tmp_path / "import_lib"
    settings = _FakeSettings({IMPORT_DEFAULT_DIRECTORY_KEY: str(prefs)})
    assert sync_single_collection_import_path(queries, settings) == "collection"
    loaded = queries.get_by_id(collections[0].collection_id)
    assert loaded is not None
    assert loaded.root_path == str(prefs)
    db.close()


def test_sync_single_collection_fills_empty_prefs_from_root(tmp_path):
    db = DatabaseManager(str(tmp_path / "abcs.db"))
    db.initialize_database()
    queries = CollectionQueries(db)
    collections = queries.get_all(active_only=False)
    root = tmp_path / "collection_lib"
    collections[0].root_path = str(root)
    queries.update(collections[0])
    settings = _FakeSettings({IMPORT_DEFAULT_DIRECTORY_KEY: ""})
    assert sync_single_collection_import_path(queries, settings) == "prefs"
    assert settings.value(IMPORT_DEFAULT_DIRECTORY_KEY) == str(root)
    db.close()


def test_sync_single_collection_skips_when_two_collections(tmp_path):
    db = DatabaseManager(str(tmp_path / "abcs.db"))
    db.initialize_database()
    queries = CollectionQueries(db)
    queries.insert(Collection(name="Second Sync Unique", active=True, root_path=""))
    prefs = tmp_path / "import_lib"
    settings = _FakeSettings({IMPORT_DEFAULT_DIRECTORY_KEY: str(prefs)})
    assert sync_single_collection_import_path(queries, settings) == ""
    for collection in queries.get_all(active_only=False):
        assert collection.root_path == ""
    db.close()


def test_apply_collection_root_blank_root_keeps_stored(tmp_path):
    stored = tmp_path / "old" / "Author" / "Title"
    assert apply_collection_root(str(stored), "") == str(stored)
    assert apply_collection_root("", str(tmp_path)) == ""
