# Shortcut review & normalization plan Feb 26

## Scope
- Review only `Alt+letter` and `Ctrl+letter/number` shortcuts.
- Keep `F1`, `Escape`, `Ctrl+Enter` as-is.
- No need to force the same number of shortcuts in every window until shortcut standards are solid.

## Normalization rules (target)

### Alt+letter
- Reserve `Alt+C` for **Close** (or Cancel/Close when only one exit action exists).
- Reserve `Alt+X` for **Cancel** when a window has both Cancel and Close.
- Use first letter for common actions where available:
	- `Alt+S` Save/Scan/Search (primary action in that window)
	- `Alt+D` Delete
	- `Alt+E` Edit
	- `Alt+I` Import
	- `Alt+B` Browse/Book list (context-based)
	- `Alt+L` Collection/List (not Close/Cancel)
- Combo/text controls should prefer first letter unless it conflicts with high-priority action.

### Ctrl+ shortcuts
- `Ctrl+N` New
- `Ctrl+S` Save
- `Ctrl+I` Import
- `Ctrl+Q` Quit (main window only)
- Keep zoom set global where supported: `Ctrl+Plus`, `Ctrl+Minus`, `Ctrl+0`

## Suggested normalization by window

### Main Window
- `Alt+C` Collection filter -> `Alt+L` Collection filter (reason: reserve `Alt+C` for Close/Cancel pattern).
- `Alt+L` Cancel selection -> `Alt+X` Cancel selection (reason: `X` for cancel action consistency).
- Keep `Ctrl+I`, `Ctrl+N`, `Ctrl+Q`, zoom keys (reason: already good standards).

### Book Details
- `Alt+K` Collection -> `Alt+L` Collection (reason: first-letter consistency with other windows).
- `Alt+L` Cancel -> `Alt+X` Cancel (reason: reserve `Alt+L` for List/Collection).
- Keep `Alt+C` Close and `Alt+S` Save (reason: standard action keys).
- Add `Ctrl+S` Save and `Ctrl+N` New (reason: cross-window Ctrl consistency).

### Import Window
- Keep `Alt+I` Import, `Alt+X` Export, `Alt+V` View, `Alt+A` Add, `Alt+C` Close (reason: first-letter mapping is clear).
- Keep `Alt+L` Collection (reason: aligns with collection standard).
- Optional: add `Ctrl+I` Import (reason: main/import consistency).

### Import Detail Window
- Keep `Alt+C` Close and `Alt+E` Error filter/Edit-context action (reason: predictable and short reach).
- If any cancel action exists, use `Alt+X` (reason: avoid `Alt+L` overload).

### Import Progress Window
- Keep `Alt+C` Close (completion state) and avoid using `Alt+L` for close/cancel (reason: global Close rule).
- If cancel scan shortcut is needed, use `Alt+X` (reason: action consistency).

### Update Window
- Keep `Alt+S` Series, `Alt+G` Genre, `Alt+L` Collection, `Alt+C` Close (reason: good first-letter mapping).
- Optional: add `Ctrl+S` Apply/Save update if save-style action exists (reason: Ctrl consistency).

### Name List Window
- `Alt+L` Cancel edit/new -> `Alt+X` Cancel edit/new (reason: `Alt+L` should stay list/collection semantic).
- Keep `Alt+C` Close, `Alt+E` Edit, `Alt+S` Save, `Alt+F` Find (reason: clear and standard).
- Add `Ctrl+S` Save, `Ctrl+N` New row where applicable (reason: common form behavior).

### Collection Window
- Keep `Alt+C` Close and `Alt+A` Active (reason: established semantic).
- If Cancel exists, set to `Alt+X` (reason: separate from Close).
- Add `Ctrl+S` Save and `Ctrl+N` New collection (reason: consistency with edit forms).

### Preferences Window
- `Alt+V` Save -> `Alt+S` Save (reason: Save should be `S` globally).
- Move current `Alt+S` Scenario -> `Alt+N` Scenario (reason: free `Alt+S` for Save).
- Keep `Alt+C` Cancel/Close (reason: global exit key rule).
- Add `Ctrl+S` Save (reason: cross-window standard).

### Backup/Restore Window
- Keep `Alt+C` Close and `Alt+B` Create backup (reason: strong first-letter match).
- Keep `Alt+L` for list semantics only (reason: avoid close/cancel conflict).
- Optional: `Ctrl+S` for “start backup” only if not conflicting (reason: consistent primary action key).

## High-priority inconsistencies to fix first
- Close/Cancel split currently mixed (`Alt+C` vs `Alt+L`) -> normalize to `Alt+C` Close, `Alt+X` Cancel.
- Collection key inconsistent (`Alt+C`, `Alt+K`, `Alt+L`) -> normalize to `Alt+L`.
- Save key inconsistent (`Alt+S` vs `Alt+V`) -> normalize to `Alt+S` (+ `Ctrl+S`).

## Next implementation pass (after approval)
- Phase 1: Exit/action keys (`Alt+C`, `Alt+X`, `Alt+S`, `Alt+L`).
- Phase 2: Add/align `Ctrl+S`, `Ctrl+N`, `Ctrl+I`.
- Phase 3: Re-run shortcut matrix + conflict report and verify no regressions.

## Test-enforcement follow-up
- Add `EXCLUDED_ALT_LETTERS` blocks to each window file from this normalization plan so `test/check_shortcut_mnemonics.py` can actively enforce the policy.



