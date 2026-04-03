# Code Review - April 3, 2026

## Scope
Reviewed the active application code in `src/` against:
- `accessibility_app_patterns.md`
- `Accessibility_best-practice_ rules (PySide6).md`
- `Accessibility_Screen_Reader_and_PySide6_best_practices.md`

Focus areas requested:
1. Standards noncompliance
2. Orphan shortcuts
3. Undocumented unique accessibility patterns
4. Redundant/unused/duplicated code

---

## Findings (ordered by severity)

### 1. Critical: `IMPORT_PROGRESS_WINDOW` context is defined but never handled by `ShortcutManager`
- Evidence:
  - `src/accessibility/shortcuts.py:17` defines `IMPORT_PROGRESS_WINDOW`.
  - `src/ui/import_progress_window.py:152-153` calls `register_alt_shortcuts(..., ShortcutContext.IMPORT_PROGRESS_WINDOW, ...)`.
  - `src/accessibility/shortcuts.py:199-221` has context branches, but no branch for `IMPORT_PROGRESS_WINDOW`.
- Impact:
  - Centralized Alt+ mappings for this context are silently skipped. This is a hidden failure mode and creates false confidence.
- Recommendation:
  - Add explicit `IMPORT_PROGRESS_WINDOW_SHORTCUTS` support branch in `register_alt_shortcuts`, or remove the call/context if intentionally local-only.

### 2. High: Orphan shortcuts in `ImportWindow` due callback key mismatch
- Evidence:
  - Central map expects `import_all_valid_button` and `export_csv_button`:
    - `src/accessibility/shortcuts.py:127`
    - `src/accessibility/shortcuts.py:129`
  - Window callback map provides `add_valid_button` and `export_button`:
    - `src/ui/import_window.py:109`
    - `src/ui/import_window.py:111`
- Impact:
  - `Alt+V` and `Alt+X` from centralized definitions do not bind.
- Recommendation:
  - Rename callback-map keys to match centralized IDs, or align centralized IDs with real widget IDs.

### 3. High: Orphan shortcut in `BookDetailsWindow` (`Alt+E` for read date)
- Evidence:
  - Central map defines read date shortcut: `src/accessibility/shortcuts.py:90`.
  - `BookDetailsWindow` callback map starts at `src/ui/book_details.py:788` and does not include `read_date`.
- Impact:
  - `Alt+E` advertised by central definitions is not registered in this window.
- Recommendation:
  - Add `'read_date': lambda: self.read_date.setFocus()` to callback map.

### 4. High: `WebMetadataWindow` shortcut map mismatch and help mismatch
- Evidence:
  - Central map defines `publisher_edit`, `source_edit`, `fetch_web_button`:
    - `src/accessibility/shortcuts.py:111`
    - `src/accessibility/shortcuts.py:112`
    - `src/accessibility/shortcuts.py:113`
  - Window callback map does not provide those keys; it includes `series_number_edit`, `read_status_bar`, `close_window`:
    - `src/ui/web_metadata.py:798`
    - `src/ui/web_metadata.py:803`
    - `src/ui/web_metadata.py:804`
  - Help advertises `Alt+N` for series number: `src/ui/web_metadata.py:842`, but centralized map has no `N` entry for web metadata.
- Impact:
  - Some documented/expected shortcuts are unbound, and help text can disagree with behavior.
- Recommendation:
  - Choose one source of truth and align all three layers: centralized definitions, callback_map keys, and F1 help text.

### 5. Medium: Standards/documentation conflict for local-vs-central shortcut ownership
- Evidence:
  - Standard says local-only for `F1`, `Escape`, `Alt+/`: `accessibility_app_patterns.md:245`.
  - Standard also says centralized for Alt+field keys: `accessibility_app_patterns.md:246`.
  - `WebMetadataWindow` registers status/help/close via centralized callback keys (`read_status_bar`, `close_window`, `show_help`) in `src/ui/web_metadata.py:803-807`.
- Impact:
  - Inconsistent shortcut architecture increases regression risk and makes troubleshooting harder.
- Recommendation:
  - Enforce one policy consistently: keep `F1`, `Escape`, `Alt+/` local in every window, and reserve central manager for field/action shortcuts.

