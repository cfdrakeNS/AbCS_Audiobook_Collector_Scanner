"""Capture repeatable baseline timing metrics for import scanning."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from core.tag_reader import BookScanner  # noqa: E402


@dataclass
class RunMetric:
    run_index: int
    elapsed_seconds: float
    books_found: int


def _count_audio_files(scanner: BookScanner, folder_path: str, include_subfolders: bool) -> int:
    total = 0
    if include_subfolders:
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                full_path = os.path.join(root, file_name)
                if scanner.tag_reader.is_supported_file(full_path):
                    total += 1
        return total

    with os.scandir(folder_path) as entries:
        for entry in entries:
            if entry.is_file() and scanner.tag_reader.is_supported_file(entry.path):
                total += 1
    return total


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record import scan baseline timings.")
    parser.add_argument("--folder", required=True,
                        help="Folder to scan for audio files")
    parser.add_argument("--repeats", type=int, default=3,
                        help="Number of repeated scan runs")
    parser.add_argument("--subfolders", action="store_true",
                        help="Include subfolders in scan")
    parser.add_argument(
        "--json-out", help="Optional path to write metrics JSON")
    args = parser.parse_args()

    folder_path = os.path.abspath(args.folder)
    if not os.path.isdir(folder_path):
        print(f"ERROR: Folder not found: {folder_path}")
        return 2

    if args.repeats < 1:
        print("ERROR: --repeats must be >= 1")
        return 2

    scanner = BookScanner()
    audio_files = _count_audio_files(scanner, folder_path, args.subfolders)

    run_metrics: list[RunMetric] = []
    for run_index in range(1, args.repeats + 1):
        started = time.perf_counter()
        books = scanner.scan_folder(
            folder_path,
            include_subfolders=args.subfolders,
            allowed_extensions=None,
            progress_callback=None,
            cancel_check=None,
        )
        elapsed = time.perf_counter() - started
        run_metrics.append(
            RunMetric(
                run_index=run_index,
                elapsed_seconds=round(elapsed, 4),
                books_found=len(books),
            )
        )

    elapsed_values = [item.elapsed_seconds for item in run_metrics]
    summary = {
        "captured_at": datetime.now().isoformat(timespec="seconds"),
        "folder": folder_path,
        "include_subfolders": args.subfolders,
        "repeats": args.repeats,
        "audio_files_detected": audio_files,
        "avg_elapsed_seconds": round(statistics.mean(elapsed_values), 4),
        "min_elapsed_seconds": round(min(elapsed_values), 4),
        "max_elapsed_seconds": round(max(elapsed_values), 4),
        "runs": [asdict(item) for item in run_metrics],
    }

    print("Import Scan Baseline")
    print(f"Folder: {summary['folder']}")
    print(f"Audio files detected: {summary['audio_files_detected']}")
    print(
        f"Runs: {summary['repeats']} | Include subfolders: {summary['include_subfolders']}")
    print(
        "Elapsed seconds (avg/min/max): "
        f"{summary['avg_elapsed_seconds']} / {summary['min_elapsed_seconds']} / {summary['max_elapsed_seconds']}"
    )
    for run in summary["runs"]:
        print(
            f"  Run {run['run_index']}: {run['elapsed_seconds']}s | books_found={run['books_found']}"
        )

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"Wrote JSON metrics: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
