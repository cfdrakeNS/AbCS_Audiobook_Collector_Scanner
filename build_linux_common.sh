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

abcs_pyinstaller_help_docs_args() {
  local args=()
  if [[ -d "help_docs" ]]; then
    args+=(--add-data="help_docs:help_docs")
  else
    echo "WARNING: help_docs/ not found — in-app help will be missing from the build." >&2
  fi

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
Comment=Audiobook Collector Scanner
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

  local install_src
  install_src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/linux/install_abcs.sh"
  if [[ ! -f "${install_src}" ]]; then
    echo "ERROR: linux/install_abcs.sh not found at ${install_src}" >&2
    return 1
  fi
  cp -f "${install_src}" "${dist_dir}/install_abcs.sh"
  chmod +x "${dist_dir}/install_abcs.sh"

  cat >"${dist_dir}/README.txt" <<EOF
AbCS (Audiobook Collector Scanner) — Linux test build
Version: ${version}

WHAT IS IN THIS FOLDER
  AbCS                  The application (single executable, no Python needed)
  abcs_icon_256x256.png Application icon — keep in this folder with AbCS
  install_abcs.sh       Recommended setup script (menu icon and permissions)
  AbCS.desktop          Desktop launcher (updated automatically by install_abcs.sh)
  README.txt            This file

IN-APP HELP
  Help topics are bundled inside the AbCS executable (help_docs/).
  Use Help → Help... or Shift+F1 in any window. See Help → Help... → overview
  for the full guide list.

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
  - Help → About shows version and splash graphic when graphics are bundled.
EOF

  echo "Wrote ${dist_dir}/AbCS.desktop"
  echo "Wrote ${dist_dir}/install_abcs.sh"
  echo "Wrote ${dist_dir}/README.txt"
  if [[ -f "${dist_dir}/${icon_name}" ]]; then
    echo "Copied ${dist_dir}/${icon_name} for launchers and file managers"
  fi
}
