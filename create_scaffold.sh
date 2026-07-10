#!/usr/bin/env bash
set -euo pipefail

# Scaffold creator for rewrite/streamlit-sqlite
# Run from repository root. Checks for clean working tree.

BRANCH="rewrite/streamlit-sqlite"

# Ensure we're in a git repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: Not inside a git repository. cd to the repo root and re-run."
  exit 1
fi

# Ensure working tree is clean
if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: Working tree is not clean. Commit or stash changes before running this script."
  git status --porcelain
  exit 1
fi

# Create and switch to branch
echo "Creating and switching to branch ${BRANCH}..."
git checkout -b "${BRANCH}"

# Create directories
mkdir -p ui core storage auth migrations scripts tests .github/workflows

# Write files
cat > app.py <<'PY'
# app.py
"""
Main Streamlit entrypoint for DLS Ultra (scaffold).
This file is intentionally thin: it initializes config, storage, and routes to UI pages.
"""
import os
from dotenv import load_dotenv
import streamlit as st

# Load .env for local development
load_dotenv()

from storage.sqlite_store import SQLiteStore
from ui import admin as admin_ui
from ui import captain as captain_ui
from ui import public as public_ui
from auth.auth import is_admin_pin_valid

DB_PATH = os.getenv("DATABASE_PATH", "dls_ultra.sqlite")

# Initialize store
store = SQLiteStore(DB_PATH)

st.set_page_config(page_title="DLS Ultra", page_icon="⚽", layout="wide")

st.markdown("""<style>body { background-color: #050101; color: #F1E194; }</style>""", unsafe_allow_html=True)

# Simple router
st.title("DLS Ultra - Admin & Captain Portal (Scaffold)")

mode = st.sidebar.selectbox("Mode", ["Public", "Captain", "Admin"]) 

if mode == "Public":
    public_ui.render(store)
elif mode == "Captain":
    captain_ui.render(store)
else:
    # Admin login required
    pin = st.sidebar.text_input("Admin PIN", type="password")
    if is_admin_pin_valid(pin):
        admin_ui.render(store)
    else:
        st.sidebar.info("Enter Admin PIN to access admin controls")
PY

cat > ui/admin.py <<'PYUI'
# ui/admin.py
"""
Admin UI scaffold: minimal features for scaffold review.
"""
import streamlit as st

def render(store):
    st.header("Admin Dashboard")
    st.markdown("This is a scaffolded admin dashboard. More features will be added.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Teams")
        teams = store.get_all_teams()
        if teams:
            for t in teams:
                st.write(f"- {t['name']} (badge: {t.get('badge', 'N/A')})")
        else:
            st.info("No teams yet")

    with col2:
        st.subheader("Pending Reports")
        prs = store.get_pending_reports()
        if prs:
            for p in prs:
                st.write(p)
        else:
            st.info("No pending reports")
PYUI

cat > ui/captain.py <<'PYUI'
# ui/captain.py
"""
Captain UI scaffold: login via token or legacy PIN and simple portal.
"""
import streamlit as st

def render(store):
    st.header("Captain Portal")
    st.markdown("Login using your captain token or legacy PIN (scaffold)")

    token = st.text_input("Captain Token / Legacy PIN", type="password")
    if st.button("Login"):
        cap = store.find_captain_by_token_or_pin(token)
        if cap:
            st.success(f"Logged in as captain for team: {cap['team_name']}")
            st.write("(Captain portal features will be added in follow-up PRs)")
        else:
            st.error("Invalid token/PIN")
PYUI

cat > ui/public.py <<'PYUI'
# ui/public.py
"""
Public UI scaffold: registration and lobby.
"""
import streamlit as st

def render(store):
    st.header("Tournament Lobby")
    st.markdown("Register a team or view basic info (scaffold)")

    code = st.text_input("Enter tournament code")
    team = st.text_input("Team name")
    if st.button("Register"):
        if team:
            res = store.add_team(team)
            if res:
                st.success(f"Team '{team}' registered (scaffold)")
            else:
                st.error("Failed to register team or team exists")
        else:
            st.error("Please enter a team name")

    st.markdown("---")
    st.subheader("Registered Teams")
    teams = store.get_all_teams()
    if teams:
        for t in teams:
            st.write(f"- {t['name']}")
    else:
        st.info("No teams yet")
PYUI

