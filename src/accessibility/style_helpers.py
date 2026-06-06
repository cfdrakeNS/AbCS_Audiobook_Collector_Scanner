"""Shared stylesheet helpers for consistent accessible control styling."""

import sys

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


def build_group_box_style(selector: str = "QGroupBox") -> str:
    """Group box styling; skip ::title subcontrol on Linux (Fusion QPainter bug)."""
    base = f"""
        {selector} {{
            color: palette(window-text);
            border: 1px solid palette(mid);
            border-radius: 6px;
            margin-top: 12px;
            padding: 12px 8px 8px 8px;
            background-color: palette(window);
        }}
    """
    if _is_linux():
        return base
    return base + f"""
        {selector}::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px 0 6px;
            color: palette(window-text);
        }}
    """


def build_card_group_box_style(selector: str = "QGroupBox") -> str:
    return build_group_box_style(selector)


def _is_linux() -> bool:
    return sys.platform.startswith("linux")


def build_theme_scrollbar_style() -> str:
    """Scrollbar styling; omit subcontrol rules on Linux (Fusion QPainter bug)."""
    if _is_linux():
        return ""
    return """
            QScrollBar:vertical {
                background-color: palette(base);
                width: 15px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background-color: palette(mid);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: palette(highlight);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
            QScrollBar:horizontal {
                background-color: palette(base);
                height: 15px;
                border: 1px solid palette(dark);
                border-radius: 3px;
            }
            QScrollBar::handle:horizontal {
                background-color: palette(mid);
                border-radius: 3px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: palette(highlight);
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                background: none;
                border: none;
            }
    """


def build_preferences_tab_style() -> str:
    """Tab bar styling for Preferences; use native Fusion tabs on Linux."""
    if _is_linux():
        return ""
    return """
            QTabWidget::pane {
                border: 1px solid palette(mid);
                background-color: palette(window);
                top: -1px;
            }
            QTabBar::tab {
                background-color: palette(button);
                color: palette(windowText);
                border: 1px solid palette(mid);
                border-bottom: none;
                padding: 6px 14px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: palette(window);
                color: palette(windowText);
            }
            QTabBar::tab:hover {
                background-color: palette(light);
            }
    """


def build_theme_combo_color_overrides() -> str:
    """Extra combo colors for theme_manager; skip popup rules on Linux."""
    if _is_linux():
        return """
                QComboBox {
                    background-color: palette(base) !important;
                    color: palette(text) !important;
                }
        """
    base = """
                QComboBox {
                    background-color: palette(base) !important;
                    color: palette(text) !important;
                }
                QComboBox QAbstractItemView {
                    background-color: palette(base) !important;
                    color: palette(text) !important;
                    selection-background-color: palette(highlight) !important;
                    selection-color: palette(highlighted-text) !important;
                }
    """
    return base + """
                QComboBox QAbstractItemView::item:selected {
                    background-color: palette(highlight) !important;
                    color: palette(highlighted-text) !important;
                }
                QComboBox QAbstractItemView::item:hover {
                    background-color: palette(highlight) !important;
                    color: palette(highlighted-text) !important;
                }
    """


def _dropdown_arrow_css(selector: str) -> str:
    """Drop-down button styling; arrow handling is platform-specific."""
    # Any ::drop-down / ::down-arrow customization breaks Fusion's QPainter stack on Linux.
    if _is_linux():
        return ""

    drop_down = f"""
        {selector}::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid palette(dark);
            background-color: palette(button);
        }}
    """
    return drop_down + f"""
        {selector}::down-arrow {{
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid palette(text);
            margin-right: 4px;
        }}
    """


def build_accessible_combo_box_style(
    scaled_height: int | None = None,
    selector: str = "QComboBox",
) -> str:
    """Cross-platform combo box style with visible dropdown arrow."""
    height_rules = ""
    if scaled_height is not None:
        height_rules = f"""
            min-height: {scaled_height}px;
            max-height: {scaled_height}px;
        """

    radius_rule = "" if _is_linux() else "border-radius: 3px;"
    item_rules = ""
    focus_rule = ""
    if not _is_linux():
        focus_rule = f"""
        {selector}:focus {{
            border: 2px solid palette(highlight);
            background-color: palette(base);
        }}
        """
        item_rules = f"""
        {selector} QAbstractItemView::item {{
            padding: 3px 8px;
        }}
        {selector} QAbstractItemView::item:selected,
        {selector} QAbstractItemView::item:hover {{
            background-color: palette(highlight);
            color: palette(highlighted-text);
        }}
        """

    return f"""
        {selector} {{
            background-color: palette(base);
            color: palette(text);
            border: 1px solid palette(dark);
            {radius_rule}
            padding: 2px 4px;
            {height_rules}
        }}
        {focus_rule}
        {_combo_popup_style(selector)}
        {item_rules}
        {_dropdown_arrow_css(selector)}
    """


