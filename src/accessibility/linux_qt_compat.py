"""Linux Qt compatibility: logging noise and minimal stylesheet strategy."""

from __future__ import annotations

import os
import sys


def install_linux_qt_compat() -> None:
    """Call before QApplication() on Linux.

    Fusion + application stylesheets can leave unbalanced QPainter stacks on some
    widgets. The UI still renders correctly; suppress the known harmless warning.
    """
    if not sys.platform.startswith("linux"):
        return

    suppress = "qt.gui.painting.warning=false"
    existing = os.environ.get("QT_LOGGING_RULES", "").strip()
    if "qt.gui.painting" not in existing:
        os.environ["QT_LOGGING_RULES"] = (
            f"{existing};{suppress}".strip(";") if existing else suppress
        )


def build_linux_scale_stylesheet(scaled_size: int, scale_percent: int) -> str:
    """Minimal zoom stylesheet for Linux (font + tables only)."""
    row_padding = int(8 * scale_percent / 100)
    status_size = int(scaled_size * 0.9)
    return f"""
        * {{
            font-size: {scaled_size}pt;
        }}
        QTableWidget::item:hover, QTableView::item:hover {{
            background: none !important;
        }}
        QTableView::item:selected,
        QTableView::item:selected:focus {{
            background-color: palette(highlight);
            color: palette(highlighted-text);
        }}
        QTableView::item {{
            padding: {row_padding}px;
        }}
        QStatusBar {{
            font-size: {status_size}pt;
        }}
    """


def build_linux_theme_stylesheet(table_rules: str, scale_block: str = "") -> str:
    """Palette carries colors on Linux; keep only table + scale rules."""
    parts = [table_rules.strip()]
    if scale_block.strip():
        parts.append(scale_block.strip())
    return "\n\n".join(parts)
