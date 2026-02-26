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

ALT_LETTERS = {chr(code) for code in range(ord("A"), ord("Z") + 1)}

# Keep empty by default; populate only if real conflicts are discovered.
VS_CODE_RESERVED_ALT_LETTERS: set[str] = set()


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


def extract_allowed_letters(file_path: Path) -> set[str] | None:
    """Extract ALLOWED_ALT_LETTERS set from file if it exists."""
    content = file_path.read_text(encoding="utf-8")

    # Look for ALLOWED_ALT_LETTERS = { ... }
    match = re.search(
        r'ALLOWED_ALT_LETTERS\s*=\s*\{([^}]+)\}', content, re.MULTILINE)
    if not match:
        return None

    # Extract letters from the set definition
    letters_text = match.group(1)
    letters = re.findall(r"['\"]([A-Z])['\"]", letters_text)
    return set(letters)


def extract_excluded_letters(file_path: Path) -> set[str] | None:
    """Extract EXCLUDED_ALT_LETTERS set from file if it exists."""
    content = file_path.read_text(encoding="utf-8")

    match = re.search(
        r'EXCLUDED_ALT_LETTERS\s*=\s*\{([^}]+)\}', content, re.MULTILINE)
    if not match:
        return None

    letters_text = match.group(1)
    letters = re.findall(r"['\"]([A-Z])['\"]", letters_text)
    return set(letters)


def scan_explicit_alt_letters(file_path: Path) -> list[MnemonicOccurrence]:
    """Find explicit Alt+<letter> key declarations in the source file."""
    occurrences: list[MnemonicOccurrence] = []
    pattern = re.compile(r'Alt\+([A-Z])', re.IGNORECASE)

    for line_number, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), start=1):
        for match in pattern.finditer(line):
            key = match.group(1).upper()
            occurrences.append(
                MnemonicOccurrence(
                    key=key,
                    widget="Shortcut",
                    text=match.group(0),
                    line=line_number,
                )
            )

    return occurrences


def find_missing_allowed_letters(
    occurrences: list[MnemonicOccurrence],
    allowed_letters: set[str]
) -> list[MnemonicOccurrence]:
    """Find mnemonics that are not in ALLOWED_ALT_LETTERS."""
    return [occ for occ in occurrences if occ.key not in allowed_letters]


