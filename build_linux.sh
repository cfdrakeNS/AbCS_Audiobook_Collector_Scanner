#!/usr/bin/env bash
set -euo pipefail

# Build AbCS Linux executable with PyInstaller.
# Run from repository root: ./build_linux.sh

if [[ ! -f "src/main.py" ]]; then
  echo "ERROR: Run this script from the repository root (src/main.py not found)."
  exit 1
fi

if [[ ! -d ".venv" ]]; then
  echo "ERROR: .venv not found. Create it first: python3 -m venv .venv"
  exit 1
fi

source .venv/bin/activate

if ! python -m pip show pyinstaller >/dev/null 2>&1; then
  echo "Installing PyInstaller..."
  python -m pip install pyinstaller
fi

echo "Cleaning old build artifacts..."
rm -rf build dist

echo "Building Linux executable (dist/AbCS)..."
python -m PyInstaller \
  --name="AbCS" \
  --onefile \
  --windowed \
  --log-level=WARN \
  --clean \
  --noconfirm \
  --add-data="data/abcdDB_def.sql:data" \
  --hidden-import="PySide6.QtCore" \
  --hidden-import="PySide6.QtGui" \
  --hidden-import="PySide6.QtWidgets" \
  --hidden-import="mutagen" \
  --hidden-import="mutagen.mp3" \
  --hidden-import="mutagen.mp4" \
  --hidden-import="mutagen.flac" \
  --hidden-import="mutagen.oggvorbis" \
  --hidden-import="mutagen.wave" \
  --exclude-module="PySide6.QtSql" \
  --exclude-module="PySide6.QtQml" \
  --exclude-module="PySide6.QtQuick" \
  --exclude-module="PySide6.QtQuickShapes" \
  --noconsole \
  src/main.py

echo
echo "Build complete: dist/AbCS"
