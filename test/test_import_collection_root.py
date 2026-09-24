"""Phase 11: Import pre-fills folder from collection root_path."""

from __future__ import annotations

from src.database.connection import DatabaseManager
from src.database.models import Collection
from src.database.queries import CollectionQueries
from src.ui.import_window import ImportWindow


def test_import_prefills_existing_collection_root(
    tmp_path, ui_scaler, theme_manager, qtbot
):
    prefs_dir = tmp_path / "prefs_default"
    prefs_dir.mkdir()
    root = tmp_path / "library"
    root.mkdir()
    (root / "book.mp3").write_bytes(b"x")

    db = DatabaseManager(str(tmp_path / "abcs.db"))
    db.initialize_database()
    queries = CollectionQueries(db)
    cid = queries.insert(
        Collection(name="Import Root Unique", active=True, root_path=str(root))
    )

    window = ImportWindow(db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    idx = window.collection_combo.findData(cid)
    assert idx >= 0
    window.collection_combo.setCurrentIndex(idx)
    assert window.folder_edit.text() == str(root)
    window.close()
    db.close()


def test_import_does_not_prefill_missing_collection_root(
    tmp_path, ui_scaler, theme_manager, qtbot, monkeypatch
):
    prefs_dir = tmp_path / "prefs_default"
    prefs_dir.mkdir()

    db = DatabaseManager(str(tmp_path / "abcs.db"))
    db.initialize_database()
    queries = CollectionQueries(db)
    cid = queries.insert(
        Collection(
            name="Import Missing Root Unique",
            active=True,
            root_path=str(tmp_path / "gone"),
        )
    )

    window = ImportWindow(db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    monkeypatch.setattr(window, "_prefs_import_directory", lambda: str(prefs_dir))
    idx = window.collection_combo.findData(cid)
    assert idx >= 0
    window.collection_combo.setCurrentIndex(idx)
    assert window.folder_edit.text() == str(prefs_dir)
    window.close()
    db.close()
