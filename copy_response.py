import sys
from PySide6.QtWidgets import QApplication
from pathlib import Path


def copy_to_clipboard():
    app = QApplication(sys.argv)
    response_file = Path(__file__).parent / "LATEST_RESPONSE.md"

    if response_file.exists():
        content = response_file.read_text(encoding="utf-8")
        clipboard = app.clipboard()
        clipboard.setText(content)
        print("Response successfully copied to clipboard.")
    else:
        print("Error: LATEST_RESPONSE.md not found.")


if __name__ == "__main__":
    copy_to_clipboard()
