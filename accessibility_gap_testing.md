# Accessibility Gap TODO — Test-First Action Plan (Mar 01, 2026)

Source context:
- `accessibility_gabs_mar01.md` (including `?update?` notes)
- `Accessibility_best-practice_ rules (PySide6).md`

## Goal
Validate each reported gap with real screen-reader testing (JAWS-first, NVDA sanity check), then make code changes only where tests confirm a real issue.

---

## Test protocol (use for every item)

1. Start JAWS first, then launch AbCS.
2. Reproduce exact flow using keyboard only.
3. Capture: window name, control/field name, spoken announcement, focus behavior, pass/fail.
4. Repeat quickly in NVDA as a comparison baseline.
5. If failure is reproducible, mark as `Code change required`.

Recommended result columns for notes:
- Gap ID
- Window
- Field/Control
- Steps
- Expected
- Actual (JAWS)
- Actual (NVDA)
- Pass/Fail
- Code change required (Y/N)

Decision legend (use in each Findings block):
- `Confirmed defect` = Accessibility break reproduced; code change needed.
- `Intentional design (noise reduction)` = Behavior is deliberate to reduce screen-reader noise/focus churn; no code change.
- `Needs design decision` = Tradeoff unclear (noise reduction vs discoverability); review before coding.

## Implementation snapshot — combo anti-noise rule (Mar 01, 2026)

- **Applied (enforced):**
  - `src/ui/book_details.py`
  - `src/ui/update_window.py`
  - `src/ui/preferences_window.py`
  - `src/ui/import_detail_window.py` (for `Author`, `Series`, `Genre` combos)
- **Intentionally left as-is:**
  - `src/ui/main_window.py`
  - `src/ui/import_window.py`

---

## GAP-01 — Import Progress read-only fields: hidden/non-focus concern

From your update: these may be intentionally hidden and removable.

### Test 01A — Hidden `Issues` row behavior
- **Window:** `ImportProgressWindow`
- **Field/Control:** `issues_label`, `issues_edit`
- **Steps:** Start import scan, watch for entries that should show issues; navigate window with Tab and Alt shortcuts.
- **Expected:** If intentionally hidden, controls should not be required for user workflow and no dead/ghost navigation should occur.
- **Look for:**
  - Does JAWS ever announce an inaccessible hidden element?
  - Does user miss important issue info because it is never announced elsewhere?
- **Decision rule:**
  - If issue details are unavailable to screen reader users when relevant → keep as gap.
  - If details are surfaced elsewhere reliably and hidden controls are unnecessary → remove this gap.

**Findings (fill in):**
- JAWS actual:
- NVDA actual:
- Pass/Fail:
- Decision:
- Follow-up:

### Test 01B — Read-only counters visibility/announcement
- **Window:** `ImportProgressWindow`
- **Field/Control:** `files_edit`, `elapsed_edit`, `added_edit`, `read_errors_edit`
- **Steps:** Run scan and trigger multiple progress updates.
- **Expected:** Current values should be available through status announcement path (`Alt+/`) even if fields are non-focusable by design.
- **Look for:**
  - Can user retrieve current progress at any time via keyboard?
  - Are updates understandable without moving to these fields?
- **Decision rule:**
  - If Alt+/ provides complete, timely progress info → design may be acceptable.
  - If not, add alternate accessible surface (focusable read-only or dedicated announce channel).

**Findings (fill in):**
- JAWS actual:
- NVDA actual:
- Pass/Fail:
- Decision:
- Follow-up:

### Test 02C — Import Detail combo anti-noise behavior
- **Window:** `ImportDetailWindow`
- **Field/Control:** `author_combo`, `series_combo`, `genre_combo`
- **Steps:**
  1. Open Import Detail and focus each combo.
  2. Press plain `Up`/`Down`.
  3. Press `Alt+Down` (open list), then `Alt+Up`/`Alt+Down` to navigate.
- **Expected:**
  - Plain `Up`/`Down` is blocked (audible beep) and does not silently change values.
  - `Alt+Up`/`Alt+Down` is allowed for explicit combo navigation.
