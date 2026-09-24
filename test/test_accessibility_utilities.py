"""Accessibility utility coverage: prose, shortcuts, plot text, SR detection, help scale, message boxes."""

from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget

from src.accessibility.dialog_prose import blocks_to_dialog_html
from src.accessibility.help_scaling import (
    HELP_SR_DEFAULT_SCALE,
    HELP_UI_SCALE_KEY,
    HelpUIScaler,
    help_preset_name,
    resolve_initial_help_scale,
    save_help_scale,
)
from src.accessibility.read_only_text import (
    PlotLineList,
    canonicalize_plot_comments,
    format_plot_text_for_navigation,
    plot_lines_for_review,
    plot_text_equivalent,
    restore_prose_line_breaks,
)
import src.accessibility.screen_reader as screen_reader
from src.accessibility.shortcut_helpers import (
    HELP_DOC_SHORTCUT,
    build_accessible_f1_popup_style,
    get_accessible_shortcuts_list,
    prepend_help_doc_shortcut,
)
from src.accessibility.style_helpers import (
    DEFAULT_MESSAGE_BOX_BUTTON_ICONS,
    MESSAGE_BOX_DELETE_CONFIRM_ICONS,
    MESSAGE_BOX_UNSAVED_TWO_ICONS,
    apply_message_box_button_icons,
    exec_styled_message_box,
    set_message_box_button_accessibility,
)


# --- dialog_prose / shortcut_helpers ---


def test_blocks_to_dialog_html_escapes_and_classes():
    html = blocks_to_dialog_html(
        [
            ("heading", "Welcome"),
            ("body", "Line with <tag>"),
            ("item", "Ctrl+I"),
            ("body", "   "),
        ]
    )
    assert 'class="heading"' in html
    assert "<strong>Welcome</strong>" in html
    assert "Line with &lt;tag&gt;" in html
    assert 'class="item"' in html
    assert "Ctrl+I" in html


def test_prepend_help_doc_shortcut_idempotent():
    base = [("F1", "Shortcuts"), ("Escape", "Close")]
    once = prepend_help_doc_shortcut(base)
    assert once[0] == HELP_DOC_SHORTCUT
    assert prepend_help_doc_shortcut(once)[0] == HELP_DOC_SHORTCUT
    assert once.count(HELP_DOC_SHORTCUT) == 1


def test_get_accessible_shortcuts_list_hides_alt_slash_without_sr(monkeypatch):
    monkeypatch.setattr(
        "src.accessibility.shortcut_helpers.is_screen_reader_active",
        lambda: False,
    )
    shortcuts = [("Alt+/", "Read status"), ("F1", "Help")]
    result = get_accessible_shortcuts_list(shortcuts)
    assert result == [("F1", "Help")]


def test_get_accessible_shortcuts_list_promotes_alt_slash_with_sr(monkeypatch):
    monkeypatch.setattr(
        "src.accessibility.shortcut_helpers.is_screen_reader_active",
        lambda: True,
    )
    shortcuts = [("F1", "Help"), ("Alt+/", "Read status")]
    result = get_accessible_shortcuts_list(shortcuts)
    assert result[0] == ("Alt+/", "Read status")
    assert ("F1", "Help") in result


def test_build_accessible_f1_popup_style_nonempty():
    style = build_accessible_f1_popup_style()
    assert "QTableWidget" in style
    assert "outline" in style


# --- read_only_text ---


def test_format_plot_preserves_prose():
    text = "First sentence. Second sentence! Third one?"
    formatted = format_plot_text_for_navigation(text)
    assert formatted == text


def test_format_plot_keeps_long_sentence_on_one_line():
    text = (
        "Through twenty-one novels featuring Lucas Davenport, Kidd, or the "
        "razor-edge world of the Night Crew, John Sandford has been writing."
    )
    formatted = format_plot_text_for_navigation(text)
    assert formatted == text


def test_restore_prose_rejoins_sentence_per_line_text():
    text = (
        "Rating: 3.5 (2 ratings)\n"
        "Sometimes, justice isn't enough.\n"
        "Through twenty-one novels featuring Lucas Davenport.\n"
        "But Dead Watch sets a whole new level."
    )
    restored = restore_prose_line_breaks(text)
    assert restored.startswith("Rating: 3.5 (2 ratings)\n")
    assert "Sometimes, justice isn't enough. Through twenty-one" in restored
    assert "\nBut Dead Watch" not in restored or restored.count("\n") == 1


