#!/usr/bin/env python3
"""
Simple test script to debug reading history window opening.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication
from src.database import get_db
from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.ui.reading_history_window import ReadingHistoryWindow

def run_manual_window_test():
    """Manual interactive test — not collected by pytest."""
    app = QApplication(sys.argv)
    
    print("Creating database connection...")
    db = get_db()
    
    print("Creating scaler and theme manager...")
    scaler = UIScaler(app)
    theme_manager = ThemeManager(app)
    
    print("Creating reading history window...")
    try:
        window = ReadingHistoryWindow(db, scaler, theme_manager)
        print("Window created successfully")
        
        print("Showing window...")
        window.show()
        print("Window shown")
        
        return app.exec()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("=== Reading History Window Test ===")
    exit_code = run_manual_window_test()
    print(f"Exit code: {exit_code}")
    sys.exit(exit_code)
