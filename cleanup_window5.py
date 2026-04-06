#!/usr/bin/env python3
"""Remove dead code from book_list_import_window.py"""
import re

with open('src/ui/book_list_import_window.py', 'r') as f:
    content = f.read()

initial_lines = len(content.splitlines())

# 1. Remove _last_csv_encoding initialization
if "self._last_csv_encoding = None" in content:
    content = content.replace("        self._last_csv_encoding = None\n", "")
    print("✓ Removed _last_csv_encoding initialization")

# 2. Remove _last_csv_encoding assignment
if "self._last_csv_encoding = encoding" in content:
    content = content.replace("                self._last_csv_encoding = encoding\n", "")
    print("✓ Removed _last_csv_encoding assignment")

# 3. Remove toggle_mode method
pattern = r'    def toggle_mode\(self\):[\s\S]*?self\.on_mode_changed\(0 if self\.new_books_radio\.isChecked\(\) else 1, True\)\n\n'
if re.search(pattern, content):
    content = re.sub(pattern, '', content, count=1)
    print("✓ Removed toggle_mode method")

# 4. Remove focus_mapping_row method
pattern = r'    def focus_mapping_row\(self, row: int\):[\s\S]*?            combo\.showPopup\(\)\n\n'
if re.search(pattern, content):
    content = re.sub(pattern, '', content, count=1)
    print("✓ Removed focus_mapping_row method")

# 5. Remove show_accessible_message method
pattern = r'    def show_accessible_message\(self, title: str, message: str\):[\s\S]*?        dlg\.exec\(\)\n\n'
if re.search(pattern, content):
    content = re.sub(pattern, '', content, count=1)
    print("✓ Removed show_accessible_message method")

# 6. Remove on_new_books_toggled method
pattern = r'    def on_new_books_toggled\(self, checked: bool\):[\s\S]*?            self\.set_status\("Mode changed to: Import New Books"\)\n\n'
if re.search(pattern, content):
    content = re.sub(pattern, '', content, count=1)
    print("✓ Removed on_new_books_toggled method")

# 7. Remove on_read_date_toggled method
pattern = r'    def on_read_date_toggled\(self, checked: bool\):[\s\S]*?            self\.set_status\("Mode changed to: Update Read Dates"\)\n\n'
if re.search(pattern, content):
    content = re.sub(pattern, '', content, count=1)
    print("✓ Removed on_read_date_toggled method")

final_lines = len(content.splitlines())
print(f"\nTotal: Removed {initial_lines - final_lines} lines")

with open('src/ui/book_list_import_window.py', 'w') as f:
    f.write(content)

print("✓ File updated successfully")
