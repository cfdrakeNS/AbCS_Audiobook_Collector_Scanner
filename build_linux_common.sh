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

  # Linux desktops read PNG icons reliably; ICO often fails to embed in the ELF binary.
  if [[ -f "graphics/abcs_icon_256x256.png" ]]; then
    args+=(--icon="graphics/abcs_icon_256x256.png")
  elif [[ -f "Graphics/abcs_icon_256x256.png" ]]; then
    args+=(--icon="Graphics/abcs_icon_256x256.png")
  elif [[ -f "graphics/abcs_icon_256x256.ico" ]]; then
    args+=(--icon="graphics/abcs_icon_256x256.ico")
  elif [[ -f "Graphics/abcs_icon_256x256.ico" ]]; then
    args+=(--icon="Graphics/abcs_icon_256x256.ico")
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
Comment=Audio Book Collector Scanner
Exec=${exec_path}
Icon=${icon_path}
Terminal=false
Categories=Utility;Audio;Office;
StartupWMClass=AbCS
EOF

  echo "Wrote ${dist_dir}/AbCS.desktop"
  if [[ -f "${dist_dir}/${icon_name}" ]]; then
    echo "Copied ${dist_dir}/${icon_name} for launchers and file managers"
  fi
}
