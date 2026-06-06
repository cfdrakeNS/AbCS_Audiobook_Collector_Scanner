"""Tests for backup file discovery (case-sensitive filesystems)."""

import os
import time
from pathlib import Path

from src.database.connection import DatabaseManager


def test_list_backups_finds_lowercase_manual_backups(tmp_path: Path):
    db_path = tmp_path / "abcs.db"
    db_path.write_bytes(b"sqlite")
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    backup_file = backup_dir / "abcs_backup_Friday_June_05_26_at_12_00.db"
    backup_file.write_bytes(b"backup")

    manager = DatabaseManager(str(db_path))
    backups = manager.list_backups()

    assert backups == [backup_file.resolve()]


def test_list_backups_finds_legacy_mixed_case_manual_backups(tmp_path: Path):
    db_path = tmp_path / "abcs.db"
    db_path.write_bytes(b"sqlite")
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    backup_file = backup_dir / "AbCS_backup_Friday_June_05_26_at_12_00.db"
    backup_file.write_bytes(b"backup")

    manager = DatabaseManager(str(db_path))
    backups = manager.list_backups()

    assert backups == [backup_file.resolve()]


def test_list_backups_finds_schema_repair_backups(tmp_path: Path):
    db_path = tmp_path / "abcs.db"
    db_path.write_bytes(b"sqlite")
    repair_backup = tmp_path / "abcs.backup_schema_repair_2026.db"
    repair_backup.write_bytes(b"repair")

    manager = DatabaseManager(str(db_path))
    backups = manager.list_backups()

    assert backups == [repair_backup.resolve()]


def test_list_backups_orders_newest_first(tmp_path: Path):
    db_path = tmp_path / "abcs.db"
    db_path.write_bytes(b"sqlite")
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    older = backup_dir / "abcs_backup_older.db"
    newer = backup_dir / "abcs_backup_newer.db"
    older.write_bytes(b"old")
    newer.write_bytes(b"new")
    now = time.time()
    os.utime(older, (now - 60, now - 60))
    os.utime(newer, (now, now))

    manager = DatabaseManager(str(db_path))
    backups = manager.list_backups()

    assert backups == [newer.resolve(), older.resolve()]


def test_restore_from_backup_removes_wal_sidecars(tmp_path: Path):
    import sqlite3

    db_path = tmp_path / "abcs.db"
    backup_path = tmp_path / "backups" / "abcs_backup_test.db"
    backup_path.parent.mkdir(parents=True)

    backup_conn = sqlite3.connect(backup_path)
    backup_conn.execute("CREATE TABLE books (id INTEGER PRIMARY KEY)")
    backup_conn.commit()
    backup_conn.close()

    active_conn = sqlite3.connect(db_path)
    active_conn.execute("PRAGMA journal_mode=WAL")
    active_conn.execute("CREATE TABLE books (id INTEGER PRIMARY KEY)")
    active_conn.execute("INSERT INTO books (id) VALUES (99)")
    active_conn.commit()
    active_conn.close()

    wal = Path(f"{db_path}-wal")
    shm = Path(f"{db_path}-shm")
    wal.write_bytes(b"stale-wal")
    shm.write_bytes(b"stale-shm")

    manager = DatabaseManager(str(db_path))
    manager.restore_from_backup(backup_path)

    restored_conn = sqlite3.connect(db_path)
    row_count = restored_conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    restored_conn.close()
    assert row_count == 0

    if wal.exists():
        assert wal.read_bytes() != b"stale-wal"
    if shm.exists():
        assert shm.read_bytes() != b"stale-shm"
