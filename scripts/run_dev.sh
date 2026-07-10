#!/usr/bin/env bash
set -e

# Load .env if present
if [ -f .env ]; then
  export $(cat .env | xargs)
fi

# Run migration if JSON exists
if [ -f dls_ultra_db.json ]; then
  python migrations/migrate_json_to_sqlite.py --json dls_ultra_db.json --db ${DATABASE_PATH:-dls_ultra.sqlite}
fi

streamlit run app.py
