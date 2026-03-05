"""
Theme manager for AbCS.
Manages color schemes and high contrast themes for accessibility.
"""

from PySide6.QtCore import QObject, Signal, QSettings
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication
from typing import Dict, Optional
from enum import Enum


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
        if 'window' in self.colors:
            palette.setColor(QPalette.Window, QColor(self.colors['window']))

        # Window text
        if 'window_text' in self.colors:
            palette.setColor(QPalette.WindowText, QColor(
                self.colors['window_text']))

        # Base (input background)
        if 'base' in self.colors:
            palette.setColor(QPalette.Base, QColor(self.colors['base']))

        # Text (input text)
        if 'text' in self.colors:
            palette.setColor(QPalette.Text, QColor(self.colors['text']))

        # Button background
        if 'button' in self.colors:
            palette.setColor(QPalette.Button, QColor(self.colors['button']))

        # Button text
        if 'button_text' in self.colors:
            palette.setColor(QPalette.ButtonText, QColor(
                self.colors['button_text']))

        # Highlight (selection)
        if 'highlight' in self.colors:
            palette.setColor(QPalette.Highlight,
                             QColor(self.colors['highlight']))

        # Highlighted text
        if 'highlight_text' in self.colors:
            palette.setColor(QPalette.HighlightedText,
                             QColor(self.colors['highlight_text']))

        # Link
        if 'link' in self.colors:
            palette.setColor(QPalette.Link, QColor(self.colors['link']))

        return palette


