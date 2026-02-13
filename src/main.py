"""
AbCS - Audio Book Collector Scanner
Main application entry point. 
 
This file is responsible for:
1. Initializing the Qt application framework
2. Setting up the database connection
3. Loading accessibility settings (scaling, themes)
4. Displaying the splash screen with statistics
5. Creating and showing the main application window
"""

# Version information - update this with each release
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from pathlib import Path
import os
import sys
from database import get_db, close_db, StatisticsQueries, SeriesQueries, GenreQueries
from accessibility.scaling import get_scaler
from accessibility.theme_manager import get_theme_manager
from ui.main_window import MainWindow
APP_VERSION = "1.4.5"
APP_BUILD_DATE = "2026-02-14"


# Add src to path if needed - this allows imports like 'from ui.main_window import MainWindow'
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def get_database_path():
    """Get the correct database path for both development and bundled executable."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # PyInstaller extracts bundled files to sys._MEIPASS
        base_path = Path(sys._MEIPASS)
        bundled_db = base_path / 'data' / 'abcs.db'

        # Copy bundled database to user directory if it doesn't exist
        # This allows the database to be writable
        user_data_dir = Path.home() / 'AppData' / 'Local' / 'AbCS'
        user_data_dir.mkdir(parents=True, exist_ok=True)
        user_db = user_data_dir / 'abcs.db'

        if not user_db.exists() and bundled_db.exists():
            import shutil
            shutil.copy2(bundled_db, user_db)

        return str(user_db)
    else:
        # Running in development mode - use default path
        return None  # Uses default from DatabaseManager


class AbCSApplication:
    """Main application controller - manages the entire application lifecycle."""

    def __init__(self):
        """Initialize application - runs once when the program starts."""
        # Create Qt application - this is the main event loop that handles all UI interactions
        # It must be created before any other Qt objects
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setApplicationName("AbCS")
        self.qt_app.setOrganizationName("AbCS")
        self.qt_app.setOrganizationDomain("abcs.app")

        # Enable accessibility for screen readers (JAWS, NVDA, etc.)
        from PySide6.QtGui import QAccessible
        QAccessible.setActive(True)

        # Explicitly set root object - ensures accessibility tree is properly anchored
        # This is critical for Windows UIA bridge to find our application
        QAccessible.setRootObject(self.qt_app)

        # Initialize database connection - connects to SQLite database file
        # get_db() creates a DatabaseManager object that handles all database operations
        db_path = get_database_path()
        self.db = get_db(db_path)  # Uses bundled DB for exe, default for dev

        # Initialize accessibility systems for user preferences
        # Handles font/UI scaling (50-200%+)
        self.scaler = get_scaler(self.qt_app)
        self.theme_manager = get_theme_manager(
            self.qt_app)  # Handles color themes

        # Main window (created later)
        self.main_window = None
        main_window = None

    def show_splash(self):
        """Show splash screen with statistics."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QAbstractItemView
        from PySide6.QtCore import Qt, QTimer

        # Get statistics from database
        stats_queries = StatisticsQueries(self.db)
        stats = stats_queries.get_statistics()

        # Create dialog
        dlg = QDialog()
        dlg.setWindowTitle(f"AbCS v{APP_VERSION} - Audio Book Collector")
        dlg.resize(500, 500)
        dlg.setAttribute(Qt.WA_DeleteOnClose)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        if stats.total_books == 0:
            # First time use - welcome message - use text for simplicity
            from PySide6.QtWidgets import QTextEdit
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            splash_text = f"""Welcome to AbCS v{APP_VERSION} - Audio Book Collector Scanner!
Build: {APP_BUILD_DATE}

No audiobooks found in the database yet.

You can:
• Import audiobooks from your computer (scan folders)
• Manually add a new book

Use F9 to import or Alt+M for menu options."""
            text_edit.setPlainText(splash_text)
            font = text_edit.font()
            font.setPointSize(self.scaler.get_scaled_size(12))
            text_edit.setFont(font)
            layout.addWidget(text_edit)
        else:
            # Show statistics for existing library in a single-column table
            table = QTableWidget()
            table.setAccessibleName("Library Statistics")
            table.setAccessibleDescription(
                "Library statistics with values right-aligned")
            table.setColumnCount(1)
            table.setHorizontalHeaderLabels(["Library Statistics"])
            table.setSelectionBehavior(QAbstractItemView.SelectRows)
            table.setSelectionMode(QAbstractItemView.SingleSelection)
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table.setAlternatingRowColors(True)
            table.verticalHeader().setVisible(False)

            # Data rows with right-aligned values
            data = [
                ("Total Books", str(stats.total_books)),
                ("Total Authors", str(stats.total_authors)),
                ("Total Series", str(stats.total_series)),
                ("Total Genres", str(stats.total_genres)),
                ("Collections", str(stats.total_collections)),
                ("Books Read", str(stats.books_read)),
                ("Books Unread", str(stats.books_unread)),
                ("Total Listening Time", stats.total_time_display),
            ]

            table.setRowCount(len(data))

            for row, (label, value) in enumerate(data):
                # Format with fixed-width label for consistent alignment
                combined_text = f"{label:<25} {value}"
                item = QTableWidgetItem(combined_text)
                item.setData(Qt.AccessibleTextRole, f"{label}: {value}")
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                table.setItem(row, 0, item)

            # Resize column to stretch
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)

            # Set font size and use monospace for alignment
            font = table.font()
            font.setPointSize(self.scaler.get_scaled_size(11))
            font.setFamily("Courier New")
            table.setFont(font)

            layout.addWidget(table)

        ok_btn = QPushButton("Continue")
        ok_btn.clicked.connect(dlg.close)
        layout.addWidget(ok_btn)

        # Store timer as instance variable to prevent garbage collection
        self.splash_timer = QTimer()
        self.splash_timer.setSingleShot(True)

        def auto_close():
            if dlg.isVisible():
                dlg.close()

        self.splash_timer.timeout.connect(auto_close)
        self.splash_timer.start(3000)  # 3 seconds

        dlg.show()
        # Process events to let the splash screen display
        self.qt_app.processEvents()

    def run(self):
        """Run the application."""
        try:
            # Create and show main window
            self.main_window = MainWindow(
                self.db, self.scaler, self.theme_manager)
            self.main_window.show()

            # Check if screen reader is detected and notify user
            from PySide6.QtGui import QAccessible
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox(self.main_window)
            msg.setWindowTitle("Screen Reader Status")
            font = msg.font()
            font.setPointSize(self.scaler.get_scaled_size(14))
            msg.setFont(font)
            if QAccessible.isActive():
                msg.setIcon(QMessageBox.Information)
                msg.setText("Screen reader is detected.")
            else:
                msg.setIcon(QMessageBox.Warning)
                msg.setText(
                    "No screen reader detected.\n\nFor best accessibility, start JAWS or NVDA before launching AbCS.")
            msg.exec()

            # Diagnostic: Check accessibility setup (commented out for production)
            # from accessibility.accessible_events import check_accessibility_support
            # a11y_status = check_accessibility_support()
            # print("\n" + "="*60)
            # print("ACCESSIBILITY DIAGNOSTICS")
            # print("="*60)
            # print(f"QAccessible.isActive(): {a11y_status['isActive']}")
            # print(f"QApplication found: {a11y_status['has_app']}")
            # print(
            #     f"QApplication has accessible interface: {a11y_status['app_has_interface']}")
            # if a11y_status['app_role']:
            #     print(f"QApplication role: {a11y_status['app_role']}")
            # if a11y_status['app_name']:
            #     print(f"QApplication name: {a11y_status['app_name']}")
            # print(
            #     "\nTIP: If QAccessible.isActive() is False, no screen reader is attached.")
            # print("      Start JAWS FIRST, then run this application.")
            # print("="*60 + "\n")

            # Run event loop - this blocks until user closes the app
            return self.qt_app.exec()

        except Exception as e:
            # Print full exception for debugging
            import traceback
            print(f"ERROR: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise
        finally:
            # Cleanup orphaned series and genres (no associated books)
            try:
                SeriesQueries(self.db).cleanup_unused()
                GenreQueries(self.db).cleanup_unused()
            except Exception:
                pass  # Don't fail on cleanup errors
            # Cleanup database connection
            close_db()


def main():
    """Application entry point."""
    app = AbCSApplication()
    sys.exit(app.run())


if __name__ == '__main__':
    main()
