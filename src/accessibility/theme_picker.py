"""Visual theme picker with color swatch previews for Preferences."""

from __future__ import annotations

from typing import Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPalette, QPen
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from src.accessibility.theme_manager import ThemeManager, ThemeName
from src.accessibility.windows_theme_detector import (
    detect_windows_dark_mode,
    get_fallback_dark_theme_colors,
    get_fallback_light_theme_colors,
)


def preview_colors_for_theme(
    theme_manager: ThemeManager, theme_id: str
) -> Dict[str, str]:
    """Return color dict used to paint a theme preview."""
    if theme_id == ThemeName.DEFAULT.value:
        windows_dark = detect_windows_dark_mode()
        if windows_dark is True:
            return dict(get_fallback_dark_theme_colors())
        if windows_dark is False:
            return dict(get_fallback_light_theme_colors())
        return dict(get_fallback_light_theme_colors())

    theme_enum = ThemeName(theme_id)
    theme = theme_manager.THEMES.get(theme_enum)
    if theme is None or not theme.colors:
        return {
            "window": "#f0f0f0",
            "window_text": "#202020",
            "base": "#ffffff",
            "text": "#202020",
            "button": "#e0e0e0",
            "button_text": "#202020",
            "highlight": "#0078d4",
            "highlight_text": "#ffffff",
        }
    return dict(theme.colors)


def _color_hex(colors: Dict[str, str], key: str, fallback: str) -> str:
    value = colors.get(key) or fallback
    return value if value.startswith("#") else fallback


class ThemeMiniPreview(QWidget):
    """Paint a small mock panel using a theme's own colors."""

    def __init__(self, colors: Dict[str, str], parent=None):
        super().__init__(parent)
        self._colors = colors
        self.setFixedHeight(52)
        self.setMinimumWidth(120)
        self.setAccessibleName("Theme color preview")

    def paintEvent(self, _event):
        colors = self._colors
        window = QColor(_color_hex(colors, "window", "#f0f0f0"))
        base = QColor(_color_hex(colors, "base", "#ffffff"))
        button = QColor(_color_hex(colors, "button", "#e0e0e0"))
        highlight = QColor(_color_hex(colors, "highlight", "#0078d4"))
        text = QColor(
            _color_hex(colors, "text", _color_hex(colors, "window_text", "#202020"))
        )

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        w = self.width()
        h = self.height()
        margin = 4

        painter.fillRect(0, 0, w, h, window)

        btn_w = max(28, (w - margin * 2) // 3)
        btn_h = max(10, h // 5)
        painter.fillRect(margin, margin, btn_w, btn_h, button)

        field_top = margin + btn_h + 4
        field_h = max(12, h - field_top - margin - 6)
        field_w = w - margin * 2
        painter.fillRect(margin, field_top, field_w, field_h, base)

        accent_h = 4
        painter.fillRect(margin, h - margin - accent_h, field_w, accent_h, highlight)

        painter.setPen(QPen(text, 1))
        painter.drawRect(0, 0, w - 1, h - 1)


class ThemePreviewCard(QFrame):
    """Selectable card showing a miniature preview of one theme."""

    activated = Signal(str)

    def __init__(
        self,
        display_name: str,
        theme_id: str,
        colors: Dict[str, str],
        parent=None,
    ):
        super().__init__(parent)
        self.theme_id = theme_id
        self._colors = colors
        self._selected = False

        self.setObjectName("themePreviewCard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.setAccessibleName(display_name)
        self.setAccessibleDescription(f"Select {display_name} theme")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.preview = ThemeMiniPreview(colors, self)
        self.name_label = QLabel(display_name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        layout.addWidget(self.preview)
        layout.addWidget(self.name_label)

        self.setMinimumWidth(148)
        self.setMinimumHeight(96)
        self._apply_theme_colors()
        self._apply_selection_style()

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self._apply_selection_style()
        self.setAccessibleDescription(
            f"Select {self.accessibleName()} theme"
            + (" — selected" if selected else "")
        )

    def is_selected(self) -> bool:
        return self._selected

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.activated.emit(self.theme_id)
            event.accept()
            return
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.activated.emit(self.theme_id)
            event.accept()
            return
        super().keyPressEvent(event)

    def focusInEvent(self, event):
        self._apply_selection_style(focused=True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self._apply_selection_style(focused=False)
        super().focusOutEvent(event)

    def _apply_theme_colors(self) -> None:
        label_color = _color_hex(
            self._colors, "window_text", _color_hex(self._colors, "text", "#202020")
        )
        self.name_label.setStyleSheet(
            f"color: {label_color}; background: transparent; border: none;"
        )

    def _apply_selection_style(self, focused: bool | None = None) -> None:
        if focused is None:
            focused = self.hasFocus()
        window = _color_hex(self._colors, "window", "#f0f0f0")

        if self._selected:
            highlight = QApplication.palette().color(QPalette.Highlight).name()
            border = f"3px solid {highlight}"
        elif focused:
            highlight = QApplication.palette().color(QPalette.Highlight).name()
            border = f"2px solid {highlight}"
        else:
            mid = QApplication.palette().color(QPalette.Mid).name()
            border = f"1px solid {mid}"

        self.setStyleSheet(
            f"""
            QFrame#themePreviewCard {{
                background-color: {window};
                border: {border};
                border-radius: 6px;
            }}
            """
        )

    def refresh_selection_style(self) -> None:
        """Re-apply selection ring after the application theme changes."""
        self._apply_selection_style()


class ThemePreviewPicker(QWidget):
    """Grid of theme preview cards with exclusive selection."""

    theme_changed = Signal(str)

    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self._theme_manager = theme_manager
        self._loading = False
        self._cards: List[ThemePreviewCard] = []
        self._theme_ids: List[str] = []

        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setHorizontalSpacing(12)
        self._grid.setVerticalSpacing(12)

        self.setAccessibleName("Theme selection")
        self.setAccessibleDescription(
            "Choose a color theme. Each option shows a sample of its colors."
        )
        self.rebuild_cards()

    def rebuild_cards(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._cards.clear()
        self._theme_ids.clear()

        themes = self._theme_manager.get_theme_names()
        columns = 3
        for index, (display_name, theme_id) in enumerate(themes):
            colors = preview_colors_for_theme(self._theme_manager, theme_id)
            card = ThemePreviewCard(display_name, theme_id, colors, self)
            row = index // columns
            col = index % columns
            self._grid.addWidget(card, row, col)
            card.activated.connect(self._on_card_activated)
            self._cards.append(card)
            self._theme_ids.append(theme_id)

    def refresh_selection_styles(self) -> None:
        for card in self._cards:
            card.refresh_selection_style()

    def set_loading(self, loading: bool) -> None:
        self._loading = loading

    def current_theme_id(self) -> Optional[str]:
        for card in self._cards:
            if card.is_selected():
                return card.theme_id
        return None

    def set_selected_theme_id(self, theme_id: str) -> None:
        for card in self._cards:
            card.set_selected(card.theme_id == theme_id)

    def _on_card_activated(self, theme_id: str) -> None:
        if self._loading:
            return
        self.set_selected_theme_id(theme_id)
        if not self._loading:
            self.theme_changed.emit(theme_id)
