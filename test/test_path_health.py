"""Unit tests for Check Books Path scan (Phase 25 / F01)."""

from __future__ import annotations

from types import SimpleNamespace

from src.core.path_health import (
    FILTER_ALL,
    FILTER_INCORRECT,
    FILTER_MISSING,
    STATUS_EMPTY,
    STATUS_INCORRECT,
    STATUS_MISSING,
    STATUS_OK,
    PathHealthCounts,
    check_book_path,
    iter_book_path_checks,
    scan_book_paths,
    summarize_statuses,
)


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
    """Same case as Michael R. Stern: stored drive/folder renamed; Play remaps."""
    root = tmp_path / "zLibrary"
    book = root / "Michael R. Stern" / "Title"
    book.mkdir(parents=True)
    (book / "track.mp3").write_bytes(b"x")
    stale = tmp_path / "Library" / "Michael R. Stern" / "Title"
    assert not stale.exists()
    assert check_book_path(str(stale), str(root)) == STATUS_INCORRECT
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
    assert [r.book_id for r in incorrect_rows] == [3, 5]
    assert all(r.status == STATUS_INCORRECT for r in incorrect_rows)
    assert incorrect_rows[1].resolved_path

    all_rows = scan_book_paths(books, collection_root=root, filter_key=FILTER_ALL)
    assert [r.book_id for r in all_rows] == [1, 2, 3, 5]
    assert STATUS_OK not in {r.status for r in all_rows}

    counts = summarize_statuses(all_rows)
    assert counts[STATUS_EMPTY] == 1
    assert counts[STATUS_MISSING] == 1
    assert counts[STATUS_INCORRECT] == 2
    assert counts[STATUS_OK] == 0


def test_path_health_counts_mixed():
    counts = PathHealthCounts()
    for status in (
        STATUS_EMPTY,
        STATUS_MISSING,
        STATUS_INCORRECT,
        STATUS_OK,
        STATUS_OK,
    ):
        counts.record(status)
    assert counts.missing == 2
    assert counts.incorrect == 1
    assert counts.valid == 2
    assert counts.processed == 5


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
    assert [r.status for r in rows] == [STATUS_INCORRECT, STATUS_INCORRECT]


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
    assert window.table.columnCount() == 3
    assert window.table.horizontalHeaderItem(0).text() == "Author"
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