def main() -> int:
    include_actions = "--include-actions" in sys.argv
    check_vs = "--check-vs" in sys.argv
    repo_root = Path(__file__).resolve().parents[1]
    ui_dir = repo_root / "src" / "ui"
    py_files = sorted(ui_dir.glob("*.py"))

    print("Checking shortcut mnemonics in src/ui/*.py")
    if not include_actions:
        print("(QAction menu mnemonics ignored; use --include-actions to include them)")
    print("-" * 50)

    total_duplicates = 0
    total_missing = 0
    total_excluded = 0
    total_vs_conflicts = 0
    total_policy_conflicts = 0

    for file_path in py_files:
        occurrences = scan_file(file_path)
        explicit_alt_occurrences = scan_explicit_alt_letters(file_path)

        filtered_occurrences = [
            occ for occ in occurrences
            if not should_ignore_occurrence(occ, include_actions)
        ]
        duplicates = find_duplicates(filtered_occurrences)

        all_alt_occurrences = filtered_occurrences + explicit_alt_occurrences

        # Check for ALLOWED_ALT_LETTERS
        allowed_letters = extract_allowed_letters(file_path)
        excluded_letters = extract_excluded_letters(file_path)
        missing_letters = []
        if allowed_letters is not None:
            missing_letters = find_missing_allowed_letters(
                filtered_occurrences, allowed_letters)

        excluded_hits = []
        if excluded_letters is not None:
            excluded_hits = [
                occ for occ in all_alt_occurrences if occ.key in excluded_letters
            ]

        policy_overlap: set[str] = set()
        if allowed_letters is not None and excluded_letters is not None:
            policy_overlap = allowed_letters.intersection(excluded_letters)

        vs_conflicts = []
        if check_vs and VS_CODE_RESERVED_ALT_LETTERS:
            vs_conflicts = [
                occ for occ in all_alt_occurrences if occ.key in VS_CODE_RESERVED_ALT_LETTERS
            ]

        if (
            not duplicates
            and not missing_letters
            and not excluded_hits
            and not policy_overlap
            and not vs_conflicts
        ):
            print(f"OK   {file_path.relative_to(repo_root)}")
            continue

        # Report duplicates
        if duplicates:
            total_duplicates += sum(len(items) -
                                    1 for items in duplicates.values())
            print(f"DUP  {file_path.relative_to(repo_root)}")
            for key in sorted(duplicates):
                print(f"  Alt+{key} appears {len(duplicates[key])} times:")
                for item in duplicates[key]:
                    print(f"    L{item.line}: {item.widget}(\"{item.text}\")")

        # Report missing from ALLOWED_ALT_LETTERS
        if missing_letters:
            total_missing += len(missing_letters)
            print(f"MISS {file_path.relative_to(repo_root)}")
            print(f"  ALLOWED_ALT_LETTERS = {sorted(allowed_letters)}")
            print(f"  Missing {len(missing_letters)} mnemonic(s):")
            for item in sorted(missing_letters, key=lambda x: x.key):
                print(
                    f"    Alt+{item.key} L{item.line}: {item.widget}(\"{item.text}\")")

        # Report EXCLUDED_ALT_LETTERS violations
        if excluded_hits:
            total_excluded += len(excluded_hits)
            print(f"EXCL {file_path.relative_to(repo_root)}")
            print(f"  EXCLUDED_ALT_LETTERS = {sorted(excluded_letters)}")
            print(
                f"  Found {len(excluded_hits)} excluded Alt+letter usage(s):")
            for item in sorted(excluded_hits, key=lambda x: (x.key, x.line)):
                print(
                    f"    Alt+{item.key} L{item.line}: {item.widget}(\"{item.text}\")")

        # Report allow/exclude policy overlap
        if policy_overlap:
            total_policy_conflicts += len(policy_overlap)
            print(f"POL  {file_path.relative_to(repo_root)}")
            print(
                f"  ALLOWED and EXCLUDED overlap: {sorted(policy_overlap)}")

        # Report VS Code reserved Alt+letter conflicts (optional)
        if vs_conflicts:
            total_vs_conflicts += len(vs_conflicts)
            print(f"VS   {file_path.relative_to(repo_root)}")
            print(
                f"  VS_CODE_RESERVED_ALT_LETTERS = {sorted(VS_CODE_RESERVED_ALT_LETTERS)}")
            print(
                f"  Found {len(vs_conflicts)} VS-reserved Alt+letter usage(s):")
            for item in sorted(vs_conflicts, key=lambda x: (x.key, x.line)):
                print(
                    f"    Alt+{item.key} L{item.line}: {item.widget}(\"{item.text}\")")

    print("-" * 50)
    if (
        total_duplicates == 0
        and total_missing == 0
        and total_excluded == 0
        and total_vs_conflicts == 0
        and total_policy_conflicts == 0
    ):
        print("No issues found.")
        return 0

    if total_duplicates > 0:
        print(f"Found {total_duplicates} duplicate mnemonic occurrence(s).")
    if total_missing > 0:
        print(
            f"Found {total_missing} mnemonic(s) missing from ALLOWED_ALT_LETTERS.")
    if total_excluded > 0:
        print(
            f"Found {total_excluded} Alt+letter usage(s) present in EXCLUDED_ALT_LETTERS.")
    if total_policy_conflicts > 0:
        print(
            f"Found {total_policy_conflicts} overlapping letter(s) between ALLOWED_ALT_LETTERS and EXCLUDED_ALT_LETTERS.")
    if total_vs_conflicts > 0:
        print(
            f"Found {total_vs_conflicts} Alt+letter usage(s) conflicting with VS_CODE_RESERVED_ALT_LETTERS.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
