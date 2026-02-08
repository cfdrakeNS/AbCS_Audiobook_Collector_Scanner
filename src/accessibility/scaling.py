"""
UI Scaling system for AbCS.
Manages application-wide font and UI scaling for accessibility.
"""

from PySide6.QtCore import QObject, Signal, QSettings
from PySide6.QtWidgets import QApplication
from typing import Optional


class UIScaler(QObject):
    """
    Manages application-wide UI scaling.

    Signals:
        scale_changed: Emitted when scale factor changes (new_scale: int)
    """

    scale_changed = Signal(int)

    # Scale presets (percentage)
    SCALE_PRESETS = {
        'Tiny': 75,
        'Small': 85,
        'Normal': 100,
        'Large': 125,
        'Extra Large': 150,
        'Huge': 175,
        'Maximum': 200
    }

    # Min/max scale
    MIN_SCALE = 50
    MAX_SCALE = 300
    SCALE_STEP = 15

    # Default scale - 150% gives ~14pt fonts (9pt base * 1.5 = 13.5pt)
    DEFAULT_SCALE = 150

    def __init__(self, app: QApplication):
        """
        Initialize UI scaler.

        Args:
            app: QApplication instance
        """
        super().__init__()
        self.app = app
        self.settings = QSettings('AbCS', 'AudioBookCollector')

        # Load saved scale or use default
        self._current_scale = self.settings.value(
            'ui_scale', self.DEFAULT_SCALE, type=int)
        self._apply_scale()

    @property
    def current_scale(self) -> int:
        """Get current scale percentage."""
        return self._current_scale

    def set_scale(self, percentage: int):
        """
        Set UI scale to specific percentage.

        Args:
            percentage: Scale percentage (50-300)
        """
        # Clamp to valid range
        percentage = max(self.MIN_SCALE, min(self.MAX_SCALE, percentage))

        if percentage != self._current_scale:
            self._current_scale = percentage
            self._apply_scale()
            self.scale_changed.emit(percentage)

            # Save to settings
            self.settings.setValue('ui_scale', percentage)

    def increase_scale(self, step: int = SCALE_STEP):
        """
        Increase scale (Ctrl/Cmd +).

        Args:
            step: Amount to increase by
        """
        new_scale = self._current_scale + step
        self.set_scale(new_scale)

    def decrease_scale(self, step: int = SCALE_STEP):
        """
        Decrease scale (Ctrl/Cmd -).

        Args:
            step: Amount to decrease by
        """
        new_scale = self._current_scale - step
        self.set_scale(new_scale)

    def reset_scale(self):
        """Reset to default scale (150% for ~14pt fonts)."""
        self.set_scale(self.DEFAULT_SCALE)

    def set_preset(self, preset_name: str):
        """
        Set scale to a named preset.

        Args:
            preset_name: One of SCALE_PRESETS keys
        """
        if preset_name in self.SCALE_PRESETS:
            self.set_scale(self.SCALE_PRESETS[preset_name])

    def get_preset_name(self) -> str:
        """
        Get name of current preset, or 'Custom'.

        Returns:
            Preset name or 'Custom'
        """
        for name, value in self.SCALE_PRESETS.items():
            if value == self._current_scale:
                return name
        return 'Custom'

    def _apply_scale(self):
        """Apply current scale to application."""
        # Calculate base font size
        # Normal = 9pt, scale proportionally
        base_size = 9  # Qt's default
        scaled_size = int(base_size * (self._current_scale / 100.0))

        # Update application font
        font = self.app.font()
        font.setPointSize(scaled_size)
        self.app.setFont(font)

        # Update stylesheet for fine-tuned control
        stylesheet = f"""
            /* Base font scaling */
            * {{
                font-size: {scaled_size}pt;
            }}

            /* Clear focus indicators */
            QComboBox:focus, QLineEdit:focus {{
                border: 2px solid palette(highlight);
                background-color: palette(base);
            }}

            /* Ensure minimum touch target size (44x44 at 100%) */
            QPushButton, QComboBox, QCheckBox {{
                min-height: {int(44 * self._current_scale / 100)}px;
                padding: {int(6 * self._current_scale / 100)}px;
            }}

            /* Table row height */
            QTableView {{
                selection-background-color: palette(highlight);
            }}

            QTableView::item:focus {{
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }}

            /* Selected rows: use highlight background and highlighted text */
            QTableView::item:selected {{
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }}

            QTableView::item {{
                padding: {int(8 * self._current_scale / 100)}px;
            }}

            /* Combo box dropdown */
            QComboBox {{
                padding-right: {int(20 * self._current_scale / 100)}px;
            }}

            /* Status bar */
            QStatusBar {{
                font-size: {int(scaled_size * 0.9)}pt;
            }}
        """

        self.app.setStyleSheet(stylesheet)

    def get_scaled_size(self, base_size: int) -> int:
        """
        Get scaled size for a given base size.

        Args:
            base_size: Base size in pixels

        Returns:
            Scaled size in pixels
        """
        return int(base_size * (self._current_scale / 100.0))


# Global instance
_scaler_instance: Optional[UIScaler] = None


def get_scaler(app: Optional[QApplication] = None) -> UIScaler:
    """
    Get global UI scaler instance.

    Args:
        app: QApplication (required on first call)

    Returns:
        UIScaler instance
    """
    global _scaler_instance
    if _scaler_instance is None:
        if app is None:
            raise ValueError(
                "QApplication required for first call to get_scaler()")
        _scaler_instance = UIScaler(app)
    return _scaler_instance
