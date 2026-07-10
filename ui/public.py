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
