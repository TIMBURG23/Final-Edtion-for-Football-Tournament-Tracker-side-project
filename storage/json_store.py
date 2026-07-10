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