### 6. Medium: Buttons disabled despite documented screen-reader guidance to keep them enabled
- Evidence:
  - Rule states keep buttons enabled with explanatory feedback: `Accessibility_best-practice_ rules (PySide6).md:127`.
  - Disabled buttons found:
    - `src/ui/book_list_import_window.py:535`
    - `src/ui/book_list_import_window.py:543`
    - `src/ui/import_detail_window.py:423`
    - `src/ui/import_detail_window.py:974`
    - `src/ui/import_window.py:424`
    - `src/ui/import_window.py:1209`
    - `src/ui/import_window.py:1601`
- Impact:
  - Reduced discoverability for screen-reader users and less actionable feedback.
- Recommendation:
  - Keep action buttons enabled and return clear status/dialog guidance when prerequisites are missing.

### 7. Medium: Return/Enter QShortcut anti-pattern present in read-date dialog flow
- Evidence:
  - Rule warns against global Return/Enter shortcuts in button windows: `Accessibility_best-practice_ rules (PySide6).md:154`.
  - `src/ui/main_window.py:263` and `src/ui/main_window.py:265` create Return/Enter shortcuts in the dialog.
- Impact:
  - Can override default Enter behavior and create inconsistent activation semantics.
- Recommendation:
  - Prefer widget-specific `keyPressEvent` logic and default button activation behavior.

### 8. Medium: Skeleton reference path drift (resolved)
- Evidence:
  - Earlier docs referenced `src/ui/accessible_window_skeleton.py`.
  - Canonical sample/skeleton reference files are in `accessible_sample/` (`accessible_sample/main.py`, `accessible_sample/accessibility_patterns.py`, `accessible_sample/README.md`).
- Impact:
  - If docs are not aligned, onboarding can point to the wrong path.
- Resolution:
  - Updated docs to reference the `accessible_sample/` location as the canonical sample implementation.

---

## Orphan Shortcut Inventory

### Confirmed orphan/misaligned mappings
1. `IMPORT_PROGRESS_WINDOW` context not handled in `ShortcutManager` (silent no-op registration)
2. `ImportWindow`
   - Central expects `import_all_valid_button`, callback provides `add_valid_button`
   - Central expects `export_csv_button`, callback provides `export_button`
3. `BookDetailsWindow`
   - Central expects `read_date`, callback map omits it
4. `WebMetadataWindow`
   - Central expects `publisher_edit`, `source_edit`, `fetch_web_button`
   - Callback map provides different keys (`series_number_edit`, etc.)
   - F1 help advertises `Alt+N` but central map has no corresponding key

### Potential duplicate binding risk
- `CollectionWindow` registers list focus both centrally (`'table': self.focus_list`) and locally (`Alt+L` `QShortcut`):
  - `src/ui/collection_window.py:194`
  - `src/ui/collection_window.py:209`

---

## Undocumented Unique Accessibility Patterns Found in Code

These are meaningful patterns in active code not clearly captured in the three standards docs:

1. Runtime duplicate-shortcut conflict scanner
- `src/accessibility/shortcuts.py:371` (`find_shortcut_conflicts`)
- Invoked during app startup checks in `src/main.py:310` and `src/main.py:385`
- Why important: proactive detection of mnemonic and shortcut collisions.

2. Hidden status-hint label injected into status bar for selection command discoverability
- `src/ui/main_window.py:463-470`, updated in `src/ui/main_window.py:2595-2596`
- Why important: gives stable, screen-reader-friendly discoverability of selection-mode shortcuts.

3. Broad hover-noise suppression pattern in tables and popup lists
- Appears in multiple windows via `setMouseTracking(False)` and hover disabling (for low-vision comfort).
- Why important: reduces visual and announcement noise, but currently under-documented as a reusable pattern.

---

## Redundant, Unused, or Duplicated Code

1. Duplicate method definition in `update_window.py`
- `def setup_shortcuts(self):` appears twice:
  - `src/ui/update_window.py:20`
  - `src/ui/update_window.py:703`
- The top-level function is redundant/dead relative to class method behavior.

