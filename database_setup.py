import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "travel_companion.db"

def create_tables():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH.as_posix())
    c = conn.cursor()

    # User table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            name TEXT,
            profile_pic TEXT,
            attraction_preference LONGTEXT,
            activity_preference LONGTEXT,
            cuisine_preference LONGTEXT,
            profile_status INT DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    create_tables()