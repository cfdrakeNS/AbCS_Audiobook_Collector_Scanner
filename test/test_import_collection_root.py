"""Import keeps the Preferences import folder when the collection changes."""

from __future__ import annotations

from src.database.connection import DatabaseManager
from src.database.models import Collection
from src.database.queries import CollectionQueries
from src.ui.import_window import ImportWindow


def test_collection_change_keeps_import_folder(
    tmp_path, ui_scaler, theme_manager, qtbot
):
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
    prefs_dir = window.settings.value("import/default_directory", "", type=str)
    assert window.folder_edit.text() == prefs_dir
    idx = window.collection_combo.findData(cid)
    assert idx >= 0
    window.collection_combo.setCurrentIndex(idx)
    assert window.folder_edit.text() == prefs_dir
    assert window.folder_edit.text() != str(root)
    window.close()
    db.close()


def test_collection_change_keeps_typed_folder(
    tmp_path, ui_scaler, theme_manager, qtbot
):
    root = tmp_path / "library"
    root.mkdir()
    typed = tmp_path / "typed"
    typed.mkdir()

    db = DatabaseManager(str(tmp_path / "abcs.db"))
    db.initialize_database()
    queries = CollectionQueries(db)
    cid = queries.insert(
        Collection(name="Import Typed Unique", active=True, root_path=str(root))
    )

    window = ImportWindow(db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    window.folder_edit.setText(str(typed))
    idx = window.collection_combo.findData(cid)
    assert idx >= 0
    window.collection_combo.setCurrentIndex(idx)
    assert window.folder_edit.text() == str(typed)
    window.close()
    db.close()
