# Work and Testing Notes - 2026-04-06

## Scope
This document summarizes the completed work and provides a focused test checklist.

## Completed Work

### Collection Active Behavior
- Main list and search now hide books whose collection is inactive.
- Reading History remains independent of collection active filtering (all-time/read-date behavior).
- Main Statistics now includes per-collection counts and tags inactive collections as `Collection Name (inactive)`.
- Collection window Save behavior follows centralized shortcut routing for Alt+S.

### Installer Updates
- Installer now follows the user's Windows theme:
  - `WizardStyle=modern dynamic`
- Installer title bar now includes version text.
- Installer version source is now the app code version in `src/main.py` (`APP_VERSION`), passed to Inno Setup via `/DMyAppVersion=` in `build_installer.bat`.
- `AbCS_installer.iss` supports override of `MyAppVersion` with fallback for manual IDE compiles.

## Files Updated
- `src/database/models.py`
- `src/database/queries.py`
- `src/ui/main_window.py`
- `src/ui/reading_history_window.py`
- `src/ui/collection_window.py`
- `AbCS_installer.iss`
- `build_installer.bat`
- `AbCS_Bug_Final_fixes.md`

## Testing Checklist

### A) Collection Active
1. In Collection window, set one collection to inactive and save.
2. In Main window, confirm books from that collection are hidden from table and search.
3. Re-activate that collection and confirm books reappear.

### B) Reading History Independence
1. Open Reading History.
2. Confirm General/Year/Month tabs show all-time read statistics.
3. Change Date Range and run Search.
4. Confirm Date Range tab changes only date-range results/status.
5. Confirm General tab totals do not change because of Date Range selection.

### C) Main Statistics Dialog
1. Open Main window -> View -> Statistics.
2. Confirm totals display.
3. Confirm one row per collection with book count appears.
4. Confirm inactive collections are labeled with `(inactive)`.
5. Confirm `No Collection` appears if applicable.

### D) Collection Alt+S Save
1. Open Collection window.
2. Enter edit/new mode.
3. Press Alt+S and confirm save executes.
4. Ensure behavior matches Name List window Save shortcut pattern.

### E) Installer Version and Theme
1. Ensure `APP_VERSION` in `src/main.py` is set to the intended release (for example, `1.9.6`).
2. Run `build_installer.bat`.
3. Confirm output installer file includes same version:
   - `releases/AbCS-Setup-<APP_VERSION>.exe`
4. Run installer on a Windows light theme machine and confirm light installer.
5. Run installer on a Windows dark theme machine and confirm dark installer.
6. Confirm installer title bar includes app name + version.

## Notes
- If installer version mismatch is seen, check `APP_VERSION` in `src/main.py` first, then rerun `build_installer.bat`.
- Building from Inno Setup IDE directly can use fallback version unless `MyAppVersion` is overridden.
