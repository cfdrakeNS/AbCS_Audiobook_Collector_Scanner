"""Listen finds book-list titles under the collection folder by import layout."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.core.audio_launcher import resolve_preview_playlist, resolve_preview_source
from src.core.library_root import find_book_under_collection


@pytest.fixture
def empty_book_db(tmp_path):
    from src.database.connection import DatabaseManager
    from src.database.models import Book
    from src.database.queries import AuthorQueries, BookQueries, CollectionQueries

    db = DatabaseManager(str(tmp_path / "listen_lookup.db"))
    db.initialize_database()
    author_id = AuthorQueries(db).insert("Lee Child")
    collection_id = CollectionQueries(db).get_all()[0].collection_id
    book_id = BookQueries(db).insert(
        Book(title="Killing Floor", author_id=author_id, collection_id=collection_id)
    )
    try:
        yield db, book_id
    finally:
        db.close()


def _audio(folder, name="01.mp3"):
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_bytes(b"x")
    return path


def test_blank_path_finds_author_title_folder(tmp_path):
    book_dir = tmp_path / "Lee Child" / "Killing Floor"
    track = _audio(book_dir)

    playlist = resolve_preview_playlist(
        "",
        collection_root=str(tmp_path),
        author_name="lee child",
        book_title="KILLING FLOOR",
    )

    assert playlist.error == ""
    assert playlist.files == (track,)
    assert playlist.found_path == str(book_dir)


def test_missing_stored_path_finds_author_title_folder(tmp_path):
    book_dir = tmp_path / "Lee Child" / "Killing Floor"
    _audio(book_dir)

    target = resolve_preview_source(
        "Z:/Old Drive/Unrelated/Folder",
        collection_root=str(tmp_path),
        author_name="Lee Child",
        book_title="Killing Floor",
    )
    assert target.path == book_dir / "01.mp3"
    assert target.found_path == str(book_dir)


def test_title_file_in_author_folder_and_title_folder_in_series(tmp_path):
    author = tmp_path / "Author"
    single = _audio(author, "Stand Alone.m4b")
    series_book = tmp_path / "Author" / "Saga" / "Book Two"
    _audio(series_book)

    assert find_book_under_collection(
        str(tmp_path), "Author", "Stand Alone"
    ) == str(single)
    assert find_book_under_collection(
        str(tmp_path), "Author", "Book Two", "Saga"
    ) == str(series_book)


def test_title_file_in_series_folder(tmp_path):
    series_file = _audio(tmp_path / "Author" / "Saga", "Book One.m4b")
    loose = tmp_path / "Author" / "Standalone"
    _audio(loose)

    assert find_book_under_collection(
        str(tmp_path), "Author", "Book One", "Saga"
    ) == str(series_file)
    assert find_book_under_collection(
        str(tmp_path), "Author", "Standalone"
    ) == str(loose)


def test_author_folder_wins_over_series_folder(tmp_path):
    in_author = tmp_path / "Author" / "Book One"
    _audio(in_author)
    _audio(tmp_path / "Author" / "Saga" / "Book One")

    assert find_book_under_collection(
        str(tmp_path), "Author", "Book One", "Saga"
    ) == str(in_author)


def test_series_named_like_book_searches_inside_series_folder(tmp_path):
    series_dir = tmp_path / "Frank Herbert" / "Dune"
    book_dir = series_dir / "1 - Dune"
    _audio(book_dir)
    _audio(series_dir / "2 - Dune Messiah")

    assert find_book_under_collection(
        str(tmp_path), "Frank Herbert", "Dune", "Dune", series_number=1
    ) == str(book_dir)


def _sand_storm_file(root):
    return _audio(
        root / "Michael R. Stern" / "Quantum Touch",
        "2 Sand Storm(Quantum Touch 02).m4b",
    )


@pytest.mark.parametrize("series_number", [2, None])
def test_series_tag_file_in_series_folder(tmp_path, series_number):
    track = _sand_storm_file(tmp_path)

    assert find_book_under_collection(
        str(tmp_path),
        "Michael R. Stern",
        "Sand Storm",
        "Quantum Touch",
        series_number=series_number,
    ) == str(track)


def test_series_tag_file_wrong_number_is_not_used(tmp_path):
    _sand_storm_file(tmp_path)

    assert find_book_under_collection(
        str(tmp_path),
        "Michael R. Stern",
        "Sand Storm",
        "Quantum Touch",
        series_number=3,
    ) == ""


def test_series_tag_folder_and_listen_saves_found_path(tmp_path):
    book_dir = tmp_path / "Michael R. Stern" / "Quantum Touch" / "Sand Storm (Quantum Touch 02)"
    _audio(book_dir)

    playlist = resolve_preview_playlist(
        "",
        collection_root=str(tmp_path),
        author_name="Michael R. Stern",
        book_title="Sand Storm",
        series_name="Quantum Touch",
        series_number=2,
    )

    assert playlist.error == ""
    assert playlist.found_path == str(book_dir)


@pytest.mark.parametrize("name", ["10 - Test", "01 Test", "1.Test"])
@pytest.mark.parametrize("series", ["", "Saga"])
def test_leading_number_folders_and_files(tmp_path, name, series):
    parent = tmp_path / "Author" / series if series else tmp_path / "Author"
    folder = parent / name
    _audio(folder)

    assert find_book_under_collection(
        str(tmp_path), "Author", "Test", series
    ) == str(folder)

    other = tmp_path / "other"
    file_parent = other / "Author" / series if series else other / "Author"
    track = _audio(file_parent, f"{name}.m4b")
    assert find_book_under_collection(
        str(other), "Author", "Test", series
    ) == str(track)


def test_title_tag_without_number_is_ignored(tmp_path):
    folder = tmp_path / "Melissa Brayden" / "Heart Block"
    _audio(folder)

    assert find_book_under_collection(
        str(tmp_path), "Melissa Brayden", "Heart Block (unabridged)"
    ) == str(folder)


def test_folder_and_file_tags_without_number_are_ignored(tmp_path):
    folder = tmp_path / "Author" / "Glass Harbor [Unabridged]"
    _audio(folder)
    assert find_book_under_collection(
        str(tmp_path), "Author", "Glass Harbor"
    ) == str(folder)

    other = tmp_path / "other"
    track = _audio(other / "Author" / "Tide Runner", "2 Copper Bridge (Unabridged).m4b")
    assert find_book_under_collection(
        str(other), "Author", "Copper Bridge", "Tide Runner", series_number=2
    ) == str(track)


def test_no_series_finds_title_file_one_folder_down(tmp_path):
    track = _audio(tmp_path / "A L Fraine" / "Rob Loxley", "1 For An Eye.m4b")
    _audio(tmp_path / "A L Fraine" / "Rob Loxley", "1 Hell To Pay.m4b")

    assert find_book_under_collection(
        str(tmp_path), "A L Fraine", "For An Eye"
    ) == str(track)


def test_two_plain_tag_folders_are_not_guessed(tmp_path):
    _audio(tmp_path / "Author" / "Glass Harbor (Abridged)")
    _audio(tmp_path / "Author" / "Glass Harbor (Unabridged)")

    assert find_book_under_collection(str(tmp_path), "Author", "Glass Harbor") == ""


def test_series_folder_with_loose_audio_is_not_the_book(tmp_path):
    _audio(tmp_path / "Author" / "Saga")

    assert find_book_under_collection(
        str(tmp_path), "Author", "Book One", "Saga"
    ) == ""


@pytest.mark.parametrize(
    "folder_name",
    ["03 - Killing Floor", "3 Killing Floor", "3-  Killing Floor", "Killing Floor - 03"],
)
def test_numbered_title_folder_matches(tmp_path, folder_name):
    book_dir = tmp_path / "Lee Child" / folder_name
    _audio(book_dir)

    assert find_book_under_collection(
        str(tmp_path), "Lee Child", "Killing Floor"
    ) == str(book_dir)
    assert find_book_under_collection(
        str(tmp_path),
        "Lee Child",
        "Killing Floor",
        series_number=3,
    ) == str(book_dir)


def test_numbered_title_folder_matches_decimal_and_title_suffix(tmp_path):
    busted = tmp_path / "Author" / "6.5 - Busted"
    _audio(busted)
    foo = tmp_path / "Author" / "03 - Foo"
    _audio(foo)

    assert find_book_under_collection(
        str(tmp_path), "Author", "Busted", series_number=6.5
    ) == str(busted)
    assert find_book_under_collection(
        str(tmp_path), "Author", "Foo - 03"
    ) == str(foo)


def test_numbered_title_folder_wrong_series_number_is_not_used(tmp_path):
    _audio(tmp_path / "Lee Child" / "03 - Killing Floor")

    assert find_book_under_collection(
        str(tmp_path),
        "Lee Child",
        "Killing Floor",
        series_number=4,
    ) == ""


def test_numbered_siblings_pick_by_series_number_only(tmp_path):
    author = tmp_path / "Author"
    _audio(author / "01 - Saga Book")
    second = author / "02 - Saga Book"
    _audio(second)

    assert find_book_under_collection(
        str(tmp_path), "Author", "Saga Book", series_number=2
    ) == str(second)
    assert find_book_under_collection(
        str(tmp_path), "Author", "Saga Book"
    ) == ""


def test_title_folder_without_number_is_not_split(tmp_path):
    book_dir = tmp_path / "George Orwell" / "1984"
    _audio(book_dir)

    assert find_book_under_collection(
        str(tmp_path), "George Orwell", "1984"
    ) == str(book_dir)


def test_numbered_single_file_in_author_folder(tmp_path):
    single = _audio(tmp_path / "Author", "02 - Stand Alone.m4b")

    assert find_book_under_collection(
        str(tmp_path), "Author", "Stand Alone"
    ) == str(single)


def test_unnamed_series_folder_found_when_book_has_no_series(tmp_path):
    book_dir = tmp_path / "Patricia Cornwell" / "Kay Scarpetta Series" / "1-  Postmortem"
    _audio(book_dir)

    playlist = resolve_preview_playlist(
        "",
        collection_root=str(tmp_path),
        author_name="Patricia Cornwell",
        book_title="Postmortem",
    )

    assert playlist.error == ""
    assert playlist.found_path == str(book_dir)


def test_unnamed_series_folder_not_searched_when_book_has_series(tmp_path):
    _audio(tmp_path / "John Sandford" / "Virgil Flowers Series" / "4 Bad Blood")

    assert find_book_under_collection(
        str(tmp_path), "John Sandford", "Bad Blood", "Virgil Flowers"
    ) == ""


def test_same_title_in_two_subfolders_is_not_guessed(tmp_path):
    author = tmp_path / "Author"
    _audio(author / "Series A" / "1 Same Title")
    _audio(author / "Series B" / "2 Same Title")

    assert find_book_under_collection(
        str(tmp_path), "Author", "Same Title"
    ) == ""


def test_title_missing_names_author_folder(tmp_path):
    author_dir = tmp_path / "Lee Child"
    _audio(author_dir / "Killing Floor")

    playlist = resolve_preview_playlist(
        "",
        collection_root=str(tmp_path),
        author_name="Lee Child",
        book_title="Die Trying",
    )

    assert playlist.files == ()
    assert playlist.found_path == ""
    assert playlist.error == (
        'Author folder found. Book title "Die Trying" was not found '
        f"in the collection folder - {author_dir}."
    )
    assert playlist.browse_dir == str(author_dir)


def test_author_missing_names_collection_folder(tmp_path):
    _audio(tmp_path / "Lee Child" / "Killing Floor")

    playlist = resolve_preview_playlist(
        "",
        collection_root=str(tmp_path),
        author_name="Ian Rankin",
        book_title="Knots and Crosses",
        collection_name="Audiobooks",
    )

    assert playlist.error == (
        'Author folder "Ian Rankin" was not found in the Audiobooks '
        f"collection folder - {tmp_path}."
    )
    assert playlist.browse_dir == str(tmp_path)


def test_missing_collection_folder_says_how_to_fix(tmp_path):
    missing_root = tmp_path / "Moved Drive"

    playlist = resolve_preview_playlist(
        "",
        collection_root=str(missing_root),
        author_name="Lee Child",
        book_title="Killing Floor",
        collection_name="Audiobooks",
    )

    assert playlist.error == (
        f"The Audiobooks collection folder is missing - {missing_root}. "
        "To fix, open Manage > Collections, edit the collection, "
        "and set the collection folder."
    )
    assert playlist.browse_dir == ""


def test_collection_folder_without_audio_reports_author_folder(tmp_path):
    (tmp_path / "notes.txt").write_text("not audio", encoding="utf-8")
    (tmp_path / "Other Author").mkdir()

    playlist = resolve_preview_playlist(
        "",
        collection_root=str(tmp_path),
        author_name="Lee Child",
        book_title="Killing Floor",
        collection_name="Audiobooks",
    )

    assert playlist.error == (
        'Author folder "Lee Child" was not found in the Audiobooks '
        f"collection folder - {tmp_path}."
    )
    assert playlist.browse_dir == str(tmp_path)


def test_series_missing_names_author_folder(tmp_path):
    author_dir = tmp_path / "Author"
    _audio(author_dir / "Other Saga" / "Book One")

    playlist = resolve_preview_playlist(
        "",
        collection_root=str(tmp_path),
        author_name="Author",
        book_title="Book One",
        series_name="Saga",
    )

    assert playlist.error == (
        'Author folder found. Series folder "Saga" was not found '
        f"in the collection folder - {author_dir}."
    )
    assert playlist.browse_dir == str(author_dir)


def _fake_player(monkeypatch):
    class Signal:
        def connect(self, *_args, **_kwargs):
            return None

    class FakePlayer:
        class PlaybackState:
            StoppedState = 0
            PlayingState = 1
            PausedState = 2

        def __init__(self):
            self.playbackStateChanged = Signal()
            self.errorOccurred = Signal()
            self.mediaStatusChanged = Signal()
            self.positionChanged = Signal()
            self._state = 0

        def setAudioOutput(self, *_args):
            return None

        def setSource(self, *_args):
            return None

        def setPlaybackRate(self, *_args):
            return None

        def setPosition(self, *_args):
            return None

        def position(self):
            return 0

        def duration(self):
            return 0

        def play(self):
            self._state = 1

        def pause(self):
            self._state = 2

        def stop(self):
            self._state = 0

        def playbackState(self):
            return self._state

    class FakeAudio:
        pass

    monkeypatch.setattr("PySide6.QtMultimedia.QMediaPlayer", FakePlayer)
    monkeypatch.setattr("PySide6.QtMultimedia.QAudioOutput", FakeAudio)


def test_browse_prompt_hides_close_and_escape_closes(qapp, ui_scaler, monkeypatch):
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

    from src.ui import preview_window

    seen = {}
    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        staticmethod(lambda *_args, **_kwargs: "should not browse"),
    )

    def press_escape():
        box = QApplication.activeModalWidget()
        assert isinstance(box, QMessageBox)
        seen["close_visible"] = box.button(QMessageBox.Close).isVisible()
        seen["browse_visible"] = box.button(QMessageBox.Open).isVisible()
        seen["text"] = box.text()
        QTest.keyClick(box, Qt.Key_Escape)

    QTimer.singleShot(50, press_escape)
    chosen = preview_window.browse_for_book_folder(None, ui_scaler, "Not found.", "")

    assert chosen == ""
    assert seen["close_visible"] is False
    assert seen["browse_visible"] is True
    assert seen["text"].endswith("Press Escape to close.")


def _browse_reply(monkeypatch, reply, chosen=""):
    from PySide6.QtWidgets import QFileDialog

    from src.ui import preview_window

    asked = []

    def fake_box(*_args, **kwargs):
        asked.append(kwargs.get("text", ""))
        return reply

    monkeypatch.setattr(preview_window, "exec_styled_message_box", fake_box)
    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        staticmethod(lambda *_args, **_kwargs: chosen),
    )
    return asked


def _close_open_preview():
    from src.ui import preview_window

    if preview_window._open_preview is not None:
        preview_window._open_preview.close()
        preview_window._open_preview = None


def test_browse_saves_chosen_folder_and_plays(
    empty_book_db, tmp_path, ui_scaler, theme_manager, monkeypatch
):
    from PySide6.QtWidgets import QMessageBox

    from src.database.queries import BookQueries
    from src.ui.preview_window import show_preview

    db, book_id = empty_book_db
    library = tmp_path / "library"
    (library / "Lee Child").mkdir(parents=True)
    elsewhere = tmp_path / "elsewhere" / "KF"
    _audio(elsewhere)
    _fake_player(monkeypatch)
    asked = _browse_reply(monkeypatch, QMessageBox.Open, str(elsewhere))
    book = SimpleNamespace(
        book_id=book_id, path="", listen_file_name="", listen_position_ms=None
    )

    ok, _message = show_preview(
        None,
        "",
        ui_scaler,
        theme_manager,
        book_title="Killing Floor",
        author_name="Lee Child",
        collection_root=str(library),
        book=book,
        db=db,
    )
    _close_open_preview()

    assert ok is True
    assert "Book title" in asked[0]
    assert book.path == str(elsewhere)
    assert BookQueries(db).get_by_id(book_id).path == str(elsewhere)


def test_close_leaves_path_blank(
    empty_book_db, tmp_path, ui_scaler, theme_manager, monkeypatch
):
    from PySide6.QtWidgets import QMessageBox

    from src.database.queries import BookQueries
    from src.ui.preview_window import show_preview

    db, book_id = empty_book_db
    library = tmp_path / "library"
    (library / "Lee Child").mkdir(parents=True)
    _browse_reply(monkeypatch, QMessageBox.Close, str(tmp_path))
    book = SimpleNamespace(
        book_id=book_id, path="", listen_file_name="", listen_position_ms=None
    )

    ok, message = show_preview(
        None,
        "",
        ui_scaler,
        theme_manager,
        book_title="Killing Floor",
        author_name="Lee Child",
        collection_root=str(library),
        book=book,
        db=db,
    )

    assert ok is False
    assert message == ""
    assert book.path == ""
    assert not BookQueries(db).get_by_id(book_id).path


def test_lookup_ignores_import_scenario_preference(tmp_path, monkeypatch):
    from PySide6.QtCore import QSettings

    monkeypatch.setattr(
        QSettings, "value", lambda self, key, default=None, **_kw: "single_item"
    )
    book_dir = tmp_path / "Lee Child" / "Killing Floor"
    _audio(book_dir)

    playlist = resolve_preview_playlist(
        "",
        collection_root=str(tmp_path),
        author_name="Lee Child",
        book_title="Killing Floor",
    )

    assert playlist.found_path == str(book_dir)


def test_found_path_is_saved_on_book(empty_book_db, tmp_path):
    from src.database.queries import BookQueries
    from src.ui.preview_window import save_found_book_path

    db, book_id = empty_book_db
    book = SimpleNamespace(book_id=book_id, path="")
    found = str(tmp_path / "Lee Child" / "Killing Floor")

    assert save_found_book_path(book, db, found) is True
    assert book.path == found
    assert BookQueries(db).get_by_id(book_id).path == found


def _blank_stats_book(book_id, **values):
    fields = dict(time_hours=0, time_minutes=0, tracks=0, size_mb=0.0, bitrate=0)
    fields.update(values)
    return SimpleNamespace(book_id=book_id, **fields)


def test_single_file_fills_length_size_bitrate_and_one_track(
    empty_book_db, tmp_path, monkeypatch
):
    from src.core import tag_reader
    from src.database.queries import BookQueries
    from src.ui.preview_window import fill_missing_book_stats

    db, book_id = empty_book_db
    track = _audio(tmp_path / "Book", "book.m4b")

    def fake_read(_self, _path):
        info = tag_reader.AudioFileInfo()
        info.duration_seconds = 2 * 3600 + 5 * 60 + 30
        info.file_size_bytes = 50 * 1024 * 1024
        info.bitrate = 64
        return info

    monkeypatch.setattr(tag_reader.TagReader, "read_file", fake_read)
    book = _blank_stats_book(book_id)

    assert fill_missing_book_stats(book, db, (track,)) is True
    saved = BookQueries(db).get_by_id(book_id)
    assert (saved.time_hours, saved.time_minutes) == (2, 5)
    assert saved.tracks == 1
    assert saved.size_mb == pytest.approx(50.0)
    assert saved.bitrate == 64
    assert (book.time_hours, book.tracks) == (2, 1)


def test_multi_file_sets_only_track_count(empty_book_db, tmp_path, monkeypatch):
    from src.core import tag_reader
    from src.database.queries import BookQueries
    from src.ui.preview_window import fill_missing_book_stats

    db, book_id = empty_book_db
    folder = tmp_path / "Book"
    files = tuple(_audio(folder, f"{n:02d}.mp3") for n in range(1, 4))

    def no_tags(*_args):
        raise AssertionError("tags should not be read for a multi-file book")

    monkeypatch.setattr(tag_reader.TagReader, "read_file", no_tags)
    book = _blank_stats_book(book_id)

    assert fill_missing_book_stats(book, db, files) is True
    saved = BookQueries(db).get_by_id(book_id)
    assert saved.tracks == 3
    assert (saved.time_hours, saved.time_minutes) == (0, 0)


def test_book_with_length_and_tracks_is_left_alone(empty_book_db, tmp_path):
    from src.ui.preview_window import fill_missing_book_stats

    db, book_id = empty_book_db
    track = _audio(tmp_path / "Book", "book.m4b")
    book = _blank_stats_book(book_id, time_hours=9, time_minutes=1, tracks=4)

    assert fill_missing_book_stats(book, db, (track,)) is False
    assert book.tracks == 4
