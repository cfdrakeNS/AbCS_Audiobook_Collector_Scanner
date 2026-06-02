"""Shared stylesheet helpers for consistent accessible control styling."""

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox


def build_accessible_button_style(
    scaled_height: int,
    selector: str = "QPushButton",
) -> str:
    """Return a compact, high-contrast button style string.

    The focus treatment keeps emphasis on the button border and disables
    any text-level focus outline for readability.
    """
    button_height = max(scaled_height - 4, 14)

    return f"""
        {selector} {{
            padding: 4px 12px;
            min-height: {button_height}px;
            max-height: {button_height}px;
            border: 1px solid palette(dark);
            border-radius: 3px;
            background-color: palette(button);
            outline: none;
        }}
        {selector}:focus {{
            background-color: palette(highlight);
            color: palette(highlighted-text);
            border: 2px solid palette(dark);
            outline: none;
        }}
        {selector}:hover {{
            border: 1px solid palette(dark);
        }}
        {selector}:pressed {{
            border: 2px solid palette(dark);
        }}
    """


def build_modern_button_style(
    scaled_height: int,
    selector: str = "QPushButton",
    primary_selector: str = "QPushButton#primaryActionButton",
    destructive_selector: str = "QPushButton#destructiveActionButton",
) -> str:
    button_height = max(scaled_height, 18)
    radius = max(int(button_height * 0.22), 4)
    return f"""
        {selector} {{
            padding: 5px 14px;
            min-height: {button_height}px;
            border: 1px solid palette(mid);
            border-radius: {radius}px;
            background-color: palette(button);
            color: palette(button-text);
            outline: none;
        }}
        {selector}:hover {{
            border: 1px solid palette(highlight);
        }}
        {selector}:focus {{
            background-color: palette(highlight);
            color: palette(highlighted-text);
            border: 2px solid palette(dark);
            outline: none;
        }}
        {selector}:pressed {{
            border: 2px solid palette(dark);
        }}
        {primary_selector} {{
            font-weight: bold;
            border: 2px solid palette(highlight);
        }}
        {destructive_selector} {{
            font-weight: bold;
        }}
    """


def build_card_panel_style(panel_object_name: str) -> str:
    """Card-style border for QWidget panels identified by objectName."""
    return f"""
        QWidget#{panel_object_name} {{
            color: palette(window-text);
            border: 1px solid palette(mid);
            border-radius: 6px;
            background-color: palette(window);
        }}
    """


def build_card_group_box_style(selector: str = "QGroupBox") -> str:
    return f"""
        {selector} {{
            color: palette(window-text);
            border: 1px solid palette(mid);
            border-radius: 6px;
            margin-top: 12px;
            padding: 12px 8px 8px 8px;
            background-color: palette(window);
        }}
        {selector}::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px 0 6px;
            color: palette(window-text);
        }}
    """


def build_table_polish_style(selector: str = "QTableView") -> str:
    return f"""
        {selector} {{
            gridline-color: palette(mid);
            selection-background-color: palette(highlight);
            selection-color: palette(highlighted-text);
            alternate-background-color: palette(window);
        }}
        {selector}:focus {{
            border: 2px solid palette(highlight);
            outline: none;
        }}
        {selector}::item:selected {{
            background-color: palette(highlight);
            color: palette(highlighted-text);
        }}
        QHeaderView::section {{
            background-color: palette(button);
            color: palette(button-text);
            border: 1px solid palette(mid);
            padding: 4px;
            font-weight: bold;
        }}
    """


def build_toolbar_button_style(
    scaled_height: int,
    selector: str = "QToolButton",
) -> str:
    button_height = max(scaled_height + 6, 24)
    return f"""
        {selector} {{
            padding: 4px 10px;
            min-height: {button_height}px;
            border: 1px solid transparent;
            border-radius: 5px;
            background-color: transparent;
            color: palette(window-text);
        }}
        {selector}:hover {{
            border: 1px solid palette(mid);
            background-color: palette(button);
        }}
        {selector}:focus {{
            border: 2px solid palette(highlight);
            background-color: palette(button);
            outline: none;
        }}
    """


