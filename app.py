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
