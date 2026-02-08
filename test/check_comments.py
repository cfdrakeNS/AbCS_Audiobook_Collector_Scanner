import sqlite3

conn = sqlite3.connect('data/abcs.db')
cursor = conn.cursor()

# Check for books with comments
cursor.execute(
    'SELECT COUNT(*) FROM books WHERE LENGTH(COALESCE(comments, "")) > 0')
count_with_comments = cursor.fetchone()[0]

cursor.execute(
    'SELECT COUNT(*) FROM books WHERE LENGTH(COALESCE(comments, "")) > 100')
count_substantial = cursor.fetchone()[0]

print(f"Books with any comments: {count_with_comments}")
print(f"Books with comments > 100 chars: {count_substantial}")

if count_substantial > 0:
    cursor.execute('''
        SELECT title, author_name, LENGTH(comments) as len 
        FROM books 
        JOIN authors ON books.author_id = authors.author_id 
        WHERE LENGTH(COALESCE(comments, "")) > 100 
        LIMIT 3
    ''')
    print("\nBooks with substantial comments:")
    for title, author, length in cursor.fetchall():
        print(f"  - {title} by {author} ({length} chars)")

conn.close()
