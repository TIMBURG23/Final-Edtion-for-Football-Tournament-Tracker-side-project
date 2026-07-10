# storage/sqlite_store.py
"""
SQLite storage implementation with transactional result writes and full recompute of cumulative stats.
"""
import sqlite3
from typing import Optional, List, Dict
from datetime import datetime
import uuid
import csv
import io
import random

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

CREATE TABLE IF NOT EXISTS results (
    match_id TEXT PRIMARY KEY,
    home_team TEXT,
    away_team TEXT,
    home_score INTEGER,
    away_score INTEGER,
    p_home INTEGER DEFAULT 0,
    p_away INTEGER DEFAULT 0,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS match_meta (
    match_id TEXT PRIMARY KEY,
    h_s TEXT, a_s TEXT,
    h_a TEXT, a_a TEXT,
    h_r TEXT, a_r TEXT
);

CREATE TABLE IF NOT EXISTS cumulative_stats (
    team TEXT PRIMARY KEY,
    P INTEGER DEFAULT 0,
    W INTEGER DEFAULT 0,
    D INTEGER DEFAULT 0,
    L INTEGER DEFAULT 0,
    GF INTEGER DEFAULT 0,
    GA INTEGER DEFAULT 0,
    GD INTEGER DEFAULT 0,
    Pts INTEGER DEFAULT 0
);
"""

def _gen_pin() -> str:
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

    # Teams
    def get_all_teams(self) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, badge, created_at FROM teams ORDER BY id")
        return [dict(r) for r in cur.fetchall()]

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

    # Captains & tokens
    def create_captain_for_team(self, team_name: str, legacy_pin: Optional[str] = None, generate_pin: bool = True) -> Optional[dict]:
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
        cur.execute("SELECT id, team_id, token, legacy_pin, token_created_at, pin_claimed FROM captains WHERE id = ?", (cur.lastrowid,))
        r = cur.fetchone()
        return dict(r) if r else None

    def claim_pin(self, captain_id: int) -> bool:
        cur = self.conn.cursor()
        cur.execute("UPDATE captains SET pin_claimed = 1 WHERE id = ?", (captain_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def get_all_captains(self) -> List[Dict]:
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

    # Results & meta
    def set_result(self, match_id: str, home_team: str, away_team: str,
                   s1: int, s2: int, p1: int = 0, p2: int = 0,
                   gs1: str = "", gs2: str = "", ha: str = "", aa: str = "", hr: str = "", ar: str = "") -> bool:
        """
        Atomically insert/update a match result and recompute cumulative stats from scratch.
        """
        try:
            cur = self.conn.cursor()
            # Start transaction
            cur.execute("BEGIN")
            # Upsert result into results table
            cur.execute("""
                INSERT INTO results(match_id, home_team, away_team, home_score, away_score, p_home, p_away, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ON CONFLICT(match_id) DO UPDATE SET
                    home_team=excluded.home_team,
                    away_team=excluded.away_team,
                    home_score=excluded.home_score,
                    away_score=excluded.away_score,
                    p_home=excluded.p_home,
                    p_away=excluded.p_away,
                    updated_at=datetime('now')
            """, (match_id, home_team, away_team, s1, s2, p1, p2))

            # Upsert meta
            cur.execute("""
                INSERT INTO match_meta(match_id, h_s, a_s, h_a, a_a, h_r, a_r)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(match_id) DO UPDATE SET
                    h_s=excluded.h_s, a_s=excluded.a_s,
                    h_a=excluded.h_a, a_a=excluded.a_a,
                    h_r=excluded.h_r, a_r=excluded.a_r
            """, (match_id, gs1, gs2, ha, aa, hr, ar))

            # Recompute cumulative stats from all results
            self._recompute_cumulative_stats(cur)

            # Commit
            self.conn.commit()
            return True
        except Exception as e:
            # On error rollback
            self.conn.rollback()
            raise

    def _recompute_cumulative_stats(self, cur=None):
        """Recalculate cumulative_stats table based on all rows in results."""
        own_cursor = False
        if cur is None:
            cur = self.conn.cursor()
            own_cursor = True

        # reset cumulative_stats
        cur.execute("DELETE FROM cumulative_stats")

        # Build stats dict
        stats = {}
        for r in cur.execute("SELECT * FROM results"):
            h = r["home_team"]
            a = r["away_team"]
            s_h = r["home_score"] or 0
            s_a = r["away_score"] or 0

            # ensure team entries
            for team in (h, a):
                if team not in stats:
                    stats[team] = {"P":0,"W":0,"D":0,"L":0,"GF":0,"GA":0,"GD":0,"Pts":0}

            # update matches played and goals
            stats[h]["P"] += 1
            stats[a]["P"] += 1
            stats[h]["GF"] += s_h
            stats[h]["GA"] += s_a
            stats[a]["GF"] += s_a
            stats[a]["GA"] += s_h

            # GD will be computed later
            if s_h > s_a:
                stats[h]["W"] += 1
                stats[h]["Pts"] += 3
                stats[a]["L"] += 1
            elif s_a > s_h:
                stats[a]["W"] += 1
                stats[a]["Pts"] += 3
                stats[h]["L"] += 1
            else:
                stats[h]["D"] += 1
                stats[a]["D"] += 1
                stats[h]["Pts"] += 1
                stats[a]["Pts"] += 1

        # compute GD and persist
        for team, s in stats.items():
            s["GD"] = s["GF"] - s["GA"]
            cur.execute("""
                INSERT INTO cumulative_stats(team, P, W, D, L, GF, GA, GD, Pts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (team, s["P"], s["W"], s["D"], s["L"], s["GF"], s["GA"], s["GD"], s["Pts"]))

        if own_cursor:
            self.conn.commit()

    # Utility getters
    def get_all_results(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM results ORDER BY match_id")
        return [dict(r) for r in cur.fetchall()]

    def get_cumulative_stats(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM cumulative_stats ORDER BY Pts DESC, GD DESC, GF DESC")
        return [dict(r) for r in cur.fetchall()]