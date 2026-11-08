#!/usr/bin/env python3
"""Build doc/third_party_licenses/qt_bundled_components.txt from Qt source tarballs.

PySide6 ships Qt binaries without license files. Qt keeps the licenses of the
third-party code built into those binaries in its source tree
(src/3rdparty/*/qt_attribution.json plus license files). This tool downloads the
Qt source archives that match the PySide6 version, reads those files, and writes
one text fragment that scripts/generate_third_party_notices.py includes.

Run it only when PySide6 changes version:
    python scripts/extract_qt_notices.py            (version from installed PySide6)
    python scripts/extract_qt_notices.py 6.11.2     (explicit version)

Archives are cached in the system temp folder under abcs_qt_src.
"""

from __future__ import annotations

import json
import os
import posixpath
import re
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "doc" / "third_party_licenses" / "qt_bundled_components.txt"

# Third-party code that is built into the Windows Qt binaries AbCS ships.
INCLUDE = {
    "qtbase": [
        "src/3rdparty/D3D12MemoryAllocator",
        "src/3rdparty/VulkanMemoryAllocator",
        "src/3rdparty/blake2",
        "src/3rdparty/double-conversion",
        "src/3rdparty/easing",
        "src/3rdparty/emoji-segmenter",
        "src/3rdparty/freetype",
        "src/3rdparty/harfbuzz-ng",
        "src/3rdparty/icc",
        "src/3rdparty/libjpeg",
        "src/3rdparty/libpng",
        "src/3rdparty/libpsl",
        "src/3rdparty/md4",
        "src/3rdparty/md4c",
        "src/3rdparty/md5",
        "src/3rdparty/pcre2",
        "src/3rdparty/rfc6234",
        "src/3rdparty/sha1",
        "src/3rdparty/sha3",
        "src/3rdparty/siphash",
        "src/3rdparty/tinycbor",
        "src/3rdparty/wintab",
        "src/3rdparty/zlib",
        "src/corelib/global",
        "src/corelib/mimetypes/3rdparty",
        "src/corelib/text",
        "src/gui/opengl",
        "src/gui/painting",
        "src/gui/rhi",
        "src/gui/text",
    ],
    "qtdeclarative": ["src/3rdparty/masm"],
    "qtimageformats": ["src/3rdparty/libtiff", "src/3rdparty/libwebp"],
    "qtmultimedia": [
        "src/3rdparty/dr_libs",
        "src/3rdparty/eigen",
        "src/3rdparty/ffmpeg",
        "src/3rdparty/pffft",
        "src/3rdparty/resonance-audio",
        "src/3rdparty/signalsmith-stretch",
        "src/3rdparty/tlsf",
    ],
    "qtsvg": ["src/svg"],
    "qtvirtualkeyboard": [
        "src/plugins/openwnn/3rdparty/openwnn",
        "src/plugins/pinyin/3rdparty/pinyin",
        "src/plugins/tcime/3rdparty/tcime",
    ],
}

LICENSE_NAME_HINTS = ("licen", "copying", "copyright", "notice")
SKIP_IDS = {"LicenseRef-Qt-Commercial"}


def qt_version() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]
    import importlib.metadata as md

    return md.version("PySide6")


def load_module(module: str, version: str) -> dict[str, bytes]:
    """Return {path inside archive: bytes} for license-related files."""
    cache = Path(tempfile.gettempdir()) / "abcs_qt_src"
    cache.mkdir(exist_ok=True)
    name = f"{module}-everywhere-src-{version}.tar.xz"
    archive = cache / name
    if not archive.exists():
        major_minor = ".".join(version.split(".")[:2])
        url = f"https://download.qt.io/archive/qt/{major_minor}/{version}/submodules/{name}"
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, archive)
    prefixes = tuple(p for p in INCLUDE[module])
    files: dict[str, bytes] = {}
    with tarfile.open(archive) as tar:
        for member in tar:
            if not member.isfile() or member.size > 2_000_000:
                continue
            rel = member.name.split("/", 1)[1] if "/" in member.name else member.name
            if rel.startswith("LICENSES/") or rel.startswith(prefixes):
                files[rel] = tar.extractfile(member).read()
    return files


