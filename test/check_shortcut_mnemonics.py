from __future__ import annotations

import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


MNEMONIC_WIDGETS = (
    "QLabel",
    "QPushButton",
    "QCheckBox",
    "QRadioButton",
    "QAction",
    "QGroupBox",
)


@dataclass
class MnemonicOccurrence:
    key: str
    widget: str
    text: str
    line: int


def extract_mnemonic(text: str) -> str | None:
    """Return mnemonic key from Qt ampersand text, ignoring escaped &&."""
    i = 0
    while i < len(text) - 1:
        if text[i] == "&":
            if text[i + 1] == "&":
                i += 2
                continue
            return text[i + 1].upper()
        i += 1
    return None


def scan_file(file_path: Path) -> list[MnemonicOccurrence]:
    occurrences: list[MnemonicOccurrence] = []
    pattern = re.compile(
        r'(QLabel|QPushButton|QCheckBox|QRadioButton|QAction|QGroupBox)\("([^"]*)"')

    for line_number, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), start=1):
        for match in pattern.finditer(line):
            widget, text = match.groups()
            if "&" not in text:
                continue
            mnemonic = extract_mnemonic(text)
            if mnemonic:
                occurrences.append(
                    MnemonicOccurrence(
                        key=mnemonic,
                        widget=widget,
                        text=text,
                        line=line_number,
                    )
                )

    return occurrences


def should_ignore_occurrence(occ: MnemonicOccurrence, include_actions: bool) -> bool:
    if occ.widget == "QAction" and not include_actions:
        return True
    return False


def find_duplicates(occurrences: list[MnemonicOccurrence]) -> dict[str, list[MnemonicOccurrence]]:
    grouped: dict[str, list[MnemonicOccurrence]] = defaultdict(list)
    for occ in occurrences:
        grouped[occ.key].append(occ)
    return {key: items for key, items in grouped.items() if len(items) > 1}


def main() -> int:
    include_actions = "--include-actions" in sys.argv
    repo_root = Path(__file__).resolve().parents[1]
    ui_dir = repo_root / "src" / "ui"
    py_files = sorted(ui_dir.glob("*.py"))

    print("Checking shortcut mnemonics in src/ui/*.py")
    if not include_actions:
        print("(QAction menu mnemonics ignored; use --include-actions to include them)")
    print("-" * 50)

    total_duplicates = 0
    for file_path in py_files:
        occurrences = scan_file(file_path)
        filtered_occurrences = [
            occ for occ in occurrences
            if not should_ignore_occurrence(occ, include_actions)
        ]
        duplicates = find_duplicates(filtered_occurrences)

        if not duplicates:
            print(f"OK   {file_path.relative_to(repo_root)}")
            continue

        total_duplicates += sum(len(items) -
                                1 for items in duplicates.values())
        print(f"DUP  {file_path.relative_to(repo_root)}")
        for key in sorted(duplicates):
            print(f"  Alt+{key} appears {len(duplicates[key])} times:")
            for item in duplicates[key]:
                print(f"    L{item.line}: {item.widget}(\"{item.text}\")")

    print("-" * 50)
    if total_duplicates == 0:
        print("No duplicate mnemonics found.")
        return 0

    print(f"Found {total_duplicates} duplicate mnemonic occurrence(s).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
