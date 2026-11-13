"""Shared pytest fixtures for AbCS tests."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from src.database.connection import DatabaseManager

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_EXIT_STATUS = pytest.StashKey[int]()


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    session.config.stash[_EXIT_STATUS] = int(exitstatus)


@pytest.hookimpl(trylast=True)
def pytest_unconfigure(config):
    """Exit with pytest's status once results and coverage are written.

    On Windows CI, Python aborts (0xC0000409) while tearing down leftover Qt
    objects after every test has passed. Deleting the widgets first crashes
    too, so the process skips interpreter shutdown instead.
    """
    if _EXIT_STATUS not in config.stash:
        return
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(config.stash[_EXIT_STATUS])


@pytest.fixture(scope="session")
def qapp():
    """Headless Qt application shared across tests."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture(scope="session")
def ui_scaler(qapp):
    """Session-scoped UIScaler — avoid rebuilding on every window test."""
    from src.accessibility.scaling import UIScaler

    return UIScaler(qapp)


@pytest.fixture(scope="session")
def theme_manager(qapp):
    """Session-scoped ThemeManager — apply stylesheet once per session.

    Creating a fresh ThemeManager per test was the dominant suite cost:
    each construction calls setStyleSheet + _repolish_open_widgets across
    every leaked top-level widget, producing O(n^2) restyles.
    """
    from src.accessibility.theme_manager import ThemeManager

    return ThemeManager(qapp)


@pytest.fixture(autouse=True)
def _destroy_leaked_widgets(qapp):
    """Drain the event loop after each test.

    Aggressive deleteLater on top-level widgets caused intermittent Windows
    access violations when qtbot had already freed the same C++ objects.
    Session-scoped ThemeManager already removes the O(n^2) restyle cost, so
    we only process pending events here.
    """
    yield
    qapp.processEvents()


@pytest.fixture(autouse=True)
def _block_network(request):
    """Block live HTTP from web_book_api unless a test opts out.

    Tests that supply their own urlopen mock or mark themselves with
    ``@pytest.mark.network`` are left alone.
    """
    if "network" in {m.name for m in request.node.iter_markers()}:
        yield
        return

    def _blocked(*_args, **_kwargs):
        raise RuntimeError(
            "Network blocked in tests. Mock urllib.request.urlopen "
            "or mark the test with @pytest.mark.network."
        )

    with patch("src.web.web_http.urllib.request.urlopen", side_effect=_blocked):
        yield


@pytest.fixture(autouse=True)
def _batch_summary_closes_without_prompt(request, monkeypatch):
    """Closing the batch summary asks before discarding; tests close it in teardown.

    Tests marked ``real_batch_confirm`` keep the real prompt.
    """
    if "real_batch_confirm" in {m.name for m in request.node.iter_markers()}:
        yield
        return
    try:
        from src.ui.batch_web_fetch_summary import BatchWebFetchSummaryDialog
    except ImportError:
        yield
        return
    monkeypatch.setattr(BatchWebFetchSummaryDialog, "_confirm_discard", lambda self: True)
    yield


@pytest.fixture(autouse=True)
def _silent_audio_output(monkeypatch):
    """Keep every test silent.

    UI tests copy data/abcs.db, which can hold real books with real paths, so
    opening Listen on one would play the actual audiobook over the screen
    reader. Tests that supply their own fake player still override this.
    """
    try:
        from PySide6 import QtMultimedia
    except ImportError:
        yield
        return

    class SilentAudioOutput(QtMultimedia.QAudioOutput):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            super().setMuted(True)
            super().setVolume(0.0)

        def setMuted(self, _muted):
            super().setMuted(True)

        def setVolume(self, _volume):
            super().setVolume(0.0)

    monkeypatch.setattr(QtMultimedia, "QAudioOutput", SilentAudioOutput)

    from src.ui.preview_window import PreviewWindow

    def _no_modal_wait(self):
        self.close()
        return 0

    monkeypatch.setattr(PreviewWindow, "exec", _no_modal_wait)
    yield


@pytest.fixture(autouse=True)
def _no_setup_splash_wait(monkeypatch):
    """Close the empty-library welcome without waiting.

    MainWindow opens it modally when the database has no books. A clean clone
    has no data/abcs.db, so temp_db starts empty and CI would wait forever.
    """
    from PySide6.QtWidgets import QDialog

    from src.ui.setup_dialogue import SetupDialog

    def _no_modal_wait(self):
        self.close()
        return QDialog.DialogCode.Rejected

    monkeypatch.setattr(SetupDialog, "exec", _no_modal_wait)
    yield


@pytest.fixture
def no_cover_placeholder(tmp_path, monkeypatch):
    """Serve a generated missing-cover image; graphics/ is not in the repo."""
    from PySide6.QtGui import QColor, QImage

    from src.accessibility import graphics_paths

    placeholder = tmp_path / "no_book_cover_512x512.png"
    image = QImage(16, 16, QImage.Format.Format_RGB32)
    image.fill(QColor("gray"))
    image.save(str(placeholder))
    original = graphics_paths.resolve_graphics_path

    def _resolve(filename: str) -> str:
        if filename == placeholder.name:
            return str(placeholder)
        return original(filename)

    monkeypatch.setattr(graphics_paths, "resolve_graphics_path", _resolve)
    return placeholder


