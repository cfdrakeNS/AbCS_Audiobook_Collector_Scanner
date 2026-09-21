"""Helpers for accessible shortcut lists and F1 popup styling."""
from src.accessibility.screen_reader import is_screen_reader_active

HELP_DOC_SHORTCUT = ("Shift+F1", "Show help for this window")


def prepend_help_doc_shortcut(shortcuts):
    """Prepend Shift+F1 as the first row in an F1 shortcuts table."""
    shortcuts = list(shortcuts)
    if shortcuts and shortcuts[0] == HELP_DOC_SHORTCUT:
        return shortcuts
    return [HELP_DOC_SHORTCUT] + shortcuts


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


def exec_f1_shortcuts_dialog(parent, window_title: str, shortcuts) -> None:
    """Show the standard one-column F1 shortcut table for a window."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QAbstractItemView,
        QHeaderView,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
    )

    from src.ui.accessible_dialog import AccessibleDialog

    dlg = AccessibleDialog(parent)
    dlg.setWindowTitle(window_title)
    dlg.setAccessibleName("Keyboard Shortcuts")
    dlg.resize(520, 360)
    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(20, 20, 20, 20)

    table = QTableWidget()
    table.setAccessibleName("Shortcuts list")
    table.setColumnCount(1)
    table.setHorizontalHeaderLabels([""])
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setTabKeyNavigation(False)
    table.setAlternatingRowColors(False)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setVisible(False)
    table.setShowGrid(False)
    table.setMouseTracking(False)
    table.viewport().setMouseTracking(False)
    table.setAttribute(Qt.WA_Hover, False)
    table.viewport().setAttribute(Qt.WA_Hover, False)
    table.setStyleSheet(build_accessible_f1_popup_style())

    rows = prepend_help_doc_shortcut(get_accessible_shortcuts_list(list(shortcuts)))
    table.setRowCount(len(rows))
    table.setVerticalHeaderLabels([""] * len(rows))
    for row, (key, desc) in enumerate(rows):
        item = QTableWidgetItem(f"{desc} - {key}")
        item.setData(Qt.AccessibleTextRole, f"{desc}: {key}")
        table.setItem(row, 0, item)
    table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    layout.addWidget(table)
    dlg.exec()


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
