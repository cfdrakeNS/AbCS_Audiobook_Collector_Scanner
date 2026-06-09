"""
StatisticsDialog - Accessible statistics popup for AbCS
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QHeaderView,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence
from src.accessibility.icon_helper import get_app_icon
from src.ui.accessible_dialog import AccessibleDialog
from src.accessibility.shortcut_helpers import build_accessible_f1_popup_style
from src.accessibility.style_helpers import (
    apply_tooltip_accessibility,
    build_table_polish_style,
)


class StatisticsDialog(AccessibleDialog):
    def __init__(self, stats, scaler, parent=None):
        super().__init__(parent)
        self.setWindowIcon(get_app_icon())
        self.setWindowTitle("Library Statistics")
        self.setAccessibleName("Library Statistics Dialog")
        self.setAccessibleDescription(
            "Dialog showing library statistics in a table format. Use Tab to navigate the table."
        )
        self.resize(500, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        table = QTableWidget()
        table.setAccessibleName("Library Statistics Table")
        table.setAccessibleDescription(
            "Table showing library statistics and their values. First column is the statistic name, second column is the value."
        )
        apply_tooltip_accessibility(
            table,
            "Library statistics summary",
            "Table showing library statistics and their values",
        )
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Statistic", "Value"])
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setTabKeyNavigation(False)
        table.setFocusPolicy(Qt.StrongFocus)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(False)
        vh = table.verticalHeader()
        vh.setVisible(False)
        vh.setAccessibleDescription("Table row headers are hidden.")
        vh.setAccessibleName("Table Row Headers")
        vh.setSectionResizeMode(QHeaderView.Fixed)
        vh.setMinimumSectionSize(0)
        vh.setMaximumSectionSize(0)
        vh.setHighlightSections(False)
        vh.setSectionsClickable(False)
        vh.setSectionsMovable(False)
        vh.setFocusPolicy(Qt.NoFocus)
        vh.setEnabled(False)
        table.setShowGrid(False)
        table.clearSelection()
        table.setMouseTracking(False)
        table.viewport().setMouseTracking(False)
        table.setAttribute(Qt.WA_Hover, False)
        table.viewport().setAttribute(Qt.WA_Hover, False)

        data = [
            ("Total Books", str(stats.total_books)),
            ("Total Authors", str(stats.total_authors)),
            ("Total Series", str(stats.total_series)),
            ("Total Genres", str(stats.total_genres)),
            ("", ""),
            ("Books Read", str(stats.books_read)),
            ("Total Hours Read", stats.total_hours_read_display),
            ("Books Unread", str(stats.books_unread)),
            ("Total Listening Time", stats.total_time_display),
        ]
        data.append(("", ""))
        data.append(("Collections", str(stats.total_collections)))
        if stats.collection_breakdown:
            for collection_name, book_count in stats.collection_breakdown:
                bullet = "• "
                formatted_count = f"{book_count:,}"
                data.append((f"{bullet}{collection_name}", formatted_count))

        table.setRowCount(len(data))
        table.setVerticalHeaderLabels([""] * len(data))

        def format_number(val):
            try:
                n = int(val.replace(",", ""))
                return f"{n:,}"
            except Exception:
                return val

        for row, (label, value) in enumerate(data):
            formatted_value = (
                format_number(value)
                if value.strip() and value.replace(",", "").isdigit()
                else value
            )
            item_label = QTableWidgetItem(label)
            item_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            accessible_text = (
                f"{label}: {formatted_value}" if label.strip() else formatted_value
            )
            item_label.setData(Qt.AccessibleTextRole, accessible_text)
            table.setItem(row, 0, item_label)
            item_value = QTableWidgetItem(formatted_value)
            item_value.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item_value.setData(Qt.AccessibleTextRole, accessible_text)
            table.setItem(row, 1, item_value)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setMinimumSectionSize(scaler.get_scaled_size(120))
        header.setStretchLastSection(True)
        layout.addWidget(table)
        self.setLayout(layout)
        self.table = table
        self.scaler = scaler
        self.apply_control_styles()
        if hasattr(scaler, "scale_changed"):
            scaler.scale_changed.connect(self.on_scale_changed)
        self.setup_shortcuts()

    def apply_control_styles(self):
        """Table polish consistent with other statistic windows."""
        table_style = (
            build_accessible_f1_popup_style()
            + build_table_polish_style("QTableWidget")
            + f"""
            QTableWidget {{
                border: 1px solid palette(mid);
                border-radius: {self.scaler.get_scaled_size(5)}px;
            }}
            """
        )
        self.table.setStyleSheet(table_style)

    def on_scale_changed(self, _scale_percentage: int):
        self.apply_control_styles()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.on_show_shortcuts)

    def on_show_shortcuts(self):
        """Show keyboard shortcuts help dialog."""
        from src.accessibility.shortcut_helpers import (
            get_accessible_shortcuts_list,
            build_accessible_f1_popup_style,
        )

        shortcuts = [
            ("Tab", "Navigate table cells"),
            ("F1", "Show this help"),
            ("Escape", "Close window"),
        ]

        dlg = AccessibleDialog(self)
        dlg.setWindowTitle("Keyboard Shortcuts - Statistics")
        dlg.setAccessibleName("Keyboard Shortcuts")
        dlg.resize(400, 300)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        table = QTableWidget()
        table.setAccessibleName("Shortcuts list")
        table.setColumnCount(1)
        table.setHorizontalHeaderLabels([""])

        table.setRowCount(len(shortcuts))
        table.setVerticalHeaderLabels([""] * len(shortcuts))
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectItems)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setTabKeyNavigation(False)
        table.setAlternatingRowColors(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setMouseTracking(False)
        table.viewport().setMouseTracking(False)
        table.setAttribute(Qt.WA_Hover, False)
        table.viewport().setAttribute(Qt.WA_Hover, False)

        shortcuts = get_accessible_shortcuts_list(shortcuts)
        table.setStyleSheet(build_accessible_f1_popup_style())

        for row, (key, desc) in enumerate(shortcuts):
            item = QTableWidgetItem(f"{desc} - {key}")
            item.setData(Qt.AccessibleTextRole, f"{desc}: {key}")
            table.setItem(row, 0, item)

        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        font = table.font()
        font.setPointSize(self.scaler.get_scaled_size(11))
        table.setFont(font)

        layout.addWidget(table)
        dlg.setLayout(layout)
        dlg.exec()

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.close()
            event.accept()
            return
        super().keyPressEvent(event)