def _find_source_database() -> Path | None:
    """Return a local dev database copy when present."""
    data_dir = PROJECT_ROOT / "data"
    candidates = [
        data_dir / "abcs.db",
        data_dir / "wh abcs.db",
    ]
    candidates.extend(
        sorted(
            data_dir.glob("abcs.db.backup.*"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
    )
    return next((path for path in candidates if path.exists()), None)


@pytest.fixture
def temp_db(tmp_path):
    """
    Writable database for UI tests.

    Uses a copy of data/abcs.db when available (richer local data).
    Otherwise creates a fresh database via initialize_database(), which
    uses test/fixtures/abcdDB_def.sql on clean clones.
    """
    target_db = tmp_path / "abcs_test.db"
    source_db = _find_source_database()
    if source_db is not None:
        shutil.copy2(source_db, target_db)
        db = DatabaseManager(str(target_db))
        db.initialize_database()
    else:
        db = DatabaseManager(str(target_db))
        db.initialize_database()
    try:
        yield db
    finally:
        db.close()


def _patch_qsettings_to_ini(monkeypatch) -> None:
    """Send QSettings(org, app) to the INI path instead of the registry.

    That constructor always uses NativeFormat, so setDefaultFormat alone
    leaves the user's real AbCS preferences exposed to tests.
    """
    import sys

    from PySide6 import QtCore

    original = QtCore.QSettings
    if getattr(original, "_abcs_ini_only", False):
        return

    class IniQSettings(original):
        _abcs_ini_only = True

        def __init__(self, *args, **kwargs):
            if (
                not kwargs
                and len(args) in (2, 3)
                and isinstance(args[0], str)
                and isinstance(args[1], str)
            ):
                super().__init__(
                    original.Format.IniFormat,
                    original.Scope.UserScope,
                    *args,
                )
            else:
                super().__init__(*args, **kwargs)

    for module in list(sys.modules.values()):
        namespace = getattr(module, "__dict__", None)
        if namespace is not None and namespace.get("QSettings") is original:
            monkeypatch.setattr(module, "QSettings", IniQSettings)


def _set_ini_settings_dir(path) -> None:
    from PySide6.QtCore import QSettings

    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        str(path),
    )


@pytest.fixture(scope="session", autouse=True)
def _no_registry_settings(tmp_path_factory):
    """Keep every test, and the session scaler and theme, off the real preferences."""
    session_dir = tmp_path_factory.mktemp("qsettings")
    with pytest.MonkeyPatch.context() as monkeypatch:
        _patch_qsettings_to_ini(monkeypatch)
        _set_ini_settings_dir(session_dir)
        yield session_dir


@pytest.fixture
def isolated_qsettings(tmp_path, monkeypatch, _no_registry_settings):
    """Give one test its own empty settings files."""
    from PySide6.QtCore import QSettings

    _patch_qsettings_to_ini(monkeypatch)
    monkeypatch.setenv("ABCS_TEST_SETTINGS_DIR", str(tmp_path))
    previous_format = QSettings.defaultFormat()
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        str(tmp_path),
    )
    settings = QSettings(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        "AbCS",
        "AbCS",
    )
    app_settings = QSettings(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        "AbCS",
        "AudioBookCollector",
    )
    settings.clear()
    app_settings.clear()
    try:
        yield settings
    finally:
        settings.clear()
        app_settings.clear()
        QSettings.setDefaultFormat(previous_format)
        _set_ini_settings_dir(_no_registry_settings)


@pytest.fixture
def main_window(qapp, temp_db, ui_scaler, theme_manager, qtbot, isolated_qsettings):
    """MainWindow with an isolated temp database and application settings."""
    from src.ui.main_window import MainWindow

    window = MainWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    yield window
    window.close()


@pytest.fixture
def reading_history_window(qapp, temp_db, ui_scaler, theme_manager, qtbot):
    """Function-scoped ReadingHistoryWindow on an isolated temp database."""
    from src.ui.reading_history_window import ReadingHistoryWindow

    window = ReadingHistoryWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)
    yield window
    window.close()


@pytest.fixture
def web_api(tmp_path, monkeypatch):
    """Isolated WebBookAPI with empty cache and cleared rate-limit cooldowns."""
    from src.web import web_book_api as wba
    from src.web import web_http as whttp
    from src.web.web_book_api import WebBookAPI, _clear_source_cooldown, _reset_shared_web_api_for_tests

    cache_file = str(tmp_path / "web_cache.json")
    monkeypatch.setattr(wba, "WEB_CACHE_FILE", cache_file)
    monkeypatch.setattr(whttp, "WEB_CACHE_FILE", cache_file)
    _clear_source_cooldown()
    _reset_shared_web_api_for_tests()
    client = WebBookAPI()
    yield client
    _clear_source_cooldown()
    _reset_shared_web_api_for_tests()
