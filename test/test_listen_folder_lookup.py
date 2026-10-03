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
        import_scenario="mass_standard",
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
        import_scenario="mass_standard",
    )
    assert target.path == book_dir / "01.mp3"
    assert target.found_path == str(book_dir)


def test_mass_standard_title_file_and_series_folder(tmp_path):
    author = tmp_path / "Author"
    single = _audio(author, "Stand Alone.m4b")
    series_book = tmp_path / "Author" / "Saga" / "Book Two"
    _audio(series_book)

    assert find_book_under_collection(
        str(tmp_path), "Author", "Stand Alone", scenario="mass_standard"
    ) == str(single)
    assert find_book_under_collection(
        str(tmp_path), "Author", "Book Two", "Saga", scenario="series_from_filename"
    ) == str(series_book)


def test_series_from_directory_uses_series_folder(tmp_path):
    series_dir = tmp_path / "Author" / "Saga"
    _audio(series_dir)
    loose = tmp_path / "Author" / "Standalone"
    _audio(loose)

    assert find_book_under_collection(
        str(tmp_path), "Author", "Book One", "Saga", scenario="series_from_directory"
    ) == str(series_dir)
    assert find_book_under_collection(
        str(tmp_path), "Author", "Standalone", scenario="series_from_directory"
    ) == str(loose)


def test_nested_series_uses_series_title_folder(tmp_path):
    nested = tmp_path / "Author" / "Saga" / "Book One"
    _audio(nested)

    assert find_book_under_collection(
        str(tmp_path),
        "Author",
        "Book One",
        "Saga",
        scenario="series_from_directory_nested",
    ) == str(nested)


def test_title_missing_names_author_folder(tmp_path):
    author_dir = tmp_path / "Lee Child"
    _audio(author_dir / "Killing Floor")

    playlist = resolve_preview_playlist(
        "",
        collection_root=str(tmp_path),
        author_name="Lee Child",
        book_title="Die Trying",
        import_scenario="mass_standard",
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
        import_scenario="mass_standard",
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
        import_scenario="mass_standard",
        collection_name="Audiobooks",
    )

    assert playlist.error == (
        f"The Audiobooks collection folder is missing - {missing_root}. "
        "To fix, open Manage > Collections, edit the collection, "
        "and set the collection folder."
    )
    assert playlist.browse_dir == ""


def test_collection_folder_without_audio_says_how_to_fix(tmp_path):
    (tmp_path / "notes.txt").write_text("not audio", encoding="utf-8")
    (tmp_path / "Other Author").mkdir()

    playlist = resolve_preview_playlist(
        "",
        collection_root=str(tmp_path),
        author_name="Lee Child",
        book_title="Killing Floor",
        import_scenario="mass_standard",
        collection_name="Audiobooks",
    )

    assert playlist.error == (
        f"The Audiobooks collection folder has no audiobook files - {tmp_path}. "
        "It may be the wrong folder. To fix, open Manage > Collections, "
        "edit the collection, and set the collection folder."
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
        import_scenario="series_from_directory_nested",
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


def test_single_item_scenario_does_not_guess(tmp_path):
    _audio(tmp_path / "Lee Child" / "Killing Floor")

    playlist = resolve_preview_playlist(
        "",
        collection_root=str(tmp_path),
        author_name="Lee Child",
        book_title="Killing Floor",
        import_scenario="single_item",
    )

    assert playlist.files == ()
    assert playlist.error == (
        "This book has no file path. The Single Author / Book Import layout "
        "has no author folders, so Listen cannot look for it in the "
        "collection folder."
    )
    assert playlist.browse_dir == str(tmp_path)


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
