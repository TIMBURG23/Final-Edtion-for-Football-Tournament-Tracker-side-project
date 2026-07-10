# storage/sqlite_store.py
"""
SQLite storage implementation with captain token & PIN registration flow.
"""
import sqlite3
import os
from typing import Optional
from datetime import datetime
import uuid
import csv
import io
import random

# small pool of emoji badges — add more as you like
BADGE_POOL = ["🦁","🦅","🐺","🐉","🦈","🐍","🐻","🐝","🦂","⚽","👑","⚡","🔥","🚀","🛡️"]

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
    pin_claimed BOOLEAN DEFAULT 0,
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

def _gen_pin() -> str:
    # 4-digit numeric PIN, leading zeros allowed
    return f"{random.randint(0, 9999):04d}"

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

    # --- Teams ---
    def get_all_teams(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, badge, created_at FROM teams ORDER BY id")
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    def add_team(self, name: str, badge: Optional[str] = None) -> bool:
        try:
            if badge is None:
                badge = random.choice(BADGE_POOL)
            cur = self.conn.cursor()
            cur.execute("INSERT INTO teams (name, badge, created_at) VALUES (?, ?, ?)",
                        (name, badge, datetime.utcnow().isoformat()))
            self.conn.commit()
            return True
        except Exception:
            return False

    # --- Captains & tokens ---
    def create_captain_for_team(self, team_name: str, legacy_pin: Optional[str] = None, generate_pin: bool = True) -> Optional[dict]:
        """
        Create a captain entry for an existing team.
        If legacy_pin provided, it will be used; else generate one if generate_pin=True.
        Returns created captain dict: {id, team_id, token, legacy_pin, token_created_at, pin_claimed}
        """
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM teams WHERE name = ?", (team_name,))
        row = cur.fetchone()
        if not row:
            return None
        team_id = row['id']

        pin = legacy_pin if legacy_pin is not None else (_gen_pin() if generate_pin else None)
        token = str(uuid.uuid4())

        cur.execute("INSERT INTO captains (team_id, token, legacy_pin, token_created_at, pin_claimed) VALUES (?, ?, ?, datetime('now'), 0)",
                    (team_id, token, pin))
        self.conn.commit()
        captain_id = cur.lastrowid

        cur.execute("SELECT id, team_id, token, legacy_pin, token_created_at, pin_claimed FROM captains WHERE id = ?", (captain_id,))
        created = cur.fetchone()
        return dict(created) if created else None

    def claim_pin(self, captain_id: int) -> bool:
        """
        Mark a captain's PIN as claimed (so it won't be shown publicly again).
        """
        cur = self.conn.cursor()
        cur.execute("UPDATE captains SET pin_claimed = 1 WHERE id = ?", (captain_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def get_all_captains(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT c.id, t.name AS team_name, c.token, c.legacy_pin, c.legacy_sha256, c.token_created_at, c.pin_claimed
            FROM captains c
            LEFT JOIN teams t ON t.id = c.team_id
            ORDER BY c.id
        """)
        return [dict(r) for r in cur.fetchall()]

    def regenerate_captain_token(self, captain_id: int) -> str:
        new_token = str(uuid.uuid4())
        cur = self.conn.cursor()
        cur.execute("UPDATE captains SET token = ?, token_created_at = datetime('now') WHERE id = ?", (new_token, captain_id))
        self.conn.commit()
        return new_token

    def export_captains_csv(self) -> str:
        rows = self.get_all_captains()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "team_name", "token", "legacy_pin", "pin_claimed", "legacy_sha256", "token_created_at"])
        for r in rows:
            writer.writerow([
                r.get("id"),
                r.get("team_name"),
                r.get("token"),
                r.get("legacy_pin"),
                int(bool(r.get("pin_claimed"))),
                int(bool(r.get("legacy_sha256"))),
                r.get("token_created_at"),
            ])
        return output.getvalue()

    def find_captain_by_token_or_pin(self, token_or_pin: str) -> Optional[dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT c.id, t.name as team_name, c.token, c.legacy_pin, c.pin_claimed FROM captains c JOIN teams t ON t.id = c.team_id WHERE c.token=? OR c.legacy_pin=?", (token_or_pin, token_or_pin))
        r = cur.fetchone()
        return dict(r) if r else None

    # --- Pending reports ---
    def get_pending_reports(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, match_id, payload, submitted_by, status, created_at FROM pending_reports WHERE status='pending'")
        return [dict(r) for r in cur.fetchall()]