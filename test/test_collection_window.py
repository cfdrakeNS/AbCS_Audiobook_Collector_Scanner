"""CollectionWindow smoke and list coverage."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from src.database.models import Collection
from src.database.queries import CollectionQueries
from src.ui.collection_window import CollectionWindow


def test_collection_window_accessible_name_and_list(
    temp_db, ui_scaler, theme_manager, qtbot
):
    name = "CW Test Collection Unique"
    CollectionQueries(temp_db).insert(Collection(name=name, active=True))

    window = CollectionWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    assert window.windowTitle() == "Collection Manager"
    assert window.accessibleName() == "Collection Manager"
    assert window.table.rowCount() >= 1

    listed = {
        window.table.item(row, window.COL_NAME).text()
        for row in range(window.table.rowCount())
    }
    assert name in listed
    assert window.table.columnCount() == 3
    assert window.table.horizontalHeaderItem(window.COL_PATH).text() == "Path"
    assert window.table.horizontalHeaderItem(window.COL_STATUS).text() == "Status"

    window.close()


def test_collection_window_saves_existing_root(
    temp_db, ui_scaler, theme_manager, qtbot, tmp_path
):
    root = tmp_path / "library"
    book_dir = root / "Author" / "Title"
    book_dir.mkdir(parents=True)
    (book_dir / "chapter.m4b").write_bytes(b"x")
    queries = CollectionQueries(temp_db)
    name = "CW Root Save Unique"
    cid = queries.insert(Collection(name=name, active=True))

    window = CollectionWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    window.focus_and_select_row(cid)
    window.on_edit()
    window.root_edit.setText(str(root))
    assert window.on_save() is True
    loaded = queries.get_by_id(cid)
    assert loaded is not None
    assert loaded.root_path == str(root)
    listed_path = None
    listed_status = None
    for row in range(window.table.rowCount()):
        name_item = window.table.item(row, window.COL_NAME)
        if name_item and name_item.data(Qt.UserRole) == cid:
            listed_path = window.table.item(row, window.COL_PATH).text()
            listed_status = window.table.item(row, window.COL_STATUS).text()
            break
    assert listed_path == str(root)
    assert listed_status == "Active"
    assert window.name_edit.text() == ""
    assert window.root_edit.text() == ""
    window.close()


def test_collection_window_warns_missing_and_empty_root(
    temp_db, ui_scaler, theme_manager, qtbot, tmp_path, monkeypatch
):
    queries = CollectionQueries(temp_db)
    name = "CW Root Warn Unique"
    cid = queries.insert(Collection(name=name, active=True))
    replies = []

    def fake_box(*_args, **_kwargs):
        return replies.pop(0)

    monkeypatch.setattr(
        "src.ui.collection_window.exec_styled_message_box", fake_box
    )

    window = CollectionWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    window.focus_and_select_row(cid)
    window.on_edit()

    replies.append(QMessageBox.No)
    window.root_edit.setText(str(tmp_path / "does_not_exist"))
    assert window.on_save() is False
    assert queries.get_by_id(cid).root_path == ""

    window.on_edit()
    replies.append(QMessageBox.Yes)
    missing = tmp_path / "still_missing"
    window.root_edit.setText(str(missing))
    assert window.on_save() is True
    assert queries.get_by_id(cid).root_path == str(missing)

    empty = tmp_path / "empty_lib"
    empty.mkdir()
    window.focus_and_select_row(cid)
    window.on_edit()
    replies.append(QMessageBox.No)
    window.root_edit.setText(str(empty))
    assert window.on_save() is False
    assert queries.get_by_id(cid).root_path == str(missing)
    window.close()