- **Look for:**
  - Silent value changes on plain arrows (should not happen).
  - Focus loss or unstable announcement while navigating combos.

**Findings (fill in):**
- JAWS actual:
- NVDA actual:
- Pass/Fail:
- Decision:
- Follow-up:

---

## GAP-02 — Keyboard reachability vs intentional `Qt.NoFocus`

From your update: `Qt.NoFocus` was intentional to prevent controls stealing focus from `Alt+/` flow.

### Test 02A — `Alt+/` reliability under load
- **Window:** `ImportProgressWindow`
- **Field/Control:** Status bar announcement path (`Alt+/`)
- **Steps:** During rapid scanning updates, press `Alt+/` repeatedly.
- **Expected:** JAWS consistently reads latest status without focus traps.
- **Look for:**
  - Missed or stale announcements
  - Focus jumping unexpectedly
  - Need to Tab through non-actionable fields

**Findings (fill in):**
- JAWS actual:
- NVDA actual:
- Pass/Fail:
- Decision:
- Follow-up:

### Test 02B — Buddy label shortcuts reality check
- **Window:** `ImportProgressWindow`
- **Field/Control:** Labels implying Alt navigation (`&Files scanned`, `Elapsed ti&me`, `&Books added`, `Read e&rrors`)
- **Steps:** Press implied Alt keys and verify target behavior.
- **Expected:** Either shortcut behavior works as implied, or labels/descriptions are corrected so they do not promise non-working keyboard targets.
- **Look for:**
  - Mismatch between spoken/documented shortcut and actual focus behavior.
- **Decision rule:**
  - If shortcuts do not function due to `NoFocus`, treat as wording/UX defect at minimum.

**Findings (fill in):**
- JAWS actual:
- NVDA actual:
- Pass/Fail:
- Decision:
- Follow-up:

---

## GAP-03 — Empty accessible names/descriptions in Main Window dialogs

(You marked this as correct.)

### Test 03A — Library Statistics dialog metadata
- **Window:** `MainWindow` → `Library Statistics` dialog (`on_show_splash` path)
- **Field/Control:** Dialog and table accessible metadata
- **Steps:** Open dialog by keyboard; use JAWS element navigation.
- **Expected:** Dialog/table should have meaningful accessible name/description.
- **Look for:**
  - JAWS announcing generic/blank container names
  - Extra effort needed to determine context

**Findings (fill in):**
- JAWS actual:
- NVDA actual:
- Pass/Fail:
- Decision:
- Follow-up:

### Test 03B — Keyboard Shortcuts dialog metadata
- **Window:** `MainWindow` → `Keyboard Shortcuts` dialog
- **Field/Control:** Dialog and shortcuts table metadata
- **Steps:** Open shortcuts dialog (F1/help path), navigate headings/table.
- **Expected:** Clear spoken context for dialog and table purpose.
- **Look for:**
  - Blank or missing object context in JAWS.
- **Decision rule:**
  - Any blank metadata reproduction = confirmed code fix needed.

**Findings (fill in):**
- JAWS actual:
- NVDA actual:
- Pass/Fail:
- Decision:
- Follow-up:

---

## GAP-04 — Status announcement inconsistency across windows

From your update: you want exact test points by window/field and what to check.

### Test 04A — MainWindow status updates
- **Window:** `MainWindow`
- **Field/Control:** `status_bar` (direct `showMessage` + focus trick)
- **Steps:** Trigger events that call `set_status` (search/select/delete-mode changes).
- **Expected:** JAWS reads updates once, promptly, with focus returning correctly.
- **Look for:**
  - Duplicate announcements
  - Lost focus after message
  - Silent status changes

**Findings (fill in):**
- JAWS actual:
- NVDA actual:
- Pass/Fail:
- Decision:
- Follow-up:

### Test 04B — BookDetails status updates
- **Window:** `BookDetailsWindow`
- **Field/Control:** `status_bar` status path
- **Steps:** Save/cancel/validation actions that post status.
- **Expected:** Reliable announcement and correct focus restoration.
- **Look for:** focus steal or missed status.

