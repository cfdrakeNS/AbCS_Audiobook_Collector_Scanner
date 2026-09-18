"""Accessible dialog for Help → Check for updates."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from src.accessibility.accessible_events import announce_dialog_opened
from src.core.update_check import UpdateCheckResult
from src.ui.accessible_dialog import AccessibleDialog


class UpdateCheckDialog(AccessibleDialog):
    def __init__(self, result: UpdateCheckResult, parent=None):
        super().__init__(parent)
        from src.accessibility.icon_helper import get_app_icon

        self.setWindowIcon(get_app_icon())
        self.result = result
        self.setWindowTitle("Check for updates")
        self.setModal(True)

        if result.offline or result.error:
            body = result.error or "Could not check for updates."
            name = "Update check failed"
        elif result.is_newer:
            body = (
                f"A newer version is available.\n\n"
                f"Current version: {result.current}\n"
                f"Latest version: {result.latest}"
            )
            name = "Update available"
        else:
            body = (
                f"You are up to date.\n\n"
                f"Current version: {result.current}\n"
                f"Latest version: {result.latest or result.current}"
            )
            name = "AbCS is up to date"

        self.setAccessibleName(name)
        self.setAccessibleDescription(body.replace("\n", " "))

        layout = QVBoxLayout(self)
        label = QLabel(body)
        label.setWordWrap(True)
        label.setFocusPolicy(Qt.StrongFocus)
        label.setAccessibleName(name)
        layout.addWidget(label)

        buttons = QHBoxLayout()
        self.open_btn = QPushButton("Open download page")
        self.open_btn.setAccessibleName("Open download page")
        self.open_btn.clicked.connect(self._open_download)
        self.open_btn.setDefault(True)
        self.close_btn = QPushButton("Close")
        self.close_btn.setAccessibleName("Close")
        self.close_btn.clicked.connect(self.accept)
        buttons.addWidget(self.open_btn)
        buttons.addWidget(self.close_btn)
        layout.addLayout(buttons)
        self.resize(420, 200)

    def _open_download(self) -> None:
        QDesktopServices.openUrl(QUrl(self.result.download_url))

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
        announce_dialog_opened(self, self.accessibleName())
        self.open_btn.setFocus(Qt.OtherFocusReason)
