---

### Detailed Anomaly Report (March 10, 2026)

**1. Shortcut Density Variance:**
	- Import Window and Preferences Window have more Alt+letter shortcuts than Main Window; this is intentional for accessibility and workflow granularity.
	- Main Window uses fewer Alt+letter shortcuts, relying more on menu-driven actions and Ctrl+key shortcuts.

**2. Legacy Shortcuts:**
	- Some legacy shortcuts (e.g., Alt+N for Cancel scan) have been removed or replaced with Escape for consistency.
	- No obsolete or dead shortcuts remain in active windows.

**3. Mnemonic Consistency:**
	- All ampersand mnemonics (&) in labels match registered Alt+letter shortcuts.
	- No mismatches found between visual mnemonics and actual shortcut keys.

**4. No Duplicate Shortcuts:**
	- No duplicate Alt+letter shortcuts found within any window context (checked via find_shortcut_conflicts).
	- No conflicts between Alt+letter and Ctrl+key shortcuts.

**5. Dead/Ghost Navigation:**
	- All documented shortcuts are functional and accessible; no dead or ghost navigation paths.
	- All shortcut help dialogs (F1) accurately reflect available shortcuts per window.

**6. Accessibility Compliance:**
	- All major actions (Save, Cancel, Delete, Import, Update) use first-letter Alt shortcuts where possible.
	- Status bar readback (Alt+/) and F1 help dialog are present in all windows.
	- No accessibility gaps found in shortcut registration or documentation.

**7. Contextual Shortcut Registration:**
	- All Alt+letter shortcuts are registered contextually via ShortcutManager; no global leakage or cross-window conflicts.

**8. Zoom and Navigation Keys:**
	- Zoom keys (Ctrl+Plus, Ctrl+Minus, Ctrl+0) are consistent and functional across all windows.
	- Navigation keys (Ctrl+Enter, Escape) are standardized.

**9. CSV Mapping:**
	- AbCS_Shortcut_mar11.csv reflects the current, normalized shortcut mapping for all major windows (updated March 11).

---
---

### Shortcut Review (March 12, 2026)

#### Centralized Shortcut Contexts (latest)
  - Main Window: Alt+B (Book list), Alt+U (Update), Alt+D (Delete), Alt+L (Cancel selection)
  - Book Details: Alt+T (Title), Alt+A (Author), Alt+Y (Year), Alt+F (Files), Alt+I (Series), Alt+G (Genre), Alt+R (Reader), Alt+C (Collection), Alt+M (Length), Alt+E (Read date), Alt+Z (Size), Alt+B (Bitrate), Alt+H (Path), Alt+O (Comments), Alt+N (New), Alt+S (Save), Alt+D (Delete), Alt+L (Cancel)
  - Import Window: Alt+C (Collection), Alt+F (Folder), Alt+E (Error filter), Alt+W (Browse), Alt+S (Import Selected), Alt+V (Import All Valid), Alt+B (Focus import list table), Alt+X (Export list to CSV)
  - Import Detail Window: Alt+T (Title), Alt+A (Author), Alt+Y (Year), Alt+F (Files), Alt+I (Series), Alt+G (Genre), Alt+R (Reader), Alt+C (Collection), Alt+M (Length), Alt+E (Errors), Alt+Z (Size), Alt+B (Bitrate), Alt+H (Path), Alt+O (Comments), Alt+S (Save), Alt+D (Discard), Alt+L (Launch Tag)
  - Update Window: Alt+S (Series), Alt+G (Genre), Alt+C (Collection), Alt+B (Focus book list)
  - Preferences Window: Alt+D (Display), Alt+P (Path & Scope), Alt+O (Options), Alt+F (Fallback), Alt+R (Validation Rules), Alt+A (Auto-Correction), Alt+S (Save), Alt+L (Cancel), Alt+/ (Status bar)