2. Duplicate imports in `book_details.py`
- Same imports repeated:
  - `src/ui/book_details.py:7` and `src/ui/book_details.py:27`
  - `src/ui/book_details.py:11` and `src/ui/book_details.py:29`
  - `src/ui/book_details.py:12` and `src/ui/book_details.py:30`

3. Duplicate SQL schema files (exact content duplicate)
- `data/abcs.sql`
- `data/abcdDB_def.sql`
- Verification: identical SHA-256 hash `037E9A1E7E88D31A2F61156661F61ABBBA9239D2598EA66E59CFC0DCE0798772`

4. Context/help coverage drift in `ShortcutManager`
- `register_alt_shortcuts` supports more contexts than `get_shortcut_help`, which only handles a subset (`MAIN_WINDOW`, `BOOK_DETAILS`, `WEB_METADATA`, `IMPORT_WINDOW`, `UPDATE_WINDOW`).
- Result: maintainability and consistency risk for F1/help generation.

---

## Overall Assessment
The project has strong accessibility intent and many robust implementations, but shortcut architecture drift is now the biggest reliability risk. The highest-value stabilization pass is to reconcile centralized shortcut IDs with each window callback map, then align help text with actual bindings.

---

## Window-by-Window Change List (single-touch implementation plan)

Goal: apply all fixes by window/file so each window is edited once, then tested before moving to the next.

### 1) `src/accessibility/shortcuts.py` (continuous across window passes)
- Working rule: update this file only as needed for the current window being fixed, then test that window.
- Do not do one large upfront refactor; keep changes incremental and scoped.
- Add `IMPORT_PROGRESS_WINDOW_SHORTCUTS` (or explicitly remove that context usage if intentional local-only behavior).
- Add `elif context == ShortcutContext.IMPORT_PROGRESS_WINDOW:` in `register_alt_shortcuts`.
- Reconcile `WEB_METADATA_SHORTCUTS` with actual web metadata fields/actions:
  - Decide whether to keep `publisher_edit`, `source_edit`, `fetch_web_button` or replace with actual IDs used in the window.
  - Add `N` mapping for series number if `Alt+N` remains supported.
- Reconcile `IMPORT_WINDOW_SHORTCUTS` IDs with actual callback IDs:
  - `import_all_valid_button` vs `add_valid_button`
  - `export_csv_button` vs `export_button`
- Verify `BOOK_DETAILS_SHORTCUTS` still includes `read_date` and is aligned to callback map.
- Expand `get_shortcut_help` coverage to all supported contexts (or document intentional exclusions).

### 2) `src/ui/import_progress_window.py`
- Status: COMPLETE (2026-04-03)
- Keep local-only keys (`F1`, `Escape`, `Alt+/`) as-is.
- If centralized context support is added, define/enable only the Alt+field keys that are truly needed for this window.
- If no centralized Alt+field keys are needed, remove `register_alt_shortcuts` call for this window to avoid silent no-op expectations.

### 6) `src/ui/backup_restore_window.py`
- Keep local-only keys (`F1`, `Escape`, `Alt+/`) aligned with standards.
- Remove `Alt+?` and keep `Alt+/` as the single status-read key.

### 3) `src/ui/import_window.py`
- Status: COMPLETE (2026-04-03)
- Update callback map key names to match centralized IDs (or vice versa in `shortcuts.py`):
  - `add_valid_button` <-> `import_all_valid_button`
  - `export_button` <-> `export_csv_button`
- Keep `F1`, `Escape`, `Alt+/`, `Alt+W` local per standards.
- Accessibility rule pass: replace button disabling with enabled actions + explicit feedback where feasible:
  - `scan_button` (Import button)
  - `add_valid_button`
- No extra scan re-entry guard is included; flow relies on existing progress-window interaction behavior.

### 4) `src/ui/book_details.py`
- Status: COMPLETE (2026-04-03)
- Add missing callback map entry for read date:
  - `'read_date': lambda: self.read_date.setFocus()`
- Decide whether `format_combo` should be centrally mapped:
  - If yes, add it to centralized `BOOK_DETAILS_SHORTCUTS`.
  - If no, remove callback key from local map.
- Remove duplicated import statements near top of file.
- Decision applied: removed local `format_combo` callback key (no centralized mapping added).

