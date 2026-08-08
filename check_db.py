import sqlite3

connection = sqlite3.connect("backend/app.db")

cursor = connection.execute(
    "SELECT name FROM sqlite_master "
    "WHERE type='table' AND name='token_revocations'"
)

result = cursor.fetchone()

print("token_revocations:", result)

connection.close()