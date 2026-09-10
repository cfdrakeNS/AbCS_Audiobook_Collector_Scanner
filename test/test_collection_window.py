"""CollectionWindow smoke and list coverage."""

from __future__ import annotations

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

    window.close()
