"""Drop Qt files AbCS does not use from a PyInstaller build.

Qt Virtual Keyboard is GPL-3.0-only. Qt PDF, Qt QML, Qt Quick, and the Mesa
software OpenGL renderer are unused. The Qt libraries AbCS does load do not
import these files.
"""

from PyInstaller.building.datastruct import TOC

# Matched against the file name PyInstaller will install, not the full path.
_MARKERS = (
    "qt6virtualkeyboard",
    "qtvirtualkeyboard",
    "qt6pdf",
    "qt6qml",
    "qt6quick",
    "opengl32sw",
)
# The PDF image-plugin file name, without matching Qt6Pdf itself.
_PDF_PLUGIN_STEMS = ("qpdf", "libqpdf")


def is_unused_qt(name):
    lowered = str(name).replace("\\", "/").lower()
    base = lowered.rsplit("/", 1)[-1]
    stem = base.split(".", 1)[0]
    if stem in _PDF_PLUGIN_STEMS:
        return True
    return any(marker in base for marker in _MARKERS)


def drop_unused_qt(toc):
    kept = []
    dropped = []
    for entry in toc:
        if is_unused_qt(entry[0]):
            dropped.append(entry[0])
        else:
            kept.append(entry)
    for name in dropped:
        print(f"AbCS build excluded unused Qt file: {name}")
    return TOC(kept)
