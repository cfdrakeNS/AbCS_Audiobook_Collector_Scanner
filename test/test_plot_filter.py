"""Tests for plot indicator threshold and plot filter behaviour."""

import pytest

from src.database.models import SearchFilter, book_has_plot, PLOT_MIN_LENGTH, Book
from src.database.queries import BookQueries, AuthorQueries
from src.database.connection import DatabaseManager


def _insert_book(db: DatabaseManager, title: str, comments: str = "") -> int:
    author_id = AuthorQueries(db).insert(f"Plot Author {title}")
    return BookQueries(db).insert(
        Book(title=title, author_id=author_id, comments=comments)
    )


def test_title_accessible_text_includes_plot_suffix():
    from PySide6.QtCore import Qt, QModelIndex
    from src.ui.main_window import BookTableModel

    model = BookTableModel(
        [
            Book(title="With Plot", comments="p" * PLOT_MIN_LENGTH),
            Book(title="No Plot", comments="Reader: Bob"),
        ]
    )

    with_plot = model.data(model.index(0, 1), Qt.DisplayRole)
    without_plot = model.data(model.index(1, 1), Qt.DisplayRole)
    with_plot_sr = model.data(model.index(0, 1), Qt.AccessibleTextRole)
    without_plot_sr = model.data(model.index(1, 1), Qt.AccessibleTextRole)

    assert with_plot == "With Plot"
    assert without_plot == "No Plot"
    assert with_plot_sr == "With Plot, plot"
    assert without_plot_sr == "No Plot"


def test_book_has_plot_requires_minimum_length():
    short = "Reader: Jane Doe"
    long_plot = "x" * PLOT_MIN_LENGTH

    assert not book_has_plot("")
    assert not book_has_plot(short)
    assert book_has_plot(long_plot)
    assert book_has_plot(f"  {long_plot}  ")


def test_plot_filter_with_plot_returns_only_long_comments(temp_db):
    book_queries = BookQueries(temp_db)
    test_titles = {"PlotTest Has Plot", "PlotTest Short Only", "PlotTest No Plot"}
    _insert_book(temp_db, "PlotTest Has Plot", "p" * PLOT_MIN_LENGTH)
    _insert_book(temp_db, "PlotTest Short Only", "Reader: Bob")
    _insert_book(temp_db, "PlotTest No Plot", "")

    books = book_queries.get_all(SearchFilter(plot_filter="With Plot"))
    titles = {book.title for book in books if book.title in test_titles}

    assert titles == {"PlotTest Has Plot"}


def test_plot_filter_without_plot_excludes_long_comments(temp_db):
    book_queries = BookQueries(temp_db)
    test_titles = {"PlotTest Has Plot", "PlotTest Short Only", "PlotTest No Plot"}
    _insert_book(temp_db, "PlotTest Has Plot", "p" * PLOT_MIN_LENGTH)
    _insert_book(temp_db, "PlotTest Short Only", "Reader: Bob")
    _insert_book(temp_db, "PlotTest No Plot", "")

    books = book_queries.get_all(SearchFilter(plot_filter="Without Plot"))
    titles = {book.title for book in books if book.title in test_titles}

    assert titles == {"PlotTest Short Only", "PlotTest No Plot"}


def test_plot_menu_selection_updates_filter(qapp, qtbot, temp_db):
    from src.ui.main_window import MainWindow
    from src.accessibility.scaling import UIScaler
    from src.accessibility.theme_manager import ThemeManager

    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    target_action = None
    for action in window.plot_filter_group.actions():
        if action.data() == "With Plot":
            target_action = action
            break

    assert target_action is not None
    target_action.trigger()

    assert window.current_filter.plot_filter == "With Plot"
    assert window.plot_filter_action.isChecked()

    window.plot_filter_action.trigger()
    assert window.current_filter.plot_filter == "All"
    assert not window.plot_filter_action.isChecked()

    window.close()


def test_read_filter_toolbar_toggle(qapp, qtbot, temp_db):
    from src.ui.main_window import MainWindow
    from src.accessibility.scaling import UIScaler
    from src.accessibility.theme_manager import ThemeManager

    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    window.read_filter_action.trigger()
    assert window.current_filter.read_filter == "Read"
    assert window.read_filter_action.isChecked()

    window.read_filter_action.trigger()
    assert window.current_filter.read_filter == "All"
    assert not window.read_filter_action.isChecked()

    window.close()


def test_unread_menu_unchecks_read_toolbar_toggle(qapp, qtbot, temp_db):
    from src.ui.main_window import MainWindow
    from src.accessibility.scaling import UIScaler
    from src.accessibility.theme_manager import ThemeManager

    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    unread_action = None
    for action in window.read_filter_group.actions():
        if action.data() == "Unread":
            unread_action = action
            break

    assert unread_action is not None
    unread_action.trigger()

    assert window.current_filter.read_filter == "Unread"
    assert not window.read_filter_action.isChecked()

    window.close()


def test_read_filter_shortcut_from_unread_sets_read(qapp, qtbot, temp_db):
    from src.ui.main_window import MainWindow
    from src.accessibility.scaling import UIScaler
    from src.accessibility.theme_manager import ThemeManager

    scaler = UIScaler(qapp)
    theme_manager = ThemeManager(qapp)
    window = MainWindow(temp_db, scaler, theme_manager)
    qtbot.addWidget(window)

    window.current_filter.read_filter = "Unread"
    window._sync_read_menu_selection()
    window._sync_read_toolbar_toggle()

    window.on_read_filter_shortcut()

    assert window.current_filter.read_filter == "Read"
    assert window.read_filter_action.isChecked()

    window.close()
