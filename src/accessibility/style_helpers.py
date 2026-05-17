"""Shared stylesheet helpers for consistent accessible control styling."""

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
