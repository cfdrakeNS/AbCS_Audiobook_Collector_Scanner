"""
Centralized AbCS Icon Helper

Provides a single function to retrieve the application icon for all windows and popups.
Ensures consistent branding and easy updates.
"""

from PySide6.QtGui import QIcon
import os
import sys


def resource_path():
    """Get absolute path to resource, works for dev, PyInstaller, and installed."""
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller bundle
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # Try lowercase graphics first, then fallback to capitalized
    icon_path = os.path.join(base, "graphics", "abcs_icon_256x256.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(base, "Graphics", "abcs_icon_256x256.ico")
    return icon_path


ICON_PATH = resource_path()


def get_app_icon() -> QIcon:
    """
    Returns the QIcon for the AbCS application.
    Use this for all setWindowIcon calls in windows and popups.
    """
    return QIcon(ICON_PATH)
