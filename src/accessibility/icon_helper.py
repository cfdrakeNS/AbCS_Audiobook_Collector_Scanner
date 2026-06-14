"""
Centralized AbCS Icon Helper

Provides the application window icon and Qt standard icons for major action buttons.
Icons are decorative; accessible names describe the action, not the icon.
"""

from __future__ import annotations

import os
import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QImageReader, QPixmap
from PySide6.QtWidgets import QApplication, QStyle

from src.accessibility.graphics_paths import (
    APP_ICON_CANDIDATES,
    resolve_app_icon_path,
    resolve_graphics_path,
)


def _icon_candidate_paths() -> list[str]:
    if sys.platform.startswith("win32"):
        candidates = (
            "abcs_icon_256x256.ico",
            "abcs_icon_256x256.png",
            "abcs_source_256.png",
            "AbCS_WinTitle.png",
            "abcs_WinTitle.png",
        )
    else:
        candidates = APP_ICON_CANDIDATES

    paths: list[str] = []
    seen: set[str] = set()
    for filename in candidates:
        path = os.path.abspath(resolve_graphics_path(filename))
        if path in seen:
            continue
        seen.add(path)
        if os.path.isfile(path):
            paths.append(path)
    return paths


def _load_icon_from_path(path: str) -> QIcon:
    """Build a multi-size QIcon; required for many Linux window managers."""
    if not os.path.isfile(path):
        return QIcon()

    reader = QImageReader(path)
    reader.setAutoTransform(True)
    image = reader.read()
    if not image.isNull():
        pixmap = QPixmap.fromImage(image)
        if not pixmap.isNull():
            icon = QIcon()
            for size in (16, 24, 32, 48, 64, 128, 256):
                scaled = pixmap.scaled(
                    QSize(size, size),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                icon.addPixmap(scaled)
            if not icon.isNull():
                return icon

    icon = QIcon(path)
    if not icon.isNull():
        return icon

    return QIcon()


def resource_path() -> str:
    """Get absolute path to the preferred application window icon asset."""
    return resolve_app_icon_path()


def get_app_icon() -> QIcon:
    """Return the QIcon for all setWindowIcon calls in windows and popups."""
    for path in _icon_candidate_paths():
        icon = _load_icon_from_path(path)
        if not icon.isNull():
            return icon
    return QIcon()


def install_app_icon(app: QApplication) -> bool:
    """Set the application window icon; returns True when an icon loaded."""
    icon = get_app_icon()
    if icon.isNull():
        return False
    app.setWindowIcon(icon)
    return True


ICON_PATH = resource_path()


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
        "plot_filter": QStyle.StandardPixmap.SP_FileDialogDetailedView,
        "read_filter": QStyle.StandardPixmap.SP_DialogApplyButton,
        "recently_added_filter": QStyle.StandardPixmap.SP_FileDialogListView,
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
