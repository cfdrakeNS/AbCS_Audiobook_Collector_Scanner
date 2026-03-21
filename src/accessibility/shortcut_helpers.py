"""Helpers for accessible shortcut lists and F1 popup styling."""
from src.accessibility.screen_reader_detector import is_screen_reader_active


def get_accessible_shortcuts_list(shortcuts):
    """
    Given a list of (key, description) tuples, filter/reorder Alt+/ for F1 popup.
    If a screen reader is active, Alt+/ is shown at the top. Otherwise, it is hidden.
    """
    alt_slash = None
    rest = []
    for tup in shortcuts:
        if tup[0] == "Alt+/":
            alt_slash = tup
        else:
            rest.append(tup)
    if is_screen_reader_active():
        # Place Alt+/ at the top if present
        return [alt_slash] + rest if alt_slash else rest
    else:
        # Hide Alt+/
        return rest


def build_accessible_f1_popup_style() -> str:
    """
    Return a shared stylesheet for F1 help popups (QTableWidget).
    
    NOTE: This only provides CSS styling. Mouse tracking must be disabled
    programmatically on the table widget itself:
        table.setMouseTracking(False)
        table.viewport().setMouseTracking(False)
        table.setAttribute(Qt.WA_Hover, False)
        table.viewport().setAttribute(Qt.WA_Hover, False)
    """
    return (
        "QTableWidget, QTableView { border: none; background: palette(base); color: palette(text); outline: 0; }"
        "QTableWidget:focus, QTableView:focus { border: none; outline: none; }"
        "QTableWidget::item, QTableView::item { color: palette(text); padding-right: 8px; }"
        "QTableWidget::item:selected, QTableView::item:selected { background: palette(highlight); color: palette(highlighted-text); border: none; outline: none; }"
        "QTableWidget::item:hover, QTableView::item:hover { background: palette(base); color: palette(text); }"
        "QTableWidget::item:focus, QTableView::item:focus { outline: none; border: none; }"
    )
