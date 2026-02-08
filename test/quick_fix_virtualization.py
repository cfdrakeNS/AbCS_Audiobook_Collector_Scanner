"""
Quick Fix: Remove QAccessible calls that may break virtualization.

This removes:
1. QAccessible.setActive(True)
2. QAccessible.setRootObject(self.qt_app)
3. Diagnostic output (since setActive check won't be meaningful)

Keeps everything else (scaling, themes, shortcuts, keyboard nav).
"""

import re
from pathlib import Path


def remove_qaccessible_calls():
    """Remove explicit QAccessible calls from main.py."""

    main_py = Path("src/main.py")

    if not main_py.exists():
        print("Error: src/main.py not found")
        return False

    # Read current content
    content = main_py.read_text(encoding='utf-8')

    # Backup
    backup = main_py.with_suffix('.py.BEFORE_FIX')
    backup.write_text(content, encoding='utf-8')
    print(f"✓ Backed up: {backup}")

    # Remove the QAccessible import and calls
    # This is the section we're removing:
    """
        # Enable accessibility for screen readers (JAWS, NVDA, etc.)
        from PySide6.QtGui import QAccessible
        QAccessible.setActive(True)

        # Explicitly set root object - ensures accessibility tree is properly anchored
        # This is critical for Windows UIA bridge to find our application
        QAccessible.setRootObject(self.qt_app)
    """

    # Pattern to match and remove
    pattern = re.compile(
        r'\s*# Enable accessibility for screen readers.*?'
        r'QAccessible\.setRootObject\(self\.qt_app\)\s*\n',
        re.DOTALL
    )

    content = pattern.sub('', content)

    # Also remove the diagnostic output in run() method
    diag_pattern = re.compile(
        r'\s*# Diagnostic: Check accessibility setup.*?'
        r'print\("=".\*60 \+ "\\n"\)\s*\n',
        re.DOTALL
    )

    content = diag_pattern.sub('', content)

    # Write cleaned content
    main_py.write_text(content, encoding='utf-8')
    print(f"✓ Removed QAccessible calls from {main_py}")

    return True


def main():
    print("\n" + "="*70)
    print("QUICK FIX: Remove QAccessible Calls")
    print("="*70)
    print("\nThis will remove:")
    print("  - QAccessible.setActive(True)")
    print("  - QAccessible.setRootObject(self.qt_app)")
    print("  - Diagnostic output")
    print("\nThis should restore JAWS virtualization (Insert+Alt+W).")
    print("\nAll other features remain:")
    print("  - Scaling, themes, shortcuts")
    print("  - Keyboard navigation")
    print("  - Status bar messages")
    print("="*70 + "\n")

    response = input("Apply fix? (yes/no): ").strip().lower()
    if response != "yes":
        print("Cancelled.")
        return

    if remove_qaccessible_calls():
        print("\n" + "="*70)
        print("FIX APPLIED")
        print("="*70)
        print("\nNow test:")
        print("  1. python src/main.py")
        print("  2. Try Insert+Alt+W to virtualize")
        print("\nIf you need to undo:")
        print("  - Restore from src/main.py.BEFORE_FIX")
        print("="*70 + "\n")
    else:
        print("\n✗ Fix failed")


if __name__ == "__main__":
    main()
