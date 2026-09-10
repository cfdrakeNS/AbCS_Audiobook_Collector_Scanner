#!/usr/bin/env python3
"""Manual interactive test for Book List Import window.

Not collected by pytest. Run:
    python scripts/manual_book_list_import.py
"""

from __future__ import annotations

import inspect
import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import QApplication


def _check_announce_function() -> bool:
    """Verify announce_status_message has the expected signature."""
    from src.accessibility.accessible_events import announce_status_message

    sig = inspect.signature(announce_status_message)
    return "status_bar" in sig.parameters and "message" in sig.parameters


def run_manual_import_window_test() -> int:
    """Show Book List Import window for manual Alt+/ accessibility checks."""
    app = QApplication(sys.argv)
    os.environ["QT_ACCESSIBILITY"] = "1"

    if not _check_announce_function():
        print("ERROR: announce_status_message signature check failed")
        return 1

    try:
        from src.accessibility.scaling import UIScaler
        from src.database.database import DatabaseManager
        from src.ui.book_list_import_window import BookListImportWindow

        db = DatabaseManager(":memory:")
        scaler = UIScaler()
        window = BookListImportWindow(db, scaler)

        print("OK: Book List Import Window created successfully")
        window.show()
        print("OK: Window displayed - test Alt+/ to check status reading")
        print("Close the window or press Ctrl+C to exit")
        return app.exec()
    except Exception as e:
        print(f"ERROR: creating window: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_manual_import_window_test())
