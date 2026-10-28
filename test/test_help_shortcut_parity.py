"""Each window's F1 shortcut keys match its help shortcut tables.

Compares keys only, not descriptions. F1, Shift+F1, Alt+/, and Escape are in
every window, so they are left out of the comparison. In a window's own topic,
rows whose action ends with "(main window)" are the keys that open the window
and are skipped too.
"""

from __future__ import annotations

import re

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget

from src.accessibility.help_paths import resolve_help_doc_path
from src.ui.accessible_dialog import AccessibleDialog

UNIVERSAL_KEYS = {"F1", "Shift+F1", "Alt+/", "Escape"}
OPENING_KEY_MARK = "(main window)"
SHORTCUTS_TOPIC = "16_shortcuts.md"
MOUSE_SECTION = "Mouse, shortcuts, and accessibility"

# Keys the help lists on purpose although F1 leaves them out in the state tested.
EXCEPTIONS = {
    "name_list": {"Ctrl+S"},  # F1 lists Save only while editing.
}

_HEADING_RE = re.compile(r"^(#{2,3})\s+(.+)$")


def _normalize(key: str) -> str:
    return " ".join(key.split())


def _shortcut_tables(markdown: str, section: str) -> list[list[tuple[str, str]]]:
    """Shortcut tables under the ``##`` or ``###`` heading named ``section``."""
    tables: list[list[tuple[str, str]]] = []
    in_section = False
    section_level = 0
    current: list[tuple[str, str]] | None = None
    for line in markdown.splitlines():
        heading = _HEADING_RE.match(line.strip())
        if heading:
            level = len(heading.group(1))
            if in_section and level <= section_level:
                break
            if heading.group(2).strip() == section:
                in_section, section_level = True, level
            current = None
            continue
        if not in_section:
            continue
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            current = None
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if [cell.casefold() for cell in cells[:2]] == ["shortcut", "action"]:
            current = []
            tables.append(current)
        elif current is not None and not set("".join(cells)) <= set("-: "):
            current.append((cells[0], cells[1] if len(cells) > 1 else ""))
    return tables


def _help_keys(filename: str, section: str, *, skip_opening_keys: bool) -> set[str]:
    markdown = resolve_help_doc_path(filename).read_text(encoding="utf-8")
    tables = _shortcut_tables(markdown, section)
    assert tables, f"No shortcut table under '{section}' in {filename}"
    keys = set()
    for key, action in tables[0]:
        if skip_opening_keys and action.endswith(OPENING_KEY_MARK):
            continue
        keys.add(_normalize(key))
    return keys - UNIVERSAL_KEYS


@pytest.fixture
def f1_keys(monkeypatch):
    """Capture the keys of the next F1 table instead of showing the dialog."""
    keys: set[str] = set()
    # Windows queue a focus call on the table after exec; keep it alive.
    shown: list = []

    def fake_exec(dlg):
        shown.append(dlg)
        table = dlg.findChild(QTableWidget)
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            spoken = item.data(Qt.AccessibleTextRole)
            if spoken:
                key = str(spoken).rsplit(": ", 1)[-1]
            else:
                key = item.text().rsplit(" - ", 1)[-1]
            keys.add(_normalize(key))
        return 0

    monkeypatch.setattr(AccessibleDialog, "exec", fake_exec)
    monkeypatch.setattr(
        "src.accessibility.shortcut_helpers.is_screen_reader_active", lambda: True
    )
    return keys


def _build_collection(db, scaler, theme):
    from src.ui.collection_window import CollectionWindow

    return CollectionWindow(db, scaler, theme)


def _build_name_list(db, scaler, theme):
    from src.ui.name_list_window import NameListWindow

    return NameListWindow(db, scaler, theme, "series")


def _build_reading_history(db, scaler, theme):
    from src.ui.reading_history_window import ReadingHistoryWindow

    return ReadingHistoryWindow(db, scaler, theme)


def _build_backup(db, scaler, theme):
    from src.ui.backup_restore_window import BackupRestoreWindow

    return BackupRestoreWindow(db, scaler, theme)


def _build_statistics(db, scaler, theme):
    from src.database.queries import StatisticsQueries
    from src.ui.statistics_dialog import StatisticsDialog

    return StatisticsDialog(StatisticsQueries(db).get_statistics(), scaler)


def _build_path_health(db, scaler, theme):
    from src.ui.path_health_window import PathHealthWindow

    return PathHealthWindow(db, scaler, theme, parent=None)


def _build_import(db, scaler, theme):
    from src.ui.import_window import ImportWindow

    return ImportWindow(db, scaler, theme)


def _build_book_list_import(db, scaler, theme):
    from src.ui.book_list_import_window import BookListImportWindow

    return BookListImportWindow(db, scaler, theme)