**Findings (fill in):**
- JAWS actual:
- NVDA actual:
- Pass/Fail:
- Decision:
- Follow-up:

### Test 04C — UpdateWindow status updates
- **Window:** `UpdateWindow`
- **Field/Control:** `status_bar` status path
- **Steps:** Change series/genre/collection, trigger status feedback.
- **Expected:** Consistent with Main/BookDetails behavior.
- **Look for:** differences in timing/announcement quality.

**Findings (fill in):**
- JAWS actual:
- NVDA actual:
- Pass/Fail:
- Decision:
- Follow-up:

### Test 04D — Windows using `announce_status_message(...)`
- **Window(s):** `ImportWindow`, `ImportProgressWindow`, `NameListWindow`, `PreferencesWindow`, `CollectionWindow`
- **Field/Control:** status announcement helper path
- **Steps:** Trigger at least 2 status events per window.
- **Expected:** Same user experience as other windows.
- **Look for:** helper-path vs direct-path inconsistencies.

**Findings (fill in):**
- JAWS actual:
- NVDA actual:
- Pass/Fail:
- Decision:
- Follow-up:

### Consolidated decision for GAP-04
- If behavior differs noticeably by window, standardize on one announcement strategy.
- If helper’s hidden-label mirror remains disabled, document why and define a safe replacement strategy.

---

## GAP-05 — Error handling focus behavior (verify no regressions)

This was rated mostly compliant; keep as regression check.

### Test 05A — Required field errors in Book Details
- **Window:** `BookDetailsWindow`
- **Field/Control:** `title_edit`, `author_combo`
- **Steps:** Clear required fields and press save.
- **Expected:** Modal error appears; focus moves to the invalid field after dismissing message.
- **Look for:** background-only errors or focus not returning to offending field.

**Findings (fill in):**
- JAWS actual:
- NVDA actual:
- Pass/Fail:
- Decision:
- Follow-up:

### Test 05B — Import/Update validation prompts
- **Window(s):** `ImportWindow`, `UpdateWindow`
- **Field/Control:** validation dialogs and follow-up focus target
- **Steps:** Trigger known validation warnings.
- **Expected:** Modal + predictable focus target.
- **Look for:** silent failures or focus landing unpredictably.

**Findings (fill in):**
- JAWS actual:
- NVDA actual:
- Pass/Fail:
- Decision:
- Follow-up:

---

## GAP-06 — NVDA repeatable regression practice

From your update: NVDA generally reads app, JAWS has most issues.

### Test 06A — Define compact cross-reader smoke suite
- **Window set:** `MainWindow`, `BookDetailsWindow`, `ImportWindow`, `ImportProgressWindow`, `UpdateWindow`
- **Field/Control set:** search box, main table, status bar (`Alt+/`), one modal validation error per window.
- **Steps:** Run same script in JAWS and NVDA.
- **Expected:** Major interaction parity; JAWS-specific issues explicitly logged.
- **Look for:** reader-specific divergences and reproducibility.

**Findings (fill in):**
- JAWS actual:
- NVDA actual:
- Pass/Fail:
- Decision:
- Follow-up:

### Test 06B — Add repeatable artifact under `test/`
- **Deliverable:** markdown checklist or scripted harness instructions (manual + expected speech outcomes).
- **Expected:** Future runs can compare outcomes, not memory.

**Findings (fill in):**
- JAWS actual:
- NVDA actual:
- Pass/Fail:
- Decision:
- Follow-up:

---

## Prioritized execution order

1. GAP-03 (empty accessible metadata) — fastest confirm/fix.
2. GAP-04 (status consistency) — highest user impact for JAWS.
3. GAP-02 + GAP-01 (Import Progress focus model) — validate your intentional design before changing code.
4. GAP-05 regression checks.
5. GAP-06 repeatable NVDA/JAWS smoke artifact.

---

## Exit criteria

- Every gap has a completed test record with Window + Field + Expected + Actual.
- Each gap is marked one of:
  - `Confirmed defect`
  - `Intentional design (no change)`
  - `Needs design decision`
- Confirmed defects have linked code-change tasks and retest results.
