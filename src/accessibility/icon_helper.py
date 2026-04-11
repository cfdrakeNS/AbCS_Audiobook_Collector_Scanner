"""
Centralized AbCS Icon Helper

Provides a single function to retrieve the application icon for all windows and popups.
Ensures consistent branding and easy updates.
"""

from PySide6.QtGui import QIcon
import os

# Path to the application icon (relative to project root)
ICON_PATH = os.path.join("data", "graphics", "abCS_icon_title_bar.ico")


def get_app_icon() -> QIcon:
    """
    Returns the QIcon for the AbCS application.
    Use this for all setWindowIcon calls in windows and popups.
    """
    return QIcon(ICON_PATH)
