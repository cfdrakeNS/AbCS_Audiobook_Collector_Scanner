"""Tests for the GitHub version check."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from src.core.update_check import (
    UpdateCheckError,
    check_for_update,
    fetch_latest_release_tag,
    is_newer_version,
    result_message,
)


class _Response:
    def __init__(self, payload: dict):
        self._raw = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def test_is_newer_version_numeric_and_v_prefix():
    assert is_newer_version("v2.16", "2.15")
    assert is_newer_version("2.15.1", "2.15")
    assert not is_newer_version("2.15", "2.15")
    assert not is_newer_version("v2.09", "2.15")


def test_check_for_update_newer_same_and_older():
    with patch(
        "src.core.update_check.fetch_latest_release_tag", return_value="v2.16"
    ):
        newer = check_for_update("2.15")
    assert newer.update_available
    assert "Version 2.16 is available" in result_message(newer)
    assert "does not install" in result_message(newer)

    with patch(
        "src.core.update_check.fetch_latest_release_tag", return_value="v2.15"
    ):
        same = check_for_update("2.15")
    assert not same.update_available
    assert result_message(same) == "Version 2.15 is up to date."

    with patch(
        "src.core.update_check.fetch_latest_release_tag", return_value="v2.09"
    ):
        older_release = check_for_update("2.15")
    assert not older_release.update_available
    assert "No update is needed." in result_message(older_release)


def test_fetch_latest_release_tag_reads_tag_name():
    response = _Response({"tag_name": "v2.16"})
    with patch("src.core.update_check.urllib.request.urlopen", return_value=response):
        assert fetch_latest_release_tag() == "v2.16"


def test_check_for_update_offline():
    import urllib.error

    with patch(
        "src.core.update_check.urllib.request.urlopen",
        side_effect=urllib.error.URLError("offline"),
    ):
        result = check_for_update("2.15")
    assert result.error
    assert not result.update_available
    assert "No network connection" in result_message(result)


def test_fetch_rejects_unusable_payload():
    response = _Response({"name": "not a tag"})
    with patch("src.core.update_check.urllib.request.urlopen", return_value=response):
        with pytest.raises(UpdateCheckError):
            fetch_latest_release_tag()


def test_startup_update_check_respects_preference(main_window, isolated_qsettings):
    from PySide6.QtCore import QSettings

    from src.core.update_check import AUTO_CHECK_UPDATES_SETTING

    started = []
    main_window._start_update_check = lambda **kwargs: started.append(kwargs)

    main_window.maybe_start_startup_update_check()
    assert started == []

    settings = QSettings("AbCS", "AudioBookCollector")
    settings.setValue(AUTO_CHECK_UPDATES_SETTING, True)
    settings.sync()
    main_window.maybe_start_startup_update_check()
    assert started == [
        {"show_dialog_always": False, "announce_progress": False}
    ]


def test_startup_update_check_opens_dialog_only_when_update_exists(
    main_window, monkeypatch
):
    from src.core.update_check import UpdateCheckResult

    shown = []

    class _FakeDialog:
        OPEN_PAGE = 1

        def __init__(self, *_args, **_kwargs):
            self.browser_opened = False

        def exec(self):
            shown.append(True)
            return 0

    monkeypatch.setattr(
        "src.ui.update_check_dialog.UpdateCheckDialog", _FakeDialog
    )
    main_window._update_check_show_always = False
    main_window._on_update_check_finished(
        UpdateCheckResult(current="2.17", latest="2.17", update_available=False)
    )
    assert shown == []

    main_window._on_update_check_finished(
        UpdateCheckResult(current="2.17", latest="2.18", update_available=True)
    )
    assert shown == [True]


def test_update_dialog_focuses_open_only_when_update_exists(qapp, ui_scaler):
    from src.core.update_check import UpdateCheckResult
    from src.ui.update_check_dialog import UpdateCheckDialog

    available = UpdateCheckResult(
        current="2.15", latest="v2.16", update_available=True
    )
    dialog = UpdateCheckDialog(available, ui_scaler)
    try:
        assert dialog.open_button.isDefault()
        assert not dialog.close_button.isDefault()
        assert dialog.focusWidget() is dialog.open_button
    finally:
        dialog.deleteLater()

    current = UpdateCheckResult(current="2.15", latest="v2.15", update_available=False)
    same = UpdateCheckDialog(current, ui_scaler)
    try:
        assert same.close_button.isDefault()
        assert not same.open_button.isDefault()
        assert same.open_button.autoDefault()
        assert same.focusWidget() is same.close_button
        same.open_button.setFocus()
        with patch(
            "src.app_urls.open_public_url", return_value=True
        ) as opener:
            same.open_button.click()
        opener.assert_called_once()
        assert same.browser_opened is True
    finally:
        same.deleteLater()