**Global Shortcuts:** Ctrl+Plus, Ctrl+Minus, Ctrl+0 (Zoom), F1 (Help), Escape (Close), Alt+/ (Read status bar), Ctrl+Enter (Open detail)

#### Normalization Rules (current)
- All Alt+letter shortcuts are registered via ShortcutManager.
- Mnemonics (&) in labels match shortcut keys.
- No duplicate Alt+letter shortcuts within a window context.
- Status bar readback is always Alt+/.
- F1 opens keyboard shortcut help dialog in all windows.
- Zoom keys are consistent across all windows.

#### Documented Gaps & Anomalies
- Import Detail Window: Alt+L (Launch Tag) is unique; ensure it's documented and registered.
- Book Details: Alt+K (Collection) is not present in shortcut manager, but Collection is mapped to Alt+C.
- Preferences Window: Some shortcuts (e.g., Alt+V for Save) are not consistently mapped; ensure Save is always Alt+S.
- Main Window: Fewer Alt+letter shortcuts; relies more on menu and Ctrl+key shortcuts.
- No duplicate Alt+letter shortcuts found in any window context.
- All F1 help dialogs reflect the correct shortcuts per window.
- Status bar read (Alt+/) is present and functional in all windows.

#### New Controls CSV
- See AbCS_Shortcut_mar11.csv for updated per-window shortcut mapping.

---
# Shortcut review & normalization plan (updated 2026-03-03)

## Scope
- Review only `Alt+letter` and `Ctrl+letter/number` shortcuts.
- Keep `F1`, `Escape`, `Ctrl+Enter` as-is.
- No need to force the same number of shortcuts in every window until shortcut standards are solid.

## Related roadmap
- See [App_Standardization_Implementation_Order.md](App_Standardization_Implementation_Order.md) for phased UI/menu standardization status and validation milestones.

## Implemented changes (current status)

### Main Window (implemented)
- Header combo shortcuts removed as part of menu standardization:
	- Removed `Alt+C` (Collection filter)
	- Removed `Alt+R` (Read filter)
	- Removed `Alt+O` (Order By)
	- Removed `Alt+S` (inline Search)
- Filters/sort now menu-driven:
	- `View > Collections`
	- `View > Read`
	- Top-level `Sort` menu
- Find workflow standardized:
	- `View > Find...`
	- `Ctrl+F` opens Find dialog
- Existing core shortcuts retained:
	- `Alt+B` book list, `Alt+U` update, `Alt+D` delete, `Alt+L` cancel selection
	- `Ctrl+I`, `Ctrl+N`, `Ctrl+Q`, zoom keys

### Preferences Window (implemented)
- Preferences uses section-navigation shortcuts (reorg-aware):
	- `Alt+D` Display
	- `Alt+S` Source & Scope
	- `Alt+O` Options
	- `Alt+F` Fallback & Parsing Behavior
	- `Alt+R` Validation Rules
	- `Alt+A` Auto-Correction
- Footer/status shortcuts:
	- `Alt+V` Save
	- `Alt+C` Cancel
	- `Alt+/` read status
	- `F1` shortcut help

### Time → Length terminology (implemented)
- User-facing `Time` label/name updated to `Length` in:
	- Main Window column/header text
	- Book Details window field label/help text
	- Import Detail window field label/help text
- Mnemonic compatibility preserved for details forms using `Length (&M):`.

## Normalization rules (target)

### Alt+letter
- Dismiss-only **Close** buttons are removed; use `Escape` as the close path.
- Use `Alt+C` for **Cancel** when a cancel action is present.
- Use first letter for common actions where available:
	- `Alt+S` Save/Scan/Search (primary action in that window)
	- `Alt+D` Delete
	- `Alt+E` Edit
	- `Alt+I` Import
	- `Alt+B` Browse/Book list (context-based)
	- `Alt+L` Collection/List or context-specific cancel where already established
- Combo/text controls should prefer first letter unless it conflicts with high-priority action.

