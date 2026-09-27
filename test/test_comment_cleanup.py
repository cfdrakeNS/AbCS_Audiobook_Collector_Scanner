"""Tests for removing iTunes technical tag data from comments."""

import importlib.util
import sqlite3
from pathlib import Path
from types import SimpleNamespace

from mutagen.id3 import COMM, ID3, TALB

from src.core.comment_cleanup import (
    clean_comment_text,
    is_technical_comment_frame,
    is_technical_comment_piece,
)
from src.core.tag_reader import AudioFileInfo, TagReader

ITUN_NORM = (
    "0000028A 0000028A 00002C35 00002C35 0000969C 0000969C "
    "0000A9F4 0000A9F4 0001DA7D 0001DA7D"
)
ITUN_SMPB = (
    "00000000 00000210 00000870 000000000075B700 00000000 00220749 "
    "00000000 00000000 00000000 00000000 00000000 00000000"
)
CDDB_DISC = "4711E807+343975+7+150+2660+18181+36113+123183+196941+249327"
CDDB_IDS = "22+813AEE62CA3EACE9668FF7396BC3995C+12573191"


def test_technical_frame_descriptions():
    for desc in ("iTunNORM", "iTunSMPB", "iTunPGAP", "iTunes_CDDB_1", "ITUNES_CDDB_IDS"):
        assert is_technical_comment_frame(desc)
    for desc in ("", "Description", "Comment", None):
        assert not is_technical_comment_frame(desc)


def test_technical_pieces():
    for piece in (ITUN_NORM, ITUN_SMPB, CDDB_DISC, CDDB_IDS):
        assert is_technical_comment_piece(piece)
    for piece in ("1999", "12", "Read by Jim Dale", "ISBN 9780140449136", "DEADBEEF"):
        assert not is_technical_comment_piece(piece)


def test_tool_frame_descriptions():
    for desc in ("MusicBrainz Album Id", "Acoustid Id", "Encoder", "Encoded by", "CDDB"):
        assert is_technical_comment_frame(desc)


def test_musicbrainz_and_tool_stamps_are_technical():
    for piece in (
        "b1a9c0e9-d987-4042-ae91-78d6a3267d69",
        "MusicBrainz Album Id: b1a9c0e9-d987-4042-ae91-78d6a3267d69",
        "LAME3.99r",
        "Lavf58.29.100",
        "iTunes 12.3.1.23",
        "iTunes v7.6.2",
        "fre:ac - free audio converter <https://www.freac.org/>",
        "http://online-audio-converter.com",
        "Exact Audio Copy V1.0 beta 3",
        "dBpoweramp Release 16.1",
        "Encoded with Nero",
    ):
        assert is_technical_comment_piece(piece), piece


def test_real_text_with_links_or_tool_words_is_kept():
    for piece in (
        "http://www.archive.org/details/leavenworth_case_librivox",
        "Released under a Creative Commons license. Visit us at http://pseudopod.org",
        "Encoder..................Fraunhofer [FhG] (Guess)",
        "Unabridged Audible Rip by Chapters -- Series: Joe Pickett, Book 16",
        "iTunes exclusive edition",
    ):
        assert not is_technical_comment_piece(piece), piece


def test_converter_stamp_removed_from_plot():
    text = "A fine plot.; fre:ac - free audio converter <https://www.freac.org/>"
    assert clean_comment_text(text) == "A fine plot."


def test_mp3_import_skips_musicbrainz_comment_frames():
    tags = ID3()
    tags.add(COMM(encoding=3, lang="eng", desc="", text=["The real plot."]))
    tags.add(
        COMM(
            encoding=3,
            lang="eng",
            desc="MusicBrainz Album Id",
            text=["b1a9c0e9-d987-4042-ae91-78d6a3267d69"],
        )
    )
    info = AudioFileInfo()
    TagReader()._read_mp3_tags(SimpleNamespace(tags=tags), info)
    assert info.comment == "The real plot."


def test_text_without_technical_data_is_unchanged():
    for text in (
        "",
        "A plain plot.",
        "Plot one; plot two",
        "Series; ; 12",
        "Paragraph one.\n\nParagraph two.",
    ):
        assert clean_comment_text(text) == text


