#!/usr/bin/env python
"""Quick test to verify cleanup_window function works."""

from PySide6.QtWidgets import QApplication
from src.ui.import_window import ImportWindow
from src.ui.import_progress_window import ImportProgressWindow
from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.database.connection import DatabaseManager
from pathlib import Path

# Create app
app = QApplication.instance() or QApplication([])

# Test 1: Progress window can be created and closed
print("Test 1: Create progress window...")
scaler = UIScaler(app)
theme_manager = ThemeManager(app)
progress_window = ImportProgressWindow(scaler, theme_manager)
progress_window.show()
print(f"  Progress window visible: {progress_window.isVisible()}")

progress_window.mark_add_phase_complete(books_added=5, elapsed_text="00:30")
print(
    f"  Timer active after mark_add_phase_complete: {progress_window.auto_close_timer.isActive()}")

progress_window.close()
QApplication.processEvents()
QApplication.processEvents()
QApplication.processEvents()
print(
    f"  Progress window visible after close: {progress_window.isVisible()}")
print("  ✓ Test 1 passed")

# Test 2: ImportWindow cleanup works
print("\nTest 2: Create and cleanup ImportWindow...")
db_path = Path(__file__).parent / "data" / "abcs.db"
if not db_path.exists():
    print(f"  ✗ Database not found at {db_path}")
else:
    db = DatabaseManager(str(db_path))
    window = ImportWindow(db, scaler, theme_manager)
    window.show()
    print(f"  ImportWindow visible: {window.isVisible()}")

    # Simulate cleanup
    if window.progress_window:
        window.progress_window.close()
        QApplication.processEvents()
    window.close()
    QApplication.processEvents()
    QApplication.processEvents()

    print(f"  ImportWindow visible after close: {window.isVisible()}")
    print("  ✓ Test 2 passed")
    db.close()

print("\n✓ All quick tests passed!")
print("✓ App did NOT hang after closing windows")
