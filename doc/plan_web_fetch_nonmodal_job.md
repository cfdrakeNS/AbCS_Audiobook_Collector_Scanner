# Non-Modal Web Fetch Jobs — Version 3 Phase 5

**Status:** Not started — next after Phases 1–4. Larger change; do not fold into selection or batch-summary polish.  
**Created:** September 2026  
**Related:** [plan_web_fetch_background_thread.md](plan_web_fetch_background_thread.md), [plan_bulk_web_metadata.md](plan_bulk_web_metadata.md), [plan_enhancements_version3_release.md](plan_enhancements_version3_release.md)

---

## What this is

Calibre-style: **keep using AbCS** while web fetch runs. Unlike Calibre’s NoFocus overlay, the job is a **real window** (Alt+Tab) and **Alt+J** raises it. When the job finishes, AbCS **takes focus back** (`raise_` / `activateWindow`) so JAWS hears the result.

Phase 1 put HTTP on a `QThread` but still **blocks** the main window with `popup.exec()`. This phase removes that block for Alt+W (one book or a batch). There is no main-window Alt+B.

Depends on Phase 1/2. Does not change Path B matching or selection-mode toolbar rules.

---

## Behavior

- Progress windows use `show()`, not `exec()`. Independent window (`parent=None` / `Qt.Window`). Escape cancels. No Cancel button.
- Main window stays usable (list, Find, filters, Book Details).
- **One job at a time.** A second Alt+W announces that a fetch is in progress and **Alt+J to return**; it does not start another thread.
- **Alt+J** on main (and Book Details) raises the progress window and announces current status.
- When finished: close progress; raise the same review / no-match / up-to-date UI as today (single book) or the **modal** batch summary (Apply all / Review / Escape), focus on the first list row. Steal focus even if the user is in another AbCS window.

**Out of scope:** OS process / multiprocessing; parallel books; Calibre NoFocus overlay; matching or plot-rule changes.

---

## Implementation

- Own the job on `MainWindow` (or a small `WebFetchJobController`): start worker, keep the progress widget, `finished` signal runs existing post-fetch paths in `on_get_web_info_clicked` and Book Details. Stop returning `WebFetchResult` through blocking `exec()`.
- Batch: `run_batch_web_fetch_with_progress` becomes start-and-callback; do not `exec()` progress.
- Files: [`src/web/web_fetch_service.py`](../src/web/web_fetch_service.py), [`src/web/batch_web_fetch.py`](../src/web/batch_web_fetch.py), [`src/ui/web_fetch_progress.py`](../src/ui/web_fetch_progress.py), [`src/ui/batch_web_fetch_progress.py`](../src/ui/batch_web_fetch_progress.py), [`src/ui/main_window.py`](../src/ui/main_window.py), Book Details, [`src/accessibility/shortcuts.py`](../src/accessibility/shortcuts.py).

---

## JAWS spike (before production)

1. Start fetch, use the book list (arrows, Find).
2. Alt+J returns to progress; progress spoken.
3. Escape cancels; focus back to main.
4. Let a job finish while focus is on the list; summary/review is announced in front.

---

## Tester gate

1. Alt+W (one book or a batch): can use the main list while progress is open.
2. Alt+J returns to the job.
3. One job only; second fetch announces, does not stack.
4. Finish raises review or batch summary; first summary row focused.
5. Escape on progress cancels; no Cancel button.

---

## Tests and help

Worker finish without blocking `exec()`; second start refused; finish opens summary. F1 / [help_docs/07_web_metadata.md](../help_docs/07_web_metadata.md) / [help_docs/16_shortcuts.md](../help_docs/16_shortcuts.md): Alt+J and keep-using-app.

Accessibility: [Accessibility and UI formatting standards](plan_enhancements_version3_release.md#accessibility-and-ui-formatting-standards-all-phases). Never use Calibre’s non-modal NoFocus overlay for anything the user must answer (batch summary stays modal).
