"""Book List Import progress-window wiring smoke tests."""

from src.ui.book_list_import_window import BookListImportWindow
from src.ui.import_progress_window import ImportProgressWindow


def test_format_elapsed_mmss():
    assert BookListImportWindow._format_elapsed(65) == "01:05"
    assert BookListImportWindow._format_elapsed(3661) == "01:01:01"


def test_progress_window_activity_and_help_override(qapp):
    from src.accessibility.scaling import UIScaler
    from src.accessibility.theme_manager import ThemeManager
    from src.ui.help_router import get_help_doc_filename

    scaler = UIScaler(qapp)
    theme = ThemeManager(qapp)
    window = ImportProgressWindow(scaler, theme)
    window.set_activity_label("import")
    window.help_doc_override = "11_import_book_list.md"
    assert window._activity_label == "import"
    assert get_help_doc_filename(window) == "11_import_book_list.md"
    # Avoid cancel prompt during teardown
    window._scan_active = False
    window.close()
