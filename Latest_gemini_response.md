### Factual Summary: Performance Plan & Protocol Adherence
* **Protocol:** I will strictly use this file for all technical explanations and code details to ensure JAWS can read the full context without truncation or lag.
* **Performance Confirmation:** Setting fuzzy matching to 0 has resolved the primary application hang for 31k records.
* **Next Immediate Step:** Implement "Signal Blocking" in `import_window.py`. This involves calling `setSortingEnabled(False)` and `setUpdatesEnabled(False)` before the 31,000-row loop to prevent UI stutter.
* **Implementation Scope:** 4 Modules (`main_window.py`, `import_window.py`, `history_window.py`, `db_manager.py`).
* **Estimated Effort:** ~15 hours total.
* **Primary Goal:** Transition from `QTableWidget` to `QTableView` (Virtualization) to make navigation for 31,000 rows instantaneous for screen readers.
* **Current State:** Phase 0 (Benchmarking) is complete. Phase 2 (Import System) optimizations are ready for implementation.