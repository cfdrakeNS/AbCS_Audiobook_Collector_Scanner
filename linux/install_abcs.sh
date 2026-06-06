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
