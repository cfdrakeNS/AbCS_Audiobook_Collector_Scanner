#!/usr/bin/env bash
set -euo pipefail

# Private AbCS build for the HP 6000 Pro and other x86-64-v1 CPUs.
# This deliberately uses Qt 6.3.2, before Qt raised its Linux x86-64
# baseline to SSE4.2/POPCNT. The normal release build remains unchanged.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

VENV_DIR=".venv-legacy"
DIST_DIR="dist-legacy-hp"
WORK_DIR="build-legacy-hp"
LEGACY_PYSIDE_VERSION="6.3.2"
PYTHON_BIN="${LEGACY_PYTHON:-python3.10}"

if [[ ! -f "src/main.py" ]]; then
  echo "ERROR: src/main.py not found in ${SCRIPT_DIR}."
  exit 1
fi

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "ERROR: Python 3.10 is required for the private legacy build."
  echo "Set LEGACY_PYTHON to a Python 3.10 executable if it is not named python3.10."
  echo "On Linux Mint 21: sudo apt install python3.10-venv"
  exit 1
fi

python_version="$("${PYTHON_BIN}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [[ "${python_version}" != "3.10" ]]; then
  echo "ERROR: ${PYTHON_BIN} is Python ${python_version}; Python 3.10 is required."
  exit 1
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "Creating isolated legacy build environment (${VENV_DIR})..."
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

echo "Installing private legacy build dependencies..."
python -m pip install --upgrade pip

# Keep non-Qt dependencies synchronized with requirements.txt while replacing
# only the release PySide6 requirement with the legacy-compatible Qt wheel.
legacy_requirements="$(mktemp)"
trap 'rm -f "${legacy_requirements}"' EXIT
python - "${legacy_requirements}" <<'PY'
from pathlib import Path
import sys

source = Path("requirements.txt").read_text(encoding="utf-8").splitlines()
filtered = [
    line
    for line in source
    if not line.strip().lower().startswith("pyside6")
]
Path(sys.argv[1]).write_text("\n".join(filtered) + "\n", encoding="utf-8")
PY

python -m pip install "PySide6==${LEGACY_PYSIDE_VERSION}"
python -m pip install -r "${legacy_requirements}"
python -m pip install "pyinstaller>=6,<7"

python - <<'PY'
from PySide6 import __version__
from PySide6.QtCore import qVersion

if __version__ != "6.3.2" or qVersion() != "6.3.2":
    raise SystemExit(
        f"ERROR: Expected PySide6/Qt 6.3.2, got PySide6 {__version__}, Qt {qVersion()}."
    )
print(f"Using PySide6 {__version__}, Qt {qVersion()} (legacy CPU build).")
PY

echo "Cleaning only private legacy build artifacts..."
rm -rf "${WORK_DIR}" "${DIST_DIR}"

# shellcheck disable=SC1091
source "${SCRIPT_DIR}/build_linux_common.sh"
mapfile -t GRAPHICS_ARGS < <(abcs_pyinstaller_graphics_args)
mapfile -t HELP_DOCS_ARGS < <(abcs_pyinstaller_help_docs_args)

echo "Building private HP executable (${DIST_DIR}/AbCS)..."
python -m PyInstaller \
  --name="AbCS" \
  --onefile \
  --windowed \
  --log-level=WARN \
  --clean \
  --noconfirm \
  --distpath="${DIST_DIR}" \
  --workpath="${WORK_DIR}" \
  --specpath="${WORK_DIR}" \
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
  src/main.py

chmod +x "${DIST_DIR}/AbCS"
abcs_write_linux_dist_assets "${DIST_DIR}"

cat >>"${DIST_DIR}/README.txt" <<'EOF'

PRIVATE LEGACY CPU BUILD
  This copy uses Qt 6.3.2 for the HP 6000 Pro (no SSE4.2/POPCNT).
  It is for private use only. Do not use it as the public release package.
EOF

echo
echo "Private legacy build complete: ${DIST_DIR}/AbCS"
echo "Copy the entire ${DIST_DIR}/ folder to the HP 6000 Pro."
echo "The normal release build and dist/ folder were not changed."
