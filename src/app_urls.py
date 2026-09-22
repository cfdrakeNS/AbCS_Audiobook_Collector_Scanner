"""Public URLs for AbCS and Aurora Accessibility."""

ABCS_WEBSITE_URL = "https://abcs.auroraaccessibility.com/"
# TEMPORARY Phase 7 testing. Help → Website and Open download page use this
# Carrd test site. Before merging to main, point this back at ABCS_WEBSITE_URL.
ABCS_UPDATE_DOWNLOAD_URL = "https://abcstest.carrd.co/"
AURORA_WEBSITE_URL = "https://auroraaccessibility.com/"
ABCS_GITHUB_RELEASES_URL = (
    "https://github.com/cfdrakeNS/AbCS_Audiobook_Collector_Scanner/releases"
)
ABCS_GITHUB_LATEST_RELEASE_API_URL = (
    "https://api.github.com/repos/cfdrakeNS/"
    "AbCS_Audiobook_Collector_Scanner/releases/latest"
)


def open_public_url(url: str) -> bool:
    """Open a public http(s) page in the default browser."""
    import os
    import sys
    import webbrowser

    target = (url or "").strip()
    if not target:
        return False
    if sys.platform == "win32":
        try:
            os.startfile(target)  # noqa: S606 - user asked to open this URL
            return True
        except OSError:
            pass
    try:
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        if QDesktopServices.openUrl(QUrl(target)):
            return True
    except Exception:
        pass
    try:
        return bool(webbrowser.open(target))
    except Exception:
        return False
