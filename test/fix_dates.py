#!/usr/bin/env python3
"""Fix read_date format in the database."""

import sqlite3
import os
from datetime import datetime

# Change to the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

conn = sqlite3.connect('data/abcs.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all books with read_date
cursor.execute(
    'SELECT book_id, read_date FROM books WHERE read_date IS NOT NULL AND read_date != "2000-01-01"')
rows = cursor.fetchall()

print(f"Processing {len(rows)} books with read_date...")

fixed_count = 0
for row in rows:
    book_id = row['book_id']
    read_date_str = row['read_date'].strip() if row['read_date'] else None

    if not read_date_str:
        continue

    # Try to parse the date
    parsed_date = None

    # Try YYYY-MM-DD format
    try:
        parsed_date = datetime.strptime(read_date_str, '%Y-%m-%d').date()
    except ValueError:
        pass

    # Try M/D/YYYY format (from Access)
    if not parsed_date:
        try:
            parsed_date = datetime.strptime(read_date_str, '%m/%d/%Y').date()
        except ValueError:
            pass

    # If we parsed it, convert to YYYY-MM-DD and update
    if parsed_date:
        formatted_date = parsed_date.strftime('%Y-%m-%d')
        if formatted_date != read_date_str:
            cursor.execute(
                'UPDATE books SET read_date = ? WHERE book_id = ?', (formatted_date, book_id))
            fixed_count += 1
            print(f"  Book {book_id}: {read_date_str} -> {formatted_date}")

# Handle 2000-01-01 placeholder dates - set them to NULL
cursor.execute(
    'UPDATE books SET read_date = NULL WHERE read_date = "2000-01-01"')
placeholder_count = cursor.rowcount
if placeholder_count > 0:
    print(f"\nRemoved {placeholder_count} placeholder dates (2000-01-01)")

conn.commit()
conn.close()

print(f"\nTotal dates converted: {fixed_count}")
print("Database updated successfully!")
