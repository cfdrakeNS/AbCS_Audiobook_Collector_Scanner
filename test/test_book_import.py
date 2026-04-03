#!/usr/bin/env python3
"""
Test script to isolate book list import window issues.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


# Check announce_status_message function directly
def test_announce_function():
    """Test the announce_status_message function signature."""
    try:
        from src.accessibility.accessible_events import announce_status_message

        print("OK: announce_status_message imported successfully")

        # Test the function signature
        import inspect

        sig = inspect.signature(announce_status_message)
        print(f"Function signature: {sig}")

        # Show parameters
        for param_name, param in sig.parameters.items():
            default = (
                param.default
                if param.default != inspect.Parameter.empty
                else "required"
            )
            print(f"  Parameter: {param_name} = {default}")

        return True

    except Exception as e:
        print(f"ERROR: announce_status_message failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_book_import_window():
    """Test the book list import window in isolation."""
    app = QApplication(sys.argv)

    # Set up accessibility
    os.environ["QT_ACCESSIBILITY"] = "1"

    # First test the function
    if not test_announce_function():
        print("ERROR: announce_status_message test failed")
        return 1

    try:
        # Import required modules
        from src.database.database import DatabaseManager
        from src.accessibility.scaling import UIScaler
        from src.ui.book_list_import_window import BookListImportWindow

        # Create database and scaler
        db = DatabaseManager(":memory:")
        scaler = UIScaler()

        # Create window
        window = BookListImportWindow(db, scaler)

        print("OK: Book List Import Window created successfully")

        # Show window for testing
        window.show()

        print("OK: Window displayed - test Alt+/ to check status reading")
        print("Press Ctrl+C to exit")

        # Run event loop
        sys.exit(app.exec())

    except Exception as e:
        print(f"ERROR: creating window: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    test_book_import_window()
