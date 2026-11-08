#!/usr/bin/env python3
"""Write AbCS_Third_Party_Notices.txt (installed with the app by build_installer.iss).

The file combines:
  * license files read from the installed Python packages (exact versions in use),
  * Python's own LICENSE.txt,
  * static texts kept in doc/third_party_licenses/ (GNU/Apache texts, Python
    runtime libraries, Qt bundled components from scripts/extract_qt_notices.py).

Run before every installer build (and after any dependency upgrade):
    python scripts/generate_third_party_notices.py
"""

from __future__ import annotations

import importlib.metadata as md
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXTS = ROOT / "doc" / "third_party_licenses"
OUT = ROOT / "AbCS_Third_Party_Notices.txt"

BAR = "=" * 72
RULE = "-" * 72
HINTS = ("licen", "copying", "notice", "authors")

# (distribution name, shown name, what AbCS uses it for, license summary, extra note)
PACKAGES = [
    ("pandas", "pandas", "Spreadsheet import (CSV, Excel, ODS)", "BSD-3-Clause", ""),
    ("numpy", "NumPy", "Required by pandas", "BSD-3-Clause and bundled components (see text)", ""),
    ("python-dateutil", "python-dateutil", "Required by pandas", "BSD-3-Clause / Apache-2.0", ""),
    ("six", "six", "Required by python-dateutil", "MIT", ""),
    ("tzdata", "tzdata", "Time zone data for pandas", "Apache-2.0", ""),
    ("pillow", "Pillow", "Collected by the build (image library)", "MIT-CMU (HPND)", ""),
    ("psutil", "psutil", "Screen reader detection", "BSD-3-Clause", ""),
    ("openpyxl", "openpyxl", "Excel (.xlsx) import", "MIT", ""),
    ("et_xmlfile", "et_xmlfile", "Required by openpyxl", "MIT", ""),
    (
        "odfpy", "odfpy", "OpenDocument (.ods) import and user guide export",
        "LGPL-2.1-or-later",
        "Copyright (C) 2006-2010 Soren Roug, European Environment Agency.\n"
        "Contributors: see the headers of the odfpy source files, for example\n"
        "Copyright (C) 2014 Georges Khaznadar.\n"
        "Licensed under the GNU Lesser General Public License, version 2.1 or\n"
        "(at your option) any later version. Full text: Appendix C.\n"
        "Source code: https://github.com/eea/odfpy\n"
        "odfpy is pure Python code. AbCS source is available, so a modified odfpy\n"
        "can be rebuilt into AbCS.",
    ),
    ("defusedxml", "defusedxml", "Required by openpyxl and odfpy", "PSF-2.0", ""),
    ("Jinja2", "Jinja2", "Collected by the build (optional pandas dependency)", "BSD-3-Clause", ""),
    ("MarkupSafe", "MarkupSafe", "Required by Jinja2", "BSD-3-Clause", ""),
    ("charset-normalizer", "charset-normalizer", "Collected by the build", "MIT", ""),
    ("typing_extensions", "typing_extensions", "Collected by the build", "PSF-2.0", ""),
    ("packaging", "packaging", "Collected by the build", "Apache-2.0 OR BSD-2-Clause", ""),
    ("pluggy", "pluggy", "Collected by the build", "MIT", ""),
    ("iniconfig", "iniconfig", "Collected by the build", "MIT", ""),
    ("colorama", "colorama", "Collected by the build", "BSD-3-Clause", ""),
    ("Pygments", "Pygments", "Collected by the build", "BSD-2-Clause", ""),
    ("pytest", "pytest", "Collected by the build", "MIT", ""),
    ("setuptools", "setuptools", "Collected by the build", "MIT (and vendored packages)", ""),
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").strip("\n")


def license_files(dist_name: str) -> list[tuple[str, str]]:
    """Return [(file name, text)] for license-like files in a distribution."""
    dist = md.distribution(dist_name)
    found: list[tuple[str, str]] = []
    seen: set[str] = set()
    for f in dist.files or []:
        text_path = str(f).replace("\\", "/")
        base = text_path.rsplit("/", 1)[-1].lower()
        if ".dist-info/" not in text_path or not any(h in base for h in HINTS):
            continue
        if "commercial" in base:
            continue
        body = read(Path(dist.locate_file(f)))
        if body in seen:
            continue
        seen.add(body)
        label = text_path.split(".dist-info/", 1)[1]
        found.append((label, body))
    return found


def section(title: str) -> str:
    return f"\n\n{BAR}\n{title}\n{BAR}\n\n"


def main() -> int:
    for needed in ("GPL-3.0.txt", "LGPL-3.0.txt", "LGPL-2.1.txt", "Apache-2.0.txt",
                   "runtime_components.txt", "qt_bundled_components.txt"):
        if not (TEXTS / needed).exists():
            print(f"ERROR: missing {TEXTS / needed}")
            return 1

    py_ver = ".".join(map(str, sys.version_info[:3]))
    pyside = md.version("PySide6")
    mutagen_ver = md.version("mutagen")
    out: list[str] = []

    out.append(
        "AbCS - Audiobook Collector Scanner\n"
        "THIRD-PARTY NOTICES\n\n"
        "AbCS itself is licensed under the AbCS Free Use and Non-Sale License,\n"
        "Version 1.0 (see AbCS_License.txt in this folder). AbCS includes and uses\n"
        "the third-party software listed below. Each component is covered by its own\n"
        "license, and those licenses are not changed by the AbCS license. This file\n"
        "gives the copyright notices and license texts those licenses require.\n"
    )

    out.append(section("1. SUMMARY"))
    rows = [
        (f"Python {py_ver}", "Python runtime", "PSF License 2.0"),
        (f"PySide6 {pyside} / Shiboken6", "Qt for Python bindings", "LGPL-3.0-only"),
        (f"Qt {pyside}", "User interface toolkit (Qt libraries)", "LGPL-3.0-only (see section 4)"),
        ("FFmpeg 7.1.3 (inside Qt Multimedia)", "Audio playback", "LGPL-2.1-or-later"),
        (f"Mutagen {mutagen_ver}", "Reads audio tags and cover art", "GPL-2.0-or-later"),
    ]
    for dist_name, shown, role, lic, _ in PACKAGES:
        rows.append((f"{shown} {md.version(dist_name)}", role, lic))
    width = max(len(r[0]) for r in rows)
    for name, role, lic in rows:
        out.append(f"{name.ljust(width)}  {lic}\n{' ' * width}  Used for: {role}\n")
    out.append(
        "\nSections 3 to 7 give the notices. Appendices A to D give the full texts of the\n"
        "GNU Lesser General Public License 3.0 and 2.1, the GNU General Public License\n"
        "3.0, and the Apache License 2.0. The GNU General Public License 2.0 is in\n"
        "section 5 with Mutagen.\n"
    )

    out.append(section("2. WHERE TO GET SOURCE CODE AND HOW TO REPLACE LIBRARIES"))
    out.append(
        "Several components below are licensed under the GNU Lesser General Public\n"
        "License (LGPL) or the GNU General Public License (GPL). These licenses give you\n"
        "these rights, which AbCS does not restrict:\n\n"
        "* You can get the complete source code of those components from the\n"
        "  locations listed in each section. If a location is unavailable, ask through\n"
        "  https://auroraaccessibility.com/ and the corresponding source will be\n"
        "  provided.\n"
        "* You can replace the Qt, PySide6, and FFmpeg libraries with your own\n"
        "  modified builds of the same version. In the install folder they are separate\n"
        "  files (Qt6*.dll, avcodec-*.dll, avformat-*.dll, avutil-*.dll,\n"
        "  swresample-*.dll, swscale-*.dll, and the PySide6 and shiboken6 .pyd and .dll\n"
        "  files in the _internal folder). Replace them with matching files and AbCS\n"
        "  will use them.\n"
        "* You can reverse engineer AbCS to the extent needed to debug such a\n"
        "  modification.\n\n"
        "The AbCS source code is available from the project page linked from the Help\n"
        "menu, Website... item.\n"
    )

    out.append(section(f"3. PYTHON {py_ver}"))
    out.append(
        "AbCS is packaged with the Python runtime.\n"
        "Copyright (c) 2001-2026 Python Software Foundation. All rights reserved.\n"
        "Copyright (c) 2000 BeOpen.com. All rights reserved.\n"
        "Copyright (c) 1995-2001 Corporation for National Research Initiatives.\n"
        "All rights reserved.\n"
        "Copyright (c) 1991-1995 Stichting Mathematisch Centrum. All rights reserved.\n"
        "Source: https://www.python.org/downloads/source/\n\n"
        "The complete Python license follows. Third-party code incorporated into\n"
        "Python is in section 7.\n\n"
    )
    out.append(read(Path(sys.base_prefix) / "LICENSE.txt") + "\n")

    out.append(section(f"4. PYSIDE6 / SHIBOKEN6 {pyside} AND QT {pyside}"))
    out.append(
        "AbCS uses Qt through PySide6 (Qt for Python) and Shiboken6.\n"
        "Copyright (C) The Qt Company Ltd. and other contributors.\n"
        "Qt and PySide6 are licensed to AbCS under the GNU Lesser General Public\n"
        "License, version 3 (LGPL-3.0-only). The text of that license is in Appendix A\n"
        "and it incorporates the GNU General Public License, version 3 (Appendix B).\n\n"
        "Qt and the Qt logo are trademarks of The Qt Company Ltd.\n\n"
        "Source code:\n"
        f"  Qt {pyside}: https://download.qt.io/archive/qt/{'.'.join(pyside.split('.')[:2])}/{pyside}/submodules/\n"
        f"  PySide6 and Shiboken6 {pyside}: https://code.qt.io/cgit/pyside/pyside-setup.git/\n"
        f"    (tag v{pyside}) and https://pypi.org/project/PySide6/{pyside}/#files\n\n"
        "AbCS uses Qt as dynamically linked libraries, so you can replace them as\n"
        "described in section 2.\n\n"
        "NOT INCLUDED: the Windows build leaves out Qt Virtual Keyboard, Qt PDF,\n"
        "Qt QML, Qt Quick, and the Mesa software OpenGL library (opengl32sw.dll).\n"
        "AbCS does not use them. Qt Virtual Keyboard is licensed under the GNU\n"
        "General Public License, version 3 (GPL-3.0-only), not the LGPL, so it is\n"
        "left out of the Windows package. A Linux build that does not apply the same\n"
        "exclusion may still contain it. If it does, that part is covered by the\n"
        "GPL, version 3 (Appendix B). Source: the qtvirtualkeyboard module at the Qt\n"
        "source location above.\n\n"
        "FFMPEG: Qt Multimedia plays audio with FFmpeg 7.1.3 (the files\n"
        "avcodec-61.dll, avformat-61.dll, avutil-59.dll, swresample-5.dll, and\n"
        "swscale-8.dll). This software uses libraries from the FFmpeg project under the\n"
        "LGPLv2.1 or later (full text in Appendix C). Copyright (c) 2000-2023 the\n"
        "FFmpeg developers. Qt states that the FFmpeg binaries it ships do not contain\n"
        "the optional GPL or LGPLv3 components. Source: https://ffmpeg.org/download.html (release n7.1.3).\n"
        "Qt's build scripts: https://code.qt.io/cgit/qt/qt5.git/tree/coin/provisioning\n\n"
    )
    out.append(read(TEXTS / "qt_bundled_components.txt") + "\n")

    out.append(section(f"5. MUTAGEN {mutagen_ver}"))
    out.append(
        "AbCS uses Mutagen to read audio file tags and embedded cover art.\n"
        "Copyright (C) 2005-2020 Joe Wreschnig, Michael Urman, Lukas Lalinsky,\n"
        "Christoph Reiter, Philipp Wolfer, Evan Purkhiser, Borewit, Boris Pruessmann,\n"
        "and other Mutagen contributors (as stated in the Mutagen source file headers).\n"
        "License: GNU General Public License, version 2 or (at your option) any later\n"
        "version (GPL-2.0-or-later). The GPL version 2 text follows.\n\n"
        "Source code for the version included with AbCS:\n"
        f"  https://pypi.org/project/mutagen/{mutagen_ver}/#files\n"
        "  https://github.com/quodlibet/mutagen\n"
        "If those locations are unavailable, ask through https://auroraaccessibility.com/\n"
        "and the complete corresponding source will be provided.\n\n"
    )
    for label, body in license_files("mutagen"):
        out.append(f"[{label}]\n\n{body}\n\n")

    out.append(section("6. OTHER PYTHON PACKAGES"))
    for dist_name, shown, role, lic, note in PACKAGES:
        out.append(f"{RULE}\n{shown} {md.version(dist_name)}\n  Used for : {role}\n  License  : {lic}\n")
        meta = md.metadata(dist_name)
        home = meta.get("Home-page") or next(
            (u.split(",", 1)[1].strip() for u in meta.get_all("Project-URL") or []
             if u.lower().startswith(("homepage", "source", "repository"))), "")
        if home:
            out.append(f"  Project  : {home}\n")
        out.append("\n")
        if note:
            out.append(note + "\n\n")
        for label, body in license_files(dist_name):
            out.append(f"[{label}]\n\n{body}\n\n")

    out.append(section("7. PYTHON RUNTIME LIBRARIES AND OTHER BUNDLED BINARIES"))
    out.append(read(TEXTS / "runtime_components.txt") + "\n")

    out.append(section("APPENDIX A: GNU LESSER GENERAL PUBLIC LICENSE, VERSION 3"))
    out.append(read(TEXTS / "LGPL-3.0.txt") + "\n")
    out.append(section("APPENDIX B: GNU GENERAL PUBLIC LICENSE, VERSION 3"))
    out.append(read(TEXTS / "GPL-3.0.txt") + "\n")
    out.append(section("APPENDIX C: GNU LESSER GENERAL PUBLIC LICENSE, VERSION 2.1"))
    out.append(read(TEXTS / "LGPL-2.1.txt") + "\n")
    out.append(section("APPENDIX D: APACHE LICENSE, VERSION 2.0"))
    out.append(read(TEXTS / "Apache-2.0.txt") + "\n")

    text = "".join(out)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    OUT.write_text(text, encoding="utf-8-sig", newline="\r\n")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
