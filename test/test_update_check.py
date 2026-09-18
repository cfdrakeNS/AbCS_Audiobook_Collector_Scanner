"""Tests for update version comparison."""

from src.core.update_check import is_newer_version


def test_is_newer_version_basic():
    assert is_newer_version("2.15", "2.14")
    assert not is_newer_version("2.14", "2.14")
    assert not is_newer_version("2.13", "2.14")


def test_is_newer_version_strips_v_prefix():
    assert is_newer_version("v2.15", "2.14")
