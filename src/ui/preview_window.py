"""In-app audiobook preview. Focus stays in AbCS."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QEvent, QTimer, QUrl, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
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
    build_modern_button_style,
    exec_styled_message_box,
)
from src.accessibility.theme_manager import ThemeManager
from src.core.audio_launcher import resolve_preview_file
from src.core.media_log import (
    mute_preview_stderr,
    restore_preview_stderr,
    silence_preview_media_logs,
)
from src.ui.accessible_dialog import AccessibleDialog

_open_preview = None


def _format_preview_length(length_text: str) -> str:
    raw = (length_text or "").strip().replace("_", "")
    if not raw or raw in {":", "00:00", "0:00"}:
        return "--:--"
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


def _format_preview_series(series_name: str, series_number="") -> str:
    name = (series_name or "").strip()
    from src.utils.text_utils import format_series_suffix

    number = format_series_suffix(series_number)
    if name and number:
        return f"{name} - {number}"
    return name or number


def _playback_status(state: str) -> str:
    return f"{state}. Press Escape to exit."


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
) -> tuple[bool, str]:
    """Resolve a book path and play it in the in-app Preview window."""
    target = resolve_preview_file(stored_path, collection_root=collection_root)
    if target.path is None:
        return False, target.error
    try:
        silence_preview_media_logs()
        from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

        silence_preview_media_logs()
        mute_preview_stderr()
    except ImportError:
        return False, "In-app preview needs Qt Multimedia."

    global _open_preview
    if _open_preview is not None:
        _open_preview.close()
        _open_preview = None

    window = PreviewWindow(
        parent,
        scaler,
        theme_manager,
        player_types=(QMediaPlayer, QAudioOutput),
    )
    ok, message = window.play_file(
        target.path,
        book_title=book_title,
        author_name=author_name,
        series_name=series_name,
        series_number=series_number,
        length_text=length_text,
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
    """Play or pause one resolved audiobook file. Escape closes and stops."""

    ALLOWED_ALT_LETTERS = {"/"}

    def __init__(
        self,
        parent,
        scaler: UIScaler,
        theme_manager: ThemeManager | None = None,
        player_types=None,
    ):
        super().__init__(parent)
        self.setWindowIcon(get_app_icon())
        self.scaler = scaler
        self.theme_manager = theme_manager
        from src.ui.help_router import preview_help_doc_for_owner

        self.help_doc_override = preview_help_doc_for_owner(parent)
        self._display_title = ""
        self._player = None
        self._audio = None
        self._video_sink = None
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

        self.setWindowTitle("Preview")
        self.setAccessibleName("Preview")
        self.setAccessibleDescription(
            "Play this audiobook inside AbCS. Enter plays or pauses. Escape closes."
        )
        self.resize(640, 220)
        self._setup_ui()
        self._setup_shortcuts()
        self.installEventFilter(self)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        info_row = QHBoxLayout()
        info_row.setSpacing(16)

        self.play_pause_button = QPushButton("Play")
        self.play_pause_button.setAccessibleName("Play or pause")
        self.play_pause_button.setAccessibleDescription(
            "Play or pause this audiobook. Press Enter."
        )
        self.play_pause_button.setDefault(False)
        self.play_pause_button.setAutoDefault(False)
        self.play_pause_button.setMinimumWidth(self.scaler.get_scaled_size(90))
        self.play_pause_button.setMinimumHeight(self.scaler.get_scaled_size(36))
        self.play_pause_button.clicked.connect(self.on_play_pause)
        self.play_pause_button.installEventFilter(self)
        info_row.addWidget(self.play_pause_button, 0, Qt.AlignTop)

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
        self.length_label = QLabel("Length:")
        self.length_label.setFocusPolicy(Qt.NoFocus)
        details.addWidget(self.title_label)
        details.addWidget(self.author_label)
        details.addWidget(self.series_label)
        details.addWidget(self.length_label)
        details.addStretch()
        info_row.addLayout(details, 1)
        layout.addLayout(info_row)
        self.track_label = self.title_label

        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        configure_status_bar_accessibility(self.status_bar)
        layout.addWidget(self.status_bar)

        scaled_height = int(20 * (self.scaler.current_scale / 100.0))
        button_style = build_modern_button_style(scaled_height)
        self.play_pause_button.setStyleSheet(button_style)
        apply_decorative_action_icon(self.play_pause_button, "preview", self.scaler)
        apply_visual_tooltip_map({self.play_pause_button: "Play or pause"})
        apply_status_bar_tooltip(self.status_bar, "Preview status")

    def _setup_shortcuts(self):
        status = QShortcut(QKeySequence("Alt+/"), self)
        status.setContext(Qt.WidgetWithChildrenShortcut)
        status.activated.connect(
            lambda: read_status_bar_message(self.status_bar, fallback="Ready")
        )
        escape = QShortcut(QKeySequence(Qt.Key_Escape), self)
        escape.setContext(Qt.WidgetWithChildrenShortcut)
        escape.activated.connect(self.close)
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        help_shortcut.activated.connect(self.on_show_shortcuts)
        from src.ui.help_router import install_shift_f1_help

        install_shift_f1_help(self, shortcut_context=Qt.WidgetWithChildrenShortcut)

    def set_status(self, message: str, announce: bool = False):
        announce_status_message(self.status_bar, message, move_focus=announce)

    def play_file(
        self,
        file_path: Path,
        book_title: str = "",
        author_name: str = "",
        series_name: str = "",
        series_number: str = "",
        length_text: str = "",
    ) -> tuple[bool, str]:
        if self._player is None:
            return False, "In-app preview needs Qt Multimedia."
        title = (book_title or "").strip() or file_path.name
        author = (author_name or "").strip()
        series = _format_preview_series(series_name, series_number)
        length = _format_preview_length(length_text)
        self._display_title = title
        self._set_info_line(self.title_label, f"Title: {title}")
        self._set_info_line(
            self.author_label, f"Author: {author}" if author else "Author:"
        )
        self._set_info_line(
            self.series_label, f"Series: {series}" if series else "Series:"
        )
        self._set_info_line(self.length_label, f"Length: {length}")
        self._player.setSource(QUrl.fromLocalFile(str(file_path)))
        self._player.play()
        self.set_status(_playback_status("Playing"), announce=True)
        self._sync_play_button()
        return True, _playback_status("Playing")

    def on_play_pause(self):
        if self._player is None:
            return
        from PySide6.QtMultimedia import QMediaPlayer

        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
            self.set_status(_playback_status("Paused"), announce=True)
        else:
            self._player.play()
            self.set_status(_playback_status("Playing"), announce=True)
        self._sync_play_button()

    def on_show_shortcuts(self):
        from src.accessibility.shortcut_helpers import exec_f1_shortcuts_dialog

        exec_f1_shortcuts_dialog(
            self,
            "Keyboard Shortcuts - Preview",
            [
                ("Enter", "Play or pause"),
                ("Escape", "Close and stop playback"),
                ("Alt+/", "Read status bar"),
                ("F1", "Show this help"),
            ],
        )

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
        self.play_pause_button.setText("Pause" if playing else "Play")
        apply_decorative_action_icon(
            self.play_pause_button,
            "pause" if playing else "preview",
            self.scaler,
        )

    def _on_state_changed(self, _state):
        self._sync_play_button()

    def _on_player_error(self, _error, message: str = ""):
        text = message or "Could not play this audiobook."
        self.set_status(text, announce=True)
        exec_styled_message_box(
            self,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Warning,
            title="Preview",
            text=text,
        )

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

    def showEvent(self, event):
        super().showEvent(event)
        self._keep_above_owner()

    def closeEvent(self, event):
        global _open_preview
        owner = self.owner_widget
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
            self.close()
            return
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            focus = self.focusWidget()
            if isinstance(focus, QPushButton) and focus.isEnabled():
                focus.click()
                return
        super().keyPressEvent(event)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.close()
                return True
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if isinstance(source, QPushButton) and source.hasFocus():
                    source.click()
                    return True
            if is_unmapped_alt_letter(event, self.ALLOWED_ALT_LETTERS):
                QApplication.beep()
                return True
        return super().eventFilter(source, event)
