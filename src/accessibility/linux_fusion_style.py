"""Linux Fusion style tweaks for QComboBox popup and painting."""

from PySide6.QtWidgets import QProxyStyle, QStyle


class LinuxFusionStyle(QProxyStyle):
    """Use scrollable combo popups; avoids Fusion menu-mode painter glitches."""

    def styleHint(self, hint, option=None, widget=None, returnType=None):
        if hint == QStyle.StyleHint.SH_ComboBox_Popup:
            return 0
        return super().styleHint(hint, option, widget, returnType)