class ThemeManager(QObject):
    """
    Manages application themes and color schemes.

    Signals:
        theme_changed: Emitted when theme changes (theme_name: str)
    """

    theme_changed = Signal(str)

    # Built-in themes
    THEMES = {
        ThemeName.DEFAULT: Theme("Default (System)", {}),  # Use system colors

        ThemeName.HIGH_CONTRAST_DARK: Theme("High Contrast Dark", {
            'window': '#000000',
            'window_text': '#FFFFFF',
            'base': '#000000',
            'text': '#FFFFFF',
            'button': '#000000',
            'button_text': '#FFFFFF',
            'highlight': '#FFFF00',  # Yellow selection
            'highlight_text': '#000000',
            'link': '#00FFFF',
        }),

        ThemeName.HIGH_CONTRAST_LIGHT: Theme("High Contrast Light", {
            'window': '#FFFFFF',
            'window_text': '#000000',
            'base': '#FFFFFF',
            'text': '#000000',
            'button': '#FFFFFF',
            'button_text': '#000000',
            'highlight': '#000080',  # Navy selection
            'highlight_text': '#FFFFFF',
            'link': '#0000FF',
        }),

        ThemeName.DARK: Theme("Dark", {
            'window': '#2B2B2B',
            'window_text': '#E0E0E0',
            'base': '#1E1E1E',
            'text': '#E0E0E0',
            'button': '#3C3C3C',
            'button_text': '#E0E0E0',
            'highlight': '#0078D4',
            'highlight_text': '#FFFFFF',
            'link': '#569CD6',
        }),

        ThemeName.SOLARIZED_LIGHT: Theme("Solarized Light", {
            'window': '#FDF6E3',
            'window_text': '#657B83',
            'base': '#EEE8D5',
            'text': '#586E75',
            'button': '#FDF6E3',
            'button_text': '#657B83',
            'highlight': '#268BD2',
            'highlight_text': '#FDF6E3',
            'link': '#268BD2',
        }),

        ThemeName.SOLARIZED_DARK: Theme("Solarized Dark", {
            'window': '#002B36',
            'window_text': '#839496',
            'base': '#073642',
            'text': '#93A1A1',
            'button': '#002B36',
            'button_text': '#839496',
            'highlight': '#268BD2',
            'highlight_text': '#FDF6E3',
            'link': '#2AA198',
        }),

        ThemeName.COMFORT_LIGHT: Theme("Comfort Light", {
            'window': '#F6F5F1',
            'window_text': '#2E3138',
            'base': '#FBFAF7',
            'text': '#30343C',
            'button': '#EDE9E0',
            'button_text': '#2E3138',
            'highlight': '#7A8FA8',
            'highlight_text': '#FFFFFF',
            'link': '#3E5F8A',
        }),

        ThemeName.MUTED_DARK: Theme("Muted Dark", {
            'window': '#23262B',
            'window_text': '#D0D6DD',
            'base': '#1C1F24',
            'text': '#D4DAE2',
            'button': '#2D3138',
            'button_text': '#D0D6DD',
            'highlight': '#5D7FA3',
            'highlight_text': '#FFFFFF',
            'link': '#7AA2CF',
        }),

        ThemeName.NORD_LIGHT: Theme("Nord Light", {
            'window': '#ECEFF4',
            'window_text': '#2E3440',
            'base': '#E5E9F0',
            'text': '#2E3440',
            'button': '#D8DEE9',
            'button_text': '#2E3440',
            'highlight': '#5E81AC',
            'highlight_text': '#ECEFF4',
            'link': '#4C72A1',
        }),

        ThemeName.OCEANIC_DARK: Theme("Oceanic Dark", {
            'window': '#1B2632',
            'window_text': '#DCE6F0',
            'base': '#14202B',
            'text': '#DCE6F0',
            'button': '#243343',
            'button_text': '#DCE6F0',
            'highlight': '#2E8BC0',
            'highlight_text': '#FFFFFF',
            'link': '#6FC3DF',
        }),

        ThemeName.FOREST_MIST: Theme("Forest Mist", {
            'window': '#EDF3EC',
            'window_text': '#2F3A33',
            'base': '#F7FAF6',
            'text': '#2F3A33',
            'button': '#DCE8DB',
            'button_text': '#2F3A33',
            'highlight': '#5F8C6A',
            'highlight_text': '#FFFFFF',
            'link': '#3F6E4C',
        }),

        ThemeName.PAPER_SEPIA: Theme("Paper Sepia", {
            'window': '#F7F1E4',
            'window_text': '#3F3427',
            'base': '#FFF9EC',
            'text': '#3F3427',
            'button': '#E8DDC8',
            'button_text': '#3F3427',
            'highlight': '#B07A3E',
            'highlight_text': '#FFFFFF',
            'link': '#8B5E2A',
        }),
    }

    def __init__(self, app: QApplication):
        """
        Initialize theme manager.

        Args:
            app: QApplication instance
        """
        super().__init__()
        self.app = app
        self.settings = QSettings('AbCS', 'AudioBookCollector')

        # Store original palette for reset
        self.original_palette = QPalette(app.palette())

        # Load saved theme or use default
        saved_theme = self.settings.value('theme', ThemeName.DEFAULT.value)
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
            self.settings.setValue('theme', theme_name)

    def get_theme_names(self) -> list:
        """
        Get list of available theme names.

        Returns:
            List of (display_name, theme_id) tuples
        """
        return [(theme.name, theme_enum.value)
                for theme_enum, theme in self.THEMES.items()]

    def get_current_theme_display_name(self) -> str:
        """Get display name of current theme."""
        for theme_enum, theme in self.THEMES.items():
            if theme_enum.value == self._current_theme_name:
                return theme.name
        return "Unknown"

    def _validate_theme_name(self, theme_name: str) -> str:
        """Validate theme name, return default if invalid."""
        valid_names = [t.value for t in ThemeName]
        if theme_name in valid_names:
            return theme_name
        return ThemeName.DEFAULT.value

    def _apply_theme(self):
        """Apply current theme to application."""
        # Get theme
        theme_enum = ThemeName(self._current_theme_name)
        theme = self.THEMES[theme_enum]

        # Create new palette
        if theme_enum == ThemeName.DEFAULT:
            # Use system default
            palette = self.original_palette
        else:
            # Start with current palette and modify
            palette = QPalette(self.app.palette())
            palette = theme.apply_to_palette(palette)

        # Apply to application
        self.app.setPalette(palette)

        # Additional stylesheet tweaks for specific themes
        extra_style = ""

        if theme_enum in [ThemeName.HIGH_CONTRAST_DARK, ThemeName.HIGH_CONTRAST_LIGHT]:
            # Ensure very clear focus indicators for high contrast
            extra_style = """
                *:focus {
                    outline: 3px solid palette(highlight);
                    outline-offset: 2px;
                }
                
                QPushButton:focus {
                    border: 3px solid palette(highlight);
                    outline: none;
                }
            """

        if extra_style:
            current_style = self.app.styleSheet()
            self.app.setStyleSheet(current_style + "\n" + extra_style)


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
                "QApplication required for first call to get_theme_manager()")
        _theme_manager_instance = ThemeManager(app)
    return _theme_manager_instance
