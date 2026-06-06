"""
AbCS - Audio Book Collector Scanner
Main application entry point.
"""
import sys
from pathlib import Path

# Add project root to sys.path so 'src.xxx' imports work correctly
root_path = Path(__file__).resolve().parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

try:
    if sys.stdout:
        sys.stdout.flush()
except Exception:
    pass

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
import ctypes
import threading
import importlib


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


def _check_trial_expiry():
    """Block startup if this is a trial build that has expired.

    build_config.TRIAL_BUILD_DATE holds an ISO date string (YYYY-MM-DD).
    * If the value is empty/None ? normal (non-trial) build, skip check.
    * If set and today's date > that date ? show expiry message and exit.
    """
    try:
        from src.build_config import TRIAL_BUILD_DATE
    except ImportError:
        try:
            from build_config import TRIAL_BUILD_DATE
        except ImportError:
            return  # build_config not available — not a trial build

    # If TRIAL_BUILD_DATE is empty or None, this is a normal build
    if not TRIAL_BUILD_DATE:
        return

    try:
        from datetime import date as _date

        expiry = _date.fromisoformat(TRIAL_BUILD_DATE)
        today = _date.today()
        if today > expiry:
            days_past = (today - expiry).days
            title = "AbCS — Trial Build Expired"
            msg = (
                f"This trial copy of AbCS expired on {TRIAL_BUILD_DATE} "
                f"({days_past} day(s) ago).\n\n"
                f"Please contact the developer for a newer build."
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

        from src.accessibility.icon_helper import install_app_icon

        self.qt_app = QApplication(sys.argv)
        if sys.platform.startswith("linux"):
            from PySide6.QtWidgets import QStyleFactory

            from src.accessibility.linux_fusion_style import LinuxFusionStyle

            fusion = QStyleFactory.create("Fusion")
            if fusion is not None:
                self.qt_app.setStyle(LinuxFusionStyle(fusion))
            else:
                self.qt_app.setStyle("Fusion")
        self.qt_app.setApplicationName("AbCS")
        self.qt_app.setOrganizationName("AbCS")
        self.qt_app.setOrganizationDomain("abcs.app")
        # Set application icon for all windows (multi-size load for Linux WMs)
        install_app_icon(self.qt_app)

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

            # Empty database dialog is now handled by SetupDialog in main_window.py
            # (No longer handled here; all old code removed)

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

    # The empty database dialog is now handled by SetupDialog in main_window.py


def main():
    """Application entry point."""
    _check_trial_expiry()
    from src.accessibility.linux_qt_compat import install_linux_qt_compat

    install_linux_qt_compat()
    app = AbCSApplication()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
