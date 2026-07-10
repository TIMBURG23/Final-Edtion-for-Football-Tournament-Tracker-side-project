# ui/admin.py
import streamlit as st
import pandas as pd

def render(store):
    st.header("Admin Dashboard")
    st.markdown("Manage teams, captain tokens and enter match results.")

    # Teams
    st.subheader("Teams")
    teams = store.get_all_teams()
    if teams:
        for t in teams:
            st.write(f"- {t['name']} (badge: {t.get('badge', 'N/A')})")
    else:
        st.info("No teams yet")

    st.markdown("---")

    # Captains
    st.subheader("Captains & Tokens")
    captains = store.get_all_captains()
    if not captains:
        st.info("No captains found.")
    else:
        df = pd.DataFrame([{
            "id": c["id"],
            "team": c.get("team_name") or "—",
            "legacy_pin": c.get("legacy_pin") or "",
            "pin_claimed": bool(c.get("pin_claimed")),
            "token_created_at": c.get("token_created_at") or ""
        } for c in captains])
        st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("Admin: Enter / Update Match Result (Quick Test Form)")

    with st.form("admin_enter_result"):
        match_id = st.text_input("Match ID (unique):", value="")
        home = st.text_input("Home team (name):", value="")
        away = st.text_input("Away team (name):", value="")
        s1 = st.number_input("Home score", min_value=0, value=0)
        s2 = st.number_input("Away score", min_value=0, value=0)
        gs1 = st.text_input("Home scorers (comma):", value="")
        gs2 = st.text_input("Away scorers (comma):", value="")
        submitted = st.form_submit_button("Confirm Result (save & recompute)")
        if submitted:
            if not match_id or not home or not away:
                st.error("match_id, home and away are required")
            else:
                try:
                    ok = store.set_result(match_id, home, away, int(s1), int(s2), 0, 0, gs1, gs2, "", "", "", "")
                    if ok:
                        st.success("Result saved and cumulative stats recomputed.")
                        # Show current standings
                        st.write("Current cumulative standings:")
                        st.dataframe(pd.DataFrame(store.get_cumulative_stats()))
                except Exception as e:
                    st.error(f"Error saving result: {e}")