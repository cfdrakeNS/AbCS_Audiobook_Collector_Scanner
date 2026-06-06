# AbCS Linux Fixes

Branch: `Linux_fixes` — **ready to merge** (v1.9.72)  
Tracking: bug **#94** in `AbCS_Bug_Final_fixes.md` (complete)

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

**Cause:** Case-sensitive glob (`AbCS_backup_*` vs `abcs_backup_*`) and missing table item colors on Linux palettes.

**Fix:** Correct backup glob; explicit `color: palette(text)` and `background-color: palette(base)` on table widgets and items; WAL sidecar handling on restore.

### 3. QPainter terminal warning

**Symptom:** `QPainter::end: Painter ended with 3 saved states` when opening Preferences theme picker.

**Fix:**
- `linux_qt_compat.py` — minimal Linux stylesheet + `QT_LOGGING_RULES` painting suppress
- `ThemeMiniPreview` uses child `QFrame` swatches (no app `QPainter` code)
- On Linux: **no** `::drop-down` / `::down-arrow` combo subcontrol CSS (Fusion draws the native arrow)
- `LinuxFusionStyle` proxy sets `SH_ComboBox_Popup` to scrollable list mode

### 4. Qt xcb startup (system packages)

**Symptom:** App fails to start with xcb platform plugin error.

**Fix:** Install apt packages (documented in `requirements.txt` and `linux_build.md`):

```bash
sudo apt install -y libxcb-cursor0 libxkbcommon-x11-0 libgl1 libegl1
sudo apt install -y libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-shape0
```

### 5. Window icons / About splash (bug #94)

**Fix:**
- `src/accessibility/graphics_paths.py` — shared resolver (project root + `_MEIPASS`, `graphics`/`Graphics`)
- `icon_helper.py` — PNG-first icon candidates on Linux, ICO-first on Windows
- `build_linux.sh` / `build_linux_debug.sh` — bundle `graphics/` via `build_linux_common.sh`
- `linux/install_abcs.sh` — menu launcher + sidecar PNG in `dist/`
- Fixed duplicate `MainWindow.__init__` that skipped `setWindowIcon()`

**Verified:** Dev and frozen builds on Mint VM and HP6000 Pro. Icon shows in taskbar/Alt+Tab; About splash loads. Mint Cinnamon may hide title-bar icons (theme limitation).

### 6. Linux user data directory

**Was:** `~/AppData/Local/AbCS` (Windows path on Linux).  
**Now:** `~/.local/share/AbCS/` via `src/app_paths.py`.

### 7. Linux distribution package

Frozen `dist/` includes: `AbCS`, `abcs_icon_256x256.png`, `AbCS.desktop`, `install_abcs.sh`, `README.txt`.

```bash
cd dist && ./install_abcs.sh
```

---

## Test checklist

### Linux Mint — verified on VM + HP6000 Pro

- [x] `python src/main.py` starts (no xcb error)
- [x] Combo arrows visible (Preferences, Main, Book detail, Import windows)
- [x] Backup/restore — filenames readable; restore works
- [x] About dialog — splash graphic shows
- [x] Frozen build (`./build_linux.sh`) — app runs; `install_abcs.sh` works
- [x] Database at `~/.local/share/AbCS/`
- [ ] Windows regression (run on dev PC before merge — see below)

### Windows (regression — run before merge)

- [ ] `python src/main.py` starts
- [ ] Combo arrows visible
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

Release build:

```bash
./build_linux.sh
cd dist && ./install_abcs.sh
```

---

## Merge status

**Ready to merge** `Linux_fixes` → `main` after Windows regression pass.

**Out of scope (follow-up branch):** Main table screen-reader announcements (cell-by-cell navigation).
