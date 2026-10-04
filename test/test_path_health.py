"""Unit tests for Check Book Locations scan (Phase 25 / F01)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.core.path_health import (
    FILTER_ALL,
    FILTER_INCORRECT,
    FILTER_MISSING,
    STATUS_EMPTY,
    STATUS_INCORRECT,
    STATUS_MISSING,
    STATUS_OK,
    STATUS_RESOLVED,
    PathHealthCounts,
    check_book_path,
    iter_book_path_checks,
    row_matches_filter,
    scan_book_paths,
    summarize_statuses,
)


@pytest.fixture(autouse=True)
def folder_warnings(monkeypatch):
    """Record the collection folder popup instead of showing it."""
    from src.ui.path_health_window import PathHealthWindow

    shown: list = []
    monkeypatch.setattr(
        PathHealthWindow,
        "_warn_collection_folder_problems",
        lambda _self, problems: shown.append(list(problems)),
    )
    return shown


def test_check_book_path_empty():
    assert check_book_path("") == STATUS_EMPTY
    assert check_book_path("   ") == STATUS_EMPTY
    assert check_book_path(None) == STATUS_EMPTY


def test_check_book_path_missing_when_unresolvable(tmp_path):
    missing = tmp_path / "gone" / "book"
    assert check_book_path(str(missing), str(tmp_path / "library")) == STATUS_MISSING


def test_check_book_path_file_exists(tmp_path):
    audio = tmp_path / "book.m4b"
    audio.write_bytes(b"x")
    assert check_book_path(str(audio)) == STATUS_OK


def test_check_book_path_folder_exists(tmp_path):
    folder = tmp_path / "Author" / "Title"
    folder.mkdir(parents=True)
    assert check_book_path(str(folder)) == STATUS_OK


def test_check_book_path_incorrect_outside_root(tmp_path):
    root = tmp_path / "library"
    root.mkdir()
    outside = tmp_path / "other" / "book"
    outside.mkdir(parents=True)
    assert check_book_path(str(outside), str(root)) == STATUS_INCORRECT
    under = root / "Author" / "Title"
    under.mkdir(parents=True)
    assert check_book_path(str(under), str(root)) == STATUS_OK


def test_check_book_path_stale_stored_but_playable_via_root(tmp_path):
    """Stored drive/folder renamed (USB letter change): remaps, path kept as stored."""
    root = tmp_path / "zLibrary"
    book = root / "Michael R. Stern" / "Title"
    book.mkdir(parents=True)
    (book / "track.mp3").write_bytes(b"x")
    stale = tmp_path / "Library" / "Michael R. Stern" / "Title"
    assert not stale.exists()
    assert check_book_path(str(stale), str(root)) == STATUS_OK
    assert check_book_path(str(stale), str(root), "") != STATUS_MISSING


def test_scan_book_paths_filters(tmp_path):
    good = tmp_path / "library" / "ok.mp3"
    good.parent.mkdir(parents=True)
    good.write_bytes(b"x")
    outside = tmp_path / "elsewhere" / "book"
    outside.mkdir(parents=True)
    stale_root = tmp_path / "library"
    stale_book = stale_root / "Author" / "Remapped"
    stale_book.mkdir(parents=True)
    stale_stored = tmp_path / "old_library" / "Author" / "Remapped"
    books = [
        SimpleNamespace(
            book_id=1,
            title="Empty Path",
            author_name="A",
            path="",
            collection_id=1,
            collection_name="Lib",
        ),
        SimpleNamespace(
            book_id=2,
            title="Missing Path",
            author_name="B",
            path=str(tmp_path / "missing"),
            collection_id=1,
            collection_name="Lib",
        ),
        SimpleNamespace(
            book_id=3,
            title="Incorrect Path",
            author_name="C",
            path=str(outside),
            collection_id=1,
            collection_name="Lib",
        ),
        SimpleNamespace(
            book_id=4,
            title="Good Path",
            author_name="D",
            path=str(good),
            collection_id=1,
            collection_name="Lib",
        ),
        SimpleNamespace(
            book_id=5,
            title="Stale Remapped",
            author_name="E",
            path=str(stale_stored),
            collection_id=1,
            collection_name="Lib",
        ),
    ]
    root = str(tmp_path / "library")

    missing_rows = scan_book_paths(
        books, collection_root=root, filter_key=FILTER_MISSING
    )
    assert [r.book_id for r in missing_rows] == [1, 2]

    incorrect_rows = scan_book_paths(
        books, collection_root=root, filter_key=FILTER_INCORRECT
    )
    assert [r.book_id for r in incorrect_rows] == [3]
    assert incorrect_rows[0].status == STATUS_INCORRECT

    all_rows = scan_book_paths(books, collection_root=root, filter_key=FILTER_ALL)
    assert [r.book_id for r in all_rows] == [1, 2, 3]
    assert STATUS_OK not in {r.status for r in all_rows}

    every_row = list(iter_book_path_checks(books, collection_root=root))
    remapped = next(r for r in every_row if r.book_id == 5)
    assert remapped.status == STATUS_OK
    assert remapped.resolved_path == ""

    counts = summarize_statuses(every_row)
    assert counts[STATUS_EMPTY] == 1
    assert counts[STATUS_MISSING] == 1
    assert counts[STATUS_INCORRECT] == 1
    assert counts[STATUS_RESOLVED] == 0
    assert counts[STATUS_OK] == 2


def test_path_health_counts_mixed():
    counts = PathHealthCounts()
    for status in (
        STATUS_EMPTY,
        STATUS_MISSING,
        STATUS_INCORRECT,
        STATUS_RESOLVED,
        STATUS_OK,
        STATUS_OK,
    ):
        counts.record(status)
    assert counts.missing == 2
    assert counts.incorrect == 1
    assert counts.resolved == 1
    assert counts.valid == 2
    assert counts.processed == 6
    assert "Corrected 1" in counts.summary()


def test_iter_book_path_checks_cancel(tmp_path):
    book_a = tmp_path / "a.mp3"
    book_a.write_bytes(b"x")
    books = [
        SimpleNamespace(
            book_id=1,
            title="One",
            author_name="A",
            path=str(book_a),
            collection_id=1,
            collection_name="Lib",
        ),
        SimpleNamespace(
            book_id=2,
            title="Two",
            author_name="B",
            path="",
            collection_id=1,
            collection_name="Lib",
        ),
        SimpleNamespace(
            book_id=3,
            title="Three",
            author_name="C",
            path="",
            collection_id=1,
            collection_name="Lib",
        ),
    ]
    seen = []

    def cancel_after_one() -> bool:
        return len(seen) >= 1

    for row in iter_book_path_checks(books, cancel_check=cancel_after_one):
        seen.append(row.book_id)
    assert seen == [1]


def test_iter_uses_per_collection_roots(tmp_path):
    root_a = tmp_path / "lib_a"
    root_b = tmp_path / "lib_b"
    book_a = root_a / "Author" / "TitleA"
    book_b = root_b / "Author" / "TitleB"
    book_a.mkdir(parents=True)
    book_b.mkdir(parents=True)
    stale_a = tmp_path / "old_a" / "Author" / "TitleA"
    stale_b = tmp_path / "old_b" / "Author" / "TitleB"
    books = [
        SimpleNamespace(
            book_id=1,
            title="A",
            author_name="A",
            path=str(stale_a),
            collection_id=10,
            collection_name="Lib A",
        ),
        SimpleNamespace(
            book_id=2,
            title="B",
            author_name="B",
            path=str(stale_b),
            collection_id=20,
            collection_name="Lib B",
        ),
    ]
    rows = list(
        iter_book_path_checks(
            books,
            collection_roots={10: str(root_a), 20: str(root_b)},
        )
    )
    assert [r.status for r in rows] == [STATUS_OK, STATUS_OK]


def _audio_folder(folder):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "01.mp3").write_bytes(b"x")
    return folder


def test_blank_path_found_by_layout_is_incorrect_with_found_path(
    tmp_path, monkeypatch
):
    root = tmp_path / "library"
    book_dir = _audio_folder(root / "Lee Child" / "Killing Floor")
    books = [
        SimpleNamespace(
            book_id=1,
            title="Killing Floor",
            author_name="Lee Child",
            path="",
            collection_id=1,
            collection_name="Lib",
        ),
        SimpleNamespace(
            book_id=2,
            title="Not Here",
            author_name="Nobody",
            path="",
            collection_id=1,
            collection_name="Lib",
        ),
    ]
    rows = list(iter_book_path_checks(books, collection_root=str(root)))
    assert rows[0].status == STATUS_RESOLVED
    assert rows[0].resolved_path == str(book_dir)
    assert rows[0].reason == ""
    assert rows[1].status == STATUS_EMPTY
    assert rows[1].resolved_path == ""
    assert "Nobody" in rows[1].reason


def test_numbered_folders_resolve_by_series_number(tmp_path, monkeypatch):
    root = tmp_path / "library"
    author = root / "Patricia Cornwell" / "Kay Scarpetta Series"
    _audio_folder(author / "1-  Postmortem")
    second = _audio_folder(author / "2 - Body Of Evidence")
    _audio_folder(author / "3 - Body Of Evidence")
    books = [
        SimpleNamespace(
            book_id=1,
            title="Postmortem",
            author_name="Patricia Cornwell",
            path=str(tmp_path / "old" / "Postmortem"),
            series_number=None,
            collection_id=1,
            collection_name="Lib",
        ),
        SimpleNamespace(
            book_id=2,
            title="Body Of Evidence",
            author_name="Patricia Cornwell",
            path="",
            series_number=2,
            collection_id=1,
            collection_name="Lib",
        ),
    ]
    rows = list(iter_book_path_checks(books, collection_root=str(root)))
    assert rows[0].status == STATUS_RESOLVED
    assert rows[0].resolved_path == str(author / "1-  Postmortem")
    assert rows[1].status == STATUS_RESOLVED
    assert rows[1].resolved_path == str(second)


def test_outside_path_found_in_collection_is_corrected_not_incorrect(tmp_path):
    root = tmp_path / "library"
    series_book = _audio_folder(root / "Lee Child" / "Jack Reacher" / "Tripwire")
    outside = _audio_folder(tmp_path / "elsewhere" / "Tripwire")
    stray = _audio_folder(tmp_path / "elsewhere" / "Stray")
    books = [
        SimpleNamespace(
            book_id=1,
            title="Tripwire",
            author_name="Lee Child",
            series_name="Jack Reacher",
            path=str(outside),
            collection_id=1,
            collection_name="Lib",
        ),
        SimpleNamespace(
            book_id=2,
            title="Stray",
            author_name="Lee Child",
            path=str(stray),
            collection_id=1,
            collection_name="Lib",
        ),
    ]
    rows = list(iter_book_path_checks(books, collection_root=str(root)))
    assert rows[0].status == STATUS_RESOLVED
    assert rows[0].resolved_path == str(series_book)
    assert rows[1].status == STATUS_INCORRECT
    assert not row_matches_filter(rows[0].status, FILTER_ALL)
    counts = PathHealthCounts()
    for row in rows:
        counts.record(row.status)
    assert (counts.resolved, counts.incorrect) == (1, 1)


def test_series_tag_file_is_corrected(tmp_path):
    root = tmp_path / "Test series from directory"
    series_dir = root / "Michael R. Stern" / "Quantum Touch"
    series_dir.mkdir(parents=True)
    track = series_dir / "2 Sand Storm(Quantum Touch 02).m4b"
    track.write_bytes(b"x")
    books = [
        SimpleNamespace(
            book_id=1,
            title="Sand Storm",
            author_name="Michael R. Stern",
            series_name="Quantum Touch",
            path="",
            collection_id=1,
            collection_name="Lib",
        )
    ]
    rows = list(iter_book_path_checks(books, collection_root=str(root)))
    assert rows[0].status == STATUS_RESOLVED
    assert rows[0].resolved_path == str(track)


def test_missing_row_says_collection_folder_missing(tmp_path, monkeypatch):
    books = [
        SimpleNamespace(
            book_id=1,
            title="Killing Floor",
            author_name="Lee Child",
            path=str(tmp_path / "old" / "Killing Floor"),
            collection_id=1,
            collection_name="Lib",
        )
    ]
    rows = list(
        iter_book_path_checks(books, collection_root=str(tmp_path / "gone_root"))
    )
    assert rows[0].status == STATUS_MISSING
    assert "collection folder is missing" in rows[0].reason


@pytest.fixture
def layout_db(tmp_path):
    from src.database.connection import DatabaseManager
    from src.database.models import Book
    from src.database.queries import AuthorQueries, BookQueries, CollectionQueries

    db = DatabaseManager(str(tmp_path / "path_health_layout.db"))
    db.initialize_database()
    root = tmp_path / "library"
    collections = CollectionQueries(db)
    collection = collections.get_all()[0]
    collection.root_path = str(root)
    collections.update(collection)
    author_id = AuthorQueries(db).insert("Lee Child")
    books = BookQueries(db)
    ids = [
        books.insert(
            Book(
                title=title,
                author_id=author_id,
                collection_id=collection.collection_id,
            )
        )
        for title in ("Killing Floor", "Die Trying", "Tripwire")
    ]
    try:
        yield db, root, collection.collection_id, ids
    finally:
        db.close()


def test_scan_corrects_resolved_paths_and_leaves_them_out(
    layout_db, ui_scaler, theme_manager, qtbot, monkeypatch
):
    from src.database.queries import BookQueries
    from src.ui.path_health_window import PathHealthWindow

    db, root, collection_id, ids = layout_db
    killing = _audio_folder(root / "Lee Child" / "Killing Floor")
    die = _audio_folder(root / "Lee Child" / "Die Trying")

    window = PathHealthWindow(db, ui_scaler, theme_manager, parent=None)
    qtbot.addWidget(window)
    window.collection_combo.setCurrentIndex(
        window.collection_combo.findData(collection_id)
    )
    assert window.filter_combo.findText("Resolved") < 0
    window.filter_combo.setCurrentIndex(window.filter_combo.findData(FILTER_ALL))
    window.run_scan()

    queries = BookQueries(db)
    assert queries.get_by_id(ids[0]).path == str(killing)
    assert queries.get_by_id(ids[1]).path == str(die)
    assert (queries.get_by_id(ids[2]).path or "") == ""
    assert [row.title for row in window._rows] == ["Tripwire"]
    assert window._last_scan_status.startswith("2 book paths corrected.")
    assert window._scan_books[ids[0]].path == str(killing)

    window.run_scan(warn_folder=False)
    assert "corrected" not in window._last_scan_status
    window.close()


def test_scan_warns_when_collection_folder_missing_and_enter_scans(
    layout_db, ui_scaler, theme_manager, qtbot, folder_warnings
):
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QApplication

    from src.ui.path_health_window import PathHealthWindow

    db, root, collection_id, _ids = layout_db
    assert not root.exists()
    window = PathHealthWindow(db, ui_scaler, theme_manager, parent=None)
    qtbot.addWidget(window)
    window.collection_combo.setCurrentIndex(
        window.collection_combo.findData(collection_id)
    )
    assert window.guide_label.focusPolicy() == Qt.TabFocus
    assert "corrected" in window.guide_label.text()

    QApplication.sendEvent(
        window.scan_button,
        QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.NoModifier),
    )

    assert folder_warnings
    assert "collection folder is missing" in folder_warnings[0][0]
    assert len(window._scan_rows_all) == 3
    window.close()


def test_open_details_pages_listed_books_in_edit_mode(
    layout_db, ui_scaler, theme_manager, qtbot, monkeypatch
):
    from src.ui import path_health_window as module

    db, root, collection_id, ids = layout_db
    captured: dict = {}

    class FakeDetails:
        _data_was_changed = False
        _books_touched_in_session = set()

        def __init__(self, *args, **kwargs):
            captured.update(kwargs)

        def on_edit_mode(self):
            pass

        def load_book_data(self):
            pass

        def exec(self):
            return 0

        def deleteLater(self):
            pass

    monkeypatch.setattr(module, "BookDetailsWindow", FakeDetails)
    window = module.PathHealthWindow(db, ui_scaler, theme_manager, parent=None)
    qtbot.addWidget(window)
    window.collection_combo.setCurrentIndex(
        window.collection_combo.findData(collection_id)
    )
    window.filter_combo.setCurrentIndex(window.filter_combo.findData(FILTER_ALL))
    window.run_scan()
    assert len(window._rows) == 3
    window.table.setCurrentCell(1, 0)

    window.on_open_details()

    listed = [book.book_id for book in captured["books_list"]]
    assert listed == [row.book_id for row in window._rows]
    assert captured["current_index"] == 1
    assert captured["keep_edit_mode"] is True
    window.close()


def test_details_close_refreshes_rows_without_full_rescan(
    layout_db, ui_scaler, theme_manager, qtbot, monkeypatch
):
    from src.ui import path_health_window as module

    db, root, collection_id, ids = layout_db
    rescan_calls: list[bool] = []

    class FakeDetails:
        _data_was_changed = True
        _books_touched_in_session = {ids[0]}

        def __init__(self, *args, **kwargs):
            pass

        def on_edit_mode(self):
            pass

        def load_book_data(self):
            pass

        def exec(self):
            return 0

        def deleteLater(self):
            pass

    monkeypatch.setattr(module, "BookDetailsWindow", FakeDetails)
    window = module.PathHealthWindow(db, ui_scaler, theme_manager, parent=None)
    qtbot.addWidget(window)
    window.collection_combo.setCurrentIndex(
        window.collection_combo.findData(collection_id)
    )
    window.run_scan(warn_folder=False)
    assert window._scan_rows_all

    def _fail_rescan(*_args, **_kwargs):
        rescan_calls.append(True)
        raise AssertionError("full Scan should not run after Book Details")

    monkeypatch.setattr(window, "run_scan", _fail_rescan)
    refresh_calls: list[set[int]] = []
    monkeypatch.setattr(
        window,
        "_refresh_books_after_details",
        lambda book_ids: refresh_calls.append(set(book_ids)),
    )
    window.table.setCurrentCell(0, 0)
    window.on_open_details()
    assert refresh_calls == [{ids[0]}]
    assert not rescan_calls
    window.close()


def test_path_health_window_all_collections_and_scan_only_on_button(
    temp_db, ui_scaler, theme_manager, qtbot, tmp_path
):
    from src.database.models import Book, Collection
    from src.database.queries import BookQueries, CollectionQueries
    from src.ui.import_progress_window import ImportProgressWindow
    from src.ui.path_health_window import PathHealthWindow

    collections = CollectionQueries(temp_db)
    second_id = collections.insert(Collection(name="Second", active=True))
    queries = BookQueries(temp_db)
    existing = collections.get_all(active_only=True)
    first_id = existing[0].collection_id
    queries.insert(
        Book(title="Empty A", path="", collection_id=first_id)
    )
    queries.insert(
        Book(
            title="Missing B",
            path=str(tmp_path / "gone"),
            collection_id=second_id,
        )
    )

    window = PathHealthWindow(temp_db, ui_scaler, theme_manager, parent=None)
    qtbot.addWidget(window)
    assert window.collection_combo.itemText(0) == "All Collections"
    assert window.collection_combo.itemData(0) is None
    window.collection_combo.setCurrentIndex(0)
    assert window.collection_combo.currentData() is None
    window.filter_combo.setCurrentIndex(
        window.filter_combo.findData(FILTER_MISSING)
    )

    # temp_db may copy a large local library; keep All-collections scan tiny.
    real_get_all = window.book_queries.get_all

    def limited_get_all(filter_criteria=None):
        books = real_get_all(filter_criteria)
        return [b for b in books if b.title in ("Empty A", "Missing B")]

    window.book_queries.get_all = limited_get_all  # type: ignore[method-assign]

    progress_shown: list = []
    real_show = ImportProgressWindow.show

    def track_show(self):
        progress_shown.append(self)
        return real_show(self)

    ImportProgressWindow.show = track_show  # type: ignore[method-assign]
    try:
        window.on_filter_changed()
        assert progress_shown == []
        window.run_scan()
    finally:
        ImportProgressWindow.show = real_show  # type: ignore[method-assign]
        window.book_queries.get_all = real_get_all  # type: ignore[method-assign]

    assert progress_shown
    assert {row.title for row in window._rows} == {"Empty A", "Missing B"}
    window.close()


def test_path_health_window_lists_problems(temp_db, ui_scaler, theme_manager, qtbot, tmp_path):
    from src.database.models import Book
    from src.database.queries import BookQueries, CollectionQueries
    from src.ui.import_progress_window import ImportProgressWindow
    from src.ui.path_health_window import PathHealthWindow

    queries = BookQueries(temp_db)
    collections = CollectionQueries(temp_db).get_all(active_only=True)
    collection_id = collections[0].collection_id if collections else None
    books = queries.get_all()
    if books:
        target = books[0]
        target.path = ""
        queries.update(target)
        author_id = target.author_id
        collection_id = target.collection_id or collection_id
    else:
        queries.insert(
            Book(
                title="Empty Path Book",
                path="",
                author_id=None,
                collection_id=collection_id,
            )
        )
        author_id = None
    queries.insert(
        Book(
            title="Missing Path Book",
            path=str(tmp_path / "does_not_exist"),
            author_id=author_id,
            collection_id=collection_id,
        )
    )

    window = PathHealthWindow(temp_db, ui_scaler, theme_manager, parent=None)
    qtbot.addWidget(window)
    if collection_id is not None:
        idx = window.collection_combo.findData(collection_id)
        if idx >= 0:
            window.collection_combo.setCurrentIndex(idx)
    window.filter_combo.setCurrentIndex(
        window.filter_combo.findData(FILTER_MISSING)
    )
    progress_shown: list[ImportProgressWindow] = []
    real_show = ImportProgressWindow.show

    def track_show(self):
        progress_shown.append(self)
        return real_show(self)

    ImportProgressWindow.show = track_show  # type: ignore[method-assign]
    try:
        window.run_scan()
    finally:
        ImportProgressWindow.show = real_show  # type: ignore[method-assign]
    assert progress_shown
    assert window.progress_window is None
    assert not window._is_scanning
    statuses = {row.status for row in window._rows}
    assert STATUS_EMPTY in statuses or STATUS_MISSING in statuses
    assert "Valid" in window._last_scan_status or "valid" in window._last_scan_status
    window.filter_combo.setCurrentIndex(
        window.filter_combo.findData(FILTER_INCORRECT)
    )
    window.run_scan()
    assert all(row.status == STATUS_INCORRECT for row in window._rows)
    assert window.table.columnCount() == 4
    assert window.table.horizontalHeaderItem(0).text() == "Author"
    assert window.table.horizontalHeaderItem(window.COL_ERROR).text() == "Error"
    assert window.table.horizontalHeaderItem(window.COL_PATH).text() == "Path"
    assert window.COL_ERROR == window.COL_PATH - 1
    window.close()


def test_path_health_window_cancel_keeps_partial(
    temp_db, ui_scaler, theme_manager, qtbot, tmp_path
):
    from src.database.models import Book
    from src.database.queries import BookQueries, CollectionQueries
    from src.ui.import_progress_window import ImportProgressWindow
    from src.ui.path_health_window import PathHealthWindow

    queries = BookQueries(temp_db)
    collections = CollectionQueries(temp_db).get_all(active_only=True)
    collection_id = collections[0].collection_id if collections else None
    author_id = None
    for i in range(8):
        queries.insert(
            Book(
                title=f"Cancel Book {i}",
                path="" if i % 2 == 0 else str(tmp_path / f"missing_{i}"),
                author_id=author_id,
                collection_id=collection_id,
            )
        )

    window = PathHealthWindow(temp_db, ui_scaler, theme_manager, parent=None)
    qtbot.addWidget(window)
    if collection_id is not None:
        idx = window.collection_combo.findData(collection_id)
        if idx >= 0:
            window.collection_combo.setCurrentIndex(idx)
    window.filter_combo.setCurrentIndex(
        window.filter_combo.findData(FILTER_MISSING)
    )

    real_show = ImportProgressWindow.show

    def show_and_cancel(self):
        self._cancel_requested = True
        return real_show(self)

    ImportProgressWindow.show = show_and_cancel  # type: ignore[method-assign]
    try:
        window.run_scan()
    finally:
        ImportProgressWindow.show = real_show  # type: ignore[method-assign]

    assert window.progress_window is None
    assert not window._is_scanning
    assert window._last_scan_status.startswith("Canceled")
    window.close()
