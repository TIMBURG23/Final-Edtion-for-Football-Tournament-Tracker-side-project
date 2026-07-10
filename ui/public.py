# ui/public.py
"""
Public UI: registration and lobby with PIN display and accept flow.
"""
import streamlit as st

def render(store):
    st.header("Tournament Lobby")
    st.markdown("Register a team and get your captain PIN. You must save the PIN now — it will be hidden after you confirm you saved it.")

    code = st.text_input("Enter tournament code")
    team = st.text_input("Team name")

    if st.button("Register"):
        if not team:
            st.error("Please enter a team name")
        else:
            # Create team (with random emoji badge)
            ok = store.add_team(team)
            if not ok:
                st.error("Failed to register team — it may already exist")
            else:
                # Create captain and generate PIN & token
                captain = store.create_captain_for_team(team)
                if captain:
                    # Save last registered captain in session to allow claiming
                    st.session_state['last_registered_captain'] = captain
                    st.success(f"Team '{team}' registered!")
                else:
                    st.error("Team registered but failed to create captain record.")

    st.markdown("---")
    st.subheader("Registered Teams")
    teams = store.get_all_teams()
    if teams:
        for t in teams:
            st.write(f"- {t['name']} {t.get('badge','')}")
    else:
        st.info("No teams yet")

    # Show credentials panel for the last registered captain until they claim the PIN
    if st.session_state.get('last_registered_captain'):
        c = st.session_state['last_registered_captain']
        # Check latest PIN status from DB (in case of reload)
        latest = store.find_captain_by_token_or_pin(c['token'])
        if latest and not latest.get('pin_claimed'):
            st.markdown("### ✅ Save your Captain Credentials — shown only once")
            st.info("Save these credentials now. After you confirm you have saved them, the PIN will no longer be shown publicly.")
            st.markdown(f"**Team:** {latest.get('team_name')}")
            st.markdown(f"**Captain PIN:** `{latest.get('legacy_pin')}`")
            st.markdown(f"**Captain Token (for advanced login):** `{latest.get('token')}`")
            if st.button("I saved this PIN — hide it now", key="claim_pin_btn"):
                store.claim_pin(latest['id'])
                st.session_state.pop('last_registered_captain', None)
                st.success("Thank you — the PIN is now hidden from public view. Use your saved token or contact the admin if you lose it.")
        else:
            # If pin already claimed, clear session
            st.session_state.pop('last_registered_captain', None)