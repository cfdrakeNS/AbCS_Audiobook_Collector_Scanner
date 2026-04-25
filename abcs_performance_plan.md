# AbCS Performance Implementation Plan

This document outlines the phased approach to optimizing AbCS for large libraries (30,000+ records) based on `abcs_performance_tuning.md`.

---

## Phase 0: Benchmarking (Complete)
*Status: Baseline Established with 34,679 records*

### Baseline Results:
*   **Library Load (34.7k):** ~0.58s - 0.63s
*   **SQL Sort:** ~0.62s
*   **Search (Filter):** ~0.55s
*   **Import (Scan):** ~0.56s
*   **Folder Import (Add):** **9.14s for 6 books** (Fuzzy Duplicate check identified as the bottleneck).
*   **Book List Import (XLS):** **CRASHED** (Currently unmeasured due to application hang; suspected bottleneck in Excel parsing or Fuzzy Duplicate matching).

---

## Phase 1: Virtualization & Threading (Deprioritized)

## Module 1: Main Library View (`src/ui/main_window.py`)
*Priority: Critical*

### Changes:
1.  **Lightweight Data:** Modify `BookTableModel` to use a list of tuples/dictionaries instead of full `Book` dataclasses to reduce object overhead.
2.  **Pagination/Chunking:** Update `BookQueries.get_all` to support `LIMIT`/`OFFSET` or `fetchmany` so we don't load 35k records into RAM at once.
3.  **Sorting:** Move sorting logic to the SQL query level (ORDER BY) or use `QSortFilterProxyModel` to avoid GUI-thread stutter.
4.  **Repaint Control:** Wrap the initial library load in `setUpdatesEnabled(False/True)` blocks.

### Testing Strategy:
*   Verify JAWS can still navigate rows/columns via arrow keys.
*   Measure "Time to Open" with a mock database of 30,000 rows.

---

## Module 2: Import System (`src/ui/import_window.py`)
*Priority: High*

### Changes:
1.  **Background Scanning:** Move the file system crawler and ID3 tag extractor into a `QThread`.
2.  **Pre-Sizing:** Calculate the number of files found before populating the results table and use `setRowCount(total)`.
3.  **Batch Updates:** Implement a timer-based UI update (e.g., refresh the table every 100 books found) rather than updating for every single file.
4.  **Sorting:** Explicitly call `setSortingEnabled(False)` before starting a scan and `True` only after the scan completes.

### Testing Strategy:
*   Ensure the "Cancel" button remains responsive during a large folder scan.
*   Confirm the Status Bar announces "Scan Complete" via `Alt+/`.

---

## Module 3: Reading History (`src/ui/history_window.py`)
*Priority: Medium*

### Changes:
1.  **Clean Slate:** Replace row-by-row deletion with `table.setRowCount(0)` when changing date filters.
2.  **Layout Fixes:** Review the layout generation for the history list. If `layout.addStretch()` is used within loops that generate many rows, replace it with fixed spacers (`QSpacerItem`) or ensure that row heights are explicitly set or managed by a simpler layout (e.g., `QFormLayout` or `QGridLayout` with fixed row sizes) to reduce layout calculation overhead.

### Testing Strategy:
*   Toggle between "3 Months" and "All Time" views; verify instantaneous refresh.
 *   Ensure the layout remains stable and visually correct after changes.

### Risks:
*   **Minor UI Adjustments:** Changes to layout might require minor visual tweaks to maintain the desired appearance.
*   **Limited Impact:** The performance gain here is likely less significant than for the main view or import, as history lists are typically smaller.

### Justification:
*   **Smooth Transitions:** Ensures that changing filters or refreshing the history list is instantaneous, providing a fluid user experience.
*   **Code Cleanliness:** Simplifies layout logic and reduces potential for layout-related performance issues.

---

## Module 4: Database Manager (`src/database/db_manager.py`)
*Priority: Medium*

### Changes:
1.  **Indexed Queries:** Verify that appropriate indexes exist on the `books` table for frequently queried columns such as `Title`, `Author_id`, `Series_id`, `Genre_id`, and `Collection_id`. Add any missing indexes to speed up `SELECT` operations, especially those used by the `QAbstractTableModel` for filtering and sorting.
2.  **Fetch Optimization:** Modify `BookQueries` methods that retrieve large datasets to use `cursor.fetchmany(N)` (e.g., `N=1000`) instead of `cursor.fetchall()`. This allows the `QAbstractTableModel` to request data in chunks, reducing peak memory usage and potentially improving responsiveness for initial data loads.
3.  **Database Connection Optimization:** Consider setting `PRAGMA journal_mode=WAL` for the SQLite connection. This can improve write performance and concurrency, which might be beneficial during import operations.

### Testing Strategy:
*   Run `EXPLAIN QUERY PLAN` on the search and sort queries.
 *   Measure memory usage during large data loads.
 *   Verify that database operations (inserts, updates, reads) remain correct and do not introduce new issues.

### Risks:
*   **Index Overhead:** Adding too many indexes can slightly increase the size of the database file and slow down `INSERT`, `UPDATE`, and `DELETE` operations. A balance must be struck.
*   **`fetchmany` Integration:** Integrating `fetchmany` with the `QAbstractTableModel` requires careful state management within the model to handle pagination.

### Justification:
*   **Backend Support:** Provides the necessary database performance to support the front-end UI optimizations, especially the virtual model.
*   **Efficiency:** Reduces query times and memory consumption, contributing to overall application responsiveness.

---

## Summary of Gains
| Feature | Current State | Target State |
| :--- | :--- | :--- |
| **30k Library Load** | 5-10 Seconds (Stuttering) | < 1 Second (Instant) |
| **RAM Usage** | High (Object Overhead) | Low (Data-only) |
| **JAWS Response** | "Not Responding" during load | Continuous Speech |