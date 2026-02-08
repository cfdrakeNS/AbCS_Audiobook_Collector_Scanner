"""
Qt Accessibility Diagnostic - checks your Qt configuration for common issues.

This script checks:
1. PySide6 and Qt versions
2. Available accessibility plugins
3. Qt platform configuration
4. Windows UIA support

Run this to diagnose potential issues before testing further.
"""

import sys
import os


def check_versions():
    """Check PySide6 and Qt versions."""
    print("\n" + "="*70)
    print("Qt VERSION CHECK")
    print("="*70)

    try:
        from PySide6 import __version__ as pyside_version
        print(f"PySide6 version: {pyside_version}")
    except Exception as e:
        print(f"ERROR: Cannot import PySide6: {e}")
        return False

    try:
        from PySide6.QtCore import qVersion
        qt_version = qVersion()
        print(f"Qt version: {qt_version}")

        # Check if version is sufficient
        major, minor, patch = qt_version.split('.')
        if int(major) >= 6 and int(minor) >= 6:
            print("✓ Qt version is 6.6+, UIA bridge should be available")
        else:
            print("⚠ Qt version is older than 6.6, UIA may not work properly")
            print("  Consider upgrading: pip install --upgrade PySide6")
    except Exception as e:
        print(f"ERROR: Cannot get Qt version: {e}")
        return False

    return True


def check_plugins():
    """Check for Qt accessibility plugins."""
    print("\n" + "="*70)
    print("Qt PLUGIN CHECK")
    print("="*70)

    try:
        from PySide6.QtCore import QCoreApplication, QLibraryInfo

        # Create minimal app to query library paths
        if not QCoreApplication.instance():
            app = QCoreApplication(sys.argv)

        plugin_path = QLibraryInfo.path(QLibraryInfo.PluginsPath)
        print(f"Qt plugins directory: {plugin_path}")

        # Check for accessibility plugin
        accessible_plugin_dir = os.path.join(plugin_path, "accessible")
        if os.path.exists(accessible_plugin_dir):
            plugins = os.listdir(accessible_plugin_dir)
            print(f"✓ Accessibility plugins found: {len(plugins)}")
            for plugin in plugins:
                print(f"  - {plugin}")
        else:
            print("⚠ Accessibility plugin directory not found")
            print("  This may indicate an incomplete PySide6 installation")

        # Check platform plugins
        platform_plugin_dir = os.path.join(plugin_path, "platforms")
        if os.path.exists(platform_plugin_dir):
            plugins = os.listdir(platform_plugin_dir)
            print(f"✓ Platform plugins found: {len(plugins)}")
            has_windows = any('windows' in p.lower() for p in plugins)
            if has_windows:
                print("  ✓ Windows platform plugin found")
            else:
                print("  ⚠ Windows platform plugin not found")
        else:
            print("⚠ Platform plugin directory not found")

    except Exception as e:
        print(f"ERROR checking plugins: {e}")
        return False

    return True


def check_environment():
    """Check relevant environment variables."""
    print("\n" + "="*70)
    print("ENVIRONMENT CHECK")
    print("="*70)

    env_vars = [
        'QT_ACCESSIBILITY_API_VERSION',
        'QT_QPA_PLATFORM',
        'QT_DEBUG_PLUGINS',
        'QT_ACCESSIBILITY',
    ]

    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"{var} = {value}")
        else:
            print(f"{var} = (not set)")

    # Check if MSAA mode would be enabled
    api_version = os.environ.get('QT_ACCESSIBILITY_API_VERSION')
    if api_version == '1':
        print("\n✓ MSAA mode is ENABLED (API version 1)")
    else:
        print("\n  UIA mode (default) - Set QT_ACCESSIBILITY_API_VERSION=1 for MSAA")


def check_windows_version():
    """Check Windows version."""
    print("\n" + "="*70)
    print("WINDOWS VERSION CHECK")
    print("="*70)

    try:
        import platform
        print(f"Platform: {platform.system()}")
        print(f"Release: {platform.release()}")
        print(f"Version: {platform.version()}")

        # Check if Windows 10+
        release = platform.release()
        if release in ['10', '11']:
            print(f"✓ Windows {release} supports UIA well")
        else:
            print(f"⚠ Windows {release} may have limited UIA support")
            print("  Consider using MSAA mode instead")

    except Exception as e:
        print(f"ERROR checking Windows version: {e}")


def check_accessibility():
    """Check if accessibility is working."""
    print("\n" + "="*70)
    print("ACCESSIBILITY API CHECK")
    print("="*70)

    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QAccessible

        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        # Try to activate accessibility
        QAccessible.setActive(True)
        is_active = QAccessible.isActive()

        print(f"QAccessible.isActive(): {is_active}")

        if is_active:
            print("✓ Qt accessibility is active")
            print(
                "  This means a screen reader is running or accessibility was manually enabled")
        else:
            print("⚠ Qt accessibility is NOT active")
            print("  Start JAWS/NVDA before running your app")

        # Try to set root object
        QAccessible.setRootObject(app)
        print("✓ QAccessible.setRootObject() succeeded")

    except Exception as e:
        print(f"ERROR checking accessibility: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def main():
    """Run all diagnostic checks."""
    print("="*70)
    print("Qt ACCESSIBILITY DIAGNOSTIC TOOL")
    print("="*70)
    print("\nThis script checks for common Qt accessibility configuration issues.")
    print("Run this with JAWS/NVDA active for best results.\n")

    success = True
    success = check_versions() and success
    success = check_plugins() and success
    check_environment()
    check_windows_version()
    success = check_accessibility() and success

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    if success:
        print("✓ Basic Qt accessibility configuration looks OK")
        print("\nIf JAWS Tab navigation still doesn't work, try:")
        print("  1. run_jaws_msaa_basic.bat (MSAA mode)")
        print("  2. run_jaws_native_window.bat (Native windows)")
        print("  3. run_jaws_with_roles.bat (Explicit roles)")
    else:
        print("⚠ Some configuration issues detected")
        print("\nSuggested fixes:")
        print("  1. Upgrade PySide6: pip install --upgrade PySide6")
        print("  2. Try MSAA mode: run_jaws_msaa_basic.bat")
        print("  3. Check PySide6 installation: pip install --force-reinstall PySide6")

    print("="*70 + "\n")


if __name__ == "__main__":
    main()
