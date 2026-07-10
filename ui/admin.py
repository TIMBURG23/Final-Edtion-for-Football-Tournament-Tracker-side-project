# ui/admin.py
"""
Admin UI: list and manage captain tokens (reveal, regenerate, export).
"""
import streamlit as st
import pandas as pd

def render(store):
    st.header("Admin Dashboard")
    st.markdown("Manage teams and captain tokens (reveal / regenerate / export).")

    # Teams section
    st.subheader("Teams")
    teams = store.get_all_teams()
    if teams:
        for t in teams:
            st.write(f"- {t['name']} (badge: {t.get('badge', 'N/A')})")
    else:
        st.info("No teams yet")

    st.markdown("---")

    # Captains / tokens section
    st.subheader("Captains & Tokens")
    captains = store.get_all_captains()
    if not captains:
        st.info("No captains found.")
        return

    # Build a dataframe for overview
    df = pd.DataFrame([{
        "id": c["id"],
        "team": c.get("team_name") or "—",
        "legacy_pin": c.get("legacy_pin") or "",
        "pin_claimed": bool(c.get("pin_claimed")),
        "legacy_sha256": bool(c.get("legacy_sha256")),
        "token_created_at": c.get("token_created_at") or ""
    } for c in captains])

    st.dataframe(df[["id","team","legacy_pin","pin_claimed","legacy_sha256","token_created_at"]], use_container_width=True)

    st.markdown("#### Actions")
    for c in captains:
        cols = st.columns([3, 2, 1])
        with cols[0]:
            st.markdown(f"**{c.get('team_name') or 'Unknown Team'}**")
            st.caption(f"Legacy PIN: {c.get('legacy_pin') or '—'} • Token created: {c.get('token_created_at') or '—'} • Claimed: {bool(c.get('pin_claimed'))}")
        with cols[1]:
            if st.button("Reveal token (show once)", key=f"reveal_{c['id']}"):
                st.code(c.get("token") or "No token")
        with cols[2]:
            if st.button("Regenerate", key=f"regen_{c['id']}"):
                new_token = store.regenerate_captain_token(c["id"])
                st.success("Token regenerated — copy it now!")
                st.code(new_token)

    # Export CSV
    csv_data = store.export_captains_csv()
    st.download_button("📥 Download captains CSV", data=csv_data, file_name="captains.csv", mime="text/csv")