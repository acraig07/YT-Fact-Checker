import sqlite3
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR     = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH      = DATA_DIR / "factchecks.db"

def get_connection():
    return sqlite3.connect(str(DB_PATH))

def initialize_db():
    """
    Create tables if they don't exist.
    Call this once at startup (or guard with if __name__ == '__main__').
    """
    conn = get_connection()
    c    = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS entries (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT    NOT NULL,
        url       TEXT    NOT NULL,
        llm1      TEXT    NOT NULL,
        llm2      TEXT    NOT NULL,
        llm3      TEXT    NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_id  INTEGER NOT NULL,
        claim     TEXT    NOT NULL,
        out1      TEXT    NOT NULL,
        out2      TEXT    NOT NULL,
        out3      TEXT    NOT NULL,
        FOREIGN KEY(entry_id) REFERENCES entries(id)
    )
    """)

    conn.commit()
    conn.close()

initialize_db()


def save_factcheck(url: str,
                   llm1: str, llm2: str, llm3: str,
                   results: dict[str, tuple[str, str, str]],
                   ts: datetime = None) -> int:
    ts = (ts or datetime.utcnow()).isoformat()
    conn = get_connection()
    c    = conn.cursor()

    c.execute(
        "INSERT INTO entries (timestamp, url, llm1, llm2, llm3) VALUES (?, ?, ?, ?, ?)",
        (ts, url, llm1, llm2, llm3)
    )
    entry_id = c.lastrowid

    for claim, (r1, r2, r3) in results.items():
        c.execute(
            "INSERT INTO responses (entry_id, claim, out1, out2, out3) "
            "VALUES (?, ?, ?, ?, ?)",
            (entry_id, claim, r1, r2, r3)
        )

    conn.commit()
    conn.close()
    return entry_id


def load_factcheck(entry_id: int):
    conn = get_connection()
    c    = conn.cursor()

    c.execute(
        "SELECT timestamp, url, llm1, llm2, llm3 "
        "FROM entries WHERE id = ?",
        (entry_id,)
    )
    meta = c.fetchone()
    if not meta:
        conn.close()
        return None

    timestamp, url, llm1, llm2, llm3 = meta

    c.execute(
        "SELECT claim, out1, out2, out3 "
        "FROM responses WHERE entry_id = ?",
        (entry_id,)
    )
    rows = c.fetchall()
    conn.close()

    results = { row[0]: (row[1], row[2], row[3]) for row in rows }
    return {
        "timestamp": timestamp,
        "url":       url,
        "llms":      [llm1, llm2, llm3],
        "results":   results
    }
