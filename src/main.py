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

from src.ui.main_window import MainWindow
from src.accessibility.shortcuts import find_shortcut_conflicts
from src.accessibility.theme_manager import get_theme_manager
from src.accessibility.scaling import get_scaler
from src.accessibility.style_helpers import build_accessible_button_style
from src.database import get_db, close_db, StatisticsQueries, SeriesQueries, GenreQueries, AuthorQueries
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont
import sys
import ctypes
import threading
from pathlib import Path
import os


def _show_native_message(title: str, message: str, auto_close_seconds: float = 3.0):
    """Show a Windows-native message box that auto-closes after a delay."""
    if not hasattr(ctypes, "windll"):
        return

    user32 = ctypes.windll.user32
    MB_ICONINFORMATION = 0x40
    MB_TOPMOST = 0x00040000
    MB_SETFOREGROUND = 0x00010000
    WM_CLOSE = 0x0010

    def _auto_close_message_box():
        hwnd = user32.FindWindowW("#32770", title)
        if hwnd:
            user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)

    timer = threading.Timer(auto_close_seconds, _auto_close_message_box)
    timer.daemon = True
    timer.start()

    user32.MessageBoxW(
        0,
        message,
        title,
        MB_ICONINFORMATION | MB_TOPMOST | MB_SETFOREGROUND,
    )
    timer.cancel()


def show_launch_message_if_executable():
    """Show an immediate Windows message when launched from bundled EXE."""
    if __name__ != '__main__':
        return
    if not getattr(sys, 'frozen', False):
        return
    if sys.platform != "win32":
        return
    if os.environ.get("ABCS_LAUNCH_MSG_SHOWN") == "1":
        return
    os.environ["ABCS_LAUNCH_MSG_SHOWN"] = "1"
    _show_native_message(
        "AbCS", "AbCS is starting. Please wait while it loads.", auto_close_seconds=4.0)


# Show launch message before importing heavier UI modules.
show_launch_message_if_executable()

