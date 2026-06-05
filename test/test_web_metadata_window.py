"""Manual layout prototype for web metadata discrepancy checkboxes.

Not a pytest module — run directly: python test/test_web_metadata_window.py
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGroupBox,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


def main() -> int:
    app = QApplication(sys.argv)

    db_data = {
        "title": "Test Title",
        "author": "Test Author",
        "year": "2022",
        "series": "Test Series",
        "genre": "Test Genre",
        "plot": "Test plot",
    }
    web_data = {
        "title": "Web Title",
        "author": "Web Author",
        "year": "2023",
        "series": "Web Series",
        "genre": "Web Genre",
        "plot": "Web plot summary.",
    }

    win = QWidget()
    win.setWindowTitle("Discrepancy Checkbox Layout Test")
    main_layout = QVBoxLayout(win)
    main_layout.setSpacing(8)
    main_layout.setContentsMargins(20, 20, 20, 20)

    title_label = QLabel(f"Title: {db_data['title']} by {db_data['author']}")
    title_label.setAccessibleName("Title")
    title_label.setAccessibleDescription("Book title and author")
    title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
    title_label.setFocusPolicy(Qt.StrongFocus)
    main_layout.addWidget(title_label)
    QShortcut(QKeySequence("Alt+T"), win).activated.connect(
        lambda: title_label.setFocus()
    )

    discrepancies = []
    for field, db_val, web_val in [
        ("title", db_data["title"], web_data["title"]),
        ("year", db_data["year"], web_data["year"]),
        ("series", db_data["series"], web_data["series"]),
        ("genre", db_data["genre"], web_data["genre"]),
    ]:
        if db_val and db_val.strip() and db_val.strip() != web_val.strip():
            discrepancies.append((field, db_val, web_val))

    if discrepancies:
        msg_box = QTextEdit()
        msg_box.setReadOnly(True)
        msg_box.setText(
            "Discrepancies found: Check to apply web changes or leave unchecked to keep current data."
        )
        msg_box.setAccessibleName("Discrepancy message")
        msg_box.setMaximumHeight(40)
        main_layout.addWidget(msg_box)
        QShortcut(QKeySequence("Alt+D"), win).activated.connect(
            lambda: msg_box.setFocus()
        )

        group_box = QGroupBox()
        group_box.setStyleSheet("QGroupBox { border: none; margin: 0; padding: 0; }")
        group_layout = QVBoxLayout(group_box)
        group_layout.setSpacing(0)
        group_layout.setContentsMargins(0, 0, 0, 0)
        for field, db_val, web_val in discrepancies:
            cb = QCheckBox(f"{field.capitalize()} from '{db_val}' to '{web_val}'")
            cb.setAccessibleName(f"Apply web {field}")
            group_layout.addWidget(cb)
        main_layout.addWidget(group_box)

    plot = QTextEdit()
    plot.setPlainText(db_data["plot"])
    plot.setReadOnly(True)
    plot.setAccessibleName("Plot/Comments")
    main_layout.addWidget(plot)

    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