def test_format_plot_preserves_existing_lines():
    text = "Line one.\nLine two."
    assert format_plot_text_for_navigation(text) == "Line one.\nLine two."


def test_format_plot_splits_rating_prefix():
    text = "Rating: 4.5 (1,234 ratings) - First sentence. Second sentence."
    formatted = format_plot_text_for_navigation(text)
    assert formatted.startswith("Rating: 4.5 (1,234 ratings)\n")
    assert "First sentence. Second sentence." in formatted


def test_format_plot_keeps_unbroken_text_on_one_line():
    text = " ".join(["word"] * 30)
    formatted = format_plot_text_for_navigation(text)
    assert formatted == text


def test_plot_line_list_puts_rating_first_then_wrapped_body():
    app = QApplication.instance() or QApplication([])
    widget = PlotLineList()
    widget.set_plot_text("Rating: 4.0\nFirst sentence. Second sentence.")
    assert widget.count() >= 2
    assert widget.item(0).text() == "Rating: 4.0"
    assert all(len(widget.item(i).text()) <= 73 for i in range(1, widget.count()))
    body = " ".join(widget.item(i).text() for i in range(1, widget.count()))
    assert "First sentence. Second sentence." == body


def test_plot_lines_for_review_wraps_at_seventy_three_chars():
    text = " ".join(["word"] * 30)
    lines = plot_lines_for_review(text)
    assert lines
    assert all(len(line) <= 73 for line in lines)
    assert " ".join(lines) == text


def test_plot_lines_for_review_does_not_break_words():
    long_word = "supercalifragilisticexpialidocious"
    assert plot_lines_for_review(long_word) == [long_word]
    text = (
        "Through twenty-one novels featuring Lucas Davenport, Kidd, or the "
        "razor-edge world of the Night Crew, John Sandford has been writing."
    )
    lines = plot_lines_for_review(text)
    assert " ".join(lines) == text
    assert all(len(line) <= 73 for line in lines)


def test_split_rating_not_confused_by_hyphen_in_body():
    """Rating on its own line must not split at the first hyphen in the plot body."""
    text = (
        "Rating: 4.0 (43 ratings)\n"
        "A missing little girl named Maggie Rose. The thrill-killing of a teacher."
    )
    formatted = format_plot_text_for_navigation(text)
    assert formatted.startswith("Rating: 4.0 (43 ratings)\n")
    lines = plot_lines_for_review(text)
    assert lines[0] == "Rating: 4.0 (43 ratings)"
    assert "thrill-killing" in " ".join(lines[1:])


def test_format_plot_flattens_newline_rating_with_wrapped_body():
    """Web metadata stores rating on line 1; body may carry 73-char wrap artifacts."""
    text = (
        "Rating: 4.0 (43 ratings)\n"
        "A missing little girl named Maggie Rose...The thrill\n"
        "killing of a beautiful elementary school teacher..."
    )
    formatted = format_plot_text_for_navigation(text)
    assert formatted.startswith("Rating: 4.0 (43 ratings)\n")
    body = formatted.split("\n", 1)[1]
    assert "\n" not in body
    assert "The thrill killing" in body


def test_canonicalize_plot_comments_matches_format():
    text = "Rating: 4.0\nword\nword"
    assert canonicalize_plot_comments(text) == format_plot_text_for_navigation(text)


def test_plot_line_list_shows_rating_on_first_row():
    app = QApplication.instance() or QApplication([])
    raw = (
        "Rating: 4.0 (43 ratings)\n"
        "A missing little girl named Maggie Rose...The thrill\n"
        "killing of a beautiful elementary school teacher."
    )
    widget = PlotLineList()
    widget.set_plot_text(canonicalize_plot_comments(raw))
    assert widget.item(0).text() == "Rating: 4.0 (43 ratings)"
    assert widget.currentRow() == 0


def test_plot_text_equivalent_ignores_line_breaks():
    left = "Rating: 4.0 - One sentence. Two sentence."
    right = "Rating: 4.0 - One sentence.\nTwo sentence."
    assert plot_text_equivalent(left, right)


# --- screen_reader ---


def _mock_processes(names):
    """Build fake psutil process_iter entries from process name strings."""
    return [
        SimpleNamespace(info={"name": name})
        for name in names
    ]


@pytest.fixture
def mock_psutil(monkeypatch):
    """Patch process_iter; caller sets process names via returned setter."""

    class FakePsutil:
        def __init__(self):
            self._names = []

        def set_processes(self, names):
            self._names = names

        def process_iter(self, _attrs):
            return _mock_processes(self._names)

    fake = FakePsutil()
    monkeypatch.setattr(screen_reader, "psutil", fake)
    return fake


def test_narrator_detected(mock_psutil):
    mock_psutil.set_processes(["explorer.exe", "Narrator.exe"])

    assert screen_reader.get_active_screen_reader() == "narrator"
    assert screen_reader.is_screen_reader_active() is True
    assert screen_reader.get_screen_reader_focus_delay_ms() == 3500


def test_jaws_detected(mock_psutil):
    mock_psutil.set_processes(["jaws.exe"])

    assert screen_reader.get_active_screen_reader() == "jaws"
    assert screen_reader.get_screen_reader_focus_delay_ms() == 300


def test_nvda_detected(mock_psutil):
    mock_psutil.set_processes(["nvda.exe"])

    assert screen_reader.get_active_screen_reader() == "nvda"
    assert screen_reader.get_screen_reader_focus_delay_ms() == 1500


def test_orca_detected(mock_psutil):
    mock_psutil.set_processes(["orca-daemon"])

    assert screen_reader.get_active_screen_reader() == "orca"
    assert screen_reader.get_screen_reader_focus_delay_ms() == 800


def test_no_screen_reader_detected(mock_psutil):
    mock_psutil.set_processes(["explorer.exe", "python.exe"])

    assert screen_reader.get_active_screen_reader() == ""
    assert screen_reader.is_screen_reader_active() is False
    assert screen_reader.get_screen_reader_focus_delay_ms() == 0


def test_psutil_unavailable(monkeypatch):
    monkeypatch.setattr(screen_reader, "psutil", None)

    assert screen_reader.get_active_screen_reader() == ""
    assert screen_reader.is_screen_reader_active() is False
    assert screen_reader.get_screen_reader_focus_delay_ms() == 0


# --- help_scaling ---


class _ScalerStub:
    def __init__(self, scale: int):
        self.current_scale = scale

    def get_scaled_size(self, base_size: int) -> int:
        return int(base_size * (self.current_scale / 100.0))


def test_help_ui_scaler_uses_local_percentage():
    scaler = HelpUIScaler(100)
    assert scaler.current_scale == 100
    assert scaler.get_scaled_size(12) == 12

    large = HelpUIScaler(150)
    assert large.get_scaled_size(12) == 18

    large.set_scale(125)
    assert large.current_scale == 125
    assert large.get_scaled_size(12) == 15


def _fresh_settings() -> QSettings:
    settings = QSettings("AbCS", "AudioBookCollector")
    settings.clear()
    return settings


def test_resolve_initial_without_screen_reader_uses_global(
    isolated_qsettings, monkeypatch
):
    monkeypatch.setattr(
        "src.accessibility.help_scaling.is_screen_reader_active",
        lambda: False,
    )
    settings = _fresh_settings()

    assert resolve_initial_help_scale(_ScalerStub(150), settings=settings) == 150
    assert not settings.contains(HELP_UI_SCALE_KEY)


def test_resolve_initial_without_screen_reader_uses_saved_help_pref(
    isolated_qsettings, monkeypatch
):
    monkeypatch.setattr(
        "src.accessibility.help_scaling.is_screen_reader_active",
        lambda: False,
    )
    settings = _fresh_settings()
    settings.setValue(HELP_UI_SCALE_KEY, 125)

    assert resolve_initial_help_scale(_ScalerStub(150), settings=settings) == 125


def test_resolve_initial_sr_defaults_100_without_persisting(
    isolated_qsettings, monkeypatch
):
    monkeypatch.setattr(
        "src.accessibility.help_scaling.is_screen_reader_active",
        lambda: True,
    )
    settings = _fresh_settings()
    settings.setValue("ui_scale", 150)
    assert not settings.contains(HELP_UI_SCALE_KEY)

    assert (
        resolve_initial_help_scale(_ScalerStub(150), settings=settings)
        == HELP_SR_DEFAULT_SCALE
    )
    assert not settings.contains(HELP_UI_SCALE_KEY)


def test_resolve_initial_sr_uses_saved_help_pref(isolated_qsettings, monkeypatch):
    monkeypatch.setattr(
        "src.accessibility.help_scaling.is_screen_reader_active",
        lambda: True,
    )
    settings = _fresh_settings()
    settings.setValue(HELP_UI_SCALE_KEY, 150)

    assert resolve_initial_help_scale(_ScalerStub(150), settings=settings) == 150


