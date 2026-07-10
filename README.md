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
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

text

3. Create .env from example and set DLS_ADMIN_PIN (dev only):
cp .env.example .env

edit .env to set DLS_ADMIN_PIN
text

4. (Optional) If you have legacy `dls_ultra_db.json` run migration:
python migrations/migrate_json_to_sqlite.py --json dls_ultra_db.json --db dls_ultra.sqlite

text

5. Run the app:
streamlit run app.py

text

## Deployment
A Dockerfile is included. Recommended hosting: DigitalOcean (App Platform or Droplet). Streamlit Cloud is an easier alternative.

## Notes about migration
- Legacy 4-digit captain PINs (if present in JSON) will be imported into the `legacy_pin` column and a secure token will be generated for each captain.
- Legacy sha256 password hashes cannot be reversed; such accounts will be marked for password reset.

## TODO
- Implement full UI parity
- Implement complete tournament logic (fixtures, results, survival)
- Add Sentry integration and feature tests

