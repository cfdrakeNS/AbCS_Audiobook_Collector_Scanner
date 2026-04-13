"""
Centralized AbCS Icon Helper

Provides a single function to retrieve the application icon for all windows and popups.
Ensures consistent branding and easy updates.
"""

from PySide6.QtGui import QIcon
import os

# Path to the application icon (absolute, relative to this file)
ICON_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "graphics", "abcs.ico")
)


def get_app_icon() -> QIcon:
    """
    Returns the QIcon for the AbCS application.
    Use this for all setWindowIcon calls in windows and popups.
    """
    import os

    return QIcon(ICON_PATH)
