"""Shared pytest fixtures for AbCS tests."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from src.database.connection import DatabaseManager

PROJECT_ROOT = Path(__file__).resolve().parent.parent


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

    with patch("src.web.web_book_api.urllib.request.urlopen", side_effect=_blocked):
        yield


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
    else:
        db = DatabaseManager(str(target_db))
        db.initialize_database()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def isolated_qsettings(tmp_path, monkeypatch):
    """Point QSettings at a throwaway location so tests do not touch user prefs."""
    from PySide6.QtCore import QSettings

    monkeypatch.setenv("ABCS_TEST_SETTINGS_DIR", str(tmp_path))
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
    settings.clear()
    yield settings
    settings.clear()


@pytest.fixture
def main_window(qapp, temp_db, ui_scaler, theme_manager, qtbot):
    """Function-scoped MainWindow on an isolated temp database."""
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
    from src.web.web_book_api import WebBookAPI, _clear_source_cooldown, _reset_shared_web_api_for_tests

    _clear_source_cooldown()
    _reset_shared_web_api_for_tests()
    monkeypatch.setattr(wba, "WEB_CACHE_FILE", str(tmp_path / "web_cache.json"))
    client = WebBookAPI()
    yield client
    _clear_source_cooldown()
    _reset_shared_web_api_for_tests()
