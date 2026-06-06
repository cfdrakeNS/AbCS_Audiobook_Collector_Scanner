#!/usr/bin/env bash
# Shared PyInstaller helpers for Linux build scripts.

abcs_graphics_dir() {
  if [[ -d "graphics" ]]; then
    printf '%s\n' "graphics"
  elif [[ -d "Graphics" ]]; then
    printf '%s\n' "Graphics"
  fi
}

abcs_pyinstaller_graphics_args() {
  local args=()
  local graphics_dir
  graphics_dir="$(abcs_graphics_dir || true)"

  if [[ -n "${graphics_dir}" ]]; then
    args+=(--add-data="${graphics_dir}:graphics")
  else
    echo "WARNING: graphics/ not found — window icons and About splash will be missing from the build." >&2
  fi

  # Do not pass --icon here. PyInstaller only embeds icons on Windows/macOS; on Linux it
  # logs "Ignoring icon" and does nothing. Icons come from bundled graphics/ at runtime
  # plus abcs_write_linux_dist_assets (sidecar PNG + AbCS.desktop).

  printf '%s\n' "${args[@]}"
}

abcs_write_linux_dist_assets() {
  local dist_dir="${1:-dist}"
  local icon_src=""
  local icon_name="abcs_icon_256x256.png"

  if [[ ! -f "${dist_dir}/AbCS" ]]; then
    echo "WARNING: ${dist_dir}/AbCS not found — skipping desktop/icon packaging." >&2
    return 0
  fi

  if [[ -f "graphics/abcs_icon_256x256.png" ]]; then
    icon_src="graphics/abcs_icon_256x256.png"
  elif [[ -f "Graphics/abcs_icon_256x256.png" ]]; then
    icon_src="Graphics/abcs_icon_256x256.png"
  fi

  if [[ -n "${icon_src}" ]]; then
    cp -f "${icon_src}" "${dist_dir}/${icon_name}"
  else
    echo "WARNING: abcs_icon_256x256.png not found — dist/ will have no sidecar icon." >&2
  fi

  local exec_path icon_path
  exec_path="$(cd "${dist_dir}" && pwd)/AbCS"
  if [[ -f "${dist_dir}/${icon_name}" ]]; then
    icon_path="$(cd "${dist_dir}" && pwd)/${icon_name}"
  else
    icon_path=""
  fi

  cat >"${dist_dir}/AbCS.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=AbCS
GenericName=Audiobook Collection Manager
Comment=Audio Book Collector Scanner
Exec=${exec_path}
Icon=${icon_path}
Terminal=false
Categories=Utility;Audio;Office;
StartupWMClass=AbCS
EOF

  local version="unknown"
  if [[ -f "src/build_config.py" ]]; then
    version="$(grep -E '^APP_VERSION[[:space:]]*=' src/build_config.py | sed -E 's/.*"([^"]+)".*/\1/' || true)"
    version="${version:-unknown}"
  fi

  cat >"${dist_dir}/install_abcs.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

# Install AbCS from this folder: menu launcher, permissions, optional data migration.
# Run from the dist folder: ./install_abcs.sh

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_BIN="${SCRIPT_DIR}/AbCS"
APP_ICON="${SCRIPT_DIR}/abcs_icon_256x256.png"
DESKTOP_SRC="${SCRIPT_DIR}/AbCS.desktop"
DESKTOP_DEST="${HOME}/.local/share/applications/AbCS.desktop"
LEGACY_DATA="${HOME}/AppData/Local/AbCS"
USER_DATA="${HOME}/.local/share/AbCS"

if [[ ! -f "${APP_BIN}" ]]; then
  echo "ERROR: AbCS executable not found in ${SCRIPT_DIR}" >&2
  exit 1
fi

echo "AbCS install folder: ${SCRIPT_DIR}"

chmod +x "${APP_BIN}"
echo "Made AbCS executable."

if [[ -d "${LEGACY_DATA}" && -f "${LEGACY_DATA}/abcs.db" && ! -f "${USER_DATA}/abcs.db" ]]; then
  echo "Migrating database from legacy path:"
  echo "  ${LEGACY_DATA}"
  echo "  -> ${USER_DATA}"
  mkdir -p "${USER_DATA}"
  cp -a "${LEGACY_DATA}/." "${USER_DATA}/"
  echo "Migration copy complete. The app also migrates on first run if needed."
fi

mkdir -p "${HOME}/.local/share/applications"

icon_line=""
if [[ -f "${APP_ICON}" ]]; then
  icon_line="Icon=${APP_ICON}"
else
  echo "WARNING: ${APP_ICON} not found — menu entry may have no icon." >&2
fi

cat >"${DESKTOP_SRC}" <<DESKTOP_EOF
[Desktop Entry]
Type=Application
Name=AbCS
GenericName=Audiobook Collection Manager
Comment=Audio Book Collector Scanner
Exec=${APP_BIN}
${icon_line}
Terminal=false
Categories=Utility;Audio;Office;
StartupWMClass=AbCS
DESKTOP_EOF

cp -f "${DESKTOP_SRC}" "${DESKTOP_DEST}"
echo "Installed menu launcher: ${DESKTOP_DEST}"

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "${HOME}/.local/share/applications"
  echo "Refreshed desktop menu database."
else
  echo "NOTE: update-desktop-database not found — log out/in or reboot if AbCS is missing from the menu."
fi

echo
echo "Done. You can:"
echo "  - Launch from the application menu (AbCS)"
echo "  - Or run: ${APP_BIN}"
echo "Database location: ${USER_DATA}/"
EOF
  chmod +x "${dist_dir}/install_abcs.sh"

  cat >"${dist_dir}/README.txt" <<EOF
AbCS (Audio Book Collector Scanner) — Linux test build
Version: ${version}

WHAT IS IN THIS FOLDER
  AbCS                  The application (single executable, no Python needed)
  abcs_icon_256x256.png Application icon — keep in this folder with AbCS
  install_abcs.sh       Recommended setup script (menu icon, permissions, migration)
  AbCS.desktop          Desktop launcher (updated automatically by install_abcs.sh)
  README.txt            This file

QUICK START (recommended)
  1. Open a terminal in this folder.
  2. Run:
       chmod +x install_abcs.sh
       ./install_abcs.sh
  3. Launch AbCS from the menu, or run ./AbCS

MANUAL START (no menu install)
       chmod +x AbCS
       ./AbCS

  Keep all files in this folder together. Do not move AbCS without the PNG icon.

REQUIREMENTS
  - 64-bit Linux (x86_64). Built for Mint/Ubuntu-style desktops.
  - Python is NOT required.
  - On a fresh system, if AbCS does not start, install Qt libraries:
       sudo apt install -y libxcb-cursor0 libxkbcommon-x11-0 libgl1 libegl1

SHARING THIS BUILD
  Zip this entire folder and send it. Testers only need the contents of dist/.

SUPPORT NOTES
  - Database and backups: ~/.local/share/AbCS/
  - Older test builds used ~/AppData/Local/AbCS — install_abcs.sh copies that data if found.
  - Help → About shows version and splash graphic when graphics are bundled.
EOF

  echo "Wrote ${dist_dir}/AbCS.desktop"
  echo "Wrote ${dist_dir}/install_abcs.sh"
  echo "Wrote ${dist_dir}/README.txt"
  if [[ -f "${dist_dir}/${icon_name}" ]]; then
    echo "Copied ${dist_dir}/${icon_name} for launchers and file managers"
  fi
}
