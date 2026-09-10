"""Lightweight BackupRestoreWindow smoke tests."""

from __future__ import annotations

from pathlib import Path

from src.ui.backup_restore_window import BackupRestoreWindow


def test_backup_restore_window_smoke(temp_db, ui_scaler, theme_manager, qtbot):
    backup_dir = Path(temp_db.db_path).parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    sample = backup_dir / "abcs_backup_smoke.db"
    sample.write_bytes(b"backup")

    window = BackupRestoreWindow(temp_db, ui_scaler, theme_manager)
    qtbot.addWidget(window)

    assert window.windowTitle() == "Backup / Restore"
    assert window.accessibleName() == "Backup Restore"
    assert window.backup_list is not None
    assert window.backup_list.rowCount() >= 1

    assert window.backup_button is not None
    assert window.browse_button is not None
    assert window.restore_button is not None
    assert window.delete_button is not None
    assert window.full_reset_button is not None

    window.close()
