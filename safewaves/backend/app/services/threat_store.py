"""
safewaves Threat Store
=======================
SQLite-backed persistent store for recent threat analysis results.
Falls back to in-memory storage if SQLite is unavailable.
"""

import json
import os
import sqlite3
import threading
from collections import deque
from typing import List


DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "threats.db",
)


class ThreatStore:
    def __init__(self, db_path: str = DB_PATH, maxlen: int = 500):
        self._maxlen = maxlen
        self._lock = threading.Lock()
        self._listeners: list = []  # SSE listeners
        try:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self._conn = sqlite3.connect(db_path, check_same_thread=False)
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS threats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_threats_created
                ON threats(created_at DESC)
            """)
            self._conn.commit()
            self._use_sqlite = True
            print(f"Threat store initialized with SQLite at {db_path}")
        except Exception as e:
            print(f"SQLite unavailable ({e}), using in-memory store")
            self._use_sqlite = False
            self._memory = deque(maxlen=maxlen)

    def add(self, threat: dict):
        with self._lock:
            if self._use_sqlite:
                self._conn.execute(
                    "INSERT INTO threats (data) VALUES (?)",
                    (json.dumps(threat),),
                )
                # Prune old records beyond maxlen
                self._conn.execute("""
                    DELETE FROM threats WHERE id NOT IN (
                        SELECT id FROM threats ORDER BY id DESC LIMIT ?
                    )
                """, (self._maxlen,))
                self._conn.commit()
            else:
                self._memory.appendleft(threat)

        # Notify SSE listeners
        for callback in self._listeners[:]:
            try:
                callback(threat)
            except Exception:
                self._listeners.remove(callback)

    def get_all(self) -> List[dict]:
        with self._lock:
            if self._use_sqlite:
                cursor = self._conn.execute(
                    "SELECT data FROM threats ORDER BY id DESC LIMIT ?",
                    (self._maxlen,),
                )
                return [json.loads(row[0]) for row in cursor.fetchall()]
            else:
                return list(self._memory)

    def get_recent(self, n: int = 10) -> List[dict]:
        with self._lock:
            if self._use_sqlite:
                cursor = self._conn.execute(
                    "SELECT data FROM threats ORDER BY id DESC LIMIT ?",
                    (n,),
                )
                return [json.loads(row[0]) for row in cursor.fetchall()]
            else:
                return list(self._memory)[:n]

    def get_stats(self) -> dict:
        """Return aggregate statistics for the dashboard."""
        with self._lock:
            if self._use_sqlite:
                total = self._conn.execute(
                    "SELECT COUNT(*) FROM threats"
                ).fetchone()[0]
                # Count threats where is_threat is true in SQL-stored JSON
                cursor = self._conn.execute(
                    "SELECT data FROM threats ORDER BY id DESC LIMIT ?",
                    (self._maxlen,),
                )
                threats_count = sum(
                    1 for row in cursor.fetchall()
                    if json.loads(row[0]).get("is_threat", False)
                )
                return {"total_analyzed": total, "threats_detected": threats_count}
            else:
                items = list(self._memory)
                return {
                    "total_analyzed": len(items),
                    "threats_detected": sum(
                        1 for d in items if d.get("is_threat", False)
                    ),
                }

    def subscribe(self, callback):
        """Register a callback for real-time SSE notifications."""
        self._listeners.append(callback)

    def unsubscribe(self, callback):
        """Remove a callback."""
        try:
            self._listeners.remove(callback)
        except ValueError:
            pass


threat_store = ThreatStore()
