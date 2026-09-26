"""App-wide QProxyStyle tweaks for accessibility."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QProxyStyle, QStyle


class AccessibleAppStyle(QProxyStyle):
    """Keep disabled menu items in the keyboard/arrow list for screen readers.

    Also forces scrollable combo popups on Linux (Fusion menu-mode painter
    glitches).
    """

    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.StyleHint.SH_Menu_AllowActiveAndDisabled:
            return 1
        if (
            hint == QStyle.StyleHint.SH_ComboBox_Popup
            and sys.platform.startswith("linux")
        ):
            return 0
        return super().styleHint(hint, option, widget, returnData)