def _combo_popup_style(selector: str) -> str:
    """Popup list styling; omit on Linux where Fusion paints combos natively."""
    if _is_linux():
        return ""
    return f"""
        {selector} QAbstractItemView {{
            background-color: palette(base);
            color: palette(text);
            border: 1px solid palette(dark);
            selection-background-color: palette(highlight);
            selection-color: palette(highlighted-text);
        }}
    """


def build_accessible_date_edit_style(
    scaled_height: int | None = None,
    selector: str = "QDateEdit",
) -> str:
    """Date edit style with the same visible dropdown arrow as combos."""
    height_rules = ""
    if scaled_height is not None:
        height_rules = f"""
            min-height: {scaled_height}px;
            max-height: {scaled_height}px;
        """

    radius_rule = "" if _is_linux() else "border-radius: 3px;"
    return f"""
        {selector} {{
            background-color: palette(base);
            color: palette(text);
            border: 1px solid palette(dark);
            {radius_rule}
            padding: 2px 4px;
            {height_rules}
        }}
        {selector}:focus {{
            border: 2px solid palette(highlight);
        }}
        {selector} QCalendarWidget {{
            background-color: palette(window);
            color: palette(window-text);
        }}
        {selector} QCalendarWidget QAbstractItemView {{
            background-color: palette(base);
            color: palette(text);
            selection-background-color: palette(highlight);
            selection-color: palette(highlighted-text);
        }}
        {_dropdown_arrow_css(selector)}
    """


def build_accessible_spinbox_style(
    scaled_height: int | None = None,
    selector: str = "QSpinBox",
) -> str:
    """Spin box height/border styling without affecting combo arrows."""
    height_rules = ""
    if scaled_height is not None:
        height_rules = f"""
            min-height: {scaled_height}px;
            max-height: {scaled_height}px;
        """
    radius_rule = "" if _is_linux() else "border-radius: 3px;"
    return f"""
        {selector} {{
            border: 1px solid palette(dark);
            {radius_rule}
            padding: 1px;
            text-align: center;
            background-color: palette(base);
            color: palette(text);
            {height_rules}
        }}
        {selector}:focus {{
            border: 2px solid palette(highlight);
        }}
    """


def build_table_polish_style(selector: str = "QTableView") -> str:
    return f"""
        {selector} {{
            background-color: palette(base);
            color: palette(text);
            gridline-color: palette(mid);
            selection-background-color: palette(highlight);
            selection-color: palette(highlighted-text);
            alternate-background-color: palette(window);
        }}
        {selector}::item {{
            color: palette(text);
            background-color: palette(base);
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


DEFAULT_MESSAGE_BOX_BUTTON_ICONS = {
    QMessageBox.Ok: "ok",
    QMessageBox.Yes: "save",
    QMessageBox.No: "cancel",
    QMessageBox.Cancel: "cancel",
    QMessageBox.Save: "save",
    QMessageBox.Discard: "delete",
    QMessageBox.Close: "close",
    QMessageBox.Apply: "save",
}

# Per-dialog overrides (action-style icons matching main-window buttons).
MESSAGE_BOX_DELETE_CONFIRM_ICONS = {
    QMessageBox.Yes: "delete",
    QMessageBox.No: "cancel",
}
MESSAGE_BOX_UNSAVED_THREE_ICONS = {
    QMessageBox.Yes: "save",
    QMessageBox.No: "edit",
    QMessageBox.Cancel: "cancel",
}
MESSAGE_BOX_UNSAVED_TWO_ICONS = {
    QMessageBox.Yes: "save",
    QMessageBox.No: "edit",
}
MESSAGE_BOX_CANCEL_SCAN_ICONS = {
    QMessageBox.Yes: "cancel",
    QMessageBox.No: "close",
}
MESSAGE_BOX_RESTORE_CONFIRM_ICONS = {
    QMessageBox.Yes: "restore",
    QMessageBox.No: "cancel",
}


def _parent_scaler(parent):
    if parent is None:
        return None
    return getattr(parent, "scaler", None)


def apply_message_box_button_icons(
    msg: QMessageBox,
    scaler=None,
    button_icon_roles: dict | None = None,
) -> None:
    """Apply decorative action icons to QMessageBox standard buttons."""
    from src.accessibility.icon_helper import apply_decorative_action_icon

    roles = {**DEFAULT_MESSAGE_BOX_BUTTON_ICONS, **(button_icon_roles or {})}
    for std_button, icon_role in roles.items():
        button = msg.button(std_button)
        if button is not None:
            apply_decorative_action_icon(button, icon_role, scaler)


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
    scaler=None,
    button_icon_roles: dict | None = None,
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

    apply_message_box_button_icons(
        msg,
        scaler if scaler is not None else _parent_scaler(parent),
        button_icon_roles,
    )

    msg.setStyleSheet(build_accessible_message_box_style(scaled_height))
    return msg.exec()
