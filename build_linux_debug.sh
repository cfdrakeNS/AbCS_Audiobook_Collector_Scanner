#!/usr/bin/env bash
set -euo pipefail

# Build and run AbCS on Linux with console output enabled.
# Use this when the app does not launch and you need a clear error log.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

BUILD_LOG_FILE="${SCRIPT_DIR}/abcs_linux_build.log"
RUN_LOG_FILE="${SCRIPT_DIR}/abcs_linux_run.log"

# Always capture setup/build output, including early failures.
: > "${BUILD_LOG_FILE}"
exec > >(tee -a "${BUILD_LOG_FILE}") 2>&1

echo "Repository directory: ${SCRIPT_DIR}"
echo "Build log file: ${BUILD_LOG_FILE}"
echo "Run log file: ${RUN_LOG_FILE}"

if [[ ! -f "src/main.py" ]]; then
  echo "ERROR: src/main.py not found in ${SCRIPT_DIR}."
  exit 1
fi

# Find virtual environment (accept both venv and .venv)
VENV_DIR=""
if [[ -d "venv" ]]; then
  VENV_DIR="venv"
elif [[ -d ".venv" ]]; then
  VENV_DIR=".venv"
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
  VENV_DIR="venv"
fi

source "${VENV_DIR}/bin/activate"

echo "Installing/updating build dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo "Cleaning old build artifacts..."
rm -rf build dist

# shellcheck disable=SC1091
source "$(dirname "$0")/build_linux_common.sh"
mapfile -t GRAPHICS_ARGS < <(abcs_pyinstaller_graphics_args)

echo "Building Linux debug executable (dist/AbCS)..."
python -m PyInstaller \
  --name="AbCS" \
  --onefile \
  --console \
  --log-level=INFO \
  --clean \
  --noconfirm \
  --add-data="data/abcdDB_def.sql:data" \
  "${GRAPHICS_ARGS[@]}" \
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
  src/main.py

chmod +x dist/AbCS
abcs_write_linux_dist_assets dist

echo
echo "Running dist/AbCS with logging..."
echo "Log file: ${RUN_LOG_FILE}"

: > "${RUN_LOG_FILE}"

set +e
./dist/AbCS 2>&1 | tee "${RUN_LOG_FILE}"
app_exit=${PIPESTATUS[0]}
set -e

if [[ ${app_exit} -ne 0 ]]; then
  echo
  echo "AbCS exited with code ${app_exit}."
  echo "Review ${RUN_LOG_FILE} for the exact startup error."

  if grep -qi 'platform plugin "xcb"' "${RUN_LOG_FILE}"; then
    echo
    echo "Detected a Qt xcb platform dependency issue."
    echo "Try: sudo apt install -y libxcb-cursor0 libxkbcommon-x11-0 libgl1 libegl1"
  fi

  exit ${app_exit}
fi

echo
echo "AbCS closed normally."
echo "Runtime output saved to ${RUN_LOG_FILE}."
