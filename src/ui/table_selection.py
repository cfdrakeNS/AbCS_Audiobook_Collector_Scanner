"""Fast whole-row selection for table views."""

from __future__ import annotations

from PySide6.QtCore import QItemSelection


def rows_to_selection(model, rows, col_count: int) -> QItemSelection:
    """Whole rows as one selection, one range per run of consecutive rows.

    One select() call per range instead of per cell keeps large selections fast
    (cell by cell took about 130 ms per Shift+Arrow step at 300 rows).
    """
    selection = QItemSelection()
    last_col = max(col_count - 1, 0)
    start = prev = None
    for row in sorted(rows):
        if start is None:
            start = prev = row
            continue
        if row == prev + 1:
            prev = row
            continue
        selection.select(model.index(start, 0), model.index(prev, last_col))
        start = prev = row
    if start is not None:
        selection.select(model.index(start, 0), model.index(prev, last_col))
    return selection
