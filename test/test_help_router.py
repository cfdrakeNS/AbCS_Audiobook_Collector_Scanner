"""Tests for help markdown conversion and routing."""

from PySide6.QtCore import Qt

from src.accessibility.help_paths import (
    discover_help_topics,
    help_doc_display_name,
    help_doc_exists,
    resolve_help_docs_dir,
)
from src.ui.help_router import (
    DUPLICATE_MODE_DOC,
    WINDOW_HELP_MAP,
    get_help_doc_filename,
)
from src.ui.help_window import HelpWindow, markdown_to_html, markdown_to_plain_text


def test_help_docs_dir_exists():
    docs_dir = resolve_help_docs_dir()
    assert docs_dir.is_dir()
    assert help_doc_exists("01_overview.md")
    assert help_doc_exists("09_backup_restore.md")
    assert help_doc_exists("15_name_list.md")
    for _label, filename in discover_help_topics():
        assert help_doc_exists(filename), filename


def test_help_doc_display_name_strips_prefix_and_underscores():
    assert help_doc_display_name("11_import_book_list.md") == "import book list"
    assert help_doc_display_name("01_overview.md") == "overview"


def test_help_content_supports_mouse_and_keyboard_navigation(qtbot):
    window = HelpWindow(None, doc_filename="01_overview.md")
    qtbot.addWidget(window)
    flags = window.help_text.textInteractionFlags()
    assert flags & Qt.TextInteractionFlag.TextSelectableByMouse
    assert flags & Qt.TextInteractionFlag.TextSelectableByKeyboard


def test_overview_suggested_order_hides_topic_filename_numbers():
    overview = resolve_help_docs_dir().joinpath("01_overview.md").read_text(
        encoding="utf-8"
    )
    assert "See [02 Import]" not in overview
    assert "See [03 Find and Filters]" not in overview
    assert "See [11 Import Book List]" not in overview


def test_discover_help_topics_uses_the_curated_app_order():
    topics = discover_help_topics()
    filenames = [filename for _label, filename in topics]
    assert filenames == [
        "01_overview.md",
        "02_import.md",
        "03_find_filters.md",
        "04_book_details.md",
        "26_listen_to_a_book.md",
        "07_web_metadata.md",
        "15_name_list.md",
        "06_collections.md",
        "08_duplicate_mode.md",
        "09_backup_restore.md",
        "05_update.md",
        "10_preferences.md",
        "24_check_book_locations.md",
        "25_export_library.md",
        "14_statistics.md",
        "11_import_book_list.md",
        "12_import_detail.md",
        "13_reading_history.md",
        "16_shortcuts.md",
        "17_default_preferences.md",
        "18_import_preferences.md",
        "19_import_explained.md",
        "20_import_book_list_explained.md",
        "21_web_metadata_explained.md",
    ]
    assert ("overview", "01_overview.md") in topics


def test_window_help_mapping():
    class BackupRestoreWindow:
        pass

    assert get_help_doc_filename(BackupRestoreWindow()) == WINDOW_HELP_MAP[
        "BackupRestoreWindow"
    ]


def test_duplicate_mode_main_window_help():
    dup_window = type("MainWindow", (), {"duplicate_mode_active": True})()
    normal_window = type("MainWindow", (), {"duplicate_mode_active": False})()
    assert get_help_doc_filename(dup_window) == DUPLICATE_MODE_DOC
    assert get_help_doc_filename(normal_window) == WINDOW_HELP_MAP["MainWindow"]


def test_preview_window_opens_listen_help():
    preview = type("PreviewWindow", (), {})()
    assert get_help_doc_filename(preview) == "26_listen_to_a_book.md"


def test_help_doc_override_on_progress_window():
    """Book List Import can force progress Shift+F1 to book-list help."""
    window = type(
        "ImportProgressWindow",
        (),
        {"help_doc_override": "11_import_book_list.md"},
    )()
    assert get_help_doc_filename(window) == "11_import_book_list.md"
    # Invalid override falls through to class map
    bad = type(
        "ImportProgressWindow",
        (),
        {"help_doc_override": "does_not_exist.md"},
    )()
    assert get_help_doc_filename(bad) == WINDOW_HELP_MAP["ImportProgressWindow"]


def test_markdown_to_html_renders_shortcut_tables_as_lines():
    md = (
        "## Shortcuts\n\n"
        "| Shortcut | Action |\n"
        "|----------|--------|\n"
        "| Alt+K | Create backup |\n"
        "| Escape | Close window |\n"
    )
    html_doc, _links = markdown_to_html(md)
    assert "<table>" not in html_doc
    assert html_doc.count('class="shortcut"') == 2
    assert "Alt+K — Create backup" in html_doc
    assert "Escape — Close window" in html_doc


