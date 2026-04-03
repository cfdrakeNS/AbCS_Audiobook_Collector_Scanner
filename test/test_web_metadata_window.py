import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QCheckBox, QGroupBox
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt

app = QApplication(sys.argv)

# Simulate DB and web data
db_data = {
    'title': 'Test Title',
    'author': 'Test Author',
    'year': '2022',
    'series': 'Test Series',
    'genre': 'Test Genre',
    'plot': 'Test plot',
}
web_data = {
    'title': 'Web Title',
    'author': 'Web Author',
    'year': '2023',
    'series': 'Web Series',
    'genre': 'Web Genre',
    'plot': 'Web plot summary.'
}

# Build main window
win = QWidget()
win.setWindowTitle("Discrepancy Checkbox Layout Test")
main_layout = QVBoxLayout(win)
main_layout.setSpacing(8)
main_layout.setContentsMargins(20, 20, 20, 20)

# Title label (Alt+T)
title_label = QLabel(f"Title: {db_data['title']} by {db_data['author']}")
title_label.setAccessibleName("Title")
title_label.setAccessibleDescription("Book title and author")
title_label.setBuddy(None)
title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
main_layout.addWidget(title_label)
title_label.setFocusPolicy(Qt.StrongFocus)
shortcut_title = QShortcut(QKeySequence("Alt+T"), win)
shortcut_title.activated.connect(lambda: title_label.setFocus())

# Discrepancy message (Alt+D)
discrepancies = []
diff_fields = [
    ("title", db_data['title'], web_data['title']),
    ("year", db_data['year'], web_data['year']),
    ("series", db_data['series'], web_data['series']),
    ("genre", db_data['genre'], web_data['genre'])
]
for field, db_val, web_val in diff_fields:
    if db_val and db_val.strip() and db_val.strip() != web_val.strip():
        discrepancies.append((field, db_val, web_val))

if discrepancies:
    msg_box = QTextEdit()
    msg_box.setReadOnly(True)
    msg_box.setText("Discrepancies found: Check to apply web changes or leave unchecked to keep current data.")
    msg_box.setAccessibleName("Discrepancy message")
    msg_box.setAccessibleDescription("Discrepancy message for web import")
    msg_box.setMaximumHeight(40)
    msg_box.setStyleSheet("font-size: 11pt; margin-bottom: 2px;")
    main_layout.addWidget(msg_box)
    shortcut_msg = QShortcut(QKeySequence("Alt+D"), win)
    shortcut_msg.activated.connect(lambda: msg_box.setFocus())

    # Discrepancy checkboxes (tight, accessible)
    group_box = QGroupBox()
    group_box.setStyleSheet("QGroupBox { border: none; margin: 0; padding: 0; }")
    group_layout = QVBoxLayout(group_box)
    group_layout.setSpacing(0)
    group_layout.setContentsMargins(0, 0, 0, 0)
    checkboxes = []
    for field, db_val, web_val in discrepancies:
        cb = QCheckBox(f"{field.capitalize()} from '{db_val}' to '{web_val}'")
        cb.setAccessibleName(f"Apply web {field}")
        cb.setChecked(False)
        cb.setStyleSheet("margin:0px;padding:0px;min-height:0px;min-width:0px;font-size:11pt;")
        group_layout.addWidget(cb)
        checkboxes.append(cb)
    main_layout.addWidget(group_box)

# Plot/comments field (always present)
plot = QTextEdit()
plot.setPlainText(db_data['plot'])
plot.setReadOnly(True)
plot.setAccessibleName("Plot/Comments")
main_layout.addWidget(plot)

win.setLayout(main_layout)
win.show()
app.exec()
