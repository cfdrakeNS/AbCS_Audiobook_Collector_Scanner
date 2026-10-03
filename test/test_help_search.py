"""Help window search across all topics (Ctrl+F)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from src.accessibility.help_search import (
    RANK_BODY,
    RANK_HEADING,
    RANK_TITLE,
    search_help,
    search_summary,
    split_help_sections,
)

_TOPIC_A = """# Backup and Restore

Backup saves a copy of your **database**.

## Restore a backup

Choose a backup file and press Restore.

## Tips

Keep backups on another drive. See [Collections](06_collections.md).
"""

_TOPIC_B = """# Collections

## Collection folder

Set the collection folder in Collection Manager.

| Key | Action |
|-----|--------|
| Alt+N | New collection |
"""


def _sections():
    sections = split_help_sections("09_backup.md", _TOPIC_A)
    sections += split_help_sections("06_collections.md", _TOPIC_B)
    return sections, ["06_collections.md", "09_backup.md"]


def _search(query, **kwargs):
    sections, order = _sections()
    return search_help(query, sections=sections, topic_order=order, **kwargs)


def test_sections_use_help_window_anchor_ids_and_plain_text():
    sections = split_help_sections("09_backup.md", _TOPIC_A)
    assert [(s.heading, s.anchor_id) for s in sections] == [
        ("Backup and Restore", ""),
        ("Restore a backup", "h0"),
        ("Tips", "h1"),
    ]
    assert "**" not in sections[0].text
    assert sections[2].text == "Keep backups on another drive. See Collections."


def test_table_rows_are_searchable_without_pipes():
    result = _search("alt+n")
    assert result.hits[0].snippet == "Alt+N - New collection"


def test_every_word_must_match_in_one_section_case_insensitive():
    assert _search("RESTORE backup").total == 2
    assert _search("restore drive").total == 0


def test_title_then_heading_then_body_ranking():
    hits = _search("backup").hits
    assert [h.rank for h in hits] == [RANK_TITLE, RANK_HEADING, RANK_BODY]
    assert hits[0].topic_title == "Backup and Restore"


def test_better_topic_first_then_curated_order():
    hits = _search("collection").hits
    assert hits[0].filename == "06_collections.md"
    hits = _search("backup").hits
    assert {h.filename for h in hits} == {"09_backup.md"}


def test_exact_phrase_ranks_above_scattered_words_and_is_the_match_text():
    hits = _search("collection folder").hits
    assert hits[0].match_text == "collection folder"
    assert hits[0].heading == "Collection folder"


def test_result_label_skips_repeated_topic_heading():
    hit = _search("database").hits[0]
    assert hit.label == "Backup and Restore - Backup saves a copy of your database."


def test_result_label_puts_section_before_guide():
    hit = _search("collection folder").hits[0]
    assert hit.label.startswith(f"Collection folder - {hit.topic_title} - ")
    assert hit.label_for(include_guide=False) == f"Collection folder - {hit.snippet}"


def test_summary_messages():
    assert search_summary(_search("")) == "Type words to search help, then press Enter."
    assert search_summary(_search("zzzz")) == "No matches for zzzz."
    assert search_summary(_search("backup")) == (
        "3 matches in 1 topic for backup."
    )
    limited = _search("backup", limit=1)
    assert limited.truncated
    assert "Showing first 1." in search_summary(limited)


def test_real_help_docs_find_listen_topic():
    result = search_help("listen")
    assert result.hits
    assert result.hits[0].filename == "26_listen_to_a_book.md"


def _window(qtbot, monkeypatch):
    from src.ui.help_window import HelpWindow

    window = HelpWindow(None, doc_filename="01_overview.md")
    qtbot.addWidget(window)
    announced = []
    monkeypatch.setattr(window, "_announce", announced.append)
    monkeypatch.setattr(
        "src.ui.help_window.QTimer.singleShot", lambda _ms, fn: fn()
    )
    return window, announced


def test_search_box_is_labelled_and_in_tab_order(qtbot, monkeypatch):
    window, _ = _window(qtbot, monkeypatch)
    assert window.search_edit.accessibleName() == "Search all help"
    assert window.search_label.buddy() is window.search_edit
    widget = window.zoom_in_button.nextInFocusChain()
    while not (widget.focusPolicy() & Qt.FocusPolicy.TabFocus):
        widget = widget.nextInFocusChain()
    assert widget is window.search_edit
    window.close()


def test_enter_fills_results_list_and_announces(qtbot, monkeypatch):
    window, announced = _window(qtbot, monkeypatch)
    window.search_edit.setText("listen")
    QTest.keyClick(window.search_edit, Qt.Key.Key_Return)

    assert window._nav_mode == "results"
    assert window.nav_list.item(0).text() == "Back to topics"
    assert window.nav_list.currentRow() == 1
    assert window.focusWidget() is window.nav_list
    assert " for listen." in announced[-1]
    window.close()


def test_no_match_leaves_focus_in_search_box(qtbot, monkeypatch):
    window, _ = _window(qtbot, monkeypatch)
    window.search_edit.setFocus()
    window.search_edit.setText("zzzzqq")
    window._run_search()
    assert window.focusWidget() is window.search_edit
    window.close()


def test_alt_l_focuses_nav_list_from_search_and_content(qtbot, monkeypatch):
    window, _ = _window(qtbot, monkeypatch)
    assert window.nav_focus_shortcut.key().toString() == "Alt+L"
    for start in (window.search_edit, window.help_text):
        start.setFocus()
        window.nav_focus_shortcut.activated.emit()
        assert window.focusWidget() is window.nav_list
    window.close()


def test_no_match_keeps_list_and_announces(qtbot, monkeypatch):
    window, announced = _window(qtbot, monkeypatch)
    window.search_edit.setText("zzzzqq")
    window._run_search()
    assert window._nav_mode == "headings"
    assert announced == ["No matches for zzzzqq."]
    window.close()


def test_opening_result_loads_topic_and_selects_match(qtbot, monkeypatch):
    window, _ = _window(qtbot, monkeypatch)
    window.search_edit.setText("listen")
    window._run_search()
    window._on_nav_item_activated(window.nav_list.item(1))

    assert window._current_filename == "26_listen_to_a_book.md"
    assert window._nav_mode == "results"
    assert window.help_text.textCursor().selectedText().casefold() == "listen"
    window.close()


def test_f3_moves_to_next_match_in_topic(qtbot, monkeypatch):
    window, _ = _window(qtbot, monkeypatch)
    window.search_edit.setText("listen")
    window._run_search()
    window._on_nav_item_activated(window.nav_list.item(1))
    first = window.help_text.textCursor().position()
    window._find_in_topic(False)
    second = window.help_text.textCursor().position()
    assert second != first
    window._find_in_topic(True)
    assert window.help_text.textCursor().position() == first
    window.close()


def test_escape_in_search_box_clears_results(qtbot, monkeypatch):
    window, announced = _window(qtbot, monkeypatch)
    window.search_edit.setText("listen")
    window._run_search()
    QTest.keyClick(window.search_edit, Qt.Key.Key_Escape)

    assert window.search_edit.text() == ""
    assert window._nav_mode == "headings"
    assert window.nav_list.item(0).text() == "All Help Topics"
    assert announced[-1] == "Search cleared."
    window.close()


def test_ctrl_f_focuses_search_box(qtbot, monkeypatch):
    window, _ = _window(qtbot, monkeypatch)
    window.help_text.setFocus()
    window.search_shortcut.activated.emit()
    assert window.focusWidget() is window.search_edit
    assert window.search_shortcut.key().toString() == "Ctrl+F"
    window.close()


def test_ctrl_f_scope_follows_focused_pane(qtbot, monkeypatch):
    window, _ = _window(qtbot, monkeypatch)
    window.help_text.setFocus()
    window.search_shortcut.activated.emit()
    assert window.search_topic_radio.isChecked()
    assert window.search_edit.accessibleName() == "Search current topic"

    window.nav_list.setFocus()
    window.search_shortcut.activated.emit()
    assert window.search_all_radio.isChecked()
    assert window.search_edit.accessibleName() == "Search all help"

    window.search_topic_radio.setChecked(True)
    window.search_shortcut.activated.emit()
    assert window.search_topic_radio.isChecked()
    window.close()


def test_scope_radios_follow_search_box_in_tab_order(qtbot, monkeypatch):
    window, _ = _window(qtbot, monkeypatch)
    assert window.search_all_radio.accessibleName() == "Search all help"
    assert window.search_topic_radio.accessibleName() == "Search current topic"
    widget = window.search_edit.nextInFocusChain()
    while not (widget.focusPolicy() & Qt.FocusPolicy.TabFocus):
        widget = widget.nextInFocusChain()
    assert widget is window.search_all_radio
    window.close()


def test_current_topic_search_only_lists_open_topic(qtbot, monkeypatch):
    window, announced = _window(qtbot, monkeypatch)
    window.search_topic_radio.setChecked(True)
    window.search_edit.setText("help")
    window._run_search()

    filenames = {
        window.nav_list.item(row).data(Qt.ItemDataRole.UserRole + 1)
        for row in range(1, window.nav_list.count())
    }
    assert window._nav_mode == "results"
    assert filenames == {"01_overview.md"}
    for row in range(1, window.nav_list.count()):
        assert f" - {window._current_title} - " not in window.nav_list.item(row).text()
    assert f" in {window._current_title} for help." in announced[-1]
    window.close()


def test_current_topic_summary_wording():
    assert search_summary(_search("zzzz"), topic_title="Backup") == (
        "No matches for zzzz in Backup."
    )
    assert search_summary(_search("backup"), topic_title="Backup") == (
        "3 matches in Backup for backup."
    )
