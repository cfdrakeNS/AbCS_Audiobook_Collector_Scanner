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

**Fix (ongoing):**
- `ThemeMiniPreview` uses child `QFrame` swatches (no app `QPainter` code)
- On Linux: **no** `::drop-down` / `::down-arrow` combo subcontrol CSS (Fusion draws the native arrow)
- `combobox-popup: 0` on Linux combos
- `LinuxFusionStyle` proxy sets `SH_ComboBox_Popup` to scrollable list mode
- Scaling skips `padding-right` on Linux combos (was clipping the arrow)

If the warning persists after `git pull`, note **when** it appears (app start, Preferences open, Import open) and run `git log -1 --oneline` to confirm you have the latest commit.

### 4. Qt xcb startup (system packages)

**Symptom:** App fails to start with xcb platform plugin error.

**Fix:** Install apt packages (documented in `requirements.txt` and `linux_build.md`):

```bash
sudo apt install -y libxcb-cursor0 libxkbcommon-x11-0 libgl1 libegl1
sudo apt install -y libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-shape0
```

### 5. Window icons / About splash (bug #94)

**Symptom:** No window title-bar icon on Linux; About splash missing in frozen build.

**Cause:** `icon_helper.py` resolved paths under `src/graphics/` (wrong) and only tried `.ico` (poor on Linux). Linux PyInstaller scripts did not bundle `graphics/`.

**Fix:**
- `src/accessibility/graphics_paths.py` — shared resolver (project root + `_MEIPASS`, `graphics`/`Graphics`)
- `icon_helper.py` — PNG-first icon candidates on Linux, ICO-first on Windows
- `about_dialogue.py` / `setup_dialogue.py` — use shared resolver
- `build_linux.sh`, `build_linux_debug.sh` — `--add-data=graphics:graphics` + `--icon` via `build_linux_common.sh`
- `make_icon.py` — also writes `abcs_icon_256x256.png` for Linux

**VM verify:** title-bar icon in dev and after `./build_linux_debug.sh`; About splash in both.

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

## Remaining work

1. Cross-platform user data dir (`XDG_DATA_HOME` on Linux) for frozen builds
2. Mark bug #94 complete after VM verifies icons in dev + frozen build
3. Merge `Linux_fixes` → `main` after VM sign-off