def test_only_technical_data_becomes_empty():
    text = f"{ITUN_NORM}; {ITUN_SMPB}; ; 14++; ; {CDDB_DISC}; 1; 2"
    assert clean_comment_text(text) == ""


def test_real_text_is_kept():
    text = f"The plot of the book; {ITUN_NORM}; {CDDB_IDS}; 3; Ann Rule; Ann Rule"
    assert clean_comment_text(text) == "The plot of the book; Ann Rule"


def test_single_file_frames_joined_by_blank_lines():
    text = f"The plot of the book.\n\n{ITUN_NORM}\n\n{ITUN_SMPB}"
    assert clean_comment_text(text) == "The plot of the book."


def test_running_twice_changes_nothing_more():
    text = f"Real note; {ITUN_NORM}; 7"
    once = clean_comment_text(text)
    assert clean_comment_text(once) == once


def test_mp3_import_skips_itunes_comment_frames():
    tags = ID3()
    tags.add(TALB(encoding=3, text=["Album"]))
    tags.add(COMM(encoding=3, lang="eng", desc="", text=["The real plot."]))
    tags.add(COMM(encoding=3, lang="eng", desc="iTunNORM", text=[" " + ITUN_NORM]))
    tags.add(COMM(encoding=3, lang="eng", desc="iTunSMPB", text=[" " + ITUN_SMPB]))
    tags.add(COMM(encoding=3, lang="eng", desc="iTunes_CDDB_1", text=[CDDB_DISC]))
    tags.add(COMM(encoding=3, lang="eng", desc="iTunes_CDDB_TrackNumber", text=["3"]))
    info = AudioFileInfo()
    TagReader()._read_mp3_tags(SimpleNamespace(tags=tags), info)
    assert info.comment == "The real plot."


def test_read_file_cleans_comment_for_any_format(tmp_path, monkeypatch):
    path = tmp_path / "book.m4b"
    path.write_bytes(b"x")
    reader = TagReader()
    fake_audio = SimpleNamespace(info=SimpleNamespace(length=1.0, bitrate=64000))
    monkeypatch.setattr("src.core.tag_reader.MutagenFile", lambda _p: fake_audio)
    monkeypatch.setattr(
        reader,
        "_read_generic_tags",
        lambda audio, info: setattr(info, "comment", f"Plot\n\n{ITUN_NORM}"),
    )
    info = reader.read_file(str(path))
    assert info.read_error is None
    assert info.comment == "Plot"


def _load_cleanup_script():
    script = Path(__file__).resolve().parent.parent / "scripts" / "clean_technical_comments.py"
    spec = importlib.util.spec_from_file_location("clean_technical_comments", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_db(path):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE authors (author_id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute(
        "CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, "
        "author_id INTEGER, comments TEXT)"
    )
    conn.execute("INSERT INTO authors VALUES (1, 'Ann Rule')")
    conn.executemany(
        "INSERT INTO books VALUES (?, ?, 1, ?)",
        [
            (1, "Junk only", f"{ITUN_NORM}; {ITUN_SMPB}; 1"),
            (2, "Mixed", f"Real plot; {CDDB_DISC}"),
            (3, "Clean", "Just a note; 12"),
            (4, "Empty", ""),
        ],
    )
    conn.commit()
    conn.close()


def _comments(path):
    conn = sqlite3.connect(path)
    rows = dict(conn.execute("SELECT book_id, comments FROM books"))
    conn.close()
    return rows


def test_cleanup_script_dry_run_changes_nothing(tmp_path):
    db = tmp_path / "abcs.db"
    _make_db(db)
    before = _comments(db)
    assert _load_cleanup_script().run_update(db, dry_run=True) == 0
    assert _comments(db) == before
    assert not list(tmp_path.glob("abcs.bak.*.db"))


def test_cleanup_script_apply_backs_up_and_cleans(tmp_path):
    db = tmp_path / "abcs.db"
    _make_db(db)
    script = _load_cleanup_script()
    assert script.run_update(db, dry_run=False) == 0
    assert len(list(tmp_path.glob("abcs.bak.*.db"))) == 1
    assert _comments(db) == {
        1: "",
        2: "Real plot",
        3: "Just a note; 12",
        4: "",
    }
    report = tmp_path / "report.txt"
    script.run_update(db, dry_run=True, report_path=report)
    assert "Books: 0" in report.read_text(encoding="utf-8")
