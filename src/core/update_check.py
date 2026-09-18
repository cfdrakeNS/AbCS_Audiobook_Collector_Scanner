"""Check GitHub releases for a newer AbCS version."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from src.app_urls import ABCS_GITHUB_RELEASES_URL
from src.build_config import APP_VERSION

GITHUB_LATEST_API = (
    "https://api.github.com/repos/cfdrakeNS/AbCS_Audiobook_Collector_Scanner"
    "/releases/latest"
)


@dataclass
class UpdateCheckResult:
    current: str
    latest: str = ""
    is_newer: bool = False
    download_url: str = ABCS_GITHUB_RELEASES_URL
    error: str = ""
    offline: bool = False


def _parse_version(text: str) -> tuple[int, ...]:
    text = (text or "").strip().lstrip("vV")
    # Drop trial suffix like 2.13t
    text = re.sub(r"[a-zA-Z]+$", "", text)
    parts = []
    for piece in text.split("."):
        try:
            parts.append(int(piece))
        except ValueError:
            parts.append(0)
    return tuple(parts) if parts else (0,)


def is_newer_version(latest: str, current: str) -> bool:
    return _parse_version(latest) > _parse_version(current)


def check_for_updates(timeout: float = 8.0) -> UpdateCheckResult:
    """Fetch the latest GitHub release and compare to APP_VERSION."""
    current = APP_VERSION
    result = UpdateCheckResult(current=current)
    req = urllib.request.Request(
        GITHUB_LATEST_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"AbCS/{current}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        result.offline = True
        result.error = f"Could not reach GitHub: {exc}"
        return result
    except Exception as exc:
        result.error = str(exc)
        return result

    tag = str(payload.get("tag_name") or "").strip()
    result.latest = tag.lstrip("vV") or tag
    html_url = (payload.get("html_url") or "").strip()
    if html_url:
        result.download_url = html_url
    if result.latest:
        result.is_newer = is_newer_version(result.latest, current)
    else:
        result.error = "Latest release tag was empty."
    return result
