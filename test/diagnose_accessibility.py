"""
JAWS/NVDA Accessibility Diagnostics for AbCS
Run this script to get detailed accessibility information.
"""

import argparse
import os
from pathlib import Path
import sys

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def print_separator(log):
    """Print separator line."""
    log("\n" + "=" * 80 + "\n")


def diagnose_qt_accessibility(args):
    """Run comprehensive accessibility diagnostics."""

    log_path = args.log_file

    def log(message):
        print(message, flush=True)
        if log_path:
            try:
                with open(log_path, "a", encoding="utf-8") as handle:
                    handle.write(f"{message}\n")
            except Exception:
                pass

    log("AbCS JAWS/NVDA Accessibility Diagnostics")
    print_separator(log)

    # Import PySide6 lazily so we can log any import hangs.
    try:
        from PySide6.QtCore import QTimer, qVersion
        from PySide6.QtGui import QAccessible
        from PySide6.QtWidgets import (
            QApplication,
            QLabel,
            QMainWindow,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )
        import PySide6
    except Exception as e:
        log(f"FATAL ERROR: Cannot import PySide6: {e}")
        return 1

    # Check PySide6 version
    try:
        log(f"PySide6 Version: {PySide6.__version__}")
    except Exception as e:
        log(f"ERROR: Cannot get PySide6 version: {e}")

    # Check Qt version
    try:
        log(f"Qt Version: {qVersion()}")
    except Exception as e:
        log(f"ERROR: Cannot get Qt version: {e}")

    print_separator(log)

    # Create Qt application
    if args.debug_plugins:
        os.environ["QT_DEBUG_PLUGINS"] = "1"
    if args.force_accessibility:
        os.environ["QT_ACCESSIBILITY"] = "1"

    log("Creating QApplication...")
    app = QApplication(sys.argv)

    # Enable accessibility BEFORE creating windows
    if not args.skip_accessibility_activate:
        log("Calling QAccessible.setActive(True)...")
        QAccessible.setActive(True)

    if not args.skip_accessibility_root:
        log("Calling QAccessible.setRootObject(app)...")
        QAccessible.setRootObject(app)

    print_separator(log)

    # Check if accessibility is active
    log(f"QAccessible.isActive(): {QAccessible.isActive()}")

    # Check for accessibility bridge plugin (path differs between Qt installs)
    log("\nChecking for accessibility bridge plugins...")
    plugins_root = Path(PySide6.__file__).parent / "plugins"
    accessible_dir = plugins_root / "accessible"
    log(f"Plugins root: {plugins_root}")
    if accessible_dir.exists():
        log(f"Accessible plugins directory exists: {accessible_dir}")
        plugins = list(accessible_dir.glob("*.dll"))
        if plugins:
            log("Found accessibility plugins:")
            for plugin in plugins:
                log(f"  - {plugin.name}")
        else:
            log("INFO: Accessible directory is present but empty.")
    else:
        log("INFO: Accessible plugins directory not present in this install.")

    print_separator(log)

    # Create a simple test window
    log("Creating test window...")
    window = QMainWindow()
    window.setWindowTitle("JAWS Accessibility Test Window")
    window.setAccessibleName("Test Window")
    window.setAccessibleDescription(
        "This is a test window for JAWS accessibility diagnostics")
    window.setObjectName("TestWindow")

    # Add simple content
    central = QWidget()
    layout = QVBoxLayout(central)

    label = QLabel(
        "If you can read this with JAWS cursor, accessibility is working!")
    label.setAccessibleName("Test Label")
    label.setAccessibleDescription("This is a test label")
    layout.addWidget(label)

    button = QPushButton("Test Button")
    button.setAccessibleName("Test Button")
    button.setAccessibleDescription("Click this button to test interaction")
    button.clicked.connect(lambda: print("Button clicked!"))
    layout.addWidget(button)

    window.setCentralWidget(central)
    window.resize(600, 400)

    def run_accessible_query():
        log("\nQuerying accessible interface for window...")
        iface = QAccessible.queryAccessibleInterface(window)
        if iface:
            log("Window accessible interface found!")
            log(f"  Role: {iface.role()}")
            log(f"  Name: {iface.text(QAccessible.Text.Name)}")
            log(f"  Description: {iface.text(QAccessible.Text.Description)}")
            log(f"  State: {iface.state()}")
            log(f"  Child count: {iface.childCount()}")

            # Check children
            if iface.childCount() > 0:
                log("\n  Children:")
                for i in range(min(5, iface.childCount())):
                    child = iface.child(i)
                    if child:
                        log(
                            f"    [{i}] Role: {child.role()}, Name: {child.text(QAccessible.Text.Name)}")
        else:
            log("ERROR: Cannot query accessible interface for window!")

    # Query accessible interface for window
    if args.skip_accessible_query:
        log("\nSkipping accessible interface query (safe mode).")
    else:
        delay_ms = max(0, args.accessible_query_delay_ms)
        if delay_ms > 0:
            log(
                f"\nScheduling accessible interface query after {delay_ms} ms...")
            QTimer.singleShot(delay_ms, run_accessible_query)
        else:
            run_accessible_query()

    print_separator(log)

    # Environment variables check
    log("Checking environment variables...")
    env_vars = [
        'QT_QPA_PLATFORM',
        'QT_ACCESSIBILITY',
        'QT_LOGGING_RULES',
        'QT_DEBUG_PLUGINS'
    ]
    for var in env_vars:
        value = os.environ.get(var, "(not set)")
        log(f"  {var}: {value}")

    print_separator(log)

    # Instructions
    log("TESTING INSTRUCTIONS:")
    log("1. The test window should now be visible")
    log("2. Try these JAWS commands:")
    log("   - Insert+T: Read window title")
    log("   - Insert+Ctrl+F1: Read window technical info")
    log("   - Numpad Plus: JAWS cursor to read window")
    log("   - Tab: Navigate to button, then Space to click")
    log("3. Look at the window class in technical info")
    log("   - Expected: Something like 'Qt6QWidget' or 'QWidget'")
    log("   - Problem: 'Qt6101QWindowIcon' (means accessibility broken)")
    log("4. Press Ctrl+C in this console to exit")
    print_separator(log)

    window.show()

    if args.auto_exit_seconds > 0:
        QTimer.singleShot(args.auto_exit_seconds * 1000, app.quit)

    # Run app
    return app.exec()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AbCS accessibility diagnostics")
    parser.add_argument("--skip-accessible-query", action="store_true",
                        help="Skip QAccessible.queryAccessibleInterface")
    parser.add_argument("--skip-accessibility-activate",
                        action="store_true", help="Skip QAccessible.setActive(True)")
    parser.add_argument("--skip-accessibility-root", action="store_true",
                        help="Skip QAccessible.setRootObject(app)")
    parser.add_argument("--debug-plugins", action="store_true",
                        help="Set QT_DEBUG_PLUGINS=1")
    parser.add_argument("--force-accessibility",
                        action="store_true", help="Set QT_ACCESSIBILITY=1")
    parser.add_argument("--auto-exit-seconds", type=int,
                        default=0, help="Auto-exit after N seconds")
    parser.add_argument("--accessible-query-delay-ms", type=int,
                        default=0, help="Delay QAccessible query to avoid startup hangs")
    parser.add_argument(
        "--log-file", default="diagnose_accessibility.log", help="Log file path")
    args = parser.parse_args()

    try:
        sys.exit(diagnose_qt_accessibility(args))
    except Exception as e:
        print(f"\nFATAL ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
