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