def test_save_help_scale_persists_choice(isolated_qsettings):
    settings = _fresh_settings()

    assert save_help_scale(125, settings=settings) == 125
    assert settings.value(HELP_UI_SCALE_KEY, type=int) == 125

    fresh_read = QSettings("AbCS", "AudioBookCollector")
    assert fresh_read.value(HELP_UI_SCALE_KEY, type=int) == 125


def test_read_saved_help_scale_handles_int_string(isolated_qsettings):
    settings = _fresh_settings()
    settings.setValue(HELP_UI_SCALE_KEY, "150")
    settings.sync()
    assert resolve_initial_help_scale(_ScalerStub(100), settings=settings) == 150


def test_help_preset_name_matches_uiscaler_presets():
    assert help_preset_name(100) == "Normal"
    assert help_preset_name(150) == "Extra Large"
    assert help_preset_name(123) == "Custom"


# --- message_box_button_icons ---


def test_apply_message_box_button_icons_sets_icons(qapp):
    msg = QMessageBox()
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    apply_message_box_button_icons(msg, button_icon_roles=MESSAGE_BOX_DELETE_CONFIRM_ICONS)

    yes_btn = msg.button(QMessageBox.Yes)
    no_btn = msg.button(QMessageBox.No)
    assert yes_btn is not None
    assert no_btn is not None
    assert not yes_btn.icon().isNull()
    assert not no_btn.icon().isNull()


def test_apply_message_box_button_icons_preserves_accessible_names(qapp):
    msg = QMessageBox()
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    set_message_box_button_accessibility(
        msg,
        {
            QMessageBox.Yes: ("Yes, save", "Save changes"),
            QMessageBox.No: ("No, edit", "Continue editing"),
        },
    )
    apply_message_box_button_icons(msg, button_icon_roles=MESSAGE_BOX_UNSAVED_TWO_ICONS)

    assert msg.button(QMessageBox.Yes).accessibleName() == "Yes, save"
    assert msg.button(QMessageBox.No).accessibleName() == "No, edit"


def test_default_message_box_icon_roles_cover_standard_buttons():
    assert QMessageBox.Ok in DEFAULT_MESSAGE_BOX_BUTTON_ICONS
    assert QMessageBox.Yes in DEFAULT_MESSAGE_BOX_BUTTON_ICONS
    assert DEFAULT_MESSAGE_BOX_BUTTON_ICONS[QMessageBox.Yes] == "save"


def test_exec_styled_message_box_applies_ok_icon(qapp):
    parent = QWidget()
    captured = {}

    def fake_exec(self):
        ok_btn = self.button(QMessageBox.Ok)
        captured["ok_btn"] = ok_btn
        captured["icon_null"] = True if ok_btn is None else ok_btn.icon().isNull()
        return int(QMessageBox.Ok)

    with patch.object(QMessageBox, "exec", fake_exec):
        result = exec_styled_message_box(
            parent,
            scaled_height=20,
            icon=QMessageBox.Information,
            title="Test",
            text="Hello",
            buttons=QMessageBox.Ok,
        )

    assert result == int(QMessageBox.Ok)
    assert captured.get("ok_btn") is not None
    assert not captured.get("icon_null")
    parent.close()


def test_message_box_button_accessibility_helper(qapp):
    """Dialog buttons should keep mnemonics but expose clear accessible text."""
    msg = QMessageBox()
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

    set_message_box_button_accessibility(
        msg,
        {
            QMessageBox.Yes: ("Yes, save", "Save changes"),
            QMessageBox.No: ("No, continue editing", "Return to editing"),
        },
    )

    assert msg.button(QMessageBox.Yes).accessibleName() == "Yes, save"
    assert msg.button(QMessageBox.Yes).accessibleDescription() == "Save changes"
    assert msg.button(QMessageBox.No).accessibleName() == "No, continue editing"
    assert msg.button(QMessageBox.No).accessibleDescription() == "Return to editing"


def test_preview_and_pause_icons_use_theme_ink(qapp):
    from src.accessibility.icon_helper import get_action_icon

    play = get_action_icon("preview")
    pause = get_action_icon("pause")
    assert play.isNull() is False
    assert pause.isNull() is False
    assert play.cacheKey() != pause.cacheKey()
