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

from accessibility.scaling import UIScaler
from accessibility.style_helpers import build_accessible_button_style, exec_styled_message_box
from accessibility.theme_manager import ThemeManager
from accessibility.key_filters import is_unmapped_alt_letter
from accessibility.accessible_events import announce_status_message


class ImportProgressWindow(QDialog):
    """Modeless progress window for long-running import scans."""

    ALLOWED_ALT_LETTERS = {
        'A', 'B', 'C', 'F', 'I', 'L', 'M', 'R', 'T'
    }

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
            "Shows import scan progress with current item, counters, and cancel control"
        )
        self.resize(760, 420)
        self.set_status("Ready")

    @property
    def cancel_requested(self) -> bool:
        return self._cancel_requested

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        title_layout = QHBoxLayout()
        self.title_label = QLabel("&Title:")
        self.title_edit = QLineEdit()
        self.title_edit.setReadOnly(True)
        self.title_edit.setFocusPolicy(Qt.NoFocus)
        self.title_edit.setAccessibleName("Current title")
        self.title_edit.setAccessibleDescription(
            "Current title being processed - Alt+T")
        self.title_label.setBuddy(self.title_edit)
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.title_edit, 1)
        layout.addLayout(title_layout)

        author_layout = QHBoxLayout()
        self.author_label = QLabel("&Author:")
        self.author_edit = QLineEdit()
        self.author_edit.setReadOnly(True)
        self.author_edit.setFocusPolicy(Qt.NoFocus)
        self.author_edit.setAccessibleName("Current author")
        self.author_edit.setAccessibleDescription(
            "Current author being processed - Alt+A")
        self.author_label.setBuddy(self.author_edit)
        author_layout.addWidget(self.author_label)
        author_layout.addWidget(self.author_edit, 1)
        layout.addLayout(author_layout)

        issues_layout = QHBoxLayout()
        self.issues_label = QLabel("&Issues:")
        self.issues_edit = QLineEdit()
        self.issues_edit.setReadOnly(True)
        self.issues_edit.setFocusPolicy(Qt.NoFocus)
        self.issues_edit.setAccessibleName("Issues")
        self.issues_edit.setAccessibleDescription(
            "Current issues for this item - Alt+I")
        self.issues_label.setBuddy(self.issues_edit)
        issues_layout.addWidget(self.issues_label)
        issues_layout.addWidget(self.issues_edit, 1)
        layout.addLayout(issues_layout)
        self.issues_label.setVisible(False)
        self.issues_edit.setVisible(False)

        counters_layout = QHBoxLayout()
        counters_layout.setSpacing(8)

        files_label = QLabel("&Files scanned:")
        self.files_edit = QLineEdit("0")
        self.files_edit.setReadOnly(True)
        self.files_edit.setFocusPolicy(Qt.NoFocus)
        self.files_edit.setMaximumWidth(90)
        self.files_edit.setAccessibleName("Files scanned")
        self.files_edit.setAccessibleDescription(
            "Number of files scanned - Alt+F")
        files_label.setBuddy(self.files_edit)

        elapsed_label = QLabel("Elapsed ti&me:")
        self.elapsed_edit = QLineEdit("00:00")
        self.elapsed_edit.setReadOnly(True)
        self.elapsed_edit.setFocusPolicy(Qt.NoFocus)
        self.elapsed_edit.setMaximumWidth(100)
        self.elapsed_edit.setAccessibleName("Elapsed time")
        self.elapsed_edit.setAccessibleDescription("Elapsed scan time - Alt+M")
        elapsed_label.setBuddy(self.elapsed_edit)

        added_label = QLabel("&Books added:")
        self.added_edit = QLineEdit("0")
        self.added_edit.setReadOnly(True)
        self.added_edit.setFocusPolicy(Qt.NoFocus)
        self.added_edit.setMaximumWidth(90)
        self.added_edit.setAccessibleName("Books added")
        self.added_edit.setAccessibleDescription(
            "Number of books added - Alt+B")
        added_label.setBuddy(self.added_edit)

        read_err_label = QLabel("Read e&rrors:")
        self.read_errors_edit = QLineEdit("0")
        self.read_errors_edit.setReadOnly(True)
        self.read_errors_edit.setFocusPolicy(Qt.NoFocus)
        self.read_errors_edit.setMaximumWidth(90)
        self.read_errors_edit.setAccessibleName("Read errors")
        self.read_errors_edit.setAccessibleDescription(
            "Number of read errors - Alt+R")
        read_err_label.setBuddy(self.read_errors_edit)

        counters_layout.addWidget(files_label)
        counters_layout.addWidget(self.files_edit)
        counters_layout.addWidget(elapsed_label)
        counters_layout.addWidget(self.elapsed_edit)
        counters_layout.addWidget(added_label)
        counters_layout.addWidget(self.added_edit)
        counters_layout.addWidget(read_err_label)
        counters_layout.addWidget(self.read_errors_edit)
        counters_layout.addStretch(1)
        layout.addLayout(counters_layout)

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
        progress_layout.addWidget(self.scan_progress, 1)
        layout.addLayout(progress_layout)

        footer_layout = QHBoxLayout()
        footer_layout.addStretch(1)

        self.cancel_button = QPushButton("Cance&l")
        self.cancel_button.setAccessibleName("Cancel")
        self.cancel_button.setAccessibleDescription(
            "Cancel running scan - Alt+L")
        self.cancel_button.clicked.connect(self.on_cancel_requested)
        footer_layout.addWidget(self.cancel_button)

        self.close_button = QPushButton("&Close")
        self.close_button.setAccessibleName("Close")
        self.close_button.setAccessibleDescription(
            "Close progress window - Alt+C")
        self.close_button.setVisible(False)
        self.close_button.clicked.connect(self.accept)
        footer_layout.addWidget(self.close_button)

        layout.addLayout(footer_layout)

        self.status_bar = QStatusBar()
        self.status_bar.setAccessibleName("Status")
        self.status_bar.setAccessibleDescription("Import progress status")
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.status_bar)

        self._apply_tab_order()

    def _apply_tab_order(self):
        if self._compact_mode:
            self.setTabOrder(self.cancel_button, self.close_button)
            return

        self.setTabOrder(self.cancel_button, self.close_button)

    def set_compact_mode(self, enabled: bool):
        self._compact_mode = bool(enabled)
        show_details = not self._compact_mode

        self.title_label.setVisible(show_details)
        self.title_edit.setVisible(show_details)
        self.author_label.setVisible(show_details)
        self.author_edit.setVisible(show_details)

        if self._compact_mode:
            self.issues_label.setVisible(False)
            self.issues_edit.setVisible(False)
        else:
            has_issues = bool(self.issues_edit.text().strip())
            self.issues_label.setVisible(has_issues)
            self.issues_edit.setVisible(has_issues)

        self._apply_tab_order()

    def setup_shortcuts(self):
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

        self.status_shortcut = QShortcut(QKeySequence("Alt+/"), self)
        self.status_shortcut.setContext(Qt.ApplicationShortcut)
        self.status_shortcut.activated.connect(self.on_read_status_bar)

        self.status_shortcut_shift = QShortcut(QKeySequence("Alt+?"), self)
        self.status_shortcut_shift.setContext(Qt.ApplicationShortcut)
        self.status_shortcut_shift.activated.connect(self.on_read_status_bar)

        self.cancel_shortcut = QShortcut(QKeySequence("Alt+L"), self)
        self.cancel_shortcut.activated.connect(self.on_cancel_requested)

        self.close_shortcut = QShortcut(QKeySequence("Alt+C"), self)
        self.close_shortcut.activated.connect(self.on_close_requested)

        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.escape_shortcut.activated.connect(self.on_close_requested)

    def install_event_filters(self):
        self.installEventFilter(self)
        for widget in self.findChildren(QLineEdit):
            widget.installEventFilter(self)
        self.cancel_button.installEventFilter(self)
        self.close_button.installEventFilter(self)
        self.status_bar.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() in (QEvent.ShortcutOverride, QEvent.KeyPress):
            is_alt = bool(event.modifiers() & Qt.AltModifier)
            is_status_key = event.key() in (Qt.Key_Slash, Qt.Key_Question)
            is_status_text = event.text() in ("/", "?")
            if is_alt and (is_status_key or is_status_text):
                self.on_read_status_bar()
                event.accept()
                return True

            if is_unmapped_alt_letter(event, self.ALLOWED_ALT_LETTERS):
                return True
        return super().eventFilter(source, event)

    def keyPressEvent(self, event):
        is_alt = bool(event.modifiers() & Qt.AltModifier)
        is_status_key = event.key() in (Qt.Key_Slash, Qt.Key_Question)
        is_status_text = event.text() in ("/", "?")
        if is_alt and (is_status_key or is_status_text):
            self.on_read_status_bar()
            event.accept()
            return
        super().keyPressEvent(event)

    def apply_control_styles(self):
        scaled_height = max(self.scaler.get_scaled_size(20), 16)

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
        for widget in self.findChildren(QLineEdit):
            widget.setStyleSheet(lineedit_style)

        progress_style = f"""
            QProgressBar {{
                min-height: {scaled_height}px;
                max-height: {scaled_height}px;
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
        status_text = self._default_status_message
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
        self.files_edit.setText(str(max(0, processed)))
        self.elapsed_edit.setText(elapsed_text)
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

    def update_current_item(self, *, title: str, author: str, issues_text: str = ""):
        if self._compact_mode:
            return

        self.title_edit.setText(title or "")
        self.author_edit.setText(author or "")

        normalized_issues = (issues_text or "").strip()
        has_issues = bool(normalized_issues)
        self.issues_label.setVisible(has_issues)
        self.issues_edit.setVisible(has_issues)
        self.issues_edit.setText(normalized_issues)

    def update_counters(
        self,
        *,
        files_scanned: int | None = None,
        elapsed_text: str | None = None,
        books_added: int | None = None,
        read_errors: int | None = None,
    ):
        if files_scanned is not None:
            self.files_edit.setText(str(max(0, int(files_scanned))))
        if elapsed_text is not None:
            self.elapsed_edit.setText(elapsed_text)
        if books_added is not None:
            self.added_edit.setText(str(max(0, int(books_added))))
        if read_errors is not None:
            self.read_errors_edit.setText(str(max(0, int(read_errors))))

    def on_cancel_requested(self):
        if not self._scan_active or self._cancel_requested:
            return

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

    def on_close_requested(self):
        if self._scan_active:
            self.on_cancel_requested()
            return
        self.accept()

    def mark_complete(
        self,
        *,
        canceled: bool,
        elapsed_text: str,
        files_scanned: int,
        books_added: int,
        read_errors: int,
        summary_text: str | None = None,
    ):
        self._scan_active = False
        self.update_counters(
            files_scanned=files_scanned,
            elapsed_text=elapsed_text,
            books_added=books_added,
            read_errors=read_errors,
        )

        if canceled:
            self.scan_progress.setFormat(f"Scan canceled ({elapsed_text})")
        else:
            self.scan_progress.setValue(100)
            self.scan_progress.setFormat(f"Scan complete ({elapsed_text})")

        self.cancel_button.setVisible(False)
        self.close_button.setVisible(True)
        self.close_button.setDefault(True)
        self.close_button.setFocus(Qt.TabFocusReason)

        if summary_text:
            self.set_status(summary_text, announce=True)
            return

        if canceled:
            self.set_status(
                f"Scan canceled. Elapsed: {elapsed_text}", announce=True)
        else:
            self.set_status(
                f"Scan complete. Elapsed: {elapsed_text}", announce=True)

    def on_show_shortcuts(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Import Progress")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(460, 420)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        shortcuts = [
            ("Alt+/", "Read status bar"),
            ("Alt+T", "Title"),
            ("Alt+A", "Author"),
            ("Alt+I", "Issues"),
            ("Alt+F", "Files scanned"),
            ("Alt+M", "Elapsed time"),
            ("Alt+B", "Books added"),
            ("Alt+R", "Read errors"),
            ("Alt+L", "Cancel scan"),
            ("Alt+C", "Close (on completion)"),
            ("F1", "Show this help"),
            ("Escape", "Close (on completion)"),
        ]

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
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setStyleSheet(
            "QTableWidget:focus { border: none; outline: none; }")

        for row, (key, description) in enumerate(shortcuts):
            text = f"{description} - {key}"
            item = QTableWidgetItem(text)
            item.setData(Qt.AccessibleTextRole, f"{description}: {key}")
            table.setItem(row, 0, item)

        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        font = table.font()
        font.setPointSize(self.scaler.get_scaled_size(11))
        table.setFont(font)
        layout.addWidget(table)

        close_btn = QPushButton("Close")
        close_btn.setAccessibleName("Close")
        close_btn.clicked.connect(dlg.accept)
        btn_font = close_btn.font()
        btn_font.setPointSize(self.scaler.get_scaled_size(11))
        close_btn.setFont(btn_font)
        layout.addWidget(close_btn)

        dlg.setTabOrder(table, close_btn)
        dlg.exec()

    def closeEvent(self, event):
        if self._scan_active:
            self.on_cancel_requested()
            event.ignore()
            return
        super().closeEvent(event)
