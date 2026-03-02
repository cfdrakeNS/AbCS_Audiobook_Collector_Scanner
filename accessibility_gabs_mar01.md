# Accessibility Gaps Review — Mar 01, 2026

Source reviewed: `Accessibility_best-practice_ rules (PySide6).md`

## Scope and interpretation

I audited the codebase against the 6 items in the source doc as:
1. Never rely on visuals alone
2. Everything reachable by keyboard
3. Accessible names/descriptions are required
4. Status updates must be announced (not status bar only)
5. Errors should move focus (or use modal)
6. NVDA should be part of validation/testing practice

---

## Rule-by-rule findings

### 1) Never rely on visuals alone
**Status:** Mostly following, with targeted gaps.

**Evidence of compliance**
- Widespread use of text labels and read-only text widgets for status/content display across windows.
- Example: `src/ui/import_progress_window.py` includes explicit labels and text values for title/author/counters.

**Gap**
- In `src/ui/import_progress_window.py` the key read-only information fields are set to `Qt.NoFocus` (e.g., title/author/issues/counters). That limits keyboard/screen-reader reachability of important text and weakens non-visual access.
### ?update? those fields I beleive are hidden and thus should be removed ? 
---

### 2) Everything must be reachable by keyboard
**Status:** Mostly following, with a concrete partial gap.

**Evidence of compliance**
- Strong Alt+letter and function-key support across windows (`src/accessibility/shortcuts.py`, plus per-window shortcut wiring).
- Frequent `Qt.StrongFocus` and tab-focus management in window code.

**Gap**
- `src/ui/import_progress_window.py` presents accessible descriptions that imply Alt navigation for data fields (e.g., `Alt+F`, `Alt+M`, `Alt+B`, `Alt+R`) but those buddy targets are `Qt.NoFocus`, so keyboard users cannot consistently land on/read those controls directly.
### ?update? did this on purpose to allow alt+/ to work otherwide the controls were grabbing focus 
---

### 3) Accessible names/descriptions are NOT optional
**Status:** Partially following (majority good, specific violations exist).

**Evidence of compliance**
- High volume of `setAccessibleName()`/`setAccessibleDescription()` usage across UI modules.

**Gaps (explicit violations)**
- `src/ui/main_window.py` sets empty accessible metadata in multiple dialogs/tables:
  - `dlg.setAccessibleName("")` and `dlg.setAccessibleDescription("")` in splash/help dialogs.
  - `table.setAccessibleName("")` and `table.setAccessibleDescription("")` in those dialogs.
- These are direct misses against Rule 3 because they intentionally remove discoverable semantics for screen readers.
### ?update? correct 
---

### 4) Status updates must be announced (not status bar only)
**Status:** Partially following.

**Evidence of compliance**
- `src/accessibility/accessible_events.py` provides `announce_status_message(...)` and several windows use it (`import_window.py`, `import_progress_window.py`, `name_list_window.py`, `preferences_window.py`, `collection_window.py`).

**Gaps**
- The hidden-label announcement path in `announce_status_message(...)` is currently disabled/commented out, so the mirror channel is not active.
- Some major windows still use direct `status_bar.showMessage(...)` + focus trick instead of centralized mirroring (notably `main_window.py`, `book_details.py`, `update_window.py`).
- Net effect: announcement behavior is inconsistent across windows and still depends heavily on temporary focus movement.
### ?update? more details as I'd like to review where the gaps occur by testing with jaws add a test for these test include win name field name and what to look for 
---

### 5) Errors should move focus (or use modal)
**Status:** Largely following.

**Evidence of compliance**
- Broad use of modal styled message boxes for warnings/errors (`exec_styled_message_box(...)` across UI).
- In form validation flows, focus is often moved to the offending field after validation errors (example: `src/ui/book_details.py` for required title/author).

**Gap**
- No major systemic violation found in sampled paths; this rule appears implemented consistently enough for current scope.

---

### 6) Test with NVDA (even if JAWS is primary)
**Status:** Partially following.

**Evidence of compliance**
- Documentation references NVDA support/testing (e.g., `README.md`, `INSTALL.md`, and accessibility notes).

**Gap**
- I did not find NVDA-specific validation automation or a repeatable test artifact under `test/` for ongoing regression checks.
- Current coverage appears mostly documentation/process guidance rather than enforceable test practice.
### ?update? I have been mainly using jaws but do run nvda which generally seems to read the app. most issue are jaws.
---

## Summary

Overall result: **Mostly compliant with meaningful partial gaps**.

Highest-priority fixes:
1. Replace empty accessible names/descriptions in `src/ui/main_window.py` dialogs/tables.
2. Make key read-only info fields in `src/ui/import_progress_window.py` keyboard-focusable (or convert to reliably announced `QLabel`/focusable read-only pattern).
3. Standardize all windows on one status-announcement path and re-enable a safe non-visual mirror mechanism (instead of mixed per-window behavior).
4. Add a lightweight NVDA regression checklist/script to `test/` or a dedicated accessibility test harness runbook.
### ?update? review each by testing then code change if required test include win name field name and what to look for 