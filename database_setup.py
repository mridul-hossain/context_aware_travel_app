import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "travel_companion.db"

def create_tables():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH.as_posix())
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS user_context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            temperature REAL,
            recommended_activity TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

if __name__ == "__main__":
    create_tables()
