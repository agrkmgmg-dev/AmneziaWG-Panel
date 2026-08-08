import sqlite3

db = "amnezia_panel.db"

conn = sqlite3.connect(db)

tables = conn.execute(
    "SELECT name FROM sqlite_master "
    "WHERE type='table' ORDER BY name"
).fetchall()

print("DATABASE:", db)
print("TABLES:")

for table in tables:
    print(" -", table[0])

version = conn.execute(
    "SELECT name FROM sqlite_master "
    "WHERE type='table' AND name='alembic_version'"
).fetchone()

print("ALEMBIC VERSION TABLE:", version)

if version:
    versions = conn.execute(
        "SELECT version_num FROM alembic_version"
    ).fetchall()
    print("ALEMBIC VERSION:", versions)

conn.close()
