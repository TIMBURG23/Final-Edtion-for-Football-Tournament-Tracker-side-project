# storage/sqlite_store.py
"""
SQLite storage implementation (minimal scaffold).
"""
import sqlite3
import os
from typing import Optional
from datetime import datetime

DB_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    badge TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS captains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER,
    token TEXT,
    legacy_pin TEXT,
    legacy_sha256 BOOLEAN DEFAULT 0,
    token_created_at TEXT,
    FOREIGN KEY(team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pending_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id TEXT,
    payload TEXT,
    submitted_by TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT
);
"""

class SQLiteStore:
    def __init__(self, path: str = "dls_ultra.sqlite"):
        self.path = path
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.initialize()

    def initialize(self):
        cur = self.conn.cursor()
        cur.executescript(DB_SCHEMA)
        self.conn.commit()

    def get_all_teams(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, badge, created_at FROM teams ORDER BY id")
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    def add_team(self, name: str) -> bool:
        try:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO teams (name, badge, created_at) VALUES (?, ?, ?)",
                        (name, "🛡️", datetime.utcnow().isoformat()))
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_pending_reports(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, match_id, payload, submitted_by, status, created_at FROM pending_reports WHERE status='pending'")
        return [dict(r) for r in cur.fetchall()]

    def find_captain_by_token_or_pin(self, token_or_pin: str) -> Optional[dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT c.id, t.name as team_name, c.token, c.legacy_pin FROM captains c JOIN teams t ON t.id = c.team_id WHERE c.token=? OR c.legacy_pin=?",
                    (token_or_pin, token_or_pin))
        r = cur.fetchone()
        return dict(r) if r else None