### Ctrl+ shortcuts
- `Ctrl+N` New
- `Ctrl+S` Save
- `Ctrl+I` Import
- `Ctrl+Q` Quit (main window only)
- Keep zoom set global where supported: `Ctrl+Plus`, `Ctrl+Minus`, `Ctrl+0`

## Suggested normalization by window (remaining / optional)

### Main Window
- Completed: filter/sort/search moved out of header into menus and `Ctrl+F` Find.
- Keep `Ctrl+I`, `Ctrl+N`, `Ctrl+Q`, zoom keys (reason: already good standards).
- Optional future decision: whether `Alt+L` cancel selection should remain as-is or migrate to `Alt+X`.

### Book Details
- Keep `Alt+K` Collection and `Alt+L` Cancel unless/until a broader cross-window remap is approved.
- Keep `Alt+S` Save and use `Escape` to close.
- Length label change completed (`Alt+M` preserved).
- Optional: add `Ctrl+S` Save and `Ctrl+N` New (reason: cross-window Ctrl consistency).

### Import Window
- Keep `Alt+I` Import, `Alt+X` Export, `Alt+V` View, `Alt+A` Add; use `Escape` to close when idle.
- Keep `Alt+L` Collection (reason: aligns with collection standard).
- Optional: add `Ctrl+I` Import (reason: main/import consistency).

### Import Detail Window
- Keep `Alt+E` Error filter/Edit-context action; use `Escape` to close.
- If any cancel action exists, prefer `Alt+C` for cancel consistency.
- Length label change completed (`Alt+M` preserved).

### Import Progress Window
- Progress counters were removed from the window UI; status bar is the authoritative progress output.
- Keep current interaction model: `Alt+L` cancel while active, `Escape` close after completion, `Alt+/` read status.

### Update Window
- Keep `Alt+S` Series, `Alt+G` Genre, `Alt+L` Collection; use `Escape` to close.

### Name List Window
- Keep `Alt+L` Cancel edit/new (current behavior), and `Escape` to close.
- Keep `Alt+E` Edit, `Alt+S` Save, `Alt+F` Find (reason: clear and standard).
- Add `Ctrl+S` Save, `Ctrl+N` New row where applicable (reason: common form behavior).

### Collection Window
- Keep `Alt+A` Active and use `Escape` to close.
- If Cancel exists, use `Alt+C` for cancel consistency.
- Add `Ctrl+S` Save and `Ctrl+N` New collection (reason: consistency with edit forms).

### Preferences Window
- Current implementation intentionally uses section-level shortcuts (`Alt+D/S/O/F/R/A`) plus `Alt+V` Save and `Alt+C` Cancel.
- Keep as-is unless a full-window save-key policy change is approved.
- Optional: add `Ctrl+S` Save if no conflict emerges.

### Backup/Restore Window
- Keep `Alt+B` Create backup and use `Escape` to close.
- Keep `Alt+L` for list semantics only (reason: avoid close/cancel conflict).
- Optional: `Ctrl+S` for “start backup” only if not conflicting (reason: consistent primary action key).

## High-priority inconsistencies to monitor next
- Confirm all dismiss-only flows use `Escape` close and no stale Close-button shortcut text remains.
- Collection key remains context-specific (`Alt+K` Book Details, `Alt+L` Import); no breakage, but not globally uniform.
- Save key remains mixed (`Alt+S` in some windows, `Alt+V` in Preferences by design).

## Next implementation pass (after approval)
- Phase 1: Decide whether to keep or remap `Alt+L` cancel behavior in detail windows.
- Phase 2: Decide whether to introduce `Ctrl+S` in Preferences and other edit forms.
- Phase 3: Re-run shortcut matrix + conflict report and verify no regressions.

## Test-enforcement follow-up
- Add `EXCLUDED_ALT_LETTERS` blocks to each window file from this normalization plan so `test/check_shortcut_mnemonics.py` can actively enforce the policy.



