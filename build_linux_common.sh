#!/usr/bin/env bash
# Shared PyInstaller helpers for Linux build scripts.

abcs_pyinstaller_graphics_args() {
  local args=()

  if [[ -d "graphics" ]]; then
    args+=(--add-data="graphics:graphics")
  elif [[ -d "Graphics" ]]; then
    args+=(--add-data="Graphics:graphics")
  else
    echo "WARNING: graphics/ not found — window icons and About splash will be missing from the build." >&2
  fi

  if [[ -f "graphics/abcs_icon_256x256.ico" ]]; then
    args+=(--icon="graphics/abcs_icon_256x256.ico")
  elif [[ -f "graphics/abcs_icon_256x256.png" ]]; then
    args+=(--icon="graphics/abcs_icon_256x256.png")
  elif [[ -f "Graphics/abcs_icon_256x256.ico" ]]; then
    args+=(--icon="Graphics/abcs_icon_256x256.ico")
  fi

  printf '%s\n' "${args[@]}"
}