### 5) `src/ui/web_metadata.py`
- Status: COMPLETE (2026-04-03)
- Keep `F1`, `Escape`, `Alt+/` as local shortcuts only (remove centralized ownership for these if currently mapped).
- Align centralized callback map keys with actual controls.
- Resolve `Alt+N` series-number mismatch end-to-end:
  - Add central mapping for `N` if supported, and keep help text.
  - Or remove `Alt+N` from help/description if not supported centrally.
- Ensure one source of truth: central map, callback map, and F1 help must match exactly.
- Decision applied: kept `Alt+N` and added centralized `series_number_edit` mapping; removed stale centralized keys for non-existent publisher/source/fetch fields.

### 7) `src/ui/collection_window.py`
- Status: COMPLETE (2026-04-03)
- Remove duplicate `Alt+L` registration path:
  - Keep either centralized `'table': self.focus_list` or local `QShortcut("Alt+L")`, not both.
- Decision applied: kept centralized `'table': self.focus_list` mapping and removed local `QShortcut("Alt+L")`.

### 8) `src/ui/main_window.py`
- Status: COMPLETE (2026-04-03)
- In read-date dialog flow, replace explicit Return/Enter shortcuts with widget/default-button behavior or scoped key handling to avoid Enter anti-pattern drift.
- Decision applied: replaced dialog-level Return/Enter `QShortcut` bindings with scoped `keyPressEvent` handling in the read-date dialog.

### 9) `src/ui/book_list_import_window.py`
- Status: COMPLETE (2026-04-03)
- Accessibility rule pass for button enablement:
  - Replace `setEnabled(False)` gating for `import_button` and `export_button` with enabled actions that provide clear status/dialog guidance when prerequisites are missing.
- Decision applied: `import_button` and `export_button` remain enabled; handlers now provide explicit status feedback when file/errors prerequisites are not met.

### 10) `src/ui/import_detail_window.py`
- Status: COMPLETE (2026-04-03)
- Accessibility rule pass for button enablement:
  - Replace `save_return_button.setEnabled(False)` states with enabled button + explicit validation/status response.
- Decision applied: `save_return_button` now remains enabled/visible, and pressing Save with no edits shows explicit modal + status feedback.

### 11) `src/ui/update_window.py`
- Status: COMPLETE (2026-04-03)
- Remove duplicate `setup_shortcuts` definition.
- Keep only the class method implementation used at runtime.
- Re-run shortcut behavior checks after cleanup.
- Verification: `src/ui/update_window.py` contains a single `setup_shortcuts(self)` definition.

### 12) Documentation files
- Status: COMPLETE (2026-04-03)
- Updated skeleton/sample references to canonical files in `accessible_sample/`:
  - `accessible_sample/main.py`
  - `accessible_sample/accessibility_patterns.py`
  - `accessible_sample/README.md`
- Updated docs:
  - `accessibility_app_patterns.md`
  - `Accessibility_best-practice_ rules (PySide6).md`

### 13) Data schema files — ✅ COMPLETE
- **Finding:** `data/abcs.sql` and `data/abcdDB_def.sql` were byte-for-byte identical.
- **Decision:** `data/abcdDB_def.sql` is canonical — referenced by `src/database/connection.py` (line 524) and all build scripts (`build.bat`, `build_linux.sh`, `build_db.bat`, `build_linux_debug.sh`, `build_web_exe.bat`). `data/abcs.sql` had zero references.
- **Action:** Moved `data/abcs.sql` → `archive/abcs.sql`.

---

## Suggested execution order for easiest testing

1. `src/ui/import_progress_window.py`
2. `src/ui/import_window.py`
3. `src/ui/book_details.py`
4. `src/ui/web_metadata.py`
5. `src/ui/backup_restore_window.py`
6. `src/ui/collection_window.py`
7. `src/ui/main_window.py`
8. `src/ui/book_list_import_window.py`
9. `src/ui/import_detail_window.py`
10. `src/ui/update_window.py`
11. Docs (`*.md` updates)
12. Schema cleanup (`data/*.sql`)

Apply `src/accessibility/shortcuts.py` updates during each step above (only for that window's mappings/help), then test immediately.
