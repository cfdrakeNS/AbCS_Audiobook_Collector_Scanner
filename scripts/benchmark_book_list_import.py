"""Manual before/after timing for book-list import batching.

Not collected by pytest (lives under scripts/). Example:

    .venv\\Scripts\\python.exe scripts/benchmark_book_list_import.py --rows 2000
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=1000)
    args = parser.parse_args()

    import pandas as pd
    from PySide6.QtWidgets import QApplication

    from src.accessibility.scaling import UIScaler
    from src.accessibility.theme_manager import ThemeManager
    from src.database.connection import DatabaseManager
    from src.ui.book_list_import_window import BookListImportWindow

    app = QApplication.instance() or QApplication([])
    tmp = tempfile.mkdtemp(prefix="abcs_bli_bench_")
    db_path = Path(tmp) / "bench.db"
    db = DatabaseManager(str(db_path))
    db.initialize_database()

    scaler = UIScaler(app)
    theme = ThemeManager(app)
    window = BookListImportWindow(db, scaler, theme)

    frame = pd.DataFrame(
        {
            "Title": [f"Bench Book {i:05d}" for i in range(args.rows)],
            "Author": [f"Bench Author {i % 50}" for i in range(args.rows)],
            "Year": [2000 + (i % 25) for i in range(args.rows)],
        }
    )
    window.file_data = frame
    window.column_count = 3
    window.update_column_combos()
    for field, col in (("title", 0), ("author", 1), ("year", 2)):
        window.field_mappings[field].setCurrentIndex(col + 1)
    window.collection_combo.setCurrentIndex(0)

    t0 = time.perf_counter()
    success, errors, duplicates, skipped = window.import_new_books()
    elapsed = time.perf_counter() - t0

    print(
        f"rows={args.rows} success={success} errors={errors} "
        f"duplicates={duplicates} skipped={skipped} elapsed={elapsed:.3f}s "
        f"({args.rows / elapsed:.0f} rows/s)"
    )
    db.close()
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
