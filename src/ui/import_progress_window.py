"""Accessible import scan progress window."""

from __future__ import annotations

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QShortcut, QKeySequence, QAccessible
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QStatusBar,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)

from src.accessibility.scaling import UIScaler
from src.accessibility.style_helpers import build_accessible_button_style, exec_styled_message_box
from src.accessibility.theme_manager import ThemeManager
from src.accessibility.key_filters import is_unmapped_alt_letter
from src.accessibility.accessible_events import announce_status_message


class ImportProgressWindow(QDialog):
    """Modeless progress window for long-running import scans."""

    # This window intentionally uses local shortcuts only (F1, Escape, Alt+/).
    ALLOWED_ALT_LETTERS = set()

    def __init__(self, scaler: UIScaler, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)

        self.scaler = scaler
        self.theme_manager = theme_manager
        self._default_status_message = "Ready"
        self._cancel_requested = False
        self._scan_active = True
        self._compact_mode = False

        self.setup_ui()
        self.setup_shortcuts()
        self.install_event_filters()
        self.apply_control_styles()

        self.setWindowTitle("Import Progress")
        self.setAccessibleName("Import Progress")
        self.setAccessibleDescription(
            "Shows import scan progress and cancel control"
        )
        self.resize(760, 176)  # Reduced height by about 20% from original 220
        self.set_status("Ready")

    @property
    def cancel_requested(self) -> bool:
        return self._cancel_requested

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 6)
        layout.setSpacing(6)

        title_layout = QHBoxLayout()
        self.title_label = QLabel("Title:")
        self.title_edit = QLineEdit()
        self.title_edit.setReadOnly(True)
        self.title_edit.setFocusPolicy(Qt.NoFocus)
        self.title_edit.setAccessibleName("Current title")
        self.title_edit.setAccessibleDescription(
            "Current title being processed")
        self.title_label.setBuddy(self.title_edit)
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.title_edit, 1)
        layout.addLayout(title_layout)

        author_layout = QHBoxLayout()
        self.author_label = QLabel("Author:")
        self.author_edit = QLineEdit()
        self.author_edit.setReadOnly(True)
        self.author_edit.setFocusPolicy(Qt.NoFocus)
        self.author_edit.setAccessibleName("Current author")
        self.author_edit.setAccessibleDescription(
            "Current author being processed")
        self.author_label.setBuddy(self.author_edit)
        author_layout.addWidget(self.author_label)
        author_layout.addWidget(self.author_edit, 1)
        layout.addLayout(author_layout)

        # Issues controls removed; all info is now on the status bar

        layout.addStretch(1)

        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(8)
        self.scan_progress = QProgressBar()
        self.scan_progress.setAccessibleName("Scan progress")
        self.scan_progress.setAccessibleDescription(
            "Shows progress while scanning audio files"
        )
        self.scan_progress.setRange(0, 100)
        self.scan_progress.setValue(0)
        self.scan_progress.setFormat("Scanning... %p%")
        # Increase progress bar height by 10%
        default_height = self.scan_progress.sizeHint().height()
        self.scan_progress.setFixedHeight(int(default_height * 1.1))
        progress_layout.addWidget(self.scan_progress, 1)
        layout.addLayout(progress_layout)

        layout.addStretch(1)

        footer_layout = QHBoxLayout()
        footer_layout.addStretch(1)

        layout.addLayout(footer_layout)

        self.status_bar = QStatusBar()
        self.status_bar.setAccessibleName("Status")
        self.status_bar.setAccessibleDescription("Import progress status")
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(self.status_bar)

        self._apply_tab_order()

    def set_show_valid_counter(self, enabled: bool):
        """Compatibility no-op: counter widgets were removed in favor of status-only updates."""
        return

    def _apply_tab_order(self):
        return

    def set_compact_mode(self, enabled: bool):
        self._compact_mode = bool(enabled)
        show_details = not self._compact_mode
        self.title_label.setVisible(show_details)
        self.title_edit.setVisible(show_details)
        self.author_label.setVisible(show_details)
        self.author_edit.setVisible(show_details)
        # Issues controls removed
        self._apply_tab_order()

    def setup_shortcuts(self):
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.setContext(Qt.ApplicationShortcut)
        self.status_shortcut.activated.connect(self.on_read_status_bar)

        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.escape_shortcut.activated.connect(self.on_close_requested)

    def install_event_filters(self):
        self.installEventFilter(self)
        for widget in self.findChildren(QLineEdit):
            widget.installEventFilter(self)
        self.status_bar.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() in (QEvent.ShortcutOverride, QEvent.KeyPress):
            is_alt = bool(event.modifiers() & Qt.AltModifier)
            is_status_key = event.key() in (
                Qt.Key_Slash,
                Qt.Key_7,
            )
            is_status_text = event.text() == "/"
            if is_alt and (is_status_key or is_status_text):
                self.on_read_status_bar()
                event.accept()
                return True

            if is_unmapped_alt_letter(event, self.ALLOWED_ALT_LETTERS):
                return True
        return super().eventFilter(source, event)

    def keyPressEvent(self, event):
        is_alt = bool(event.modifiers() & Qt.AltModifier)
        is_status_key = event.key() in (
            Qt.Key_Slash,
            Qt.Key_7,
        )
        is_status_text = event.text() == "/"
        if is_alt and (is_status_key or is_status_text):
            self.on_read_status_bar()
            event.accept()
            return
        super().keyPressEvent(event)

    def apply_control_styles(self):
        scaled_height = max(self.scaler.get_scaled_size(20), 16)
        progress_height = max(self.scaler.get_scaled_size(14), 12)

        lineedit_style = f"""
            QLineEdit {{
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
                padding: 2px 4px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }}
            QLineEdit:focus {{
                border: 2px solid palette(highlight);
                background-color: palette(base);
            }}
        """
        # Use theme manager styling for text boxes
        for widget in self.findChildren(QLineEdit):
            widget.setStyleSheet("")  # Clear local style

        progress_style = f"""
            QProgressBar {{
                min-height: {progress_height}px;
                max-height: {progress_height}px;
                border: 1px solid palette(dark);
                border-radius: 3px;
                text-align: center;
                background-color: palette(base);
            }}
            QProgressBar::chunk {{
                background-color: palette(highlight);
            }}
        """
        self.scan_progress.setStyleSheet(progress_style)

        button_style = build_accessible_button_style(
            self.scaler.get_scaled_size(20))
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(button_style)

        self.status_bar.setFixedHeight(
            max(self.scaler.get_scaled_size(22), 18))

    def set_status(self, message: str, announce: bool = False):
        self._default_status_message = message
        announce_status_message(self.status_bar, message, move_focus=announce)

    def on_read_status_bar(self):
        status_text = self.status_bar.currentMessage() or self._default_status_message
        if QAccessible.isActive():
            self.set_status(status_text, announce=True)
        else:
            exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Status Bar",
                text=f"No screen reader active.\n\nStatus: {status_text}",
            )

    def update_scan_progress(
        self,
        *,
        processed: int,
        total: int,
        elapsed_text: str,
        current_title: str = "",
        current_author: str = "",
    ):
        if current_title:
            self.title_edit.setText(current_title)
        if current_author:
            self.author_edit.setText(current_author)

        if total > 0:
            percent = int((processed / total) * 100)
            self.scan_progress.setValue(max(0, min(100, percent)))
            self.scan_progress.setFormat(f"Scanning {processed}/{total}")
        else:
            self.scan_progress.setValue(0)
            self.scan_progress.setFormat("Scanning...")

    def prepare_for_add_phase(self, total_books: int):
        """Prepare progress display for add phase."""
        safe_total = max(0, int(total_books))
        self._scan_active = True
        self.scan_progress.setValue(0)
        if safe_total > 0:
            self.scan_progress.setFormat(f"Adding... 0/{safe_total}")
            self.set_status(
                f"Adding started. 0/{safe_total}. Press Alt+/ for status.", announce=True)
        else:
            self.scan_progress.setFormat("Adding...")
            self.set_status(
                "Adding started. Press Alt+/ for status.", announce=True)

    def update_add_progress(
        self,
        *,
        processed: int,
        total: int,
        books_added: int | None = None,
        elapsed_text: str | None = None,
    ):
        """Update progress during add/processing phase."""
        safe_total = max(0, int(total))
        safe_processed = max(0, int(processed))
        if safe_total > 0:
            safe_processed = min(safe_processed, safe_total)
            percent = int((safe_processed / safe_total) * 100)
            self.scan_progress.setValue(percent)
            self.scan_progress.setFormat(
                f"Adding... {safe_processed}/{safe_total}")
            status_text = f"Adding {safe_processed}/{safe_total}"
        else:
            self.scan_progress.setValue(0)
            self.scan_progress.setFormat("Adding...")
            status_text = "Adding"

        if elapsed_text is not None:
            status_text = f"{status_text} | Elapsed {elapsed_text}"

        self.set_status(status_text)

    def update_current_item(self, *, title: str, author: str, issues_text: str = ""):
        if self._compact_mode:
            return

        self.title_edit.setText(title or "")
        self.author_edit.setText(author or "")
        # Issues controls removed

    def update_counters(
        self,
        *,
        files_scanned: int | None = None,
        elapsed_text: str | None = None,
        books_added: int | None = None,
        valid_books: int | None = None,
        read_errors: int | None = None,
    ):
        return

    def on_close_requested(self):
        if self._scan_active and not self._cancel_requested:
            reply = exec_styled_message_box(
                self,
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Question,
                title="Cancel Scan",
                text=(
                    "Cancel the current scan?\n\n"
                    "Yes: stop scanning and keep partial results.\n"
                    "No: continue scanning."
                ),
                buttons=QMessageBox.Yes | QMessageBox.No,
                default_button=QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self._cancel_requested = True
                self.set_status("Canceling scan...")
            else:
                self.set_status("Continuing scan")
            return
        self.accept()

    def mark_scan_complete(
        self,
        *,
        canceled: bool,
        elapsed_text: str,
        files_scanned: int,
        books_added: int,
        valid_books: int,
        read_errors: int,
        summary_text: str | None = None,
    ):
        """Mark scan phase as complete."""
        self.mark_complete(
            canceled=canceled,
            elapsed_text=elapsed_text,
            files_scanned=files_scanned,
            books_added=books_added,
            valid_books=valid_books,
            read_errors=read_errors,
            summary_text=summary_text,
        )

    def mark_add_complete(self, books_added: int, elapsed_text: str):
        """Mark add phase as complete."""
        self._scan_active = False
        self.scan_progress.setValue(100)
        self.scan_progress.setFormat(
            f"Add complete - {books_added} book(s) added ({elapsed_text})")
        self.setFocusPolicy(Qt.StrongFocus)
        self.raise_()
        self.activateWindow()
        self.setFocus(Qt.TabFocusReason)
        self.set_status(
            f"Add complete. {books_added} book(s) added. Esc to close", announce=True)

    def mark_complete(
        self,
        *,
        canceled: bool,
        elapsed_text: str,
        files_scanned: int,
        books_added: int,
        valid_books: int,
        read_errors: int,
        summary_text: str | None = None,
    ):
        self._scan_active = False
        self.update_counters(
            files_scanned=files_scanned,
            elapsed_text=elapsed_text,
            books_added=books_added,
            valid_books=valid_books,
            read_errors=read_errors,
        )

        if canceled:
            self.scan_progress.setFormat(f"Scan canceled ({elapsed_text})")
        else:
            self.scan_progress.setValue(100)
            self.scan_progress.setFormat(f"Scan complete ({elapsed_text})")

        self.setFocusPolicy(Qt.StrongFocus)
        self.raise_()
        self.activateWindow()
        self.setFocus(Qt.TabFocusReason)

        if summary_text:
            message = summary_text.strip()
            if "esc to close" not in message.lower():
                message = f"{message}. Esc to close"
            self.set_status(message, announce=True)
            return

        if canceled:
            self.set_status(
                f"Scan canceled. Elapsed: {elapsed_text}. Esc to close.", announce=True)
        else:
            self.set_status(
                f"Scan complete. Elapsed: {elapsed_text}. Esc to close.", announce=True)

    def on_show_shortcuts(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Import Progress")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(500, 350)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        shortcuts = [
            ("Escape", "Close window"),
            ("Alt+/", "Read status bar"),
            ("F1", "Show this help"),
        ]
        from src.accessibility.shortcut_helpers import get_accessible_shortcuts_list, build_accessible_f1_popup_style
        shortcuts = get_accessible_shortcuts_list(shortcuts)

        table = QTableWidget()
        table.setAccessibleName("Shortcuts list")
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([""])
        table.setRowCount(len(shortcuts))
        table.setVerticalHeaderLabels([""] * len(shortcuts))
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        
        # Disable hover highlighting for low-vision comfort
        table.setMouseTracking(False)
        table.viewport().setMouseTracking(False)
        table.setAttribute(Qt.WA_Hover, False)
        table.viewport().setAttribute(Qt.WA_Hover, False)
        
        table.setStyleSheet(build_accessible_f1_popup_style())

        for row, (key, description) in enumerate(shortcuts):
            combined_text = f"{description} - {key}" if key else description
            item = QTableWidgetItem(combined_text)
            item.setData(
                Qt.AccessibleTextRole,
                f"{description}: {key}" if key else description,
            )
            table.setItem(row, 0, item)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        font = table.font()
        font.setPointSize(self.scaler.get_scaled_size(11))
        table.setFont(font)

        layout.addWidget(table)
        dlg.exec()

    def closeEvent(self, event):
        if self._scan_active and not self._cancel_requested:
            self.on_close_requested()
            event.ignore()
            return
        super().closeEvent(event)