def apply_status_bar_tooltip(status_bar, tooltip: str) -> None:
    """Sighted-user tooltip only; never set accessible description on status bars."""
    status_bar.setToolTip(tooltip)


def apply_tooltip_accessibility(widget, tooltip: str, description: str | None = None):
    """Apply tooltip; set accessible description on widgets, status tip on QAction."""
    widget.setToolTip(tooltip)
    if isinstance(widget, QAction):
        # QAction has no setAccessibleDescription in PySide6; status tip is the fallback.
        widget.setStatusTip(description or tooltip)
        return
    if description and hasattr(widget, "setAccessibleDescription"):
        widget.setAccessibleDescription(description)


def apply_visual_tooltip_map(tooltip_map) -> None:
    """Apply short tooltips to widgets or actions.

    Map values may be a tooltip string (uses existing accessible description when set)
    or a (tooltip, description) tuple.
    """
    for widget, spec in tooltip_map.items():
        if isinstance(spec, tuple):
            tooltip, description = spec[0], spec[1] if len(spec) > 1 else None
        else:
            tooltip = spec
            description = None
            if not isinstance(widget, QAction) and hasattr(
                widget, "accessibleDescription"
            ):
                existing = widget.accessibleDescription()
                if existing:
                    description = existing
        apply_tooltip_accessibility(widget, tooltip, description)

def build_accessible_message_box_style(scaled_height: int) -> str:
    """Return a shared QMessageBox style with theme-aware colors."""
    return "\n".join(
        [
            "QMessageBox {",
            "    background-color: palette(window);",
            "    color: palette(window-text);",
            "    border: 2px solid palette(dark);",
            "    border-radius: 5px;",
            "}",
            "QMessageBox QLabel {",
            "    color: palette(window-text);",
            "    border: none;",
            "}",
            "QMessageBox QPushButton {",
            "    background-color: palette(button);",
            "    color: palette(button-text);",
            "    border: 1px solid palette(dark);",
            "    border-radius: 3px;",
            "    padding: 5px 15px;",
            "    min-width: 80px;",
            "    outline: none;",
            "}",
            "QMessageBox QPushButton:hover {",
            "    background-color: palette(mid);",
            "}",
            "QMessageBox QPushButton:default {",
            "    background-color: palette(highlight);",
            "    color: palette(highlighted-text);",
            "}",
        ]
    )


def set_message_box_button_accessibility(
    msg: QMessageBox,
    button_roles: dict,
):
    for role, (name, description) in button_roles.items():
        button = msg.button(role)
        if button is not None:
            button.setAccessibleName(name)
            button.setAccessibleDescription(description)


def exec_styled_message_box(
    parent,
    scaled_height: int,
    *,
    icon: QMessageBox.Icon,
    title: str,
    text: str,
    buttons=QMessageBox.Ok,
    default_button=None,
    button_texts=None,
    button_accessibility=None,
    window_icon=None,
) -> int:
    """Show a styled QMessageBox and return the exec result."""
    msg = QMessageBox(parent)
    if icon is not None:
        msg.setIcon(icon)
    else:
        msg.setIcon(QMessageBox.NoIcon)
    # Set window icon (top left) for accessibility popups
    try:
        if window_icon is not None:
            msg.setWindowIcon(window_icon)
        else:
            from src.accessibility.icon_helper import get_app_icon

            msg.setWindowIcon(get_app_icon())
    except Exception:
        pass
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setStandardButtons(buttons)

    if default_button is not None:
        msg.setDefaultButton(default_button)

    if button_texts:
        for button_role, button_text in button_texts.items():
            button = msg.button(button_role)
            if button is not None:
                button.setText(button_text)

    if button_accessibility:
        set_message_box_button_accessibility(msg, button_accessibility)

    msg.setStyleSheet(build_accessible_message_box_style(scaled_height))
    return msg.exec()
