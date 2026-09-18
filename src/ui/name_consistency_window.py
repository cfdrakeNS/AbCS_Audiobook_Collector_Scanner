"""Name consistency review dialog — confirm each similar-name group."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from src.accessibility.accessible_events import announce_dialog_opened
from src.core.name_consistency import (
    SimilarGroup,
    find_similar_author_groups,
    find_similar_genre_groups,
)
from src.database.queries import AuthorQueries, GenreQueries
from src.ui.accessible_dialog import AccessibleDialog


class NameConsistencyWindow(AccessibleDialog):
    """Review and merge similar author/genre names one group at a time."""

    def __init__(self, db, scaler, theme_manager, parent=None):
        super().__init__(parent)
        from src.accessibility.icon_helper import get_app_icon

        self.setWindowIcon(get_app_icon())
        self.db = db
        self.scaler = scaler
        self.theme_manager = theme_manager
        self.author_queries = AuthorQueries(db)
        self.genre_queries = GenreQueries(db)
        self.groups: list[SimilarGroup] = []
        self.index = 0
        self.merged_count = 0
        self.skipped_count = 0

        self.setWindowTitle("Name consistency check")
        self.setAccessibleName("Name consistency check")
        self.setAccessibleDescription(
            "Review similar author and genre spellings and merge them after confirming each group."
        )
        self.setModal(True)

        layout = QVBoxLayout(self)
        self.summary_label = QLabel("Scanning…")
        self.summary_label.setWordWrap(True)
        self.summary_label.setFocusPolicy(Qt.StrongFocus)
        layout.addWidget(self.summary_label)

        self.list_widget = QListWidget()
        self.list_widget.setAccessibleName("Similar names in this group")
        layout.addWidget(self.list_widget)

        buttons = QHBoxLayout()
        self.merge_btn = QPushButton("Merge into suggested")
        self.merge_btn.setAccessibleName("Merge into suggested")
        self.merge_btn.setDefault(True)
        self.merge_btn.clicked.connect(self.on_merge)
        self.skip_btn = QPushButton("Skip group")
        self.skip_btn.setAccessibleName("Skip group")
        self.skip_btn.clicked.connect(self.on_skip)
        self.close_btn = QPushButton("Close")
        self.close_btn.setAccessibleName("Close")
        self.close_btn.clicked.connect(self.accept)
        buttons.addWidget(self.merge_btn)
        buttons.addWidget(self.skip_btn)
        buttons.addWidget(self.close_btn)
        layout.addLayout(buttons)
        self.resize(520, 380)

        self._scan()

    def _scan(self) -> None:
        authors = self.author_queries.get_all()
        author_counts: dict[int, int] = {}
        rows = self.db.execute(
            "SELECT author_id, COUNT(*) FROM books "
            "WHERE author_id IS NOT NULL GROUP BY author_id"
        ).fetchall()
        for author_id, count in rows:
            author_counts[int(author_id)] = int(count)

        genres = self.genre_queries.get_all()
        genre_counts: dict[int, int] = {}
        rows = self.db.execute(
            "SELECT genre_id, COUNT(*) FROM books "
            "WHERE genre_id IS NOT NULL GROUP BY genre_id"
        ).fetchall()
        for genre_id, count in rows:
            genre_counts[int(genre_id)] = int(count)

        self.groups = find_similar_author_groups(
            authors, threshold=0.85, book_counts=author_counts
        ) + find_similar_genre_groups(
            genres, threshold=0.85, book_counts=genre_counts
        )
        self.index = 0
        if not self.groups:
            self.summary_label.setText("No similar author or genre groups found.")
            self.merge_btn.setEnabled(False)
            self.skip_btn.setEnabled(False)
            self.list_widget.clear()
        else:
            self._show_group()

    def _show_group(self) -> None:
        if self.index >= len(self.groups):
            self.summary_label.setText(
                f"Finished reviewing all groups. "
                f"Merged {self.merged_count}, skipped {self.skipped_count}."
            )
            self.merge_btn.setEnabled(False)
            self.skip_btn.setEnabled(False)
            self.list_widget.clear()
            return
        group = self.groups[self.index]
        kind = "Author" if group.kind == "authors" else "Genre"
        self.summary_label.setText(
            f"{kind} group {self.index + 1} of {len(self.groups)}. "
            f"Suggested canonical name: {group.suggested_name}."
        )
        self.list_widget.clear()
        for item_id, name in group.items:
            count = group.book_counts.get(item_id, 0)
            mark = " (suggested)" if item_id == group.suggested_id else ""
            self.list_widget.addItem(
                QListWidgetItem(f"{name} — {count} book(s){mark}")
            )
        self.merge_btn.setEnabled(True)
        self.skip_btn.setEnabled(True)

    def on_merge(self) -> None:
        if self.index >= len(self.groups):
            return
        group = self.groups[self.index]
        target = group.suggested_id
        if target is None:
            self.on_skip()
            return
        if group.kind == "authors":
            for author_id, _name in group.items:
                if author_id != target:
                    self.author_queries.merge(author_id, target)
        else:
            for genre_id, _name in group.items:
                if genre_id != target:
                    self.genre_queries.merge(genre_id, target)
        self.merged_count += 1
        self.index += 1
        self._show_group()

    def on_skip(self) -> None:
        self.skipped_count += 1
        self.index += 1
        self._show_group()

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
        announce_dialog_opened(self, "Name consistency check")
        if self.merge_btn.isEnabled():
            self.merge_btn.setFocus(Qt.OtherFocusReason)
        else:
            self.summary_label.setFocus(Qt.OtherFocusReason)
