"""
AccessibleDialog — base class for all QDialog windows in AbCS.

Fixes JAWS Insert+T reading the wrong window title.

Root cause
----------
Qt's accessibility bridge (MSAA/UIA) exposes QDialog(parent=X) as an
accessibility CHILD of X. When JAWS presses Insert+T it walks up the
accessibility tree from the focused control:

  focused_control → ... → BookDetailsWindow → MainWindow

and reads MainWindow's title instead of "Book Details".

Fix
---
Pass parent=None to QDialog.__init__ so this dialog is a ROOT in the
accessibility tree. JAWS then walks up, finds no further window ancestor,
and correctly reads this dialog's title.

Win32 owner is set separately via SetWindowLongPtrW so the dialog still
groups with its owner in the taskbar and stays above it in z-order —
without creating an accessibility parent chain.
"""

import sys

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Qt, QTimer


def _set_win32_owner(child_hwnd: int, owner_hwnd: int) -> None:
    """Set the Win32 owner of a window without making it a Qt child widget."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        # GWL_HWNDPARENT (-8) sets the owner (not parent) for popup windows.
        ctypes.windll.user32.SetWindowLongPtrW(child_hwnd, -8, owner_hwnd)
    except Exception:
        pass


class AccessibleDialog(QDialog):
    """
    QDialog subclass that appears as a root window in the MSAA/UIA
    accessibility tree so JAWS Insert+T reads the correct title.

    Subclasses that override showEvent must call super().showEvent(event).
    Subclasses that override done() must call super().done(r).
    """

    def __init__(self, parent=None):
        self._owner_widget = parent
        # No Qt parent → no accessibility parent chain → JAWS reads THIS
        # window's title instead of the parent's.
        super().__init__(None)
        self.setAttribute(Qt.WA_NativeWindow, True)
        if parent is not None:
            # Force HWND creation, then wire up Win32 ownership so the dialog
            # groups with the owner in the taskbar and stays above it.
            _ = self.winId()
            _set_win32_owner(int(self.winId()), int(parent.winId()))

    def showEvent(self, event):
        super().showEvent(event)
        # Re-fire a focus event 300 ms after opening.  Subclasses typically
        # set focus via singleShot(0), which fires before JAWS has registered
        # the new window.  This later shot ensures JAWS receives the focus
        # event while the dialog is already in its window list, so Insert+T
        # reads the correct title without the user needing to Tab first.
        # Modeless utility windows (e.g. import progress) set
        # _announce_focus_on_show = False to avoid stealing focus repeatedly.
        if getattr(self, "_announce_focus_on_show", True):
            QTimer.singleShot(300, self._refire_focus_for_screen_reader)

    def _refire_focus_for_screen_reader(self):
        if not self.isVisible():
            return
        widget = self.focusWidget()
        if widget is not None and widget is not self:
            widget.clearFocus()
            widget.setFocus(Qt.OtherFocusReason)
        else:
            self.setFocus(Qt.OtherFocusReason)

    def done(self, r):
        super().done(r)
