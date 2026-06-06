# AbCS Linux Fixes

Branch: `Linux_fixes`  
Tracking: bug **#94** in `AbCS_Bug_Final_fixes.md` (deferred to this branch)

---

## Issues addressed

### 1. Combo box dropdown arrow not visible (Linux Mint)

**Symptom:** Dropdown selector/arrow invisible on QComboBox controls across Preferences, Main (duplicate/find), Book detail, Import, Import detail, Book list import.

**Cause:** Global `QComboBox::down-arrow` CSS in `theme_manager.py` used `image: none` plus a solid square — renders poorly on Linux. Several windows also applied local combo stylesheets without arrow rules, overriding the global theme.

**Fix:**
- Added `build_accessible_combo_box_style()` in `src/accessibility/style_helpers.py` with a CSS triangle arrow
- `theme_manager.py` now uses shared combo/date/spin helpers
- `preferences_window.py` clears per-combo overrides; spinboxes use `build_accessible_spinbox_style()`
- `main_window.py` duplicate/find dialogs use shared combo style
- `book_details.py` clears local combo overrides
- `main.py` sets Qt **Fusion** style on Linux for consistent palette/stylesheet behavior

### 2. Backup/restore file list not visible

**Symptom:** Backup filenames not readable in the table on Linux.

**Cause:** `build_table_polish_style()` did not set default item text/background colors; Linux palettes could make text match the background.

**Fix:** Explicit `color: palette(text)` and `background-color: palette(base)` on table widgets and items.

### 3. QPainter terminal warning

**Symptom:** `QPainter::end: Painter ended with 3 saved states` when opening Preferences theme picker.

**Fix:** `ThemeMiniPreview.paintEvent` in `theme_picker.py` now uses `with QPainter(self)`.

### 4. Qt xcb startup (system packages)

**Symptom:** App fails to start with xcb platform plugin error.

**Fix:** Install apt packages (documented in `requirements.txt` and `linux_build.md`):

```bash
sudo apt install -y libxcb-cursor0 libxkbcommon-x11-0 libgl1 libegl1
sudo apt install -y libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-shape0
```

### 5. Window icons / About splash (bug #94 — still open)

**Status:** About splash works in dev when `graphics/` exists. Window title-bar icons still need the icon path / build bundling work from the original Linux plan (`icon_helper.py`, `build_linux.sh` graphics bundling).

---

## Files changed (combo/table/painter pass)

| File | Change |
|------|--------|
| `src/accessibility/style_helpers.py` | Shared combo/date/spin/table styles |
| `src/accessibility/theme_manager.py` | Use shared helpers for global combo CSS |
| `src/ui/preferences_window.py` | Stop overriding combo arrow styling |
| `src/ui/main_window.py` | Duplicate/find combo dialogs use shared style |
| `src/ui/book_details.py` | Clear local combo overrides |
| `src/accessibility/theme_picker.py` | QPainter context manager |
| `src/main.py` | Fusion style on Linux |
| `requirements.txt` | Note apt deps for xcb |

---

## Test checklist

Test on **both Windows and Linux Mint** after pulling `Linux_fixes`.

### Linux Mint

- [ ] `python src/main.py` starts (no xcb error)
- [ ] Preferences — all combo arrows visible (preset, zoom, severities, duplicate match)
- [ ] Preferences theme picker — no `QPainter::end` warnings in terminal
- [ ] Main window — duplicate mode combo arrow visible
- [ ] Main window — Find dialog combo arrow visible
- [ ] Book detail — collection combo arrow visible
- [ ] Import — collection + error filter combo arrows visible
- [ ] Import detail — collection combo arrow visible
- [ ] Book list import — collection combo arrow visible
- [ ] Backup/restore — backup filenames readable in table
- [ ] About dialog — splash graphic still shows
- [ ] Spot-check Default + one custom theme

### Windows (regression)

- [ ] Same combo boxes as above — arrows still visible
- [ ] Backup/restore table readable
- [ ] Themes unchanged (no Fusion on Windows)
- [ ] Window icons still show

---

## VM workflow

```bash
cd ~/AbCS
git pull origin Linux_fixes
source venv/bin/activate
python src/main.py
```

For packaged build test:

```bash
./build_linux_debug.sh
```

---

## Remaining work (original Linux plan)

1. Centralize graphics path resolution (`icon_helper` vs `about_dialogue`)
2. Bundle `graphics/` in `build_linux.sh` / `build_linux_debug.sh`
3. PNG + ICO icon fallback for window title bars
4. Cross-platform user data dir (`XDG_DATA_HOME` on Linux)
5. Mark bug #94 complete after VM verifies icons in dev + frozen build
