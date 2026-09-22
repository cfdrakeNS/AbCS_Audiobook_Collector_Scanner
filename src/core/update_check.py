"""Compare the installed AbCS version with the latest GitHub release."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from src.app_urls import ABCS_GITHUB_LATEST_RELEASE_API_URL
from src.build_config import APP_VERSION

CHECK_TIMEOUT_SECONDS = 8.0


class UpdateCheckError(Exception):
    """A check finished without a usable version."""


@dataclass
class UpdateCheckResult:
    current: str
    latest: str = ""
    update_available: bool = False
    error: str = ""

    @property
    def ok(self) -> bool:
        return not self.error


def parse_version(text: str) -> tuple[int, ...]:
    """Turn ``v2.15`` or ``2.15.1`` into a number tuple. Non-numeric tails are ignored."""
    raw = (text or "").strip()
    if raw[:1].lower() == "v":
        raw = raw[1:]
    raw = raw.split("-", 1)[0].strip()
    parts: list[int] = []
    for piece in raw.split("."):
        digits = ""
        for char in piece:
            if char.isdigit():
                digits += char
            else:
                break
        if digits:
            parts.append(int(digits))
    return tuple(parts)


def is_newer_version(latest: str, current: str) -> bool:
    """True when ``latest`` is a higher release than ``current``."""
    left = parse_version(latest)
    right = parse_version(current)
    if not left or not right:
        return False
    width = max(len(left), len(right))
    left = left + (0,) * (width - len(left))
    right = right + (0,) * (width - len(right))
    return left > right


def display_version(text: str) -> str:
    raw = (text or "").strip()
    if raw[:1].lower() == "v":
        raw = raw[1:]
    return raw or text


def result_message(result: UpdateCheckResult) -> str:
    """Sentence spoken in the dialog and on the main status bar."""
    if result.error:
        return result.error
    current = display_version(result.current)
    latest = display_version(result.latest)
    if result.update_available:
        return (
            f"Version {latest} is available. You have version {current}. "
            "Open download page opens the AbCS website. "
            "This check does not install the update."
        )
    if is_newer_version(result.current, result.latest):
        return (
            f"You have version {current}. "
            f"The latest release is version {latest}. No update is needed."
        )
    return f"Version {current} is up to date."


def fetch_latest_release_tag(timeout: float = CHECK_TIMEOUT_SECONDS) -> str:
    """Return the ``tag_name`` from GitHub ``releases/latest``."""
    from src.build_config import APP_VERSION as version

    request = urllib.request.Request(
        ABCS_GITHUB_LATEST_RELEASE_API_URL,
        headers={
            "User-Agent": f"AbCS/{version}",
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise UpdateCheckError(
            "Could not check for updates. GitHub did not return the version."
        ) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        if isinstance(exc, TimeoutError) or "timed out" in str(exc).lower():
            raise UpdateCheckError(
                "Could not check for updates. The request timed out."
            ) from exc
        raise UpdateCheckError(
            "Could not check for updates. No network connection."
        ) from exc
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise UpdateCheckError(
            "Could not check for updates. The version information was not usable."
        ) from exc

    if not isinstance(payload, dict):
        raise UpdateCheckError(
            "Could not check for updates. The version information was not usable."
        )
    tag = str(payload.get("tag_name") or "").strip()
    if not parse_version(tag):
        raise UpdateCheckError(
            "Could not check for updates. The version information was not usable."
        )
    return tag


def check_for_update(
    current: str | None = None, timeout: float = CHECK_TIMEOUT_SECONDS
) -> UpdateCheckResult:
    """Check GitHub and compare with the installed version. Does not open a browser."""
    installed = (current or APP_VERSION).strip()
    try:
        latest = fetch_latest_release_tag(timeout=timeout)
    except UpdateCheckError as exc:
        return UpdateCheckResult(current=installed, error=str(exc))
    except Exception:
        return UpdateCheckResult(
            current=installed,
            error="Could not check for updates. The version information was not usable.",
        )
    return UpdateCheckResult(
        current=installed,
        latest=latest,
        update_available=is_newer_version(latest, installed),
    )