def test_markdown_to_html_splits_sentences_in_bullets_and_tables():
    md = (
        "- First bullet sentence. **Second** bullet sentence.\n\n"
        "| Field | Behavior |\n"
        "|-------|----------|\n"
        "| Empty | First table sentence. Second table sentence. |\n"
    )
    html_doc, _links = markdown_to_html(md)
    assert "<li><p>First bullet sentence.</p>" in html_doc
    assert "<p><strong>Second</strong> bullet sentence.</p>" in html_doc
    assert "</li>" in html_doc
    assert html_doc.count('class="table-row"') == 2
    assert "First table sentence." in html_doc
    assert "Second table sentence." in html_doc


def test_markdown_to_html_formats_faq_blocks():
    md = "## Common confusion\n\n**Where are files stored?**\nThey live in the backup folder.\n"
    html_doc, _links = markdown_to_html(md)
    assert 'class="faq-q"' in html_doc
    assert 'class="faq-a"' in html_doc
    assert "Where are files stored?" in html_doc
    assert "backup folder" in html_doc


def test_markdown_to_html_applies_body_and_step_indent_classes():
    md = "## Section\n\nBody text here.\n\n1. First step.\n"
    html_doc, _links = markdown_to_html(md)
    assert 'class="body"' in html_doc
    assert 'class="step"' in html_doc


def test_markdown_to_html_renumbers_steps_after_heading():
    md = "## Steps\n\n1. First step.\n2. Second step.\n\n### Section\n\n3. Third step.\n4. Fourth step.\n"
    html_doc, _links = markdown_to_html(md)
    assert "1. First step." in html_doc
    assert "2. Second step." in html_doc
    assert "1. Third step." in html_doc
    assert "2. Fourth step." in html_doc
    assert "3. Third step." not in html_doc


def test_markdown_to_html_keeps_numbered_list_items_together():
    md = "1. Open **Manage** menu.\n2. Click **Backup**.\n"
    html_doc, _links = markdown_to_html(md)
    assert "<ol>" not in html_doc
    assert "<li>" not in html_doc
    assert "1. Open <strong>Manage</strong> menu." in html_doc
    assert "2. Click <strong>Backup</strong>." in html_doc
    assert "<p>1.</p>" not in html_doc


def test_markdown_to_html_splits_multi_sentence_numbered_steps():
    md = (
        "## Section\n\n"
        "1. First sentence. **Second** sentence. Third sentence.\n"
        "2. Final step.\n"
    )
    html_doc, _links = markdown_to_html(md)
    assert '<p class="step">1. First sentence.</p>' in html_doc
    assert '<p class="step-cont"><strong>Second</strong> sentence.</p>' in html_doc
    assert '<p class="step-cont">Third sentence.</p>' in html_doc
    assert '<p class="step">2. Final step.</p>' in html_doc


def test_markdown_to_html_splits_sentences_into_paragraphs():
    md = (
        "Backup and Restore lets you save a copy of your entire AbCS database "
        "and restore it later. You can also delete old backup files."
    )
    html_doc, _links = markdown_to_html(md)
    assert html_doc.count('class="body"') == 2
    assert "restore it later." in html_doc
    assert "delete old backup files." in html_doc


def test_markdown_to_html_uses_bold_headings_and_no_blank_paragraphs():
    md = "# Title\n\nBody with **bold**.\n\n## Section\n\n- one\n"
    html_doc, links = markdown_to_html(md)
    assert "<strong>Title</strong>" in html_doc
    assert 'class="heading1"' in html_doc
    assert "<strong>bold</strong>" in html_doc
    assert 'class="heading2"' in html_doc
    assert "<li>one</li>" in html_doc
    assert "<p></p>" not in html_doc
    assert links == []


def test_markdown_to_html_embeds_named_anchors_in_headings():
    md = "## Section One\n\nBody.\n\n### Sub section\n\nMore."
    html_doc, _links = markdown_to_html(md)
    assert '<a name="h0"><strong>Section One</strong></a>' in html_doc
    assert '<a name="h1"><strong>Sub section</strong></a>' in html_doc


def test_markdown_to_plain_text_strips_formatting():
    md = "# Title\n\nSee [Import](02_import.md).\n\n- one\n"
    plain, links = markdown_to_plain_text(md)
    assert "Title" in plain
    assert "Import" in plain
    assert "[Import]" not in plain
    assert links == [("Import", "02_import.md")]
