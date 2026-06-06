"""
Theme manager for AbCS.
Manages color schemes and high contrast themes for accessibility.
"""

import re
import sys

from PySide6.QtCore import QObject, Signal, QSettings
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication, QWidget
from typing import Dict, Optional
from enum import Enum
from .style_helpers import (
    build_accessible_combo_box_style,
    build_accessible_date_edit_style,
    build_accessible_spinbox_style,
    build_group_box_style,
    build_theme_combo_color_overrides,
    build_theme_scrollbar_style,
)
from .windows_theme_detector import (
    detect_windows_dark_mode,
    get_fallback_dark_theme_colors,
    get_fallback_light_theme_colors,
)


class ThemeName(Enum):
    """Available theme names."""

    DEFAULT = "default"
    HIGH_CONTRAST_DARK = "high_contrast_dark"
    HIGH_CONTRAST_LIGHT = "high_contrast_light"
    DARK = "dark"
    SOLARIZED_LIGHT = "solarized_light"
    SOLARIZED_DARK = "solarized_dark"
    COMFORT_LIGHT = "comfort_light"
    MUTED_DARK = "muted_dark"
    NORD_LIGHT = "nord_light"
    OCEANIC_DARK = "oceanic_dark"
    FOREST_MIST = "forest_mist"
    PAPER_SEPIA = "paper_sepia"


class Theme:
    """Represents a color theme."""

    def __init__(self, name: str, colors: Dict[str, str]):
        """
        Initialize theme.

        Args:
            name: Theme display name
            colors: Dictionary of color roles to hex colors
        """
        self.name = name
        self.colors = colors

    def apply_to_palette(self, palette: QPalette) -> QPalette:
        """
        Apply theme colors to a QPalette.

        Args:
            palette: Palette to modify

        Returns:
            Modified palette
        """
        # Window (background)
        if "window" in self.colors:
            palette.setColor(QPalette.Window, QColor(self.colors["window"]))

        # Window text
        if "window_text" in self.colors:
            palette.setColor(QPalette.WindowText, QColor(self.colors["window_text"]))

        # Base (input background)
        if "base" in self.colors:
            palette.setColor(QPalette.Base, QColor(self.colors["base"]))

        # Text (input text)
        if "text" in self.colors:
            palette.setColor(QPalette.Text, QColor(self.colors["text"]))

        # Button background
        if "button" in self.colors:
            palette.setColor(QPalette.Button, QColor(self.colors["button"]))

        # Button text
        if "button_text" in self.colors:
            palette.setColor(QPalette.ButtonText, QColor(self.colors["button_text"]))

        # Highlight (selection)
        if "highlight" in self.colors:
            palette.setColor(QPalette.Highlight, QColor(self.colors["highlight"]))

        # Highlighted text
        if "highlight_text" in self.colors:
            palette.setColor(
                QPalette.HighlightedText, QColor(self.colors["highlight_text"])
            )

        # Link
        if "link" in self.colors:
            palette.setColor(QPalette.Link, QColor(self.colors["link"]))

        return palette


