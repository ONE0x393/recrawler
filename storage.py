import os
import sqlite3
import time
from typing import Iterable


class SeenStore:
    def __init__(self, db_path: str, max_seen: int) -> None:
        self._db_path = db_path
        self._max_seen = max_seen
        self._ensure_parent_dir()
        self._init_db()

    def _ensure_parent_dir(self) -> None:
        parent_dir = os.path.dirname(self._db_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS seen (
                    source TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    PRIMARY KEY (source, item_id)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_seen_source_time ON seen(source, created_at)"
            )

    def get_seen_set(self, source: str, item_ids: Iterable[str]) -> set[str]:
        ids = list(item_ids)
        if not ids:
            return set()
        placeholders = ",".join("?" for _ in ids)
        query = f"SELECT item_id FROM seen WHERE source = ? AND item_id IN ({placeholders})"
        with self._connect() as conn:
            rows = conn.execute(query, [source, *ids]).fetchall()
        return {row[0] for row in rows}

    def mark_seen_many(self, source: str, item_ids: Iterable[str]) -> None:
        ids = list(item_ids)
        if not ids:
            return
        now = int(time.time())
        rows = [(source, item_id, now) for item_id in ids]
        with self._connect() as conn:
            conn.executemany(
                "INSERT OR IGNORE INTO seen (source, item_id, created_at) VALUES (?, ?, ?)",
                rows,
            )
        self.prune(source)

    def prune(self, source: str) -> None:
        if self._max_seen <= 0:
            return
        query = (
            "DELETE FROM seen WHERE source = ? AND item_id NOT IN ("
            "SELECT item_id FROM seen WHERE source = ? ORDER BY created_at DESC LIMIT ?"
            ")"
        )
        with self._connect() as conn:
            conn.execute(query, (source, source, self._max_seen))