def _build_preferences(db, scaler, theme):
    from src.ui.preferences_window import PreferencesWindow

    return PreferencesWindow(scaler, theme)


def _build_update(db, scaler, theme):
    from src.ui.update_window import UpdateWindow

    return UpdateWindow(db, scaler, selected_book_ids=set())


def _build_book_details(db, scaler, theme):
    from src.ui.book_details import BookDetailsWindow

    return BookDetailsWindow(db, scaler, book=None, parent=None, theme_manager=theme)


def _build_batch_progress(db, scaler, theme):
    from src.ui.batch_web_fetch_progress import BatchWebFetchProgressDialog

    return BatchWebFetchProgressDialog(2)


def _build_help(db, scaler, theme):
    from src.ui.help_window import HelpWindow

    return HelpWindow(None, doc_filename="01_overview.md")


# (id, builder, F1 handler name, section in 16_shortcuts.md, own topic, own section)
WINDOWS = [
    ("collection", _build_collection, "on_show_shortcuts", "Collection window",
     "06_collections.md", MOUSE_SECTION),
    ("name_list", _build_name_list, "on_show_shortcuts",
     "Name list window (Authors, Series, Genre)", "15_name_list.md", MOUSE_SECTION),
    ("reading_history", _build_reading_history, "on_show_shortcuts",
     "Reading History window", "13_reading_history.md", MOUSE_SECTION),
    ("backup", _build_backup, "on_show_shortcuts", "Backup / Restore window",
     "09_backup_restore.md", MOUSE_SECTION),
    ("statistics", _build_statistics, "on_show_shortcuts", "Statistics dialog",
     "14_statistics.md", MOUSE_SECTION),
    ("path_health", _build_path_health, "on_show_shortcuts",
     "Check Book Locations window", "24_check_book_locations.md", MOUSE_SECTION),
    ("import", _build_import, "on_show_shortcuts", "Import window",
     "02_import.md", MOUSE_SECTION),
    ("book_list_import", _build_book_list_import, "on_show_shortcuts",
     "Book List Import window", "11_import_book_list.md", MOUSE_SECTION),
    ("preferences", _build_preferences, "on_show_shortcuts", "Preferences window",
     "10_preferences.md", MOUSE_SECTION),
    ("update", _build_update, "on_show_shortcuts", "Update window",
     "05_update.md", MOUSE_SECTION),
    ("book_details", _build_book_details, "on_show_shortcuts", "Book Details",
     "04_book_details.md", MOUSE_SECTION),
    ("batch_progress", _build_batch_progress, "_show_shortcuts",
     "Batch web fetch progress", None, None),
    ("help", _build_help, "on_show_shortcuts", "Help window",
     "01_overview.md", "Help window shortcuts"),
]


def _window_f1_keys(window, handler: str, f1_keys: set[str]) -> set[str]:
    getattr(window, handler)()
    assert f1_keys, "F1 table was not captured"
    return set(f1_keys) - UNIVERSAL_KEYS


def _assert_same(window_id: str, where: str, f1: set[str], help_keys: set[str]) -> None:
    allowed = EXCEPTIONS.get(window_id, set())
    only_f1 = sorted(f1 - help_keys)
    only_help = sorted(help_keys - f1 - allowed)
    assert not only_f1 and not only_help, (
        f"{window_id}: F1 and {where} differ.\n"
        f"  In F1 only: {only_f1}\n  In help only: {only_help}"
    )


@pytest.mark.parametrize(
    "window_id, builder, handler, section, topic, topic_section",
    WINDOWS,
    ids=[entry[0] for entry in WINDOWS],
)
def test_f1_keys_match_help(
    window_id, builder, handler, section, topic, topic_section,
    temp_db, ui_scaler, theme_manager, qtbot, isolated_qsettings, f1_keys,
):
    window = builder(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    try:
        f1 = _window_f1_keys(window, handler, f1_keys)
    finally:
        window.close()

    shortcuts_keys = _help_keys(SHORTCUTS_TOPIC, section, skip_opening_keys=False)
    _assert_same(window_id, f"{SHORTCUTS_TOPIC} '{section}'", f1, shortcuts_keys)

    if topic:
        own_keys = _help_keys(topic, topic_section, skip_opening_keys=True)
        _assert_same(window_id, f"{topic} '{topic_section}'", f1, own_keys)


def test_main_window_f1_keys_match_help(main_window, f1_keys):
    f1 = _window_f1_keys(main_window, "on_show_shortcuts", f1_keys)
    _assert_same(
        "main", f"{SHORTCUTS_TOPIC} 'Main window'", f1,
        _help_keys(SHORTCUTS_TOPIC, "Main window", skip_opening_keys=False),
    )
    _assert_same(
        "main", f"03_find_filters.md '{MOUSE_SECTION}'", f1,
        _help_keys("03_find_filters.md", MOUSE_SECTION, skip_opening_keys=True),
    )
