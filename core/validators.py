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
