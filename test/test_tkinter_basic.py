"""
Tkinter basic test - alternative GUI framework to compare with PySide6.

This tests if JAWS can read Tkinter applications. If this works but PySide6
doesn't, it suggests a Qt-specific accessibility issue.

HOW TO TEST:
1. Start JAWS FIRST
2. Run: python test\test_tkinter_basic.py
3. Try these JAWS commands:
   - Insert+T: Read window title
   - Tab: Navigate to button
   - Space: Click button
"""

import tkinter as tk
from tkinter import ttk


def on_button_click():
    """Handle button click."""
    global click_count
    click_count += 1
    status_label.config(text=f"Button clicked {click_count} times")
    print(f"Button clicked {click_count} times")


def main():
    """Run the Tkinter test application."""
    global status_label, click_count
    click_count = 0

    print("\n" + "="*60)
    print("JAWS BASIC TKINTER TEST")
    print("="*60)
    print("With JAWS running, try:")
    print("  Insert+T        - Read window title")
    print("  Tab             - Navigate to button")
    print("  Insert+Tab      - Read current control")
    print("  Space           - Click button")
    print("="*60 + "\n")

    # Create main window
    root = tk.Tk()
    root.title("JAWS Tkinter Test")
    root.geometry("500x300")

    # Add padding
    main_frame = ttk.Frame(root, padding="20")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Label
    label = ttk.Label(
        main_frame,
        text="This is a Tkinter test. JAWS should read this.",
        font=("Arial", 14),
        wraplength=400
    )
    label.grid(row=0, column=0, pady=20)

    # Button
    button = ttk.Button(
        main_frame,
        text="Click Me",
        command=on_button_click
    )
    button.grid(row=1, column=0, pady=20)

    # Status label (like status bar)
    status_label = ttk.Label(
        main_frame,
        text="Ready - Press Tab to navigate",
        font=("Arial", 12)
    )
    status_label.grid(row=2, column=0, pady=20)

    # Configure grid weights
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)

    # Run application
    root.mainloop()


if __name__ == "__main__":
    main()
