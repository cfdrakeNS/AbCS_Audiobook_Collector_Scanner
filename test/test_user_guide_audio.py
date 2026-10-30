"""scripts/generate_user_docs_odt.py --audio: concurrency, reuse, renames, cleanup.

edge-tts is replaced with a fake, so these tests need no internet.
"""

from __future__ import annotations

import asyncio
import importlib.util
import sys
import types
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "generate_user_docs_odt.py"


@pytest.fixture(scope="module")
def guide():
    spec = importlib.util.spec_from_file_location("generate_user_docs_odt", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    # Dataclasses look the module up by name while it loads.
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        yield module
    finally:
        sys.modules.pop(spec.name, None)


class FakeTts:
    """Stands in for the edge_tts module and records every synthesis."""

    def __init__(self):
        self.made: list[str] = []
        self.fail_texts: set[str] = set()
        # Marker text to number of times the service refuses it before it works.
        self.busy: dict[str, int] = {}
        self.active = 0
        self.max_active = 0
        fake = self

        class Communicate:
            def __init__(self, text, voice):
                self.text = text
                self.voice = voice

            async def save(self, path):
                fake.active += 1
                fake.max_active = max(fake.max_active, fake.active)
                try:
                    await asyncio.sleep(0.01)
                    Path(path).write_bytes(b"partial")
                    if any(marker in self.text for marker in fake.fail_texts):
                        raise RuntimeError("service refused")
                    for marker, remaining in fake.busy.items():
                        if marker in self.text and remaining:
                            fake.busy[marker] = remaining - 1
                            raise RuntimeError("No audio was received.")
                    Path(path).write_text(f"{self.voice}|{self.text}", encoding="utf-8")
                    name = Path(path).name
                    assert name.endswith(".part"), "MP3 must be written under a temporary name"
                    fake.made.append(name[: -len(".part")])
                finally:
                    fake.active -= 1

        self.module = types.ModuleType("edge_tts")
        self.module.Communicate = Communicate


@pytest.fixture
def tts(monkeypatch, guide):
    fake = FakeTts()
    monkeypatch.setitem(sys.modules, "edge_tts", fake.module)
    monkeypatch.setattr(guide, "RETRY_DELAYS_SECONDS", (0, 0, 0))
    return fake


def _use_topics(monkeypatch, guide, items):
    """``items`` is a list of (title, body text) in help order."""
    topics = [
        guide.Topic(
            filename=f"{index:02d}_t.md",
            title=title,
            bookmark="",
            blocks=[guide.Heading(1, title), guide.Paragraph(body)],
        )
        for index, (title, body) in enumerate(items, start=1)
    ]
    monkeypatch.setattr(guide, "load_topics", lambda: topics)


def _mp3s(folder: Path) -> list[str]:
    return sorted(path.name for path in folder.glob("*.mp3"))


def test_unchanged_text_is_reused(tmp_path, monkeypatch, guide, tts):
    _use_topics(monkeypatch, guide, [("Alpha", "First."), ("Beta", "Second.")])
    assert guide.build_audio(tmp_path, "voice-a", make_mp3=True) == 0
    assert sorted(tts.made) == ["01 Alpha.mp3", "02 Beta.mp3"]

    tts.made.clear()
    assert guide.build_audio(tmp_path, "voice-a", make_mp3=True) == 0
    assert tts.made == []
    assert _mp3s(tmp_path) == ["01 Alpha.mp3", "02 Beta.mp3"]


def test_changed_text_or_voice_is_made_again(tmp_path, monkeypatch, guide, tts):
    _use_topics(monkeypatch, guide, [("Alpha", "First."), ("Beta", "Second.")])
    guide.build_audio(tmp_path, "voice-a", make_mp3=True)

    _use_topics(monkeypatch, guide, [("Alpha", "First, edited."), ("Beta", "Second.")])
    tts.made.clear()
    guide.build_audio(tmp_path, "voice-a", make_mp3=True)
    assert tts.made == ["01 Alpha.mp3"]

    tts.made.clear()
    guide.build_audio(tmp_path, "voice-b", make_mp3=True)
    assert sorted(tts.made) == ["01 Alpha.mp3", "02 Beta.mp3"]


def test_renumbered_topic_is_renamed_not_remade(tmp_path, monkeypatch, guide, tts):
    _use_topics(monkeypatch, guide, [("Alpha", "First."), ("Beta", "Second.")])
    guide.build_audio(tmp_path, "voice-a", make_mp3=True)
    beta_audio = (tmp_path / "02 Beta.mp3").read_text(encoding="utf-8")

    _use_topics(
        monkeypatch,
        guide,
        [("Alpha", "First."), ("Glossary", "New topic."), ("Beta", "Second.")],
    )
    tts.made.clear()
    guide.build_audio(tmp_path, "voice-a", make_mp3=True)
    assert tts.made == ["02 Glossary.mp3"]
    assert (tmp_path / "03 Beta.mp3").read_text(encoding="utf-8") == beta_audio
    assert _mp3s(tmp_path) == ["01 Alpha.mp3", "02 Glossary.mp3", "03 Beta.mp3"]


def test_swapped_topics_keep_the_right_audio(tmp_path, monkeypatch, guide, tts):
    monkeypatch.setattr(
        guide,
        "load_topics",
        lambda: [
            guide.Topic("01_a.md", "One", "", [guide.Paragraph("Text A.")]),
            guide.Topic("02_b.md", "Two", "", [guide.Paragraph("Text B.")]),
        ],
    )
    guide.build_audio(tmp_path, "v", make_mp3=True)
    one = (tmp_path / "01 One.mp3").read_text(encoding="utf-8")
    two = (tmp_path / "02 Two.mp3").read_text(encoding="utf-8")

    monkeypatch.setattr(
        guide,
        "load_topics",
        lambda: [
            guide.Topic("01_b.md", "Two", "", [guide.Paragraph("Text B.")]),
            guide.Topic("02_a.md", "One", "", [guide.Paragraph("Text A.")]),
        ],
    )
    tts.made.clear()
    guide.build_audio(tmp_path, "v", make_mp3=True)
    assert tts.made == []
    assert (tmp_path / "01 Two.mp3").read_text(encoding="utf-8") == two
    assert (tmp_path / "02 One.mp3").read_text(encoding="utf-8") == one


def test_force_remakes_everything(tmp_path, monkeypatch, guide, tts):
    _use_topics(monkeypatch, guide, [("Alpha", "First."), ("Beta", "Second.")])
    guide.build_audio(tmp_path, "voice-a", make_mp3=True)
    tts.made.clear()
    guide.build_audio(tmp_path, "voice-a", make_mp3=True, force=True)
    assert sorted(tts.made) == ["01 Alpha.mp3", "02 Beta.mp3"]


def test_failed_topic_leaves_no_mp3_and_is_made_next_run(
    tmp_path, monkeypatch, guide, tts
):
    _use_topics(monkeypatch, guide, [("Alpha", "First."), ("Beta", "Broken.")])
    tts.fail_texts = {"Broken"}
    assert guide.build_audio(tmp_path, "voice-a", make_mp3=True) == 1
    assert _mp3s(tmp_path) == ["01 Alpha.mp3"]
    assert not list(tmp_path.glob("*.part"))

    tts.fail_texts = set()
    tts.made.clear()
    assert guide.build_audio(tmp_path, "voice-a", make_mp3=True) == 0
    assert tts.made == ["02 Beta.mp3"]


def test_busy_service_is_retried_until_it_answers(tmp_path, monkeypatch, guide, tts, capsys):
    _use_topics(monkeypatch, guide, [("Alpha", "First."), ("Name List", "Busy topic.")])
    tts.busy = {"Busy topic": 3}
    assert guide.build_audio(tmp_path, "voice-a", make_mp3=True) == 0
    assert _mp3s(tmp_path) == ["01 Alpha.mp3", "02 Name List.mp3"]
    assert capsys.readouterr().err.count("retrying 02 Name List.mp3") == 3


def test_failed_progress_line_says_failed(tmp_path, monkeypatch, guide, tts, capsys):
    _use_topics(monkeypatch, guide, [("Alpha", "Broken.")])
    tts.fail_texts = {"Broken"}
    guide.build_audio(tmp_path, "voice-a", make_mp3=True)
    assert "[1/1] 01 Alpha.mp3 FAILED" in capsys.readouterr().out


def test_leftover_numbered_files_removed_other_files_kept(
    tmp_path, monkeypatch, guide, tts
):
    (tmp_path / "22 Import Explained - Under the Hood.mp3").write_bytes(b"old")
    (tmp_path / "22 Import Explained - Under the Hood.txt").write_text("old")
    (tmp_path / "abcs_userguide.odt").write_bytes(b"guide")
    (tmp_path / "notes.txt").write_text("mine")
    _use_topics(monkeypatch, guide, [("Alpha", "First.")])

    guide.build_audio(tmp_path, "voice-a", make_mp3=True)

    names = sorted(path.name for path in tmp_path.iterdir())
    assert names == [
        ".audio_manifest.json",
        "01 Alpha.mp3",
        "01 Alpha.txt",
        "abcs_userguide.odt",
        "notes.txt",
    ]


def test_text_only_leaves_existing_mp3s_alone(tmp_path, monkeypatch, guide, tts):
    (tmp_path / "09 Old Topic.mp3").write_bytes(b"old")
    _use_topics(monkeypatch, guide, [("Alpha", "First.")])
    guide.build_audio(tmp_path, "voice-a", make_mp3=False)
    assert (tmp_path / "09 Old Topic.mp3").exists()
    assert (tmp_path / "01 Alpha.txt").exists()
    assert tts.made == []


def test_jobs_limits_topics_sent_at_once(tmp_path, monkeypatch, guide, tts):
    _use_topics(monkeypatch, guide, [(f"Topic {n}", f"Body {n}.") for n in range(1, 9)])
    guide.build_audio(tmp_path, "voice-a", make_mp3=True, jobs=3)
    assert len(tts.made) == 8
    assert tts.max_active == 3


def test_jobs_option_accepts_only_one_to_eight(guide):
    import argparse

    assert guide._jobs_count("8") == 8
    for bad in ("0", "9", "x"):
        with pytest.raises(argparse.ArgumentTypeError):
            guide._jobs_count(bad)
