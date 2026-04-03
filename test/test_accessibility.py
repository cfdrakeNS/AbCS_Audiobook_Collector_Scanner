"""
Test script for minimal accessibility window
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from src.ui.accessibility_test_window import MinimalTestWindow

def test_accessibility():
    """Test basic accessibility shortcuts."""
    app = QApplication(sys.argv)
    
    print("=== Accessibility Test ===")
    print("Test F1: Should show message box")
    print("Test Alt+/: Should read status")
    print("Test Escape: Should close window")
    print("========================")
    
    window = MinimalTestWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_accessibility())
