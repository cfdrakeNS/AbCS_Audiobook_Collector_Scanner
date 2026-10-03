"""Phase 29 standard shortcuts — registry and key bindings."""

from __future__ import annotations

from src.accessibility.shortcuts import ShortcutManager
from src.ui.book_list_import_window import BookListImportWindow
from src.ui.import_detail_window import ImportDetailWindow


def test_book_details_shortcut_map_phase29():
    shortcuts = ShortcutManager.BOOK_DETAILS_SHORTCUTS
    assert shortcuts["N"] == ("Narrator", "reader_edit")
    assert shortcuts["R"] == ("Read date", "read_date")
    assert shortcuts["S"] == ("Series", "series_label_display")
    assert "U" not in shortcuts
    assert "I" not in shortcuts


def test_save_uses_ctrl_s_not_alt_s_in_shortcut_maps():
    for mapping in (
        ShortcutManager.IMPORT_DETAIL_WINDOW_SHORTCUTS,
        ShortcutManager.WEB_METADATA_SHORTCUTS,
        ShortcutManager.COLLECTION_WINDOW_SHORTCUTS,
        ShortcutManager.PREFERENCES_WINDOW_SHORTCUTS,
    ):
        assert "S" not in mapping
    # Name list uses Alt+S for Sort; Save stays Ctrl+S.
    assert ShortcutManager.NAMELIST_WINDOW_SHORTCUTS["S"] == ("Sort", "sort_combo")


def test_reading_history_search_is_alt_s_only():
    shortcuts = ShortcutManager.READING_HISTORY_WINDOW_SHORTCUTS
    assert shortcuts["S"] == ("Search", "refresh_button")
    assert "R" not in shortcuts or shortcuts.get("R") != shortcuts.get("S")


def test_import_detail_alt_letters_match_registry():
    shortcuts = ShortcutManager.IMPORT_DETAIL_WINDOW_SHORTCUTS
    assert set(shortcuts) == set(ImportDetailWindow.ALLOWED_ALT_LETTERS)
    assert "S" not in shortcuts
    assert shortcuts["N"] == ("Narrator", "reader_edit")


def test_main_toolbar_has_no_import_action(main_window):
    roles = [role for _action, role in main_window._toolbar_actions]
    assert "import" not in roles


def test_book_list_import_narrator_field_label(
    qtbot, temp_db, ui_scaler, theme_manager, isolated_qsettings
):
    window = BookListImportWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    narrator_row = None
    for row in range(window.mapping_table.rowCount()):
        widget = window.mapping_table.cellWidget(row, 0)
        if widget is not None and widget.text().strip() == "Narrator":
            narrator_row = row
            break
    assert narrator_row is not None
    shortcuts = ShortcutManager.BOOK_LIST_IMPORT_WINDOW_SHORTCUTS
    assert shortcuts["R"] == ("Narrator field mapping", "reader_mapping")
    window.close()
