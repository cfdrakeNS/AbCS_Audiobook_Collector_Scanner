"""Tests for dynamic SQLite PRAGMA sizing."""

from unittest.mock import MagicMock, patch

from src.database.connection import (
    DEFAULT_SQLITE_CACHE_KB,
    DEFAULT_SQLITE_MMAP_BYTES,
    _compute_sqlite_pragmas,
)


def _mock_db_size(db_bytes: int, wal_bytes: int = 0):
    """Return exists/getsize side effects for db_path and db_path-wal."""

    def exists(path: str) -> bool:
        return path.endswith(".db") or path.endswith(".db-wal")

    def getsize(path: str) -> int:
        if path.endswith(".db-wal"):
            return wal_bytes
        return db_bytes

    return exists, getsize


def _ram_mock(gb: int) -> MagicMock:
    ram = MagicMock()
    ram.total = gb * 1024 * 1024 * 1024
    return ram


@patch("src.database.connection.os.path.getsize")
@patch("src.database.connection.os.path.exists", return_value=False)
def test_missing_db_uses_defaults(_mock_exists, _mock_getsize):
    cache_kb, mmap_bytes = _compute_sqlite_pragmas("/tmp/missing.db")
    assert cache_kb == DEFAULT_SQLITE_CACHE_KB
    assert mmap_bytes == DEFAULT_SQLITE_MMAP_BYTES


@patch("psutil.virtual_memory")
@patch("src.database.connection.os.path.getsize")
@patch("src.database.connection.os.path.exists")
def test_small_db_on_16gb_ram_keeps_desktop_floor(mock_exists, mock_getsize, mock_virtual_memory):
    exists, getsize = _mock_db_size(int(1.7 * 1024 * 1024))
    mock_exists.side_effect = exists
    mock_getsize.side_effect = getsize
    mock_virtual_memory.return_value = _ram_mock(16)

    cache_kb, mmap_bytes = _compute_sqlite_pragmas("/data/abcs.db")

    assert cache_kb == -32768  # 32 MB floor on 8 GB+ machines
    assert mmap_bytes == 134217728  # 128 MB floor on 8 GB+ machines


@patch("psutil.virtual_memory")
@patch("src.database.connection.os.path.getsize")
@patch("src.database.connection.os.path.exists")
def test_30mb_db_on_16gb_ram_scales_up(mock_exists, mock_getsize, mock_virtual_memory):
    exists, getsize = _mock_db_size(30 * 1024 * 1024)
    mock_exists.side_effect = exists
    mock_getsize.side_effect = getsize
    mock_virtual_memory.return_value = _ram_mock(16)

    cache_kb, mmap_bytes = _compute_sqlite_pragmas("/data/abcs.db")

    assert cache_kb == -61440  # 60 MB (30 * 2)
    assert mmap_bytes == 134217728  # 120 MB scaled, floored to 128 MB on 8 GB+


@patch("psutil.virtual_memory")
@patch("src.database.connection.os.path.getsize")
@patch("src.database.connection.os.path.exists")
def test_30mb_db_on_4gb_ram_respects_lower_caps(mock_exists, mock_getsize, mock_virtual_memory):
    exists, getsize = _mock_db_size(30 * 1024 * 1024)
    mock_exists.side_effect = exists
    mock_getsize.side_effect = getsize
    mock_virtual_memory.return_value = _ram_mock(4)

    cache_kb, mmap_bytes = _compute_sqlite_pragmas("/data/abcs.db")

    assert cache_kb == -61440  # 60 MB
    assert mmap_bytes == 125829120  # 120 MB, no 128 MB desktop floor below 8 GB


@patch("psutil.virtual_memory")
@patch("src.database.connection.os.path.getsize")
@patch("src.database.connection.os.path.exists")
def test_db_size_includes_wal_file(mock_exists, mock_getsize, mock_virtual_memory):
    db_bytes = 10 * 1024 * 1024
    wal_bytes = 5 * 1024 * 1024
    exists, getsize = _mock_db_size(db_bytes, wal_bytes)
    mock_exists.side_effect = exists
    mock_getsize.side_effect = getsize
    mock_virtual_memory.return_value = _ram_mock(16)

    cache_kb, mmap_bytes = _compute_sqlite_pragmas("/data/abcs.db")

    # 15 MB total DB footprint -> cache 30 MB, raised to 32 MB floor on 8 GB+ RAM
    assert cache_kb == -32768  # 32 MB floor
    assert mmap_bytes == 134217728  # 128 MB floor


@patch("psutil.virtual_memory", side_effect=RuntimeError("psutil unavailable"))
@patch("src.database.connection.os.path.getsize")
@patch("src.database.connection.os.path.exists")
def test_psutil_failure_falls_back_to_default_ram_assumption(
    mock_exists, mock_getsize, _mock_virtual_memory
):
    exists, getsize = _mock_db_size(30 * 1024 * 1024)
    mock_exists.side_effect = exists
    mock_getsize.side_effect = getsize

    cache_kb, mmap_bytes = _compute_sqlite_pragmas("/data/abcs.db")

    # 8 GB fallback still applies desktop floor for 30 MB DB
    assert cache_kb == -61440  # 60 MB
    assert mmap_bytes == 134217728  # 128 MB floor via 8 GB fallback
