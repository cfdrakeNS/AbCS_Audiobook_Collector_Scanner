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
from src.accessibility.shortcut_helpers import build_accessible_f1_popup_style


class StatisticsDialog(QDialog):
    def __init__(self, stats, scaler, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Library Statistics")
        self.setAccessibleName("")
        self.setAccessibleDescription("")
        self.resize(500, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        table = QTableWidget()
        table.setAccessibleName("")
        table.setAccessibleDescription("")
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Statistic", "Value"])
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(False)
        vh = table.verticalHeader()
        vh.setVisible(False)
        vh.setAccessibleDescription("")
        vh.setAccessibleName("")
        vh.setSectionResizeMode(QHeaderView.Fixed)
        vh.setMinimumSectionSize(0)
        vh.setMaximumSectionSize(0)
        vh.setHighlightSections(False)
        vh.setSectionsClickable(False)
        vh.setSectionsMovable(False)
        vh.setFocusPolicy(Qt.NoFocus)
        vh.setEnabled(False)
        table.setShowGrid(False)
        table.setFocusPolicy(Qt.StrongFocus)
        table.clearSelection()
        table.setStyleSheet(build_accessible_f1_popup_style())

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
            item_label.setData(Qt.AccessibleTextRole, label)
            item_label.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setItem(row, 0, item_label)
            item_value = QTableWidgetItem(formatted_value)
            item_value.setData(Qt.AccessibleTextRole, formatted_value)
            item_value.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setItem(row, 1, item_value)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setMinimumSectionSize(scaler.get_scaled_size(120))
        header.setStretchLastSection(True)
        layout.addWidget(table)
        self.setLayout(layout)
        self.table = table
        # Set focus to the top row, first column
        QTimer.singleShot(0, lambda: self.table.setCurrentCell(0, 0))
        QTimer.singleShot(0, lambda: self.table.setFocus(Qt.TabFocusReason))
