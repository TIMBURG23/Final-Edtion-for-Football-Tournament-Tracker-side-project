# ui/admin.py
import streamlit as st
import pandas as pd
from datetime import datetime

def render(store, is_admin: bool = True):
    if not is_admin:
        st.error("Admin access required.")
        st.stop()

    st.header("Admin Dashboard")
    st.markdown("Manage teams, captain tokens and enter match results.")

    tab_teams, tab_captains, tab_results = st.tabs(
        ["🏆 Teams", "🧢 Captains & Tokens", "⚽ Enter Result"]
    )

    # TEAMS
    with tab_teams:
        teams = store.get_all_teams()
        if not teams:
            st.info("No teams yet")
        else:
            search = st.text_input("Search teams", key="team_search")
            filtered = [t for t in teams if search.lower() in t["name"].lower()] if search else teams
            df_teams = pd.DataFrame([{"Team": t["name"], "Badge": t.get("badge", "—")} for t in filtered])
            st.dataframe(df_teams, hide_index=True, use_container_width=True)
            st.caption(f"{len(filtered)} of {len(teams)} teams shown")

    # CAPTAINS
    with tab_captains:
        captains = store.get_all_captains()
        if not captains:
            st.info("No captains found.")
        else:
            search_c = st.text_input("Search captains/teams", key="captain_search")
            filtered_c = (
                [c for c in captains if search_c.lower() in (c.get("team_name") or "").lower()]
                if search_c else captains
            )

            df = pd.DataFrame([{
                "id": c["id"],
                "team": c.get("team_name") or "—",
                "pin_status": "Set ✅" if c.get("legacy_pin") else "Not set",
                "pin_claimed": bool(c.get("pin_claimed")),
                "token_created_at": c.get("token_created_at") or "",
            } for c in filtered_c])

            st.dataframe(df, hide_index=True, use_container_width=True)

            st.caption(
                "PINs are not shown in the table. Use 'Reveal PIN' below when necessary — every reveal is logged."
            )

            with st.expander("🔑 Reveal a single captain PIN", expanded=False):
                team_options = ["Select..."] + [c.get("team_name", "—") for c in captains]
                chosen = st.selectbox("Team", team_options, key="reveal_pin_team")
                if chosen != "Select...":
                    match = next((c for c in captains if c.get("team_name") == chosen), None)
                    st.write("Selected:", chosen)
                    confirm = st.checkbox("I confirm this reveal is necessary", key=f"confirm_reveal_{chosen}")
                    if confirm and st.button("Reveal PIN", key="reveal_pin_btn"):
                        if match and match.get("legacy_pin"):
                            st.code(match["legacy_pin"])
                            if hasattr(store, "log_admin_action"):
                                store.log_admin_action(f"Admin revealed PIN for {chosen}", actor="admin", timestamp=datetime.utcnow().isoformat())
                        else:
                            st.warning("No PIN set for this team.")

            with st.expander("🔁 Regenerate a captain token", expanded=False):
                team_options2 = ["Select..."] + [c.get("team_name", "—") for c in captains]
                chosen2 = st.selectbox("Team (regen)", team_options2, key="regen_token_team")
                if chosen2 != "Select...":
                    match2 = next((c for c in captains if c.get("team_name") == chosen2), None)
                    if st.button("Regenerate token", key=f"regen_btn_{chosen2}"):
                        if match2:
                            new = store.regenerate_captain_token(match2["id"])
                            st.success("Token regenerated — copy it now")
                            st.code(new)
                            if hasattr(store, "log_admin_action"):
                                store.log_admin_action(f"Admin regenerated token for {chosen2}", actor="admin", timestamp=datetime.utcnow().isoformat())
                        else:
                            st.warning("Selected team not found.")

    # RESULTS
    with tab_results:
        st.subheader("Enter / Update Match Result")
        team_names = [t["name"] for t in store.get_all_teams()]
        if len(team_names) < 2:
            st.warning("Need at least 2 registered teams before entering a result.")
        else:
            with st.form("admin_enter_result"):
                col1, col2 = st.columns(2)
                with col1:
                    home = st.selectbox("Home team", team_names, key="home_team_select")
                with col2:
                    away_options = [t for t in team_names if t != home]
                    away = st.selectbox("Away team", away_options, key="away_team_select")

                match_id = st.text_input(
                    "Match ID",
                    value=f"{home}_v_{away}" if home and away else "",
                    help="Auto-filled from the teams selected. Change only if you know what you're doing.",
                )

                s1 = st.number_input("Home score", min_value=0, value=0)
                s2 = st.number_input("Away score", min_value=0, value=0)
                gs1 = st.text_input("Home scorers (comma-separated):", value="")
                gs2 = st.text_input("Away scorers (comma-separated):", value="")

                existing = store.get_result(match_id) if hasattr(store, "get_result") else None
                confirm_overwrite = True
                if existing:
                    st.warning(
                        f"⚠️ A result already exists for `{match_id}` "
                        f"({existing.get('home_score','?')}-{existing.get('away_score','?')}). "
                        "Submitting will overwrite it and recompute stats."
                    )
                    confirm_overwrite = st.checkbox("I understand this will overwrite the existing result", key="confirm_overwrite")

                submitted = st.form_submit_button("Confirm Result (save & recompute)")

                if submitted:
                    # defensive validation
                    team_list = [t["name"] for t in store.get_all_teams()]
                    if not match_id or not home or not away:
                        st.error("match_id, home and away are required")
                    elif home == away:
                        st.error("Home and away teams must be different.")
                    elif home not in team_list or away not in team_list:
                        st.error("Selected teams must be from the registered team list.")
                    elif existing and not confirm_overwrite:
                        st.error("Please confirm overwrite before submitting.")
                    else:
                        try:
                            ok = store.set_result(
                                match_id, home, away, int(s1), int(s2),
                                0, 0, gs1, gs2, "", "", "", ""
                            )
                            if ok:
                                st.success("Result saved and cumulative stats recomputed.")
                                standings = store.get_cumulative_stats()
                                df_standings = pd.DataFrame(standings)
                                # deterministic sort
                                if not df_standings.empty and "Pts" in df_standings.columns:
                                    df_standings = df_standings.sort_values(["Pts","GD","GF","team"], ascending=[False,False,False,True])
                                st.write("Current cumulative standings:")
                                st.dataframe(df_standings, hide_index=True, use_container_width=True)
                                if hasattr(store, "log_admin_action"):
                                    store.log_admin_action(f"Admin saved result {match_id} {home}-{away} {s1}-{s2}", actor="admin", timestamp=datetime.utcnow().isoformat())
                            else:
                                st.error("Result was not saved — store.set_result returned a falsy value.")
                        except Exception as e:
                            st.error(f"Error saving result: {e}")