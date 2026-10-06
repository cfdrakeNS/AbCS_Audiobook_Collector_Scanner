"""Phase 11: collection library root checks and CRUD."""

from __future__ import annotations

from pathlib import Path

from src.core.library_root import (
    IMPORT_DEFAULT_DIRECTORY_KEY,
    apply_collection_root,
    author_folder_in_collection,
    browse_start_directory,
    folder_exists,
    folder_has_supported_audio,
    path_exists,
    path_is_under_root,
    resolve_book_location,
    root_path_issue,
    sync_single_collection_import_path,
)
from src.database.connection import DatabaseManager
from src.database.models import Collection
from src.database.queries import CollectionQueries


def test_path_exists_treats_permission_error_as_missing(monkeypatch):
    from src.core import library_root

    class _RaisingPath:
        def exists(self):
            raise PermissionError(13, "Permission denied")

    monkeypatch.setattr(library_root, "Path", lambda _p: _RaisingPath())
    assert path_exists("/media/sf_test/Author/Title") is False


def test_resolve_book_location_survives_permission_error_on_stored_path(monkeypatch):
    from src.core import library_root

    stored = "/media/sf_test/Lewis Carroll/Alice in Wonderland"

    class _RaisingPath:
        def exists(self):
            raise PermissionError(13, "Permission denied")

    monkeypatch.setattr(library_root, "Path", lambda _p: _RaisingPath())
    result = resolve_book_location(stored, "", "")
    assert result == stored


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


def test_author_folder_in_collection(tmp_path):
    root = tmp_path / "library"
    author = root / "Lee Child"
    author.mkdir(parents=True)
    assert author_folder_in_collection(str(root), "Lee Child") == str(author)
    assert author_folder_in_collection(str(root), "lee child") == str(author)
    assert author_folder_in_collection(str(root), "Nobody") == ""
    assert author_folder_in_collection("", "Lee Child") == ""


def test_browse_start_directory_order(tmp_path):
    book_dir = tmp_path / "Author" / "Title"
    book_dir.mkdir(parents=True)
    file_path = book_dir / "chapter.mp3"
    file_path.write_bytes(b"x")
    root = tmp_path / "library_root"
    root.mkdir()
    prefs = tmp_path / "prefs_import"
    prefs.mkdir()

    assert browse_start_directory(str(book_dir), str(root), str(prefs)) == str(
        book_dir
    )
    assert browse_start_directory(str(file_path), str(root), str(prefs)) == str(
        book_dir
    )

    missing = tmp_path / "gone" / "book"
    assert browse_start_directory(str(missing), str(root), str(prefs)) == str(root)
    assert browse_start_directory(str(missing), "", str(prefs)) == str(prefs)
    assert browse_start_directory(str(missing), "", "") == ""


def test_browse_start_directory_uses_play_remap(tmp_path):
    stored = tmp_path / "old_drive" / "lib" / "Author" / "Title"
    collection = tmp_path / "collection" / "lib"
    remapped = collection / "Author" / "Title"
    remapped.mkdir(parents=True)
    (remapped / "01.mp3").write_bytes(b"x")
    assert browse_start_directory(str(stored), str(collection), "") == str(remapped)

    import_root = tmp_path / "import" / "lib"
    imp_book = import_root / "Author" / "Title"
    imp_book.mkdir(parents=True)
    (imp_book / "01.mp3").write_bytes(b"x")
    # Collection folder empty of this book name path — use import remap
    empty_collection = tmp_path / "empty_collection" / "lib"
    empty_collection.mkdir(parents=True)
    assert browse_start_directory(
        str(stored), str(empty_collection), str(import_root)
    ) == str(imp_book)

def test_path_is_under_root(tmp_path):
    root = tmp_path / "root"
    child = root / "Author" / "Title"
    child.mkdir(parents=True)
    other = tmp_path / "elsewhere"
    other.mkdir()
    assert path_is_under_root(str(child), str(root)) is True
    assert path_is_under_root(str(other), str(root)) is False
    assert path_is_under_root("", str(root)) is False
    assert path_is_under_root(str(child), "") is False


def test_resolve_book_location_fallback_order(tmp_path):
    stored = tmp_path / "old_drive" / "lib" / "Author" / "Title"
    collection = tmp_path / "collection" / "lib"
    import_root = tmp_path / "import" / "lib"
    missing = resolve_book_location(str(stored), str(collection), str(import_root))
    assert missing == str(collection / "Author" / "Title")
    assert Path(missing).exists() is False

    imp_book = import_root / "Author" / "Title"
    imp_book.mkdir(parents=True)
    (imp_book / "a.mp3").write_bytes(b"x")
    assert resolve_book_location(str(stored), str(collection), str(import_root)) == str(
        imp_book
    )

    coll_book = collection / "Author" / "Title"
    coll_book.mkdir(parents=True)
    (coll_book / "c.mp3").write_bytes(b"x")
    assert resolve_book_location(str(stored), str(collection), str(import_root)) == str(
        coll_book
    )

    stored.mkdir(parents=True)
    (stored / "s.mp3").write_bytes(b"x")
    assert resolve_book_location(str(stored), str(collection), str(import_root)) == str(
        stored
    )


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


def test_apply_collection_root_windows_stored_path_on_any_os(tmp_path):
    root = tmp_path / "Lib"
    stored = r"F:\testing books\Lib\Michael R. Stern\Sand Storm"
    assert apply_collection_root(stored, str(root)) == str(
        root / "Michael R. Stern" / "Sand Storm"
    )

    other = tmp_path / "Portable"
    book = other / "Author" / "Title"
    book.mkdir(parents=True)
    assert apply_collection_root(r"F:\Old\Author\Title", str(other)) == str(book)


def test_apply_collection_root_ignores_case(tmp_path):
    book = tmp_path / "Lib" / "Michael R. Stern" / "Sand Storm"
    book.mkdir(parents=True)
    for stored in (
        r"F:\lib\MICHAEL R. STERN\sand storm",
        r"F:\Old\michael r. stern\SAND STORM",
    ):
        remapped = apply_collection_root(stored, str(tmp_path / "Lib"))
        assert remapped.casefold() == str(book).casefold()
        assert Path(remapped).is_dir()


def test_apply_collection_root_blank_root_keeps_stored(tmp_path):
    stored = tmp_path / "old" / "Author" / "Title"
    assert apply_collection_root(str(stored), "") == str(stored)
    assert apply_collection_root("", str(tmp_path)) == ""
