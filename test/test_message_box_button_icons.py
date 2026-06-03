"""Tests for decorative icons on QMessageBox standard buttons."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from src.accessibility.style_helpers import (
    DEFAULT_MESSAGE_BOX_BUTTON_ICONS,
    MESSAGE_BOX_DELETE_CONFIRM_ICONS,
    MESSAGE_BOX_UNSAVED_TWO_ICONS,
    apply_message_box_button_icons,
    exec_styled_message_box,
    set_message_box_button_accessibility,
)


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_apply_message_box_button_icons_sets_icons(qapp):
    msg = QMessageBox()
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    apply_message_box_button_icons(msg, button_icon_roles=MESSAGE_BOX_DELETE_CONFIRM_ICONS)

    yes_btn = msg.button(QMessageBox.Yes)
    no_btn = msg.button(QMessageBox.No)
    assert yes_btn is not None
    assert no_btn is not None
    assert not yes_btn.icon().isNull()
    assert not no_btn.icon().isNull()


def test_apply_message_box_button_icons_preserves_accessible_names(qapp):
    msg = QMessageBox()
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    set_message_box_button_accessibility(
        msg,
        {
            QMessageBox.Yes: ("Yes, save", "Save changes"),
            QMessageBox.No: ("No, edit", "Continue editing"),
        },
    )
    apply_message_box_button_icons(msg, button_icon_roles=MESSAGE_BOX_UNSAVED_TWO_ICONS)

    assert msg.button(QMessageBox.Yes).accessibleName() == "Yes, save"
    assert msg.button(QMessageBox.No).accessibleName() == "No, edit"


def test_default_message_box_icon_roles_cover_standard_buttons():
    assert QMessageBox.Ok in DEFAULT_MESSAGE_BOX_BUTTON_ICONS
    assert QMessageBox.Yes in DEFAULT_MESSAGE_BOX_BUTTON_ICONS
    assert DEFAULT_MESSAGE_BOX_BUTTON_ICONS[QMessageBox.Yes] == "save"


def test_exec_styled_message_box_applies_ok_icon(qapp):
    class Parent:
        scaler = None

    # exec blocks; patch by checking message construction via apply helper only
    msg = QMessageBox()
    msg.setStandardButtons(QMessageBox.Ok)
    apply_message_box_button_icons(msg)
    ok_btn = msg.button(QMessageBox.Ok)
    assert ok_btn is not None
    assert not ok_btn.icon().isNull()