def ids_in(expression: str) -> list[str]:
    parts = re.split(r"\s+(?:AND|OR|WITH)\s+|[()]", expression or "")
    return [p.strip() for p in parts if p and p.strip()]


def text_of(data: bytes) -> str:
    return data.decode("utf-8", errors="replace").replace("\r\n", "\n").strip("\n")


def main() -> int:
    version = qt_version()
    seen: dict[int, str] = {}
    entries: list[str] = []
    count = 0
    for module in INCLUDE:
        files = load_module(module, version)
        for directory in INCLUDE[module]:
            attr = files.get(f"{directory}/qt_attribution.json")
            if attr is None:
                print(f"WARNING: no attribution for {module}/{directory}")
                continue
            data = json.loads(attr.decode("utf-8"), strict=False)
            if isinstance(data, dict):
                data = [data]
            for entry in data:
                count += 1
                name = entry.get("Name", entry.get("Id", directory))
                lines = [
                    "-" * 72,
                    f"{name}" + (f" {entry['Version']}" if re.fullmatch(r"\d[\w.\-]{0,24}", entry.get("Version") or "") else ""),
                    f"  Qt module : {module}",
                ]
                if entry.get("Homepage"):
                    lines.append(f"  Homepage  : {entry['Homepage']}")
                lines.append(f"  License   : {entry.get('LicenseId') or entry.get('License')}")
                copyright_text = entry.get("Copyright") or ""
                if isinstance(copyright_text, list):
                    copyright_text = "\n              ".join(copyright_text)
                if copyright_text:
                    lines.append(f"  Copyright : {copyright_text.strip()}")
                usage = (entry.get("QtUsage") or "").replace("\\l ", "").replace("\n", " ")
                usage = re.sub(r"\{([^}]*)\}\{([^}]*)\}", r"\2 (\1)", usage)
                if usage:
                    lines.append(f"  Used for  : {usage.strip()}")
                lines.append("")
                texts: list[tuple[str, str]] = []
                if entry.get("LicenseFile"):
                    path = posixpath.normpath(posixpath.join(directory, entry["LicenseFile"]))
                    if path in files:
                        texts.append((path, text_of(files[path])))
                else:
                    for spdx in ids_in(entry.get("LicenseId", "")):
                        if spdx in SKIP_IDS:
                            continue
                        hit = [p for p in files if p.startswith(directory + "/")
                               and spdx.lower() in posixpath.basename(p).lower()]
                        if hit:
                            texts.append((hit[0], text_of(files[hit[0]])))
                        elif f"LICENSES/{spdx}.txt" in files:
                            texts.append((f"LICENSES/{spdx}.txt", text_of(files[f"LICENSES/{spdx}.txt"])))
                    if not texts:
                        for p in sorted(files):
                            base = posixpath.basename(p).lower()
                            if posixpath.dirname(p) == directory and any(h in base for h in LICENSE_NAME_HINTS):
                                texts.append((p, text_of(files[p])))
                for path, body in texts:
                    key = hash(body)
                    if key in seen:
                        lines.append(f"[License text '{posixpath.basename(path)}' is identical to the one shown under {seen[key]}.]")
                    else:
                        seen[key] = name
                        lines.append(f"[License text: {posixpath.basename(path)}]")
                        lines.append("")
                        lines.append(body)
                    lines.append("")
                entries.append("\n".join(lines))

    header = (
        f"QT {version} BUNDLED THIRD-PARTY COMPONENTS\n"
        + "=" * 72
        + "\nThe Qt libraries that ship with AbCS (through PySide6) contain the third-party\n"
        "code listed below. Each entry shows the license and copyright notice that\n"
        "Qt documents for it. Source: the attribution files in the Qt "
        f"{version} source release\n(https://download.qt.io/archive/qt/).\n\n"
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(header + "\n".join(entries) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {OUT} ({count} components, {OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
