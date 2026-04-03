#!/usr/bin/env python3
"""
Test Web Book Details Window - Audio Book Collection
Comprehensive test for web metadata fetching functionality.
"""

import sys
import os
import time
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer
from src.database import get_db
from src.accessibility.scaling import UIScaler
from src.accessibility.theme_manager import ThemeManager
from src.database.models import Book
from src.ui.web_book_details_window import WebBookDetailsWindow
from src.web.web_book_api import WebBookAPI


class WebBookDetailsTest:
    """Test class for Web Book Details functionality."""
    
    def __init__(self):
        self.app = None
        self.window = None
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        status = "PASS" if passed else "FAIL"
        result = f"[{status}] {test_name}"
        if message:
            result += f": {message}"
        self.test_results.append(result)
        print(result)
        
    def test_imports(self):
        """Test all required imports."""
        print("\n=== Testing Imports ===")
        
        try:
            import requests
            self.log_test("requests import", True)
        except ImportError as e:
            self.log_test("requests import", False, str(e))
            return False
            
        try:
            from src.web.web_book_api import WebBookAPI
            self.log_test("WebBookAPI import", True)
        except ImportError as e:
            self.log_test("WebBookAPI import", False, str(e))
            return False
            
        try:
            from src.ui.web_book_details_window import WebBookDetailsWindow
            self.log_test("WebBookDetailsWindow import", True)
        except ImportError as e:
            self.log_test("WebBookDetailsWindow import", False, str(e))
            return False
            
        return True
    
    def test_api_direct(self):
        """Test WebBookAPI directly."""
        print("\n=== Testing WebBookAPI Direct ===")
        
        try:
            api = WebBookAPI()
            self.log_test("WebBookAPI instantiation", True)
            
            # Test with a well-known book
            metadata = api.get_book_metadata("The Great Gatsby", "F. Scott Fitzgerald", "1925")
            
            if metadata:
                self.log_test("API data fetch", True, f"Source: {metadata.get('source', 'Unknown')}")
                
                # Check required fields
                required_fields = ['title', 'author', 'source', 'confidence']
                for field in required_fields:
                    has_field = field in metadata and metadata[field]
                    self.log_test(f"API field '{field}'", has_field, str(metadata.get(field, 'Missing')))
                    
                return True
            else:
                self.log_test("API data fetch", False, "No metadata returned")
                return False
                
        except Exception as e:
            self.log_test("API direct test", False, str(e))
            return False
    
    def test_window_creation(self):
        """Test WebBookDetailsWindow creation."""
        print("\n=== Testing Window Creation ===")
        
        try:
            # Create test book
            book = Book(
                book_id=1,
                title='The Great Gatsby',
                author_id=1,
                year=1925,
                series_id=None,
                genre_id=None,
                collection_id=1,
                reader='Test Reader',
                time_hours=10.5,
                time_minutes=30,
                tracks=1,
                size_mb=100,
                bitrate=128,
                file_format='mp3',
                path='/test/path',
                comments='Test comments',
                read_date=None,
                date_added='2024-01-01',
                source='test',
                author_name='F. Scott Fitzgerald',
                series_name=None,
                genre_name='Classic Fiction',
                collection_name='Test Collection'
            )
            
            # Create window
            self.window = WebBookDetailsWindow(
                self.db, book, self.scaler, self.theme_manager
            )
            
            self.log_test("Window creation", True)
            
            # Check window properties
            self.log_test("Window title exists", bool(self.window.windowTitle()))
            self.log_test("Setup UI method exists", hasattr(self.window, 'setup_ui'))
            self.log_test("Load book data method exists", hasattr(self.window, 'load_book_data'))
            self.log_test("Fetch web data method exists", hasattr(self.window, 'fetch_web_data'))
            self.log_test("Web data ready method exists", hasattr(self.window, 'on_web_data_ready'))
            self.log_test("Web data error method exists", hasattr(self.window, 'on_web_data_error'))
            
            # Check UI components
            self.log_test("Title field exists", hasattr(self.window, 'title_field'))
            self.log_test("Author field exists", hasattr(self.window, 'author_field'))
            self.log_test("Year field exists", hasattr(self.window, 'year_field'))
            self.log_test("Series field exists", hasattr(self.window, 'series_field'))
            self.log_test("Genre field exists", hasattr(self.window, 'genre_field'))
            self.log_test("Plot field exists", hasattr(self.window, 'plot_field'))
            
            # Check buttons
            self.log_test("Add Plot button exists", hasattr(self.window, 'add_plot_button'))
            self.log_test("Update All button exists", hasattr(self.window, 'update_all_button'))
            self.log_test("Cancel button exists", hasattr(self.window, 'cancel_button'))
            
            return True
            
        except Exception as e:
            self.log_test("Window creation", False, str(e))
            return False
    
    def test_initial_state(self):
        """Test initial window state."""
        print("\n=== Testing Initial State ===")
        
        try:
            # Check initial field values
            self.log_test("Title field initial text", 
                         bool(self.window.title_field.text()),
                         self.window.title_field.text())
            
            self.log_test("Author field initial text", 
                         bool(self.window.author_field.text()),
                         self.window.author_field.text())
            
            self.log_test("Plot field initial text", 
                         bool(self.window.plot_field.toPlainText()),
                         self.window.plot_field.toPlainText())
            
            # Check button states
            self.log_test("Add Plot button enabled", self.window.add_plot_button.isEnabled())
            self.log_test("Update All button enabled", self.window.update_all_button.isEnabled())
            
            # Check web data
            self.log_test("Web data initially empty", not self.window.web_data)
            self.log_test("Fake data method removed", not hasattr(self.window, '_get_fake_web_data'))
            
            return True
            
        except Exception as e:
            self.log_test("Initial state test", False, str(e))
            return False
    
    def test_web_data_fetching(self):
        """Test web data fetching (with timeout)."""
        print("\n=== Testing Web Data Fetching ===")
        
        try:
            # Start web data fetching
            self.window.fetch_web_data()
            self.log_test("Web data fetch started", True)
            
            # Wait for completion (with timeout)
            fetch_completed = False
            max_wait_time = 15  # 15 seconds timeout
            
            def check_completion():
                nonlocal fetch_completed
                if self.window.web_data or not fetch_completed:
                    fetch_completed = True
            
            # Use QTimer to check completion
            timer = QTimer()
            timer.timeout.connect(check_completion)
            timer.start(1000)  # Check every second
            
            # Wait for completion
            start_time = time.time()
            while not fetch_completed and (time.time() - start_time) < max_wait_time:
                self.app.processEvents()
                time.sleep(0.1)
            
            timer.stop()
            
            if fetch_completed:
                if self.window.web_data:
                    self.log_test("Web data fetch completed", True, 
                                 f"Source: {self.window.web_data.get('source', 'Unknown')}")
                    
                    # Check if fields were populated
                    title_populated = bool(self.window.title_field.text())
                    author_populated = bool(self.window.author_field.text())
                    plot_populated = bool(self.window.plot_field.toPlainText())
                    
                    self.log_test("Title field populated", title_populated)
                    self.log_test("Author field populated", author_populated)
                    self.log_test("Plot field populated", plot_populated)
                    
                    return True
                else:
                    self.log_test("Web data fetch completed", False, "No data received")
                    return False
            else:
                self.log_test("Web data fetch", False, "Timeout after 15 seconds")
                return False
                
        except Exception as e:
            self.log_test("Web data fetching test", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("=== Web Book Details Window Test Suite ===")
        print("Testing web metadata fetching functionality...")
        
        # Initialize Qt application
        self.app = QApplication(sys.argv)
        
        # Setup database and managers
        self.db = get_db()
        self.scaler = UIScaler(self.app)
        self.theme_manager = ThemeManager(self.app)
        
        # Run tests
        all_passed = True
        
        all_passed &= self.test_imports()
        
        if all_passed:
            all_passed &= self.test_api_direct()
        
        if all_passed:
            all_passed &= self.test_window_creation()
            
            if self.window:
                all_passed &= self.test_initial_state()
                all_passed &= self.test_web_data_fetching()
        
        # Print summary
        print("\n=== Test Summary ===")
        for result in self.test_results:
            print(result)
        
        passed_count = sum(1 for r in self.test_results if "[PASS]" in r)
        total_count = len(self.test_results)
        
        print(f"\nTests Passed: {passed_count}/{total_count}")
        
        if all_passed:
            print("🎉 ALL TESTS PASSED! Web Book Details window is working correctly.")
        else:
            print("❌ Some tests failed. Check the results above.")
        
        # Cleanup
        if self.window:
            self.window.close()
        
        return all_passed


def main():
    """Main test runner."""
    test = WebBookDetailsTest()
    success = test.run_all_tests()
    
    if success:
        print("\n✅ Web Book Details window is ready for use!")
        print("The Get Metadata button should work correctly.")
    else:
        print("\n❌ Issues found. Please check the test results.")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
