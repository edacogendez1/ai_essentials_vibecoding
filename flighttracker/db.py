import sqlite3
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS watches (
    id INTEGER PRIMARY KEY,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    depart_date TEXT NOT NULL,
    return_date TEXT NOT NULL DEFAULT '',
    currency TEXT NOT NULL DEFAULT 'USD',
    UNIQUE(origin, destination, depart_date, return_date)
);
CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY,
    watch_id INTEGER NOT NULL REFERENCES watches(id) ON DELETE CASCADE,
    price REAL NOT NULL,
    checked_at TEXT NOT NULL
);
"""


class DB:
    def __init__(self, path="flights.db"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)

    def add_watch(self, origin, destination, depart_date, return_date=None, currency="USD"):
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO watches (origin, destination, depart_date, return_date, currency)"
            " VALUES (?, ?, ?, ?, ?)",
            (origin.upper(), destination.upper(), depart_date, return_date or "", currency.upper()),
        )
        self.conn.commit()
        return cur.lastrowid if cur.rowcount else None

    def remove_watch(self, watch_id):
        cur = self.conn.execute("DELETE FROM watches WHERE id = ?", (watch_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def watches(self):
        return self.conn.execute("SELECT * FROM watches ORDER BY id").fetchall()

    def lowest_price(self, watch_id):
        row = self.conn.execute(
            "SELECT MIN(price) AS p FROM prices WHERE watch_id = ?", (watch_id,)
        ).fetchone()
        return row["p"]

    def price_count(self, watch_id):
        return self.conn.execute(
            "SELECT COUNT(*) AS c FROM prices WHERE watch_id = ?", (watch_id,)
        ).fetchone()["c"]

    def record_price(self, watch_id, price):
        self.conn.execute(
            "INSERT INTO prices (watch_id, price, checked_at) VALUES (?, ?, ?)",
            (watch_id, price, datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )
        self.conn.commit()

    def history(self, watch_id):
        return self.conn.execute(
            "SELECT price, checked_at FROM prices WHERE watch_id = ? ORDER BY id", (watch_id,)
        ).fetchall()
