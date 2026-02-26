"""Tests for manual backup, restore, and full reset database flows."""

from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path

from database.connection import DatabaseManager


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _temp_db(tmp_path):
    data_dir = Path(PROJECT_ROOT) / "data"
    candidates = [
        data_dir / "abcs.db",
        data_dir / "wh abcs.db",
    ]
    backup_candidates = sorted(
        data_dir.glob("abcs.db.backup.*"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    candidates.extend(backup_candidates)

    source_db = next((path for path in candidates if path.exists()), None)
    if source_db is None:
        raise FileNotFoundError(
            f"No testable database found in {data_dir}. Expected one of: abcs.db, wh abcs.db, or abcs.db.backup.*"
        )

    target_db = tmp_path / "abcs_test.db"
    shutil.copy2(source_db, target_db)
    db = DatabaseManager(str(target_db))
    db.initialize_database()
    return db


def test_create_manual_backup_and_list(tmp_path):
    db = _temp_db(tmp_path)
    try:
        backup_path = db.create_manual_backup()
        backups = db.list_backups()

        assert backup_path.exists()
        assert backup_path.parent.name == "backups"
        assert any(path == backup_path.resolve() for path in backups)
    finally:
        db.close()


def test_restore_from_backup_reverts_changes(tmp_path):
    db = _temp_db(tmp_path)
    marker = f"restore-marker-{uuid.uuid4().hex[:8]}"

    try:
        backup_path = db.create_manual_backup()

        db.execute(
            "INSERT INTO collections (name, active) VALUES (?, 1)",
            (marker,),
        )
        db.connect().commit()

        inserted = db.fetch_one(
            "SELECT collection_id FROM collections WHERE name = ?",
            (marker,),
        )
        assert inserted is not None

        db.restore_from_backup(backup_path)

        restored = db.fetch_one(
            "SELECT collection_id FROM collections WHERE name = ?",
            (marker,),
        )
        assert restored is None
    finally:
        db.close()


def test_full_reset_recreates_schema_and_returns_backup(tmp_path):
    db = _temp_db(tmp_path)
    marker = f"reset-marker-{uuid.uuid4().hex[:8]}"

    try:
        db.execute(
            "INSERT INTO collections (name, active) VALUES (?, 1)",
            (marker,),
        )
        db.connect().commit()

        backup_path = db.full_reset_database(create_backup=True)

        assert backup_path is not None
        assert backup_path.exists()

        marker_row = db.fetch_one(
            "SELECT collection_id FROM collections WHERE name = ?",
            (marker,),
        )
        assert marker_row is None

        collection_count_row = db.fetch_one("SELECT COUNT(*) FROM collections")
        assert collection_count_row is not None
        assert collection_count_row[0] >= 1
    finally:
        db.close()
