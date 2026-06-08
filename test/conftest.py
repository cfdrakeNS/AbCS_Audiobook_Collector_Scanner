"""Shared pytest fixtures for AbCS tests."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

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
