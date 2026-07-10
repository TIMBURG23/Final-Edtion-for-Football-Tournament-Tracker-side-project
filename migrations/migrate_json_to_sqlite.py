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
