"""Thin sqlite3 wrapper. Synchronous; fine for v0.1 volume."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    tg_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    language TEXT CHECK(language IN ('uz', 'ru')) DEFAULT 'uz',
    phone TEXT,
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_tg_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
        -- open | accepted | awaiting_address | awaiting_amount
        -- | awaiting_payment_method | awaiting_phone | ready
        -- | enroute | delivered | cancelled
    address TEXT,
    location_lat REAL,
    location_lng REAL,
    phone TEXT,
    items_amount INTEGER,        -- in sum, excluding delivery
    payment_method TEXT,         -- 'cash' | 'transfer'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_tg_id) REFERENCES users(tg_id)
);

CREATE INDEX IF NOT EXISTS idx_orders_customer_status ON orders(customer_tg_id, status);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
"""


OPEN_STATUSES = {
    "open",                       # just created via 'New order' tap, no relay yet
    "in_conversation",            # first message relayed, conversation in progress
    "accepted",                   # merchant confirmed line items
    "awaiting_address",
    "awaiting_amount",
    "awaiting_payment_method",
    "awaiting_phone",
    "ready",
    "enroute",
}


# Idempotent ALTERs for upgrading from older schemas that lacked these columns.
_MIGRATIONS = [
    "ALTER TABLE orders ADD COLUMN items_amount INTEGER",
    "ALTER TABLE orders ADD COLUMN payment_method TEXT",
]


class Storage:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.executescript(SCHEMA)
            for stmt in _MIGRATIONS:
                try:
                    c.execute(stmt)
                except sqlite3.OperationalError:
                    pass  # column already exists

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    # --- users ------------------------------------------------------------

    def upsert_user(
        self,
        tg_id: int,
        *,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
    ) -> sqlite3.Row:
        with self._conn() as c:
            c.execute(
                """
                INSERT INTO users (tg_id, username, first_name)
                VALUES (?, ?, ?)
                ON CONFLICT(tg_id) DO UPDATE SET
                    username = COALESCE(excluded.username, username),
                    first_name = COALESCE(excluded.first_name, first_name),
                    last_seen_at = CURRENT_TIMESTAMP
                """,
                (tg_id, username, first_name),
            )
            row = c.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,)).fetchone()
            assert row is not None
            return row

    def get_user(self, tg_id: int) -> Optional[sqlite3.Row]:
        with self._conn() as c:
            return c.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,)).fetchone()

    def set_user_language(self, tg_id: int, language: str) -> None:
        assert language in {"uz", "ru"}
        with self._conn() as c:
            c.execute("UPDATE users SET language = ? WHERE tg_id = ?", (language, tg_id))

    def set_user_phone(self, tg_id: int, phone: str) -> None:
        with self._conn() as c:
            c.execute("UPDATE users SET phone = ? WHERE tg_id = ?", (phone, tg_id))

    def has_completed_order(self, tg_id: int) -> bool:
        with self._conn() as c:
            row = c.execute(
                "SELECT 1 FROM orders WHERE customer_tg_id = ? AND status = 'delivered' LIMIT 1",
                (tg_id,),
            ).fetchone()
            return row is not None

    # --- orders -----------------------------------------------------------

    def get_open_order(self, tg_id: int) -> Optional[sqlite3.Row]:
        placeholders = ",".join("?" for _ in OPEN_STATUSES)
        with self._conn() as c:
            return c.execute(
                f"""
                SELECT * FROM orders
                WHERE customer_tg_id = ? AND status IN ({placeholders})
                ORDER BY id DESC LIMIT 1
                """,
                (tg_id, *OPEN_STATUSES),
            ).fetchone()

    def open_or_get_order(self, tg_id: int) -> sqlite3.Row:
        existing = self.get_open_order(tg_id)
        if existing is not None:
            return existing
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO orders (customer_tg_id) VALUES (?)",
                (tg_id,),
            )
            order_id = cur.lastrowid
            row = c.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
            assert row is not None
            return row

    def get_order(self, order_id: int) -> Optional[sqlite3.Row]:
        with self._conn() as c:
            return c.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()

    def set_status(self, order_id: int, status: str) -> None:
        with self._conn() as c:
            c.execute(
                "UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, order_id),
            )

    def set_address(
        self,
        order_id: int,
        *,
        address: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
    ) -> None:
        with self._conn() as c:
            c.execute(
                """
                UPDATE orders SET address = COALESCE(?, address),
                                  location_lat = COALESCE(?, location_lat),
                                  location_lng = COALESCE(?, location_lng),
                                  updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (address, lat, lng, order_id),
            )

    def set_phone(self, order_id: int, phone: str) -> None:
        with self._conn() as c:
            c.execute(
                "UPDATE orders SET phone = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (phone, order_id),
            )

    def set_items_amount(self, order_id: int, amount: int) -> None:
        with self._conn() as c:
            c.execute(
                "UPDATE orders SET items_amount = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (amount, order_id),
            )

    def set_payment_method(self, order_id: int, method: str) -> None:
        assert method in {"cash", "transfer"}
        with self._conn() as c:
            c.execute(
                "UPDATE orders SET payment_method = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (method, order_id),
            )

    def list_open_orders(self) -> list[sqlite3.Row]:
        placeholders = ",".join("?" for _ in OPEN_STATUSES)
        with self._conn() as c:
            return list(
                c.execute(
                    f"""
                    SELECT o.*, u.username, u.first_name
                    FROM orders o
                    JOIN users u ON u.tg_id = o.customer_tg_id
                    WHERE o.status IN ({placeholders})
                    ORDER BY o.id DESC
                    """,
                    tuple(OPEN_STATUSES),
                )
            )
