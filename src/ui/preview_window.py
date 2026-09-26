"""In-app audiobook preview. Focus stays in AbCS."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QEvent, QSettings, QSize, QTimer, QUrl, Qt
from PySide6.QtGui import QKeySequence, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QStatusBar,
    QVBoxLayout,
)

from src.accessibility.accessible_events import (
    announce_status_message,
    configure_status_bar_accessibility,
    read_status_bar_message,
)
from src.accessibility.icon_helper import apply_decorative_action_icon, get_app_icon
from src.accessibility.key_filters import is_unmapped_alt_letter
from src.accessibility.scaling import UIScaler
from src.accessibility.style_helpers import (
    apply_status_bar_tooltip,
    apply_visual_tooltip_map,
    exec_styled_message_box,
)
from src.accessibility.theme_manager import ThemeManager
from src.core.audio_launcher import read_embedded_cover, resolve_preview_playlist
from src.core.media_log import (
    mute_preview_stderr,
    restore_preview_stderr,
    silence_preview_media_logs,
)
from src.ui.accessible_dialog import AccessibleDialog

_open_preview = None
SEEK_STEP_MS = 30_000
SLIDER_STEP_MS = 5_000
SAVE_PROMPT_BELOW_MS = 5 * 60 * 1000
SPEED_OPTIONS = (0.75, 1.0, 1.25, 1.5, 1.75, 2.0)
SPEED_SETTINGS_KEY = "preview/playback_rate"


def _format_preview_length(length_text: str) -> str:
    raw = (length_text or "").strip().replace("_", "")
    if not raw or raw in {":", "00:00", "0:00", "--:--"}:
        return ""
    if ":" in raw:
        parts = raw.split(":", 1)
        try:
            hours = int(parts[0] or 0)
            minutes = int(parts[1] or 0)
        except ValueError:
            return raw
        if minutes > 59:
            return raw
        return f"{hours:02d}:{minutes:02d}"
    return raw


def _length_from_book_or_text(book, length_text: str) -> str:
    """Prefer the stored book length when the caller passed nothing useful."""
    formatted = _format_preview_length(length_text)
    if formatted:
        return formatted
    if book is None:
        return ""
    try:
        hours = int(getattr(book, "time_hours", 0) or 0)
        minutes = int(getattr(book, "time_minutes", 0) or 0)
    except (TypeError, ValueError):
        return ""
    if hours or minutes:
        return f"{hours:02d}:{minutes:02d}"
    display = _format_preview_length(getattr(book, "time_display", "") or "")
    return display


def _format_preview_series(series_name: str, series_number="") -> str:
    name = (series_name or "").strip()
    from src.utils.text_utils import format_series_suffix

    number = format_series_suffix(series_number)
    if name and number:
        return f"{name} - {number}"
    return name or number


def _format_position_ms(ms: int) -> str:
    total_sec = max(0, int(ms) // 1000)
    hours, rem = divmod(total_sec, 3600)
    minutes, seconds = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def _playback_status(state: str) -> str:
    return f"{state}. Press Escape to exit."


def load_preview_speed() -> float:
    settings = QSettings("AbCS", "AudioBookCollector")
    raw = settings.value(SPEED_SETTINGS_KEY, 1.0)
    try:
        rate = float(raw)
    except (TypeError, ValueError):
        return 1.0
    if rate in SPEED_OPTIONS:
        return rate
    return 1.0


def save_preview_speed(rate: float) -> None:
    settings = QSettings("AbCS", "AudioBookCollector")
    settings.setValue(SPEED_SETTINGS_KEY, float(rate))


def show_preview(
    parent,
    stored_path: str,
    scaler: UIScaler,
    theme_manager: ThemeManager | None = None,
    book_title: str = "",
    author_name: str = "",
    series_name: str = "",
    series_number: str = "",
    length_text: str = "",
    collection_root: str = "",
    book=None,
    db=None,
) -> tuple[bool, str]:
    """Resolve a book path and play it in the in-app Preview window."""
    listen_file = ""
    listen_ms = None
    if book is not None:
        listen_file = getattr(book, "listen_file_name", "") or ""
        listen_ms = getattr(book, "listen_position_ms", None)
    playlist = resolve_preview_playlist(
        stored_path,
        collection_root=collection_root,
        listen_file_name=listen_file,
    )
    if playlist.error or not playlist.files:
        return False, playlist.error or "No file path is set."
    try:
        silence_preview_media_logs()
        from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

        silence_preview_media_logs()
        mute_preview_stderr()
    except ImportError:
        return False, "Playing books needs Qt Multimedia."

    global _open_preview
    if _open_preview is not None:
        _open_preview.close()
        _open_preview = None

    window = PreviewWindow(
        parent,
        scaler,
        theme_manager,
        player_types=(QMediaPlayer, QAudioOutput),
        book=book,
        db=db,
    )
    ok, message = window.play_playlist(
        playlist,
        book_title=book_title,
        author_name=author_name,
        series_name=series_name,
        series_number=series_number,
        length_text=length_text,
        resume_ms=listen_ms,
    )
    if not ok:
        window.close()
        return False, message
    _open_preview = window
    window.show()
    window._keep_above_owner()
    window.play_pause_button.setFocus(Qt.TabFocusReason)
    if parent is not None:
        window.exec()
    return True, message


class PreviewWindow(AccessibleDialog):
    """Play an audiobook inside AbCS with transport and resume."""

    ALLOWED_ALT_LETTERS = {"/", "N", "P", "S"}

    def __init__(
        self,
        parent,
        scaler: UIScaler,
        theme_manager: ThemeManager | None = None,
        player_types=None,
        book=None,
        db=None,
    ):
        super().__init__(parent)
        self.setWindowIcon(get_app_icon())
        self.scaler = scaler
        self.theme_manager = theme_manager
        self._book = book
        self._db = db
        from src.ui.help_router import preview_help_doc_for_owner

        self.help_doc_override = preview_help_doc_for_owner(parent)
        self._display_title = ""
        self._book_length_text = ""
        self._player = None
        self._audio = None
        self._video_sink = None
        self._playlist: tuple[Path, ...] = ()
        self._playlist_index = 0
        self._folder_mode = False
        self._resume_ms: int | None = None
        self._pending_resume = False
        self._save_progress_on_close = True
        self._closing = False
        self._slider_dragging = False
        self._updating_slider_from_player = False
        self.setWindowModality(Qt.ApplicationModal)
        if player_types is not None:
            media_player_type, audio_output_type = player_types
            self._audio = audio_output_type()
            self._player = media_player_type()
            self._player.setAudioOutput(self._audio)
            try:
                from PySide6.QtMultimedia import QVideoSink

                self._video_sink = QVideoSink()
                self._player.setVideoOutput(self._video_sink)
            except Exception:
                pass
            self._player.playbackStateChanged.connect(self._on_state_changed)
            self._player.errorOccurred.connect(self._on_player_error)
            self._player.mediaStatusChanged.connect(self._on_media_status)
            if hasattr(self._player, "positionChanged"):
                self._player.positionChanged.connect(self._on_position_changed)
            if hasattr(self._player, "durationChanged"):
                self._player.durationChanged.connect(self._on_duration_changed)

        self.setWindowTitle("Play")
        self.setAccessibleName("Play")
        self.setAccessibleDescription(
            "Play this audiobook inside AbCS. Space plays or pauses. "
            "Alt+Left rewinds. Alt+Right fast-forwards. Escape closes."
        )
        self.resize(720, 300)
        self._setup_ui()
        self._setup_shortcuts()
        self.installEventFilter(self)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        info_row = QHBoxLayout()
        info_row.setSpacing(16)

        details = QVBoxLayout()
        details.setSpacing(4)
        self.title_label = QLabel("Title:")
        self.title_label.setFocusPolicy(Qt.NoFocus)
        self.title_label.setWordWrap(True)
        self.author_label = QLabel("Author:")
        self.author_label.setFocusPolicy(Qt.NoFocus)
        self.author_label.setWordWrap(True)
        self.series_label = QLabel("Series:")
        self.series_label.setFocusPolicy(Qt.NoFocus)
        self.series_label.setWordWrap(True)
        self.series_label.hide()
        self.length_label = QLabel("Length:")
        self.length_label.setFocusPolicy(Qt.NoFocus)
        self.file_label = QLabel("File:")
        self.file_label.setFocusPolicy(Qt.NoFocus)
        self.file_label.setWordWrap(True)
        self.part_label = QLabel("")
        self.part_label.setFocusPolicy(Qt.NoFocus)
        self.part_label.setWordWrap(True)
        self.part_label.hide()
        details.addWidget(self.title_label)
        details.addWidget(self.author_label)
        details.addWidget(self.series_label)
        details.addWidget(self.length_label)
        details.addWidget(self.file_label)
        details.addWidget(self.part_label)
        info_row.addLayout(details, 1)

        self.cover_label = QLabel()
        self.cover_label.setFocusPolicy(Qt.NoFocus)
        self.cover_label.setAccessibleName("Cover")
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.hide()
        info_row.addWidget(self.cover_label, 0, Qt.AlignTop)
        layout.addLayout(info_row)
        self.track_label = self.title_label

        layout.addSpacing(2)

        self.position_label = QLabel("0:00")
        self.position_label.setFocusPolicy(Qt.NoFocus)
        self.position_label.setAlignment(Qt.AlignCenter)
        self.position_label.setAccessibleName("Play position")
        font = self.position_label.font()
        font.setBold(True)
        time_pt = max(self.scaler.get_scaled_size(20), 16)
        font.setPointSize(time_pt)
        self.position_label.setFont(font)
        pad_y = max(self.scaler.get_scaled_size(8), 6)
        pad_x = max(self.scaler.get_scaled_size(20), 14)
        chip_radius = max(self.scaler.get_scaled_size(14), 10)
        self.position_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {time_pt}pt;
                font-weight: 700;
                padding: {pad_y}px {pad_x}px;
                border: 1px solid palette(mid);
                border-radius: {chip_radius}px;
                background-color: palette(base);
            }}
            """
        )
        layout.addWidget(self.position_label, 0, Qt.AlignHCenter)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setAccessibleName("Seek in current file")
        self.position_slider.setAccessibleDescription(
            "Move through the current audio file. Left and Right arrows seek "
            "five seconds. Page Up and Page Down seek thirty seconds."
        )
        self.position_slider.setRange(0, 0)
        self.position_slider.setSingleStep(SLIDER_STEP_MS)
        self.position_slider.setPageStep(SEEK_STEP_MS)
        self.position_slider.setEnabled(False)
        self.position_slider.setFocusPolicy(Qt.StrongFocus)
        groove_h = max(self.scaler.get_scaled_size(14), 12)
        handle_h = max(self.scaler.get_scaled_size(28), 22)
        handle_w = max(self.scaler.get_scaled_size(18), 14)
        self.position_slider.setMinimumHeight(handle_h + 8)
        self.position_slider.setStyleSheet(
            f"""
            QSlider::groove:horizontal {{
                height: {groove_h}px;
                background: palette(mid);
                border: 1px solid palette(dark);
                border-radius: {groove_h // 2}px;
            }}
            QSlider::sub-page:horizontal {{
                background: palette(highlight);
                border: 1px solid palette(dark);
                border-radius: {groove_h // 2}px;
                height: {groove_h}px;
            }}
            QSlider::add-page:horizontal {{
                background: palette(mid);
                border: 1px solid palette(dark);
                border-radius: {groove_h // 2}px;
                height: {groove_h}px;
            }}
            QSlider::handle:horizontal {{
                width: {handle_w}px;
                height: {handle_h}px;
                margin: -{(handle_h - groove_h) // 2}px 0;
                background: palette(button);
                border: 2px solid palette(button-text);
                border-radius: {handle_w // 2}px;
            }}
            QSlider::handle:horizontal:focus {{
                background: palette(highlight);
                border: 2px solid palette(highlight);
            }}
            """
        )
        self.position_slider.installEventFilter(self)
        self.position_slider.sliderPressed.connect(self._on_slider_pressed)
        self.position_slider.sliderReleased.connect(self._on_slider_released)
        self.position_slider.valueChanged.connect(self._on_slider_value_changed)
        layout.addWidget(self.position_slider)

        transport = QHBoxLayout()
        transport.setSpacing(10)
        transport.setContentsMargins(0, 4, 0, 0)
        min_side = self.scaler.get_scaled_size(40)
        play_side = self.scaler.get_scaled_size(48)
        icon_side = self.scaler.get_scaled_size(22)
        play_icon_side = self.scaler.get_scaled_size(26)
        round_style = self._round_transport_button_style(min_side)
        play_style = self._round_transport_button_style(play_side, emphasis=True)

        self.previous_button = QPushButton()
        self.previous_button.setAccessibleName("Previous file")
        self.previous_button.setAccessibleDescription(
            "Play the previous audio file. Shortcut Alt+P."
        )
        self.rewind_button = QPushButton()
        self.rewind_button.setAccessibleName("Rewind 30 seconds")
        self.rewind_button.setAccessibleDescription(
            "Jump back 30 seconds. Shortcut Alt+Left."
        )
        self.play_pause_button = QPushButton()
        self.play_pause_button.setAccessibleName("Play or pause")
        self.play_pause_button.setAccessibleDescription(
            "Play or pause this audiobook. Shortcut Space."
        )
        self.forward_button = QPushButton()
        self.forward_button.setAccessibleName("Forward 30 seconds")
        self.forward_button.setAccessibleDescription(
            "Jump ahead 30 seconds. Shortcut Alt+Right."
        )
        self.next_button = QPushButton()
        self.next_button.setAccessibleName("Next file")
        self.next_button.setAccessibleDescription(
            "Play the next audio file. Shortcut Alt+N."
        )

        icon_roles = (
            (self.previous_button, "media_previous", min_side, icon_side, round_style),
            (self.rewind_button, "media_rewind", min_side, icon_side, round_style),
            (self.play_pause_button, "preview", play_side, play_icon_side, play_style),
            (self.forward_button, "media_forward", min_side, icon_side, round_style),
            (self.next_button, "media_next", min_side, icon_side, round_style),
        )
        transport.addStretch(1)
        for button, role, side, glyph, style in icon_roles:
            button.setText("")
            button.setDefault(False)
            button.setAutoDefault(False)
            button.setFixedSize(side, side)
            button.setFocusPolicy(Qt.StrongFocus)
            button.setStyleSheet(style)
            button.setIconSize(QSize(glyph, glyph))
            apply_decorative_action_icon(button, role, self.scaler)
            button.installEventFilter(self)
            transport.addWidget(button)

        self.speed_combo = QComboBox()
        self.speed_combo.setAccessibleName("Playback speed")
        self.speed_combo.setAccessibleDescription(
            "Speed for every book. Saved for the next time you play. Shortcut Alt+S."
        )
        for rate in SPEED_OPTIONS:
            self.speed_combo.addItem(f"{rate:g}x", rate)
        speed_h = max(self.scaler.get_scaled_size(28), 24)
        self.speed_combo.setFixedHeight(speed_h)
        self.speed_combo.setMinimumWidth(self.scaler.get_scaled_size(64))
        self.speed_combo.setFocusPolicy(Qt.StrongFocus)
        speed_radius = max(self.scaler.get_scaled_size(4), 4)
        self.speed_combo.setStyleSheet(
            f"""
            QComboBox {{
                padding: 2px 8px;
                min-height: {speed_h - 6}px;
                max-height: {speed_h}px;
                border: 1px solid palette(button-text);
                border-radius: {speed_radius}px;
                background-color: palette(button);
                color: palette(button-text);
                outline: none;
            }}
            QComboBox:focus {{
                border: 2px solid palette(highlight);
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }}
            """
        )
        self.speed_combo.installEventFilter(self)
        transport.addStretch(2)
        transport.addWidget(self.speed_combo, 0, Qt.AlignVCenter)
        layout.addLayout(transport)

        self.previous_button.clicked.connect(self.on_previous)
        self.rewind_button.clicked.connect(self.on_rewind)
        self.play_pause_button.clicked.connect(self.on_play_pause)
        self.forward_button.clicked.connect(self.on_forward)
        self.next_button.clicked.connect(self.on_next)
        self.speed_combo.currentIndexChanged.connect(self._on_speed_changed)

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        configure_status_bar_accessibility(self.status_bar)
        layout.addWidget(self.status_bar)

        apply_visual_tooltip_map(
            {
                self.previous_button: "Previous file",
                self.rewind_button: "Rewind 30 seconds",
                self.play_pause_button: "Play or pause",
                self.forward_button: "Forward 30 seconds",
                self.next_button: "Next file",
                self.speed_combo: "Playback speed",
                self.position_slider: "Seek in current file",
            }
        )
        apply_status_bar_tooltip(self.status_bar, "Play status")
        self._apply_saved_speed(announce=False)
        self._update_position_label(0)
        self._reset_position_slider()
        self._apply_preview_tab_order()

    @staticmethod
    def _round_transport_button_style(side: int, emphasis: bool = False) -> str:
        """Circular icon buttons for Preview transport."""
        radius = max(side // 2, 8)
        border = "2px" if emphasis else "1px"
        return f"""
            QPushButton {{
                padding: 0px;
                min-width: {side}px;
                max-width: {side}px;
                min-height: {side}px;
                max-height: {side}px;
                border: {border} solid palette(button-text);
                border-radius: {radius}px;
                background-color: palette(button);
                color: palette(button-text);
                outline: none;
            }}
            QPushButton:disabled {{
                border: {border} solid palette(mid);
                color: palette(mid);
            }}
            QPushButton:hover {{
                border: {border} solid palette(highlight);
            }}
            QPushButton:focus {{
                background-color: palette(highlight);
                color: palette(highlighted-text);
                border: 2px solid palette(highlight);
                outline: none;
            }}
            QPushButton:pressed {{
                border: 2px solid palette(highlight);
            }}
        """

    def _transport_focus_widgets(self):
        """Transport row order: Prev, Rewind, Play, Forward, Next, Speed."""
        return [
            self.previous_button,
            self.rewind_button,
            self.play_pause_button,
            self.forward_button,
            self.next_button,
            self.speed_combo,
        ]

    def _preview_focus_chain(self):
        """Full Tab chain including Rewind and Forward even if Qt would skip them."""
        widgets = [self.position_slider, *self._transport_focus_widgets()]
        return [
            widget
            for widget in widgets
            if widget.isEnabled()
            and widget.isVisible()
            and widget.focusPolicy() != Qt.NoFocus
        ]

    def _move_preview_focus(self, forward: bool) -> bool:
        """Move Tab/arrow focus through the Preview control chain."""
        chain = self._preview_focus_chain()
        if not chain:
            return False
        focus = QApplication.focusWidget()
        if focus is self.status_bar:
            focus = None
        if focus not in chain:
            target = chain[0] if forward else chain[-1]
            target.setFocus(Qt.TabFocusReason)
            return True
        index = chain.index(focus) + (1 if forward else -1)
        if index < 0 or index >= len(chain):
            return False
        chain[index].setFocus(Qt.TabFocusReason)
        return True

    def _move_transport_focus(self, forward: bool) -> bool:
        """Left/Right among transport controls only (not the seek slider)."""
        widgets = [
            widget
            for widget in self._transport_focus_widgets()
            if widget.isEnabled() and widget.isVisible()
        ]
        if not widgets:
            return False
        focus = QApplication.focusWidget()
        if focus not in widgets:
            return False
        index = widgets.index(focus)
        index = (index + (1 if forward else -1)) % len(widgets)
        widgets[index].setFocus(Qt.TabFocusReason)
        return True

    def focusNextPrevChild(self, next_):
        """Force Tab through Rewind and Forward; Qt/JAWS otherwise skip them."""
        if self._move_preview_focus(forward=bool(next_)):
            return True
        return super().focusNextPrevChild(next_)

    def _apply_preview_tab_order(self) -> None:
        """Seek slider, then Prev / Rewind / Play / Forward / Next / Speed."""
        chain = self._preview_focus_chain()
        for left, right in zip(chain, chain[1:]):
            self.setTabOrder(left, right)

    def _setup_shortcuts(self):
        status = QShortcut(QKeySequence("Alt+/"), self)
        status.setContext(Qt.WidgetWithChildrenShortcut)
        status.activated.connect(
            lambda: read_status_bar_message(self.status_bar, fallback="Ready")
        )
        escape = QShortcut(QKeySequence(Qt.Key_Escape), self)
        escape.setContext(Qt.WidgetWithChildrenShortcut)
        escape.activated.connect(self.request_close)
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        help_shortcut.activated.connect(self.on_show_shortcuts)
        from src.ui.help_router import install_shift_f1_help

        install_shift_f1_help(self, shortcut_context=Qt.WidgetWithChildrenShortcut)

        for keys, slot in (
            ("Space", self.on_play_pause),
            ("Alt+N", self.on_next),
            ("Alt+P", self.on_previous),
            ("Alt+Left", self.on_rewind),
            ("Alt+Right", self.on_forward),
            ("Alt+S", self._focus_speed),
        ):
            shortcut = QShortcut(QKeySequence(keys), self)
            shortcut.setContext(Qt.WidgetWithChildrenShortcut)
            shortcut.activated.connect(slot)

    def set_status(self, message: str, announce: bool = False):
        announce_status_message(self.status_bar, message, move_focus=announce)

    def play_playlist(
        self,
        playlist,
        book_title: str = "",
        author_name: str = "",
        series_name: str = "",
        series_number: str = "",
        length_text: str = "",
        resume_ms: int | None = None,
    ) -> tuple[bool, str]:
        if self._player is None:
            return False, "Playing books needs Qt Multimedia."
        if not playlist.files:
            return False, playlist.error or "No file path is set."
        title = (book_title or "").strip() or playlist.files[0].name
        author = (author_name or "").strip()
        series = _format_preview_series(series_name, series_number)
        length = _length_from_book_or_text(self._book, length_text)
        self._display_title = title
        self._book_length_text = length
        self._set_info_line(self.title_label, f"Title: {title}")
        self._set_info_line(
            self.author_label, f"Author: {author}" if author else "Author:"
        )
        if series:
            self._set_info_line(self.series_label, f"Series: {series}")
            self.series_label.show()
        else:
            self.series_label.clear()
            self.series_label.setAccessibleName("")
            self.series_label.hide()
        if length:
            self._set_info_line(self.length_label, f"Length: {length}")
            self.length_label.show()
        else:
            self.length_label.clear()
            self.length_label.setAccessibleName("")
            self.length_label.hide()
        self._playlist = tuple(playlist.files)
        self._playlist_index = min(
            max(playlist.start_index, 0), len(self._playlist) - 1
        )
        self._folder_mode = bool(playlist.folder_mode)
        self._resume_ms = int(resume_ms) if resume_ms else None
        self._pending_resume = self._resume_ms is not None and self._resume_ms > 0
        self._save_progress_on_close = True
        self._load_current_file(autoplay=True)
        self.set_status(_playback_status("Playing"), announce=True)
        self._sync_play_button()
        self._sync_transport_enabled()
        self._update_position_label(
            self._resume_ms if self._pending_resume and self._resume_ms else 0
        )
        return True, _playback_status("Playing")

    def play_file(
        self,
        file_path: Path,
        book_title: str = "",
        author_name: str = "",
        series_name: str = "",
        series_number: str = "",
        length_text: str = "",
    ) -> tuple[bool, str]:
        from types import SimpleNamespace

        return self.play_playlist(
            SimpleNamespace(
                files=(file_path,),
                start_index=0,
                folder_mode=False,
                error="",
            ),
            book_title=book_title,
            author_name=author_name,
            series_name=series_name,
            series_number=series_number,
            length_text=length_text,
        )

    def on_play_pause(self):
        if self._player is None:
            return
        from PySide6.QtMultimedia import QMediaPlayer

        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
            self._sync_play_button()
            self._focus_play_pause()
            self.set_status(_playback_status("Paused"), announce=True)
        else:
            self._player.play()
            self._sync_play_button()
            self._focus_play_pause()
            self.set_status(_playback_status("Playing"), announce=True)

    def on_rewind(self):
        # Keep focus on Rewind so Tab/arrows can stay on this control.
        self._seek_by(-SEEK_STEP_MS)

    def on_forward(self):
        self._seek_by(SEEK_STEP_MS)

    def on_previous(self):
        if self._playlist_index <= 0:
            self.set_status("Already at the first file.", announce=True)
            self._focus_play_pause()
            return
        self._playlist_index -= 1
        self._pending_resume = False
        self._resume_ms = None
        self._load_current_file(autoplay=True)
        # Focus Play before announce so restore does not land on Speed
        # when Previous becomes disabled.
        self._focus_play_pause()
        self.set_status(
            f"Previous file. {_playback_status('Playing')}", announce=True
        )

    def on_next(self):
        if self._playlist_index >= len(self._playlist) - 1:
            self.set_status("Already at the last file.", announce=True)
            self._focus_play_pause()
            return
        self._playlist_index += 1
        self._pending_resume = False
        self._resume_ms = None
        self._load_current_file(autoplay=True)
        self._focus_play_pause()
        self.set_status(f"Next file. {_playback_status('Playing')}", announce=True)

    def on_show_shortcuts(self):
        from src.accessibility.shortcut_helpers import exec_f1_shortcuts_dialog

        exec_f1_shortcuts_dialog(
            self,
            "Keyboard Shortcuts - Play",
            [
                ("Space", "Play or pause"),
                ("Alt+Left", "Rewind 30 seconds"),
                ("Alt+Right", "Forward 30 seconds"),
                ("Alt+P", "Previous file"),
                ("Alt+N", "Next file"),
                ("Alt+S", "Playback speed"),
                ("Left/Right", "Move between transport buttons, or seek on the slider"),
                ("Page Up/Down", "Seek thirty seconds on the position slider"),
                ("Escape", "Close"),
                ("Alt+/", "Read status bar"),
                ("F1", "Show this help"),
            ],
        )

    def _focus_play_pause(self) -> None:
        """Keep keyboard focus on Play/Pause after transport button actions.

        Focus before status announce so restore returns here. Do not schedule a
        delayed re-focus — that steals Tab from Rewind and Forward.
        """
        if self._closing:
            return
        button = getattr(self, "play_pause_button", None)
        if button is None or not button.isEnabled():
            return
        button.setFocus(Qt.OtherFocusReason)

    def _focus_speed(self):
        self.speed_combo.setFocus(Qt.ShortcutFocusReason)

    def _apply_saved_speed(self, announce: bool = False) -> None:
        rate = load_preview_speed()
        index = self.speed_combo.findData(rate)
        if index < 0:
            index = self.speed_combo.findData(1.0)
        self.speed_combo.blockSignals(True)
        self.speed_combo.setCurrentIndex(max(index, 0))
        self.speed_combo.blockSignals(False)
        self._set_playback_rate(rate, announce=announce, persist=False)

    def _on_speed_changed(self, _index: int = 0) -> None:
        rate = self.speed_combo.currentData()
        if rate is None:
            return
        self._set_playback_rate(float(rate), announce=True, persist=True)

    def _set_playback_rate(
        self, rate: float, announce: bool = False, persist: bool = True
    ) -> None:
        if self._player is not None:
            try:
                self._player.setPlaybackRate(rate)
            except Exception:
                pass
        if persist:
            save_preview_speed(rate)
        if announce:
            self.set_status(f"Speed {rate:g}x.", announce=True)

    def _seek_by(self, delta_ms: int) -> None:
        if self._player is None:
            return
        duration = max(0, int(self._player.duration()))
        current = max(0, int(self._player.position()))
        target = max(0, current + int(delta_ms))
        if duration > 0:
            target = min(target, duration)
        self._seek_to(target, announce=True)

    def _seek_to(self, position_ms: int, announce: bool = False) -> None:
        if self._player is None:
            return
        duration = max(0, int(self._player.duration()))
        target = max(0, int(position_ms))
        if duration > 0:
            target = min(target, duration)
        self._player.setPosition(target)
        self._set_slider_value(target)
        self._update_position_label(target)
        if announce:
            self.set_status(f"Position {_format_position_ms(target)}.", announce=True)

    def _reset_position_slider(self) -> None:
        self._slider_dragging = False
        self.position_slider.setEnabled(False)
        self._set_slider_range(0)
        self._set_slider_value(0)

    def _set_slider_range(self, duration_ms: int) -> None:
        duration = max(0, int(duration_ms))
        self._updating_slider_from_player = True
        try:
            self.position_slider.setRange(0, duration)
            self.position_slider.setEnabled(duration > 0)
        finally:
            self._updating_slider_from_player = False

    def _set_slider_value(self, position_ms: int) -> None:
        self._updating_slider_from_player = True
        try:
            self.position_slider.setValue(max(0, int(position_ms)))
        finally:
            self._updating_slider_from_player = False

    def _on_duration_changed(self, duration: int) -> None:
        if self._closing:
            return
        self._set_slider_range(duration)
        if self._player is not None:
            self._set_slider_value(int(self._player.position()))

    def _on_slider_pressed(self) -> None:
        self._slider_dragging = True

    def _on_slider_released(self) -> None:
        self._slider_dragging = False
        self._seek_to(self.position_slider.value(), announce=True)

    def _on_slider_value_changed(self, value: int) -> None:
        if self._updating_slider_from_player:
            return
        self._update_position_label(value)
        # Keyboard changes fire valueChanged without pressed/released.
        if not self._slider_dragging:
            self._seek_to(value, announce=False)

    def _on_position_changed(self, position: int) -> None:
        if self._closing or self._slider_dragging:
            return
        self._set_slider_value(position)
        self._update_position_label(position)

    def _update_position_label(self, position_ms: int = 0) -> None:
        current = _format_position_ms(position_ms)
        if self._book_length_text:
            text = f"{current} / {self._book_length_text}"
        else:
            text = current
        self.position_label.setText(text)
        self.position_label.setAccessibleName(f"Play position {text}")

    def _load_current_file(self, autoplay: bool = True) -> None:
        if self._player is None or not self._playlist:
            return
        file_path = self._playlist[self._playlist_index]
        self._set_info_line(self.file_label, f"File: {file_path.name}")
        self._update_part_label()
        self._show_cover(file_path)
        self._reset_position_slider()
        self._player.setSource(QUrl.fromLocalFile(str(file_path)))
        self._set_playback_rate(load_preview_speed(), announce=False, persist=False)
        if autoplay:
            self._player.play()
        self._sync_play_button()
        self._sync_transport_enabled()

    def _update_part_label(self) -> None:
        """Show Part n / total under the file name when more than one file."""
        total = len(self._playlist)
        if total <= 1:
            self.part_label.clear()
            self.part_label.setAccessibleName("")
            self.part_label.hide()
            return
        part = self._playlist_index + 1
        text = f"Part {part} / {total}"
        self._set_info_line(self.part_label, text)
        self.part_label.show()

    def _show_cover(self, file_path: Path) -> None:
        """Show embedded art when the file has it. Say nothing when it does not."""
        data = read_embedded_cover(file_path)
        pixmap = QPixmap()
        if not data or not pixmap.loadFromData(data):
            self.cover_label.clear()
            self.cover_label.hide()
            return
        side = self.scaler.get_scaled_size(120)
        radius = max(self.scaler.get_scaled_size(12), 8)
        self.cover_label.setFixedSize(side, side)
        self.cover_label.setStyleSheet(
            f"""
            QLabel {{
                border: 1px solid palette(mid);
                border-radius: {radius}px;
                background-color: palette(base);
                padding: 2px;
            }}
            """
        )
        self.cover_label.setPixmap(
            pixmap.scaled(
                side - 4,
                side - 4,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )
        self.cover_label.setAccessibleName("Cover")
        self.cover_label.show()
        self.resize(max(self.width(), 720), max(self.height(), side + 140))

    def _set_info_line(self, label: QLabel, text: str) -> None:
        label.setText(text)
        label.setAccessibleName(text)
        label.setAccessibleDescription("")

    def _sync_play_button(self):
        from PySide6.QtMultimedia import QMediaPlayer

        playing = (
            self._player is not None
            and self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        )
        self.play_pause_button.setText("")
        apply_decorative_action_icon(
            self.play_pause_button,
            "pause" if playing else "preview",
            self.scaler,
        )
        self.play_pause_button.setAccessibleName(
            "Pause" if playing else "Play"
        )

    def _sync_transport_enabled(self) -> None:
        multi = len(self._playlist) > 1
        self.previous_button.setEnabled(multi and self._playlist_index > 0)
        self.next_button.setEnabled(
            multi and self._playlist_index < len(self._playlist) - 1
        )

    def _on_state_changed(self, _state):
        self._sync_play_button()

    def _on_media_status(self, status) -> None:
        from PySide6.QtMultimedia import QMediaPlayer

        if self._player is None or self._closing:
            return
        if status in (
            QMediaPlayer.MediaStatus.LoadedMedia,
            QMediaPlayer.MediaStatus.BufferedMedia,
        ):
            if self._pending_resume and self._resume_ms:
                self._player.setPosition(int(self._resume_ms))
                self._pending_resume = False
                self._resume_ms = None
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self._playlist_index < len(self._playlist) - 1:
                self._playlist_index += 1
                self._pending_resume = False
                self._resume_ms = None
                self._load_current_file(autoplay=True)
                self._focus_play_pause()
                self.set_status(
                    f"Next file. {_playback_status('Playing')}", announce=True
                )
            else:
                self._clear_listen_progress()
                self._save_progress_on_close = False
                self._focus_play_pause()
                self.set_status(
                    "Finished. Progress cleared. Press Escape to exit.",
                    announce=True,
                )

    def _on_player_error(self, _error, message: str = ""):
        text = message or "Could not play this audiobook."
        self.set_status(text, announce=True)
        exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Warning,
            title="Play",
            text=text,
        )

    def _current_progress(self) -> tuple[int | None, str]:
        if self._player is None or not self._playlist:
            return None, ""
        position = max(0, int(self._player.position()))
        file_name = ""
        if self._folder_mode:
            file_name = self._playlist[self._playlist_index].name
        if position <= 0 and not file_name:
            return None, ""
        return position, file_name

    def _persist_listen_progress(
        self, position_ms: int | None, file_name: str
    ) -> None:
        if self._book is not None:
            self._book.listen_position_ms = position_ms
            self._book.listen_file_name = file_name or ""
        book_id = getattr(self._book, "book_id", None) if self._book else None
        if self._db is None or book_id is None:
            return
        from src.database import BookQueries

        BookQueries(self._db).update_listen_progress(
            book_id, position_ms, file_name or ""
        )

    def _clear_listen_progress(self) -> None:
        self._persist_listen_progress(None, "")

    def _save_listen_progress(self) -> None:
        if not self._save_progress_on_close:
            return
        position_ms, file_name = self._current_progress()
        if position_ms is None:
            return
        self._persist_listen_progress(position_ms, file_name)

    def _keep_above_owner(self):
        self.raise_()
        self.activateWindow()
        owner = self.owner_widget
        if owner is None or sys.platform != "win32":
            return
        try:
            import ctypes

            child = int(self.winId())
            owner_hwnd = int(owner.winId())
            ctypes.windll.user32.SetWindowLongPtrW(child, -8, owner_hwnd)
            hwnd_top = 0
            ctypes.windll.user32.SetWindowPos(
                child, hwnd_top, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040
            )
        except Exception:
            pass

    def request_close(self) -> None:
        """Escape/close: ask before saving when position is under 5 minutes."""
        if self._closing:
            return
        if self._player is not None:
            try:
                from PySide6.QtMultimedia import QMediaPlayer

                if (
                    self._player.playbackState()
                    == QMediaPlayer.PlaybackState.PlayingState
                ):
                    self._player.pause()
                    self._sync_play_button()
            except Exception:
                pass
        if self._save_progress_on_close:
            position_ms, _file_name = self._current_progress()
            if (
                position_ms is not None
                and 0 < position_ms < SAVE_PROMPT_BELOW_MS
            ):
                reply = exec_styled_message_box(
                    self,
                    self.scaler.get_scaled_size(20),
                    icon=QMessageBox.Question,
                    title="Save position?",
                    text="Save listening position?",
                    buttons=QMessageBox.Yes | QMessageBox.No,
                    default_button=QMessageBox.No,
                )
                if reply != QMessageBox.Yes:
                    self._save_progress_on_close = False
        self.close()

    def showEvent(self, event):
        super().showEvent(event)
        self._keep_above_owner()

    def closeEvent(self, event):
        global _open_preview
        self._closing = True
        owner = self.owner_widget
        self._save_listen_progress()
        if self._player is not None:
            self._player.stop()
        restore_preview_stderr()
        if _open_preview is self:
            _open_preview = None
        super().closeEvent(event)
        if owner is not None and hasattr(owner, "restore_main_focus_after_modal"):
            QTimer.singleShot(0, owner.restore_main_focus_after_modal)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.request_close()
            return
        if event.key() == Qt.Key_Space:
            self.on_play_pause()
            return
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            focus = self.focusWidget()
            if isinstance(focus, QAbstractButton) and focus.isEnabled():
                focus.click()
                return
        super().keyPressEvent(event)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.request_close()
                return True
            if event.key() == Qt.Key_Space and not isinstance(source, QComboBox):
                self.on_play_pause()
                return True
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if isinstance(source, QAbstractButton) and source.hasFocus():
                    source.click()
                    return True
            if event.key() in (Qt.Key_Tab, Qt.Key_Backtab):
                # Own Tab path so Rewind / Forward are never skipped.
                forward = event.key() == Qt.Key_Tab and not (
                    event.modifiers() & Qt.ShiftModifier
                )
                if self._move_preview_focus(forward=forward):
                    return True
            if event.key() in (Qt.Key_Left, Qt.Key_Right):
                # Arrow between transport controls (includes Rewind / Forward).
                # Leave Left/Right on the seek slider for scrubbing.
                if source in self._transport_focus_widgets():
                    if self._move_transport_focus(event.key() == Qt.Key_Right):
                        return True
            if is_unmapped_alt_letter(event, self.ALLOWED_ALT_LETTERS):
                QApplication.beep()
                return True
        return super().eventFilter(source, event)
