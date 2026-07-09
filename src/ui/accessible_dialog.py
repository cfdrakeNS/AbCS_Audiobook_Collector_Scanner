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


def _focus_refire_delay_ms() -> int:
    """Return the focus-refire delay in milliseconds.

    300 ms is the minimum safe value for JAWS and NVDA.  Reducing below this
    causes JAWS to receive the clearFocus/setFocus pair while still in its own
    window-open reading sequence, which triggers a spurious full-window read
    (the same behaviour as Insert+B).  It also causes NVDA Alt+/ speech to be
    interrupted when the timer fires during a status bar announcement.

    Qt 6.11 improved MSAA/UIA top-level window registration on Windows, but
    the refire uses focus events (not registration), so the improvement does
    not reduce the safe minimum delay.  Keep 300 ms unconditionally.
    """
    return 300


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

    @property
    def owner_widget(self):
        """Logical owner window (Qt parent() is None for screen-reader isolation)."""
        return self._owner_widget

    def showEvent(self, event):
        super().showEvent(event)
        # Re-fire a focus event after opening so JAWS/NVDA receive it once
        # the dialog is registered in the AT window list and Insert+T reads
        # the correct title without the user needing to Tab first.
        # The delay is 100 ms on Qt 6.11+ (improved window/focus registration)
        # and 300 ms on older Qt builds.
        # Modeless utility windows (e.g. import progress) set
        # _announce_focus_on_show = False to avoid stealing focus repeatedly.
        if getattr(self, "_announce_focus_on_show", True):
            QTimer.singleShot(
                _focus_refire_delay_ms(), self._refire_focus_for_screen_reader
            )

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