# Version information - update this with each release
APP_VERSION = "1.9.2"
APP_BUILD_DATE = "2026-03-27"


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
        first_run_marker = user_data_dir / '.bundled_first_run_complete'

        if bundled_db.exists():
            import shutil

            # First run of bundled app: always reset local DB from embedded DB.
            # This ensures stale local databases don't persist across fresh installs.
            if not first_run_marker.exists():
                if user_db.exists():
                    try:
                        user_db.unlink()
                    except Exception:
                        # If unlink fails, attempt to overwrite on copy below.
                        pass
                shutil.copy2(bundled_db, user_db)
                first_run_marker.write_text('1', encoding='utf-8')
            elif not user_db.exists():
                # Subsequent runs: recreate local DB only if missing.
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
        self.db.initialize_database()

        if getattr(sys, 'frozen', False) and getattr(self.db, "schema_repair_performed", False):
            repair_message = getattr(
                self.db,
                "schema_repair_message",
                "Database upgraded from legacy format for compatibility.",
            )
            _show_native_message("AbCS", repair_message,
                                 auto_close_seconds=5.0)

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

        if stats.total_books == 0:
            # First time use - welcome message using standalone accessible message box
            from PySide6.QtWidgets import QMessageBox
            from src.accessibility.style_helpers import exec_styled_message_box
            
            splash_message = f"""Welcome to AbCS v{APP_VERSION} - Audio Book Collector Scanner!
Build: {APP_BUILD_DATE}

No audiobooks found in the database yet.

You can:
• Import audiobooks from your computer (scan folders)
• Manually add a new book

Use Ctrl+I to import or Alt+M for menu options."""
            
            exec_styled_message_box(
                self.main_window if self.main_window else self.qt_app.activeWindow(),
                self.scaler.get_scaled_size(20),
                icon=QMessageBox.Information,
                title="Welcome to AbCS",
                text=splash_message,
                buttons=QMessageBox.Ok,
                default_button=QMessageBox.Ok
            )
            return  # Skip statistics dialog for empty database

        # Create statistics dialog for existing library
        dlg = QDialog()
        dlg.setWindowTitle(f"AbCS v{APP_VERSION} - Audio Book Collector")
        dlg.resize(500, 500)
        dlg.setAttribute(Qt.WA_DeleteOnClose)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

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
        ok_btn.setAccessibleName("Continue")
        ok_btn.setAccessibleDescription("Close this statistics dialog and continue to the main application")
        ok_btn.clicked.connect(dlg.close)
        layout.addWidget(ok_btn)

        # Set focus to statistics table for keyboard navigation
        def focus_statistics_table():
            table.setFocus()
            if table.rowCount() > 0:
                table.setCurrentCell(0, 0)

        # Focus table after dialog is shown
        QTimer.singleShot(100, focus_statistics_table)

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

            if getattr(self.db, "schema_repair_performed", False):
                repair_message = getattr(self.db, "schema_repair_message", "")
                if repair_message:
                    self.main_window.set_status(
                        repair_message, timeout_ms=20000, announce=True)

            self._show_empty_library_dialog_if_needed()

            shortcut_conflicts = find_shortcut_conflicts(self.main_window)
            if shortcut_conflicts:
                first_issue = shortcut_conflicts[0]
                self.main_window.status_bar.showMessage(
                    f"Shortcut conflict detected: {first_issue}")

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
            # Cleanup orphaned lookup records (no associated books)
            try:
                AuthorQueries(self.db).cleanup_unused()
                SeriesQueries(self.db).cleanup_unused()
                GenreQueries(self.db).cleanup_unused()
            except Exception:
                pass  # Don't fail on cleanup errors

            try:
                self.db.vacuum()
            except Exception:
                pass
        
        exec_styled_message_box(
            self.main_window if self.main_window else self.qt_app.activeWindow(),
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Information,
            title="Welcome to AbCS",
            text=splash_message,
            buttons=QMessageBox.Ok,
            default_button=QMessageBox.Ok
        )
        return  # Skip statistics dialog for empty database

    def run(self):
        """Run the application."""
        try:
            # Create and show main window
            self.main_window = MainWindow(
                self.db, self.scaler, self.theme_manager)
            self.main_window.show()

            if getattr(self.db, "schema_repair_performed", False):
                repair_message = getattr(self.db, "schema_repair_message", "")
                if repair_message:
                    self.main_window.set_status(
                        repair_message, timeout_ms=20000, announce=True)

            self._show_empty_library_dialog_if_needed()

            shortcut_conflicts = find_shortcut_conflicts(self.main_window)
            if shortcut_conflicts:
                first_issue = shortcut_conflicts[0]
                self.main_window.status_bar.showMessage(
                    f"Shortcut conflict detected: {first_issue}")

            # Run event loop - this blocks until user closes the app
            return self.qt_app.exec()

        except Exception as e:
            # Print full exception for debugging
            import traceback
            print(f"ERROR: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise
        finally:
            # Cleanup orphaned lookup records (no associated books)
            try:
                AuthorQueries(self.db).cleanup_unused()
                SeriesQueries(self.db).cleanup_unused()
                GenreQueries(self.db).cleanup_unused()
            except Exception:
                pass  # Don't fail on cleanup errors

            try:
                self.db.vacuum()
            except Exception:
                pass

            # Cleanup database connection
            close_db()

    def _show_empty_library_dialog_if_needed(self):
        """Show action dialog whenever the database has no books."""
        stats = StatisticsQueries(self.db).get_statistics()
        if stats.total_books != 0:
            return

        # Use exec_styled_message_box like delete confirmation for JAWS Insert+B compatibility
        from PySide6.QtWidgets import QMessageBox
        from src.accessibility.style_helpers import exec_styled_message_box
        
        empty_library_message = """The database is empty.

To get started, import audiobooks from your folders.
You can also open Preferences to adjust colors and font size.

What would you like to do?"""
        
        reply = exec_styled_message_box(
            self.main_window,
            self.scaler.get_scaled_size(20),
            icon=QMessageBox.Information,
            title="Welcome to AbCS - Database Empty",
            text=empty_library_message,
            buttons=QMessageBox.Ok,
            default_button=QMessageBox.Ok
        )
        
        # After user reads message, show action options
        if reply == QMessageBox.Ok:
            self._show_action_options()

    def _show_action_options(self):
        """Show simple action dialog with buttons."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout
        
        dlg = QDialog(self.main_window)
        dlg.setWindowTitle("AbCS - Choose Action")
        dlg.resize(400, 150)

        layout = QVBoxLayout(dlg)
        
        button_row = QHBoxLayout()
        
        import_btn = QPushButton("Import")
        import_btn.setAccessibleName("Import")
        import_btn.setAccessibleDescription("Import audiobooks from your computer folders")
        
        continue_btn = QPushButton("Continue")
        continue_btn.setAccessibleName("Continue")
        continue_btn.setAccessibleDescription("Continue to the main application")
        continue_btn.setDefault(True)

        button_style = build_accessible_button_style(self.scaler.get_scaled_size(20))
        import_btn.setStyleSheet(button_style)
        continue_btn.setStyleSheet(button_style)

        button_row.addWidget(import_btn)
        button_row.addStretch(1)
        button_row.addWidget(continue_btn)
        layout.addLayout(button_row)

        def on_import():
            dlg.accept()
            self.main_window.on_import()

        import_btn.clicked.connect(on_import)
        continue_btn.clicked.connect(dlg.accept)
        
        # Add Ctrl+I shortcut
        from PySide6.QtGui import QShortcut, QKeySequence
        import_shortcut = QShortcut(QKeySequence("Ctrl+I"), dlg)
        import_shortcut.activated.connect(on_import)

        dlg.exec()


def main():
    """Application entry point."""
    app = AbCSApplication()
    sys.exit(app.run())


if __name__ == '__main__':
    main()
