#!/usr/bin/env bash
set -euo pipefail

# Rebuild repo .venv for older CPUs missing SSE4.2/POPCNT.
# This uses Python 3.12 + PySide6 < 6.7, which works on this hardware class.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

if ! command -v python3.12 >/dev/null 2>&1; then
  echo "ERROR: python3.12 is required but not found."
  echo "Install it first, then rerun this script."
  exit 1
fi

BACKUP_DIR=""
if [[ -d ".venv" ]]; then
  stamp="$(date +%Y%m%d_%H%M%S)"
  BACKUP_DIR=".venv_backup_${stamp}"
  echo "Backing up existing .venv -> ${BACKUP_DIR}"
  mv .venv "${BACKUP_DIR}"
fi

echo "Creating new .venv with python3.12..."
python3.12 -m venv .venv
source .venv/bin/activate

echo "Installing dependencies (legacy-CPU compatible Qt stack)..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt "PySide6<6.7"

echo
echo "Installed versions:"
python -m pip show PySide6 shiboken6 | sed -n '1,40p'

echo
echo "Smoke test: importing QtCore..."
python - <<'PY'
from PySide6 import QtCore
print(f"Qt runtime version: {QtCore.qVersion()}")
PY

echo
echo "Legacy CPU environment fix complete."
echo "Use: source .venv/bin/activate && python src/main.py"
if [[ -n "${BACKUP_DIR}" ]]; then
  echo "Old environment backup: ${BACKUP_DIR}"
fi
