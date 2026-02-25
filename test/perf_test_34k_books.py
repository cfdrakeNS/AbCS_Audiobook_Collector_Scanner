#!/usr/bin/env python
"""
Performance test: Measure sort order change speed on 34k-book database.
Run this after starting the app to capture before/after metrics.
"""

import sqlite3
import time
import json
from pathlib import Path

DB_PATH = Path("data/abcs.db")


def time_sort_order(order_by_clause):
    """Measure how long a sort order query takes."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # This mirrors the BookQueries.get_all() pattern from src/database/queries.py
    queries = {
        "Title": """
            SELECT b.book_id, b.title, a.name as author_name
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.author_id
            ORDER BY b.title
        """,
        "Author": """
            SELECT b.book_id, b.title, a.name as author_name
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.author_id
            ORDER BY a.name, b.year, b.title
        """,
        "Genre": """
            SELECT b.book_id, b.title, g.name as genre_name
            FROM books b
            LEFT JOIN genres g ON b.genre_id = g.genre_id
            ORDER BY g.name IS NULL, g.name, b.title
        """,
        "Series": """
            SELECT b.book_id, b.title, s.name as series_name
            FROM books b
            LEFT JOIN series s ON b.series_id = s.series_id
            ORDER BY s.name IS NULL, s.name, b.year, b.title
        """,
    }

    start = time.perf_counter()
    cursor.execute(queries[order_by_clause])
    rows = cursor.fetchall()
    elapsed = time.perf_counter() - start

    conn.close()

    return elapsed, len(rows)


def run_performance_test(repeats=3):
    """Run sort performance test and record results."""

    print("=" * 60)
    print("34K-BOOK DATABASE PERFORMANCE TEST")
    print("=" * 60)

    # Check database is loaded
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM books")
    book_count = cursor.fetchone()[0]
    conn.close()

    print(f"\nDatabase: {book_count:,} books\n")

    results = {}

    for order_name in ["Title", "Author", "Genre", "Series"]:
        print(f"Testing {order_name} sort...")
        times = []

        for run in range(repeats):
            elapsed, rows = time_sort_order(order_name)
            times.append(elapsed)
            print(f"  Run {run+1}: {elapsed:.4f}s ({rows:,} rows)")

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        results[order_name] = {
            "runs": repeats,
            "avg_seconds": round(avg_time, 4),
            "min_seconds": round(min_time, 4),
            "max_seconds": round(max_time, 4),
            "rows": rows,
        }

        print(f"  Average: {avg_time:.4f}s")
        if avg_time > 1.0:
            print(f"  ⚠️  WARNING: Sort took > 1 second!")
        elif avg_time > 0.1:
            print(f"  ✓ Acceptable (< 0.1s ideal, < 1s acceptable)")
        else:
            print(f"  ✓ Excellent!")
        print()

    # Save results
    output_file = Path("perf_results_34k_books.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✓ Results saved to: {output_file}")

    return results


if __name__ == "__main__":
    results = run_performance_test(repeats=3)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for order, metrics in results.items():
        status = "✓" if metrics["avg_seconds"] < 1.0 else "✗"
        print(f"{status} {order:10} avg={metrics['avg_seconds']:.4f}s")
