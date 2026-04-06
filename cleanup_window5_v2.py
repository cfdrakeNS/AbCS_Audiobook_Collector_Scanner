#!/usr/bin/env python3
"""Remove dead code from book_list_import_window.py - line-based removal"""

with open('src/ui/book_list_import_window.py', 'r') as f:
    lines = f.readlines()

initial_count = len(lines)
result = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Skip _last_csv_encoding = None initialization
    if 'self._last_csv_encoding = None' in line:
        print(f"Skipping line {i+1}: {line.strip()}")
        i += 1
        continue
    
    # Skip _last_csv_encoding = encoding assignment
    if 'self._last_csv_encoding = encoding' in line:
        print(f"Skipping line {i+1}: {line.strip()}")
        i += 1
        continue
    
    # Skip toggle_mode method (lines until next 'def ')
    if 'def toggle_mode(self):' in line:
        print(f"Skipping toggle_mode method starting at line {i+1}")
        while i < len(lines) and not (lines[i].startswith('    def ') and i > 0 and 'toggle_mode' not in lines[i]):
            i += 1
        if i < len(lines) and lines[i].startswith('    def ') and 'toggle_mode' not in lines[i]:
            continue
        else:
            i += 1
            continue
    
    # Skip focus_mapping_row method
    if 'def focus_mapping_row(self, row: int):' in line:
        print(f"Skipping focus_mapping_row method starting at line {i+1}")
        while i < len(lines) and not (lines[i].startswith('    def ') and 'focus_mapping_row' not in lines[i]):
            i += 1
        if i < len(lines) and lines[i].startswith('    def '):
            continue
        else:
            i += 1
            continue
    
    # Skip show_accessible_message method
    if 'def show_accessible_message(self, title: str, message: str):' in line:
        print(f"Skipping show_accessible_message method starting at line {i+1}")
        while i < len(lines) and not (lines[i].startswith('    def ') and 'show_accessible_message' not in lines[i]):
            i += 1
        if i < len(lines) and lines[i].startswith('    def '):
            continue
        else:
            i += 1
            continue
    
    # Skip on_new_books_toggled method
    if 'def on_new_books_toggled(self, checked: bool):' in line:
        print(f"Skipping on_new_books_toggled method starting at line {i+1}")
        while i < len(lines) and not (lines[i].startswith('    def ') and 'on_new_books_toggled' not in lines[i]):
            i += 1
        if i < len(lines) and lines[i].startswith('    def '):
            continue
        else:
            i += 1
            continue
    
    # Skip on_read_date_toggled method
    if 'def on_read_date_toggled(self, checked: bool):' in line:
        print(f"Skipping on_read_date_toggled method starting at line {i+1}")
        while i < len(lines) and not (lines[i].startswith('    def ') and 'on_read_date_toggled' not in lines[i]):
            i += 1
        if i < len(lines) and lines[i].startswith('    def '):
            continue
        else:
            i += 1
            continue
    
    result.append(line)
    i += 1

with open('src/ui/book_list_import_window.py', 'w') as f:
    f.writelines(result)

final_count = len(result)
print(f"\nRemoved {initial_count - final_count} lines")
print("✓ File updated")
