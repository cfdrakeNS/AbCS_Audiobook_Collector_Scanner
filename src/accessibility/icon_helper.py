"""
Centralized AbCS Icon Helper

Provides the application window icon and Qt standard icons for major action buttons.
Icons are decorative; accessible names describe the action, not the icon.
"""

from __future__ import annotations

import os
import sys

from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QStyle


def resource_path():
    """Get absolute path to resource, works for dev, PyInstaller, and installed."""
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    icon_path = os.path.join(base, "graphics", "abcs_icon_256x256.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(base, "Graphics", "abcs_icon_256x256.ico")
    return icon_path


ICON_PATH = resource_path()


def get_app_icon() -> QIcon:
    """Return the QIcon for all setWindowIcon calls in windows and popups."""
    return QIcon(ICON_PATH)


def _action_pixmap_map() -> dict[str, QStyle.StandardPixmap]:
    """Map logical action roles to Qt standard pixmaps (no extra dependencies)."""
    mapping: dict[str, QStyle.StandardPixmap] = {
        "add": QStyle.StandardPixmap.SP_DialogApplyButton,
        "add_book": QStyle.StandardPixmap.SP_FileDialogNewFolder,
        "browse": QStyle.StandardPixmap.SP_DirOpenIcon,
        "cancel": QStyle.StandardPixmap.SP_DialogCancelButton,
        "close": QStyle.StandardPixmap.SP_DialogCloseButton,
        "delete": QStyle.StandardPixmap.SP_TrashIcon,
        "edit": QStyle.StandardPixmap.SP_FileDialogContentsView,
        "export": QStyle.StandardPixmap.SP_DialogSaveButton,
        "find": QStyle.StandardPixmap.SP_FileDialogContentsView,
        "help": QStyle.StandardPixmap.SP_DialogHelpButton,
        "import": QStyle.StandardPixmap.SP_DriveNetIcon,
        "new": QStyle.StandardPixmap.SP_FileDialogNewFolder,
        "ok": QStyle.StandardPixmap.SP_DialogOkButton,
        "preferences": QStyle.StandardPixmap.SP_FileDialogInfoView,
        "restore": QStyle.StandardPixmap.SP_BrowserReload,
        "save": QStyle.StandardPixmap.SP_DialogSaveButton,
        "scan": QStyle.StandardPixmap.SP_DriveNetIcon,
        "search_web": QStyle.StandardPixmap.SP_BrowserReload,
        "statistics": QStyle.StandardPixmap.SP_ComputerIcon,
        "update": QStyle.StandardPixmap.SP_FileDialogContentsView,
    }
    if hasattr(QStyle.StandardPixmap, "SP_DialogResetButton"):
        mapping["restore"] = QStyle.StandardPixmap.SP_DialogResetButton
    return mapping


def get_action_icon(role: str) -> QIcon:
    """Return a theme-aware standard icon for a known action role, or an empty icon."""
    pixmap = _action_pixmap_map().get(role)
    if pixmap is None:
        return QIcon()
    app = QApplication.instance()
    if app is None:
        return QIcon()
    style = app.style()
    if style is None:
        return QIcon()
    return style.standardIcon(pixmap)


def action_icon_size(scaler=None, base_pixels: int = 16) -> QSize:
    """Icon size scaled with UIScaler when available."""
    if scaler is not None and hasattr(scaler, "get_scaled_size"):
        side = max(scaler.get_scaled_size(base_pixels), 12)
    else:
        side = base_pixels
    return QSize(side, side)


def apply_decorative_action_icon(widget, role: str, scaler=None) -> None:
    """Place a standard icon beside visible text without changing accessible names."""
    icon = get_action_icon(role)
    if icon.isNull():
        return
    if isinstance(widget, QAction):
        widget.setIcon(icon)
        return
    widget.setIcon(icon)
    if hasattr(widget, "setIconSize"):
        widget.setIconSize(action_icon_size(scaler))