cat > storage/base_store.py <<'BST'
# storage/base_store.py
"""
Abstract storage interface used by UI and core logic.
Concrete implementations must implement these methods.
"""
from abc import ABC, abstractmethod

class BaseStore(ABC):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def get_all_teams(self):
        pass

    @abstractmethod
    def add_team(self, name):
        pass

    @abstractmethod
    def get_pending_reports(self):
        pass

    @abstractmethod
    def find_captain_by_token_or_pin(self, token_or_pin):
        pass
BST

cat > storage/sqlite_store.py <<'SQL'
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
SQL

cat > storage/json_store.py <<'JST'
# storage/json_store.py
"""
Helpers to read legacy JSON DB (dls_ultra_db.json) and write backups.
"""
import json
from typing import Optional

def read_legacy_json(path: str) -> Optional[dict]:
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return None

def write_backup(path: str, data: dict) -> bool:
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False
JST

cat > auth/auth.py <<'AUTH'
# auth/auth.py
"""
Authentication helpers: bcrypt password hashing and admin PIN check.
"""
import os
import bcrypt
import uuid
from dotenv import load_dotenv

load_dotenv()

ADMIN_PIN = os.getenv("DLS_ADMIN_PIN", "changeme")

def is_admin_pin_valid(pin: str) -> bool:
    return pin == ADMIN_PIN

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def check_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False

def generate_token() -> str:
    return str(uuid.uuid4())
AUTH

cat > core/validators.py <<'VAL'
# core/validators.py
"""
Validation helpers (fixed validate_team_name)
"""
import re

def validate_team_name(team_name: str):
    if not team_name or not team_name.strip():
        return False, "Team name cannot be empty"

    # Forbid only a small set of problematic characters, allow v and underscore
    forbidden_chars = ['"', "'", "\n"]
    for ch in forbidden_chars:
        if ch in team_name:
            return False, f"Team name cannot contain '{ch}'"

    if len(team_name) > 50:
        return False, "Team name too long (max 50 characters)"

    # Disallow control characters
    if re.search(r"[\x00-\x1f]", team_name):
        return False, "Team name contains control characters"

    return True, ""
VAL

cat > migrations/migrate_json_to_sqlite.py <<'MIG'
# migrations/migrate_json_to_sqlite.py
"""
Migration script to import legacy dls_ultra_db.json into SQLite.
"""
import argparse
import json
import os
from storage.sqlite_store import SQLiteStore
from storage.json_store import read_legacy_json
from auth.auth import generate_token

def migrate(json_path: str, db_path: str):
    store = SQLiteStore(db_path)
    data = read_legacy_json(json_path)
    report = {"imported_teams": [], "errors": []}

    if not data:
        print("No JSON data found; initializing empty DB")
        return report

    teams = data.get('teams', [])

    for t in teams:
        try:
            name = t
            store.add_team(name)
            # Create captain record if PIN exists
            pins = data.get('captain_pins', {})
            pin = pins.get(name)
            if pin:
                # Insert into captains table
                cur = store.conn.cursor()
                token = generate_token()
                cur.execute("SELECT id FROM teams WHERE name=?", (name,))
                row = cur.fetchone()
                team_id = row['id'] if row else None
                cur.execute("INSERT INTO captains (team_id, token, legacy_pin, token_created_at) VALUES (?, ?, ?, datetime('now'))", (team_id, token, pin))
                store.conn.commit()
            report['imported_teams'].append(name)
        except Exception as e:
            report['errors'].append({"team": t, "error": str(e)})

    print("Migration complete. Report:")
    print(json.dumps(report, indent=2))
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', default='dls_ultra_db.json')
    parser.add_argument('--db', default='dls_ultra.sqlite')
    args = parser.parse_args()

    migrate(args.json, args.db)
MIG

cat > requirements.txt <<'REQ'
streamlit
pandas
bcrypt
python-dotenv
pytest
pytest-cov
REQ

cat > Dockerfile <<'DOCK'
FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PORT=8501
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
DOCK

cat > .github/workflows/ci.yml <<'CI'
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest -q
CI

cat > README.md <<'RMD'
# DLS Ultra - Rewrite (Scaffold)

This branch contains a scaffolded rewrite of the original single-file Streamlit app.

## Goals
- Modularize code
- Use SQLite for persistence
- Improve auth and security
- Provide migration path from existing dls_ultra_db.json

## Quickstart (local)

1. Clone the repo and checkout the branch `rewrite/streamlit-sqlite`.
2. Create a virtual environment and install dependencies:
