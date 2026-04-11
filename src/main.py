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
from src.database import (
    get_db,
    close_db,
    StatisticsQueries,
    SeriesQueries,
    GenreQueries,
    AuthorQueries,
)
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
import sys
import ctypes
import threading
import importlib
from pathlib import Path


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


# Version information - update this with each release
APP_VERSION = "1.9.8"


def _check_trial_expiry():
    """Block startup if this is a trial build that has expired."""
    try:
        from build_config import TRIAL_BUILD, TRIAL_DAYS, TRIAL_BUILD_DATE
    except ImportError:
        return  # Not a trial build

    if not TRIAL_BUILD:
        return

    try:
        from datetime import date as _date

        build = _date.fromisoformat(TRIAL_BUILD_DATE)
        age_days = (_date.today() - build).days
        if age_days >= TRIAL_DAYS:
            title = "AbCS — Tester Build Expired"
            msg = (
                f"This tester copy of AbCS (build {TRIAL_BUILD_DATE}) is "
                f"{age_days} days old and has expired.\n\n"
                f"Tester builds expire after {TRIAL_DAYS} days to ensure "
                f"everyone is testing the latest version.\n\n"
                f"Please ask for a newer build to continue."
            )
            _show_native_message(title, msg, auto_close_seconds=60.0)
            sys.exit(1)
    except SystemExit:
        raise
    except Exception:
        pass  # Never block startup on a date-parse failure


# Add src to path if needed - this allows imports like 'from ui.main_window import MainWindow'
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def get_database_path():
    """Get the correct database path for both development and bundled executable."""
    if getattr(sys, "frozen", False):
        # Running as compiled executable
        # PyInstaller extracts bundled files to sys._MEIPASS
        base_path = Path(sys._MEIPASS)
        bundled_db = base_path / "data" / "abcs.db"

        # Copy bundled database to user directory if it doesn't exist
        # This allows the database to be writable
        user_data_dir = Path.home() / "AppData" / "Local" / "AbCS"
        user_data_dir.mkdir(parents=True, exist_ok=True)
        user_db = user_data_dir / "abcs.db"
        first_run_marker = user_data_dir / ".bundled_first_run_complete"

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
                first_run_marker.write_text("1", encoding="utf-8")
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
        from PySide6.QtGui import QIcon

        self.qt_app = QApplication(sys.argv)
        self.qt_app.setApplicationName("AbCS")
        self.qt_app.setOrganizationName("AbCS")
        self.qt_app.setOrganizationDomain("abcs.app")
        # Set application icon for all windows (Windows prefers .ico)
        self.qt_app.setWindowIcon(QIcon("data/graphics/abCS_icon.ico"))

        self._spreadsheet_dependency_report = self._check_spreadsheet_dependencies()

        # Enable accessibility for screen readers
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

        if getattr(sys, "frozen", False) and getattr(
            self.db, "schema_repair_performed", False
        ):
            repair_message = getattr(
                self.db,
                "schema_repair_message",
                "Database upgraded from legacy format for compatibility.",
            )
            _show_native_message("AbCS", repair_message, auto_close_seconds=5.0)

        # Initialize accessibility systems for user preferences
        # Handles font/UI scaling (50-200%+)
        self.scaler = get_scaler(self.qt_app)
        self.theme_manager = get_theme_manager(self.qt_app)  # Handles color themes

        # Main window (created later)
        self.main_window = None
        main_window = None

    def _check_spreadsheet_dependencies(self) -> dict:
        """Check spreadsheet import engines at startup so build regressions are obvious."""
        modules_to_check = [
            ("pandas", "pandas"),
            ("openpyxl", "openpyxl"),
            ("odfpy", "odf"),
            ("odfpy-opendocument", "odf.opendocument"),
        ]

        available = []
        missing = []

        for display_name, module_name in modules_to_check:
            try:
                importlib.import_module(module_name)
                available.append(display_name)
            except Exception:
                missing.append(display_name)

        mode = "packaged" if getattr(sys, "frozen", False) else "development"
        if missing:
            print(
                f"[AbCS Startup Dependency Check] mode={mode}; missing={', '.join(missing)}",
                file=sys.stderr,
            )
        else:
            print(
                f"[AbCS Startup Dependency Check] mode={mode}; spreadsheet engines OK",
                file=sys.stderr,
            )

        return {
            "available": available,
            "missing": missing,
        }

    def run(self):
        """Run the application."""
        try:
            # Create and show main window
            self.main_window = MainWindow(self.db, self.scaler, self.theme_manager)
            self.main_window.show()

            if getattr(self.db, "schema_repair_performed", False):
                repair_message = getattr(self.db, "schema_repair_message", "")
                if repair_message:
                    self.main_window.set_status(
                        repair_message, timeout_ms=20000, announce=True
                    )

            missing_dependencies = self._spreadsheet_dependency_report.get(
                "missing", []
            )
            if missing_dependencies:
                self.main_window.set_status(
                    "Startup dependency warning: missing "
                    + ", ".join(missing_dependencies),
                    timeout_ms=15000,
                    announce=True,
                )

            self._show_empty_library_dialog_if_needed()

            shortcut_conflicts = find_shortcut_conflicts(self.main_window)
            if shortcut_conflicts:
                first_issue = shortcut_conflicts[0]
                self.main_window.status_bar.showMessage(
                    f"Shortcut conflict detected: {first_issue}"
                )

            # Diagnostic: Check accessibility setup (commented out for production)
            # ...existing code...

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

        from PySide6.QtWidgets import (
            QDialog,
            QVBoxLayout,
            QHBoxLayout,
            QLabel,
            QPushButton,
            QTableWidget,
            QTableWidgetItem,
            QHeaderView,
            QAbstractItemView,
        )

        guidance_lines = [
            "Database is empty.",
            "Use Tab key to move to the option buttons and press Enter to select.",
            "Import Books: Scan audiobook folders and read tags automatically.",
            "Import List: Import from spreadsheet files (CSV, XLSX, XLS).",
            "Preferences: Adjust colors and font size.",
            "Continue: Stay in the main window.",
            "Non-commercial use only; fee-based distribution requires written permission from C.F. Drake and Contributors.",
        ]

        # Mirror working popup pattern by announcing guidance in status bar as well.
        self.main_window.set_status(
            "Database empty dialog opened. Choose Import Books, Import List, Preferences, or Continue.",
            timeout_ms=12000,
            announce=True,
        )

        dlg = QDialog(self.main_window)
        dlg.setModal(True)
        dlg.setWindowTitle("Welcome to AbCS - Database Empty")
        dlg.setAccessibleName("Database Empty - Choose Import Option")
        dlg.setAccessibleDescription("Choose how to start with an empty database")
        dlg.resize(self.scaler.get_scaled_size(700), self.scaler.get_scaled_size(300))

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        heading = QLabel("Choose one option to get started", dlg)
        heading.setAccessibleName("Choose one option to get started")
        heading_font = heading.font()
        heading_font.setPointSize(self.scaler.get_scaled_size(12))
        heading.setFont(heading_font)
        layout.addWidget(heading)

        guidance_table = QTableWidget(dlg)
        guidance_table.setAccessibleName("Empty database guidance")
        guidance_table.setAccessibleDescription(
            "Read-only guidance text for startup options. Use arrow keys to read line by line."
        )
        guidance_table.setColumnCount(1)
        guidance_table.setRowCount(len(guidance_lines))
        guidance_table.setHorizontalHeaderLabels([""])
        guidance_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        guidance_table.setSelectionMode(QAbstractItemView.SingleSelection)
        guidance_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        guidance_table.setTabKeyNavigation(False)
        guidance_table.setAlternatingRowColors(False)
        guidance_table.setShowGrid(False)
        guidance_table.verticalHeader().setVisible(False)
        guidance_table.horizontalHeader().setVisible(False)
        guidance_table.setStyleSheet(
            "QTableWidget:focus { border: none; outline: none; }"
            "QTableWidget::item:selected { background-color: transparent; color: palette(text); }"
            "QTableWidget::item:focus { outline: none; }"
        )

        for row, line in enumerate(guidance_lines):
            item = QTableWidgetItem(line)
            item.setData(Qt.AccessibleTextRole, line)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            guidance_table.setItem(row, 0, item)

        guidance_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        guidance_table.setMaximumHeight(self.scaler.get_scaled_size(150))
        table_font = guidance_table.font()
        table_font.setPointSize(self.scaler.get_scaled_size(11))
        guidance_table.setFont(table_font)
        layout.addWidget(guidance_table)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)

        import_books_btn = QPushButton("Import Books", dlg)
        import_list_btn = QPushButton("Import List", dlg)
        preferences_btn = QPushButton("Preferences", dlg)
        continue_btn = QPushButton("Continue", dlg)

        reference_button_style = self.main_window.update_button.styleSheet()
        for btn in (import_books_btn, import_list_btn, preferences_btn, continue_btn):
            btn.setStyleSheet(reference_button_style)
            button_row.addWidget(btn)

        layout.addLayout(button_row)

        choice = {"value": "continue"}

        import_books_btn.clicked.connect(
            lambda: (choice.update(value="import_books"), dlg.accept())
        )
        import_list_btn.clicked.connect(
            lambda: (choice.update(value="import_list"), dlg.accept())
        )
        preferences_btn.clicked.connect(
            lambda: (choice.update(value="preferences"), dlg.accept())
        )
        continue_btn.clicked.connect(
            lambda: (choice.update(value="continue"), dlg.accept())
        )

        dlg.setTabOrder(guidance_table, import_books_btn)
        dlg.setTabOrder(import_books_btn, import_list_btn)
        dlg.setTabOrder(import_list_btn, preferences_btn)
        dlg.setTabOrder(preferences_btn, continue_btn)

        def focus_guidance_table() -> None:
            if guidance_table.rowCount() > 0:
                guidance_table.setCurrentCell(0, 0)
            guidance_table.setFocus(Qt.ActiveWindowFocusReason)

        QTimer.singleShot(0, focus_guidance_table)
        QTimer.singleShot(150, focus_guidance_table)
        dlg.exec()

        # Handle user's choice
        if choice["value"] == "import_books":
            self.main_window.on_import()
        elif choice["value"] == "import_list":
            self.main_window.on_book_list_import()
        elif choice["value"] == "preferences":
            self.main_window.on_preferences()
        elif choice["value"] == "continue":
            pass


def main():
    """Application entry point."""
    _check_trial_expiry()
    app = AbCSApplication()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
