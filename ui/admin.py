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
