#!/usr/bin/env bash
set -euo pipefail

# Build AbCS Linux executable with PyInstaller.
# Run from repository root: ./build_linux.sh

if [[ ! -f "src/main.py" ]]; then
  echo "ERROR: Run this script from the repository root (src/main.py not found)."
  exit 1
fi

# Find virtual environment (accept both venv and .venv)
VENV_DIR=""
if [[ -d "venv" ]]; then
  VENV_DIR="venv"
elif [[ -d ".venv" ]]; then
  VENV_DIR=".venv"
else
  echo "ERROR: venv not found. Create it first: python3 -m venv venv"
  exit 1
fi

source "${VENV_DIR}/bin/activate"

if ! python -m pip show pyinstaller >/dev/null 2>&1; then
  echo "Installing PyInstaller..."
  python -m pip install pyinstaller
fi

echo "Cleaning old build artifacts..."
rm -rf build dist

# shellcheck disable=SC1091
source "$(dirname "$0")/build_linux_common.sh"
mapfile -t GRAPHICS_ARGS < <(abcs_pyinstaller_graphics_args)
mapfile -t HELP_DOCS_ARGS < <(abcs_pyinstaller_help_docs_args)

echo "Building Linux executable (dist/AbCS)..."
python -m PyInstaller \
  --name="AbCS" \
  --onefile \
  --windowed \
  --log-level=WARN \
  --clean \
  --noconfirm \
  --add-data="data/abcdDB_def.sql:data" \
  "${GRAPHICS_ARGS[@]}" \
  "${HELP_DOCS_ARGS[@]}" \
  --hidden-import="PySide6.QtCore" \
  --hidden-import="PySide6.QtGui" \
  --hidden-import="PySide6.QtWidgets" \
  --hidden-import="mutagen" \
  --hidden-import="mutagen.mp3" \
  --hidden-import="mutagen.mp4" \
  --hidden-import="mutagen.flac" \
  --hidden-import="mutagen.oggvorbis" \
  --hidden-import="mutagen.wave" \
  --hidden-import="openpyxl" \
  --hidden-import="odf" \
  --hidden-import="odf.opendocument" \
  --collect-submodules="odf" \
  --exclude-module="PySide6.QtSql" \
  --exclude-module="PySide6.QtQml" \
  --exclude-module="PySide6.QtQuick" \
  --exclude-module="PySide6.QtQuickShapes" \
  --noconsole \
  src/main.py

chmod +x dist/AbCS
abcs_write_linux_dist_assets dist

if [[ ! -f dist/install_abcs.sh ]]; then
  echo "ERROR: dist/install_abcs.sh was not created." >&2
  exit 1
fi

echo
echo "dist contents:"
ls -la dist/

echo
echo "Build complete: dist/AbCS"
echo "Test package: zip the dist/ folder; testers run ./install_abcs.sh (see dist/README.txt)"
echo "Optional launcher: copy dist/AbCS.desktop to ~/.local/share/applications/ then run: update-desktop-database ~/.local/share/applications"
echo
echo "Expected PyInstaller warnings on Linux (safe to ignore):"
echo "  - Library user32 / msvcrt not found (Windows-only ctypes checks)"
