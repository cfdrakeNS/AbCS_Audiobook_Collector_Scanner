# AbCS Linux Fixes — Status

**Status:** Complete (June 2026)  
**VM sign-off:** Accepted. Linux builds bundle graphics, help, and schema; window icons and About/setup splash load via `graphics_paths` at runtime. A separate formal VM checklist log was not kept — this document and [linux_build.md](linux_build.md) are the source of truth.

---

## What was fixed

| Area | Implementation |
|------|----------------|
| Graphics paths | [`src/accessibility/graphics_paths.py`](src/accessibility/graphics_paths.py) — dev, PyInstaller, and installed layouts |
| App icon | [`src/accessibility/icon_helper.py`](src/accessibility/icon_helper.py) — multi-size `QIcon` from bundled PNG/ICO |
| User data dir | [`src/app_paths.py`](src/app_paths.py) — XDG-style paths on Linux |
| Linux builds | [`build_linux.sh`](build_linux.sh), [`build_linux_debug.sh`](build_linux_debug.sh), [`build_linux_common.sh`](build_linux_common.sh) — bundle `graphics/`, `help_docs/`, schema SQL |
| Dist packaging | `dist/install_abcs.sh`, `AbCS.desktop`, sidecar PNG icon, `README.txt` |
| Main window | `setWindowIcon` on startup |
| Qt on Linux | Combo/table tweaks in `linux_qt_compat.py`, `linux_fusion_style.py` |

Original tracker item **#94** (window icons and About graphic missing on Linux) is resolved in code and covered by manual QA on the Linux Mint/Ubuntu test path described in [linux_build.md](linux_build.md).

---

## How to verify on a VM

1. Build with `./build_linux.sh` (release) or `./build_linux_debug.sh` (console + logs).
2. Run `./install_abcs.sh` from `dist/` or launch `./dist/AbCS` directly.
3. Confirm: application icon in launcher/file manager, **Help → About** splash graphic, **Help → Help...** topics load.
4. If Qt xcb errors appear, install packages listed in `dist/README.txt` and [linux_build.md](linux_build.md).

Use `abcs_linux_build.log` and `abcs_linux_run.log` (from `build_linux_debug.sh`) when diagnosing startup failures.

---

## Related

- [linux_build.md](linux_build.md) — full build guide
- [doc/plans_status.md](doc/plans_status.md) — rollout plan status
- [doc/qa_verification.md](doc/qa_verification.md) — overall manual QA note
- Detailed historical bug log: local `archive/AbCS_Bug_Final_fixes.md` (gitignored)