class ThemeManager(QObject):
    """
    Manages application themes and color schemes.

    Signals:
        theme_changed: Emitted when theme changes (theme_name: str)
    """

    theme_changed = Signal(str)
    SCALE_STYLE_BEGIN = "/* AbCS Scale Styles:BEGIN */"
    SCALE_STYLE_END = "/* AbCS Scale Styles:END */"

    # Built-in themes
    THEMES = {
        ThemeName.DEFAULT: Theme("Default (System)", {}),  # Use system colors
        ThemeName.HIGH_CONTRAST_DARK: Theme(
            "High Contrast Dark",
            {
                "window": "#000000",
                "window_text": "#FFFFFF",
                "base": "#000000",
                "text": "#FFFFFF",
                "button": "#000000",
                "button_text": "#FFFFFF",
                "highlight": "#00FF00",  # Bright green selection - more visible than yellow
                "highlight_text": "#000000",
                "link": "#00FFFF",
            },
        ),
        ThemeName.HIGH_CONTRAST_LIGHT: Theme(
            "High Contrast Light",
            {
                "window": "#FFFFFF",
                "window_text": "#000000",
                "base": "#FFFFFF",
                "text": "#000000",
                "button": "#FFFFFF",
                "button_text": "#000000",
                "highlight": "#000080",  # Navy selection
                "highlight_text": "#FFFFFF",
                "link": "#0000FF",
            },
        ),
        ThemeName.DARK: Theme(
            "Dark",
            {
                "window": "#2B2B2B",
                "window_text": "#E0E0E0",
                "base": "#1E1E1E",
                "text": "#E0E0E0",
                "button": "#3C3C3C",
                "button_text": "#E0E0E0",
                "highlight": "#0078D4",
                "highlight_text": "#FFFFFF",
                "link": "#569CD6",
            },
        ),
        ThemeName.SOLARIZED_LIGHT: Theme(
            "Solarized Light",
            {
                "window": "#FDF6E3",
                "window_text": "#4B5B63",  # Darkened from #657B83 for better contrast
                "base": "#EEE8D5",
                "text": "#586E75",
                "button": "#FDF6E3",
                "button_text": "#4B5B63",  # Darkened to match window_text
                "highlight": "#268BD2",
                "highlight_text": "#FDF6E3",
                "link": "#268BD2",
            },
        ),
        ThemeName.SOLARIZED_DARK: Theme(
            "Solarized Dark",
            {
                "window": "#002B36",
                "window_text": "#6B8B8B",  # Darkened from #839496 for better contrast
                "base": "#073642",
                "text": "#93A1A1",
                "button": "#002B36",
                "button_text": "#6B8B8B",  # Darkened to match window_text
                "highlight": "#268BD2",
                "highlight_text": "#FDF6E3",
                "link": "#2AA198",
            },
        ),
        ThemeName.COMFORT_LIGHT: Theme(
            "Comfort Light",
            {
                "window": "#F6F5F1",
                "window_text": "#40434A",  # Balanced contrast - not too dark, not too light
                "base": "#FBFAF7",
                "text": "#30343C",
                "button": "#EDE9E0",
                "button_text": "#40434A",  # Match window_text
                "highlight": "#3A506B",
                "highlight_text": "#FFFFFF",
                "link": "#3A506B",
            },
        ),
        ThemeName.MUTED_DARK: Theme(
            "Muted Dark",
            {
                "window": "#23262B",
                "window_text": "#D0D6DD",
                "base": "#1C1F24",
                "text": "#D4DAE2",
                "button": "#2D3138",
                "button_text": "#D0D6DD",
                "highlight": "#5D7FA3",
                "highlight_text": "#FFFFFF",
                "link": "#7AA2CF",
            },
        ),
        ThemeName.NORD_LIGHT: Theme(
            "Nord Light",
            {
                "window": "#ECEFF4",
                "window_text": "#2E3440",
                "base": "#E5E9F0",
                "text": "#2E3440",
                "button": "#D8DEE9",
                "button_text": "#2E3440",
                "highlight": "#5E81AC",
                "highlight_text": "#ECEFF4",
                "link": "#4C72A1",
            },
        ),
        ThemeName.OCEANIC_DARK: Theme(
            "Oceanic Dark",
            {
                "window": "#1B2632",
                "window_text": "#DCE6F0",
                "base": "#14202B",
                "text": "#DCE6F0",
                "button": "#243343",
                "button_text": "#DCE6F0",
                "highlight": "#2E8BC0",
                "highlight_text": "#FFFFFF",
                "link": "#6FC3DF",
            },
        ),
        ThemeName.FOREST_MIST: Theme(
            "Forest Mist",
            {
                "window": "#EDF3EC",
                "window_text": "#2F3A33",
                "base": "#F7FAF6",
                "text": "#2F3A33",
                "button": "#DCE8DB",
                "button_text": "#2F3A33",
                "highlight": "#5F8C6A",
                "highlight_text": "#FFFFFF",
                "link": "#3F6E4C",
            },
        ),
        ThemeName.PAPER_SEPIA: Theme(
            "Paper Sepia",
            {
                "window": "#F7F1E4",
                "window_text": "#3F3427",
                "base": "#FFF9EC",
                "text": "#3F3427",
                "button": "#E8DDC8",
                "button_text": "#3F3427",
                "highlight": "#B07A3E",
                "highlight_text": "#FFFFFF",
                "link": "#8B5E2A",
            },
        ),
    }

    def __init__(self, app: QApplication):
        """
        Initialize theme manager.

        Args:
            app: QApplication instance
        """
        super().__init__()
        self.app = app
        self.settings = QSettings("AbCS", "AudioBookCollector")

        # Store original palette for reset
        self.original_palette = QPalette(app.palette())
        # Preserve any pre-existing application stylesheet so theme-specific
        # additions can be replaced cleanly instead of accumulating.
        self.base_stylesheet = app.styleSheet() or ""

        # Load saved theme or use default
        saved_theme = self.settings.value("theme", ThemeName.DEFAULT.value)
        self._current_theme_name = self._validate_theme_name(saved_theme)
        self._apply_theme()

    @property
    def current_theme_name(self) -> str:
        """Get current theme name."""
        return self._current_theme_name

    def set_theme(self, theme_name: str):
        """
        Set current theme.

        Args:
            theme_name: Name from ThemeName enum
        """
        theme_name = self._validate_theme_name(theme_name)

        if theme_name != self._current_theme_name:
            self._current_theme_name = theme_name
            self._apply_theme()
            self.theme_changed.emit(theme_name)

            # Save to settings
            self.settings.setValue("theme", theme_name)

    def get_theme_names(self) -> list:
        """
        Get list of available theme names.

        Returns:
            List of (display_name, theme_id) tuples
        """
        return [
            (theme.name, theme_enum.value) for theme_enum, theme in self.THEMES.items()
        ]

    def _validate_theme_name(self, theme_name: str) -> str:
        """Validate theme name, return default if invalid."""
        valid_names = [t.value for t in ThemeName]
        if theme_name in valid_names:
            return theme_name
        return ThemeName.DEFAULT.value

    def _apply_theme(self):
        """Apply current theme to application."""
        existing_stylesheet = self.app.styleSheet() or ""
        scale_block = self._extract_scale_block(existing_stylesheet)

        # Get theme
        theme_enum = ThemeName(self._current_theme_name)
        theme = self.THEMES[theme_enum]

        # Create new palette
        # Always start from the original palette so switching between themes
        # does not carry stale color roles from the previous theme.
        palette = QPalette(self.original_palette)

        if theme_enum == ThemeName.DEFAULT:
            # Always check system theme detection and apply workaround if needed
            windows_dark = detect_windows_dark_mode()
            if windows_dark is True:
                # Always use Windows registry for dark mode (Qt detection is broken)
                colors = get_fallback_dark_theme_colors()
                workaround_theme = Theme("Windows Dark (Registry)", colors)
                palette = workaround_theme.apply_to_palette(palette)
            elif windows_dark is False:
                # Use Windows registry for light mode too
                print("ACCESSIBILITY: Using Windows registry for light theme detection")
                colors = get_fallback_light_theme_colors()
                workaround_theme = Theme("Windows Light (Registry)", colors)
                palette = workaround_theme.apply_to_palette(palette)
            else:
                # Fallback to original system palette if registry fails or on non-Windows
                # Only print message on Windows (Linux doesn't have Windows registry)
                if sys.platform == "win32":
                    print(
                        "ACCESSIBILITY: Registry detection failed, using Qt system palette"
                    )
        else:
            # Apply custom theme colors
            palette = theme.apply_to_palette(palette)

        # Apply to application
        self.app.setPalette(palette)

        # Disable mouse hover highlighting for all tables
        table_hover_disable = """
            QTableWidget::item:hover, QTableView::item:hover {
                background: none !important;
            }
            QTableView:focus { border: none; outline: none; }
            QTableView::item:selected { background-color: palette(highlight); color: palette(highlighted-text); }
            QTableView::item:focus { outline: none; }
            QTableWidget { alternate-background-color: transparent; }
            QTableView { alternate-background-color: transparent; }
        """

        # Additional stylesheet tweaks for specific themes
        extra_style = ""

        groupbox_style = build_group_box_style()

        # Menu styling for better theme consistency
        menu_style = f"""
            QMenu {
                background-color: palette(base);
                border: 1px solid palette(dark);
                padding: 2px;
            }
            QMenu::item {
                padding: 4px 16px 4px 16px;
                border: none;
            }
            QMenu::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QMenu::separator {
                height: 1px;
                background-color: palette(mid);
                margin-left: 10px;
                margin-right: 10px;
            }
            QMenuBar {
                background-color: palette(window);
                color: palette(window-text);
                border: none;
            }
            QMenuBar::item {
                padding: 4px 8px 4px 8px;
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QHeaderView {
                background-color: palette(window);
                color: palette(window-text);
                border: none;
                border-bottom: 1px solid palette(dark);
            }
            QHeaderView::section {
                background-color: palette(window);
                color: palette(window-text);
                padding: 4px;
                border: none;
                border-right: 1px solid palette(dark);
                border-bottom: 1px solid palette(dark);
            }
            QLineEdit {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid palette(dark);
                border-radius: 3px;
                padding: 2px 4px;
            }
            QLineEdit:focus {
                border: 2px solid palette(highlight);
            }
            QLineEdit:disabled {
                background-color: palette(window);
                color: palette(window-text);
                border: 1px solid palette(mid);
            }
            QTextEdit {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid palette(dark);
                border-radius: 3px;
            }
            QTextEdit:focus {
                border: 2px solid palette(highlight);
            }
            QPlainTextEdit {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid palette(dark);
                border-radius: 3px;
            }
            QPlainTextEdit:focus {
                border: 2px solid palette(highlight);
            }
            {build_theme_scrollbar_style()}
            QMessageBox {
                background-color: palette(window);
                color: palette(window-text);
                border: 2px solid palette(dark);
                border-radius: 5px;
            }
            QMessageBox QLabel {
                color: palette(window-text);
            }
            QMessageBox QPushButton {
                background-color: palette(button);
                color: palette(button-text);
                border: 1px solid palette(dark);
                border-radius: 3px;
                padding: 5px 15px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: palette(mid);
            }
            QMessageBox QPushButton:default {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
        """

        spinbox_style = build_accessible_spinbox_style(18)
        dateedit_style = build_accessible_date_edit_style(18)
        combo_style = build_accessible_combo_box_style(18)

        # Apply menu styling for ALL themes
        if theme_enum in [ThemeName.HIGH_CONTRAST_DARK, ThemeName.HIGH_CONTRAST_LIGHT]:
            # Ensure very clear focus indicators for high contrast + menu styling
            extra_style = f"""
                QPushButton:focus {{
                    border: 3px solid palette(highlight);
                    outline: none;
                }}
                {groupbox_style}
                {menu_style}
                {combo_style}
                {spinbox_style}
                {dateedit_style}
                {build_theme_combo_color_overrides()}
                /* High contrast text box fixes */
                QLineEdit {{
                    background-color: palette(base) !important;
                    color: palette(text) !important;
                }}
                QTextEdit {{
                    background-color: palette(base) !important;
                    color: palette(text) !important;
                }}
                QPlainTextEdit {{
                    background-color: palette(base) !important;
                    color: palette(text) !important;
                }}
                /* High contrast spin box and date edit fixes */
                QSpinBox {{
                    background-color: palette(base) !important;
                    color: palette(text) !important;
                }}
                QDateEdit {{
                    background-color: palette(base) !important;
                    color: palette(text) !important;
                }}
            """
        else:
            # Apply menu styling for all themes (including default)
            extra_style = f"""
                {groupbox_style}
                {menu_style}
                {combo_style}
                {spinbox_style}
                {dateedit_style}
                {build_theme_combo_color_overrides()}
                /* Text box fixes for all themes */
                QLineEdit {{
                    background-color: palette(base) !important;
                    color: palette(text) !important;
                }}
                QTextEdit {{
                    background-color: palette(base) !important;
                    color: palette(text) !important;
                }}
                QPlainTextEdit {{
                    background-color: palette(base) !important;
                    color: palette(text) !important;
                }}
                /* Spin box and date edit fixes for all themes */
                QSpinBox {{
                    background-color: palette(base) !important;
                    color: palette(text) !important;
                }}
                QDateEdit {{
                    background-color: palette(base) !important;
                    color: palette(text) !important;
                }}
            """

        # Always apply table hover disabling
        full_stylesheet = self.base_stylesheet + "\n" + table_hover_disable
        if extra_style:
            full_stylesheet += "\n" + extra_style
        if scale_block:
            full_stylesheet += "\n" + scale_block
        self.app.setStyleSheet(full_stylesheet)

        self._repolish_open_widgets()

    def _extract_scale_block(self, stylesheet: str) -> str:
        """Extract scaling stylesheet block if present."""
        pattern = re.compile(
            rf"{re.escape(self.SCALE_STYLE_BEGIN)}.*?{re.escape(self.SCALE_STYLE_END)}",
            re.DOTALL,
        )
        match = pattern.search(stylesheet or "")
        return match.group(0) if match else ""

    def _repolish_open_widgets(self):
        """Force immediate visual refresh of open windows after theme changes."""
        linux = sys.platform.startswith("linux")
        for top_level in self.app.topLevelWidgets():
            if not isinstance(top_level, QWidget):
                continue

            widgets = [top_level]
            if not linux:
                widgets.extend(top_level.findChildren(QWidget))

            for widget in widgets:
                style = widget.style()
                style.unpolish(widget)
                style.polish(widget)
                # Handle widgets with problematic update methods
                try:
                    widget.update()
                except TypeError:
                    # Skip widgets that don't support parameterless update()
                    pass


# Global instance
_theme_manager_instance: Optional[ThemeManager] = None


def get_theme_manager(app: Optional[QApplication] = None) -> ThemeManager:
    """
    Get global theme manager instance.

    Args:
        app: QApplication (required on first call)

    Returns:
        ThemeManager instance
    """
    global _theme_manager_instance
    if _theme_manager_instance is None:
        if app is None:
            raise ValueError(
                "QApplication required for first call to get_theme_manager()"
            )
        _theme_manager_instance = ThemeManager(app)
    return _theme_manager_instance
