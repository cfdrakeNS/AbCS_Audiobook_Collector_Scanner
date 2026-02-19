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
    """Return a shared QMessageBox style with clean labels and button borders."""
    return "\n".join(
        [
            "QLabel { border: none; }",
            build_accessible_button_style(
                scaled_height,
                selector="QPushButton",
            ),
        ]
    )


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
) -> int:
    """Show a styled QMessageBox and return the exec result."""
    msg = QMessageBox(parent)
    msg.setIcon(icon)
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

    msg.setStyleSheet(build_accessible_message_box_style(scaled_height))
    return msg.exec()
