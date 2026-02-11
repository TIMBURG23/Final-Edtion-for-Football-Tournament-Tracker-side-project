import streamlit as st
import pandas as pd
import itertools
import random
import json
import os
import re
import copy
import base64
from datetime import datetime
import hashlib
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="DLS Ultra Admin", page_icon="⚽", layout="wide", initial_sidebar_state="collapsed")

# --- COMPATIBILITY SHIM (Fixes the Button Issue on Cloud & Local) ---
def safe_rerun():
    """Handles rerun for both new and old Streamlit versions automatically"""
    if hasattr(st, 'rerun'):
        st.rerun()
    elif hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    else:
        st.warning("⚠️ Auto-reload not supported. Please manually refresh your browser.")

# --- CSS STYLING (Deep Burgundy & Golden Sand Theme) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Teko:wght@300;500;700&family=Rajdhani:wght@500;700&display=swap');

    /* BASE THEME - DEEP BURGUNDY BACKGROUND */
    .stApp {
        background-color: #050101;
        background-image: radial-gradient(circle at 50% -20%, #5B0E14 0%, #2a0408 50%, #000000 90%);
        color: #F1E194;
    }

    /* TYPOGRAPHY - GOLD */
    h1, h2, h3 { 
        font-family: 'Teko', sans-serif !important; 
        text-transform: uppercase; 
        margin: 0 !important; 
        color: #F1E194 !important;
        letter-spacing: 1.5px;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.5);
    }
    
    p, div, label, span, li {
        font-family: 'Rajdhani', sans-serif;
        color: #e2d2a3;
    }

    /* TITLES */
    .big-title {
        font-size: 5rem; font-weight: 700; text-align: center;
        background: linear-gradient(180deg, #F1E194 0%, #946c1e 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0 0 40px rgba(91, 14, 20, 0.8);
        margin-bottom: 20px;
    }

    /* GLASS PANELS (Burgundy Tint + Gold Border) */
    .glass-panel {
        background: rgba(40, 5, 8, 0.7); 
        border: 1px solid #F1E194; 
        border-radius: 8px; 
        padding: 20px; 
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(5px);
    }

    /* INPUTS & SELECTBOXES */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background: rgba(0, 0, 0, 0.8) !important; 
        color: #F1E194 !important; 
        border: 1px solid #5B0E14 !important;
        font-family: 'Rajdhani';
    }
    
    /* RADIO BUTTONS */
    div[role="radiogroup"] label {
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid #5B0E14;
        padding: 10px;
        border-radius: 5px;
    }

    /* BUTTONS (Gold Outline -> Gold Fill) */
    .stButton > button {
        background: transparent; 
        border: 1px solid #F1E194; 
        color: #F1E194;
        font-family: 'Rajdhani', sans-serif; 
        font-weight: 700; 
        text-transform: uppercase; 
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover { 
        background: #F1E194; 
        color: #5B0E14; 
        border-color: #F1E194;
        box-shadow: 0 0 20px rgba(241, 225, 148, 0.4);
    }
    
    /* SPECIAL BUTTONS */
    .approve-btn { background: linear-gradient(90deg, #2E7D32 0%, #4CAF50 100%) !important; color: white !important; border: 1px solid #4CAF50 !important; }
    .reject-btn { background: linear-gradient(90deg, #C62828 0%, #F44336 100%) !important; color: white !important; border: 1px solid #F44336 !important; }
    .reset-btn { background: linear-gradient(90deg, #FF8F00 0%, #FFA726 100%) !important; color: white !important; border: 1px solid #FFA726 !important; }
    .captain-btn { background: linear-gradient(90deg, #1565C0 0%, #2196F3 100%) !important; color: white !important; border: 1px solid #2196F3 !important; }
    .danger-btn { background: linear-gradient(90deg, #B71C1C 0%, #D32F2F 100%) !important; color: white !important; border: 1px solid #FF5252 !important; }

    /* DATAFRAME / TABLE STYLE OVERRIDES */
    div[data-testid="stDataFrame"] {
        border: 1px solid #5B0E14;
        background-color: rgba(0,0,0,0.4);
    }

    /* FOOTER */
    .footer { 
        text-align: center; padding: 20px; 
        color: #946c1e; 
        font-family: 'Rajdhani'; 
        border-top: 1px solid #5B0E14; 
        margin-top: 50px; 
    }
    .designer-name { color: #F1E194; font-weight: bold; letter-spacing: 1px; }

    /* SPECIAL STATUS CLASSES */
    .club-badge { font-size: 3rem; margin-bottom: 10px; }
    
    .drop-zone { 
        background: linear-gradient(90deg, rgba(139, 0, 0, 0.2) 0%, transparent 100%); 
        border-left: 4px solid #ff4444; 
        padding-left: 10px;
    }
    .safe-zone { 
        background: linear-gradient(90deg, rgba(241, 225, 148, 0.1) 0%, transparent 100%); 
        border-left: 4px solid #F1E194; 
        padding-left: 10px;
    }
    .bye-zone { 
        background: linear-gradient(90deg, rgba(255, 215, 0, 0.2) 0%, transparent 100%); 
        border-left: 4px solid #FFD700; 
        padding-left: 10px;
    }
    
    .pending-report {
        background: linear-gradient(90deg, rgba(255, 193, 7, 0.2) 0%, transparent 100%);
        border: 2px solid #FFC107;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { border-color: #FFC107; }
        50% { border-color: #FFA000; }
        100% { border-color: #FFC107; }
    }

    .phase-badge { 
        display: inline-block; 
        padding: 4px 12px; 
        border-radius: 0px; 
        font-size: 0.9rem; 
        font-weight: bold; 
        margin-left: 10px; 
        border: 1px solid #F1E194; 
        color: #F1E194; 
        background: rgba(91, 14, 20, 0.8);
    }
    
    .sudden-death { 
        background: linear-gradient(90deg, #000 0%, #5B0E14 50%, #000 100%); 
        color: white; 
        border: 2px solid #ff0000; 
    }
    .golden-boot { color: #F1E194; font-weight: bold; font-size: 1.5rem; text-shadow: 0 0 10px #F1E194; }
    
    /* TOAST */
    div[data-baseweb="toast"] {
        background-color: #5B0E14 !important;
        color: #F1E194 !important;
        border: 1px solid #F1E194 !important;
    }
    
    /* METRICS */
    div[data-testid="stMetricValue"] {
        color: #F1E194 !important;
        font-family: 'Teko' !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #946c1e !important;
    }
    
    /* BRACKET STYLES */
    .bracket-match {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #5B0E14;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .bracket-winner {
        background: linear-gradient(90deg, rgba(241, 225, 148, 0.2) 0%, transparent 100%);
        border-left: 3px solid #F1E194;
    }
    
    /* CAPTAIN PORTAL */
    .captain-portal {
        background: linear-gradient(135deg, rgba(21, 101, 192, 0.2) 0%, rgba(33, 150, 243, 0.1) 100%);
        border: 2px solid #2196F3;
    }
    
    /* NOTIFICATION BADGE */
    .notification-badge {
        position: absolute;
        top: -5px;
        right: -5px;
        background: #F44336;
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        font-size: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Rajdhani';
        font-weight: bold;
    }
    
    /* PROGRESS BAR */
    .progress-container {
        width: 100%;
        background-color: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        margin: 10px 0;
        height: 20px;
    }
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #F1E194 0%, #946c1e 100%);
        border-radius: 10px;
        text-align: center;
        line-height: 20px;
        color: #000;
        font-weight: bold;
        font-family: 'Rajdhani';
    }
    
    /* NEWS FEED */
    .news-item {
        padding: 10px;
        margin: 5px 0;
        border-left: 3px solid #F1E194;
        background: rgba(0, 0, 0, 0.2);
    }
    .news-item:last-child {
        border-bottom: none;
    }
    
    /* FILE UPLOAD */
    .uploadedFile {
        background: rgba(0, 0, 0, 0.5) !important;
        border: 1px solid #5B0E14 !important;
    }
    
    /* PAST CHAMPIONS */
    .champion-card {
        background: linear-gradient(135deg, rgba(241, 225, 148, 0.1) 0%, rgba(148, 108, 30, 0.2) 100%);
        border: 2px solid #F1E194;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
    .champion-year {
        font-size: 0.9rem;
        color: #946c1e;
        font-weight: bold;
    }
    .champion-name {
        font-size: 1.5rem;
        color: #F1E194;
        font-weight: bold;
        margin: 5px 0;
    }
    .champion-format {
        font-size: 0.8rem;
        color: #e2d2a3;
    }
    
    /* CAPTAIN CREDENTIALS */
    .credentials-box {
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid #2196F3;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    /* PIN DISPLAY */
    .pin-display {
        font-family: 'Courier New', monospace;
        font-weight: bold;
        color: #F1E194;
        background: rgba(0, 0, 0, 0.5);
        padding: 5px 10px;
        border-radius: 4px;
        border: 1px solid #5B0E14;
    }
    
    /* FIXED RESULT BUTTON */
    .fixed-result-btn {
        background: linear-gradient(90deg, #FF9800 0%, #FFB74D 100%) !important;
        color: white !important;
        border: 1px solid #FF9800 !important;
        font-size: 0.8rem !important;
        padding: 5px 10px !important;
    }
    
    /* DISABLED STATE */
    .disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
    
    /* EDIT MODE HIGHLIGHT */
    .edit-mode {
        background: linear-gradient(90deg, rgba(255, 152, 0, 0.2) 0%, transparent 100%);
        border: 2px solid #FF9800;
    }
</style>
""", unsafe_allow_html=True)

# --- 💾 DATABASE ---
DB_FILE = "dls_ultra_db.json"
BADGE_POOL = ["🦁", "🦅", "🐺", "🐉", "🦈", "🐍", "🐻", "🐝", "🦂", "🕷️", "⚓", "⚔️", "🛡️", "👑", "⚡", "🔥", "🌪️", "🌊", "🏰", "🚀", "💀", "👹", "👽", "🤖", "👻", "🎃", "💎", "🎯", "🎲", "🎱"]

# Default tournament code
DEFAULT_TOURNAMENT_CODE = "DLS2026"

def init_defaults():
    defaults = {
        'teams': [], 'format': 'League', 'current_round': 'Group Stage',
        'fixtures': [], 'results': {}, 'match_meta': {},
        'started': False, 'groups': {}, 'champion': None, 'active_teams': [], 
        'team_badges': {}, 'news': [], 
        'legacy_stats': {}, 'team_history': {},
        'eliminated_teams': [], 'round_number': 1, 'survival_history': [],
        'battle_phase': 'Phase 1: The Purge',
        'bye_team': None,
        'cumulative_stats': {},
        'cumulative_player_stats': {},
        'sudden_death_round': 0,
        'phase1_match_count': 2,
        'world_cup_stage': 'Group Stage',
        'knockout_bracket': {},
        'knockout_round': 1,
        'knockout_winners': {},
        'match_history': {},
        
        # Captain's Portal Additions
        'captain_pins': {},  # team_name: pin
        'pending_reports': [],  # List of pending match reports
        'tournament_code': DEFAULT_TOURNAMENT_CODE,
        'user_mode': 'Admin',  # 'Admin' or 'Captain'
        'logged_in_captain': None,
        'captain_pin_verified': False,
        'team_passwords': {},  # team_name: hashed_password
        'captain_logs': [],  # Log of captain actions
        
        # NEW: Past Champions Feature
        'past_champions': [],  # List of dictionaries with champion info
        'champion_history': {},  # Year/Tournament -> Champion mapping
        
        # NEW: Fixed Results by Captains
        'fixed_results': {},  # match_id -> result fixed by captain
        'captain_fixed_matches': {},  # team_name -> list of match_ids they fixed
        'admin_approved_results': {}  # match_id -> True if approved by admin
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                # Load all existing data
                for key in ['teams', 'format', 'current_round', 'fixtures', 'results', 
                          'match_meta', 'started', 'groups', 'champion', 'active_teams',
                          'team_badges', 'news', 'legacy_stats', 
                          'team_history', 'eliminated_teams', 'round_number', 
                          'survival_history', 'battle_phase', 'bye_team', 
                          'cumulative_stats', 'cumulative_player_stats', 
                          'sudden_death_round', 'phase1_match_count',
                          'world_cup_stage', 'knockout_bracket', 'knockout_round',
                          'knockout_winners', 'match_history']:
                    if key in data:
                        if key == 'fixtures':
                            st.session_state[key] = [tuple(f) for f in data[key]] if isinstance(data[key], list) else []
                        else:
                            st.session_state[key] = data[key]
                
                # Load Captain's Portal data with defaults
                st.session_state.captain_pins = data.get('captain_pins', {})
                st.session_state.pending_reports = data.get('pending_reports', [])
                st.session_state.tournament_code = data.get('tournament_code', DEFAULT_TOURNAMENT_CODE)
                st.session_state.user_mode = data.get('user_mode', 'Admin')
                st.session_state.logged_in_captain = data.get('logged_in_captain', None)
                st.session_state.captain_pin_verified = data.get('captain_pin_verified', False)
                st.session_state.team_passwords = data.get('team_passwords', {})
                st.session_state.captain_logs = data.get('captain_logs', [])
                
                # Load Past Champions
                st.session_state.past_champions = data.get('past_champions', [])
                st.session_state.champion_history = data.get('champion_history', {})
                
                # Load Fixed Results data
                st.session_state.fixed_results = data.get('fixed_results', {})
                st.session_state.captain_fixed_matches = data.get('captain_fixed_matches', {})
                st.session_state.admin_approved_results = data.get('admin_approved_results', {})

                # Initialize badges for new teams
                for t in st.session_state.teams:
                    if t not in st.session_state.team_badges:
                        st.session_state.team_badges[t] = random.choice(BADGE_POOL)
                        
                # Initialize captain pins for existing teams
                for t in st.session_state.teams:
                    if t not in st.session_state.captain_pins:
                        st.session_state.captain_pins[t] = generate_pin()
                        
                # Initialize captain fixed matches for existing teams
                for t in st.session_state.teams:
                    if t not in st.session_state.captain_fixed_matches:
                        st.session_state.captain_fixed_matches[t] = []
        except Exception as e:
            st.error(f"Error loading data: {e}")
            init_defaults()
    else:
        init_defaults()

def save_data_internal():
    """Save all data including captain's portal data"""
    try:
        data = {
            # Existing data
            "teams": st.session_state.teams,
            "format": st.session_state.format,
            "current_round": st.session_state.current_round,
            "fixtures": st.session_state.fixtures,
            "results": st.session_state.results,
            "match_meta": st.session_state.match_meta,
            "started": st.session_state.started,
            "groups": st.session_state.groups,
            "champion": st.session_state.champion,
            "active_teams": st.session_state.active_teams,
            "team_badges": st.session_state.team_badges,
            "news": st.session_state.news,
            "legacy_stats": st.session_state.legacy_stats,
            "team_history": st.session_state.team_history,
            "eliminated_teams": st.session_state.eliminated_teams,
            "round_number": st.session_state.round_number,
            "survival_history": st.session_state.survival_history,
            "battle_phase": st.session_state.battle_phase,
            "bye_team": st.session_state.bye_team,
            "cumulative_stats": st.session_state.cumulative_stats,
            "cumulative_player_stats": st.session_state.cumulative_player_stats,
            "sudden_death_round": st.session_state.sudden_death_round,
            "phase1_match_count": st.session_state.phase1_match_count,
            "world_cup_stage": st.session_state.world_cup_stage,
            "knockout_bracket": st.session_state.knockout_bracket,
            "knockout_round": st.session_state.knockout_round,
            "knockout_winners": st.session_state.knockout_winners,
            "match_history": st.session_state.match_history,
            
            # Captain's Portal data
            "captain_pins": st.session_state.captain_pins,
            "pending_reports": st.session_state.pending_reports,
            "tournament_code": st.session_state.tournament_code,
            "user_mode": st.session_state.user_mode,
            "logged_in_captain": st.session_state.logged_in_captain,
            "captain_pin_verified": st.session_state.captain_pin_verified,
            "team_passwords": st.session_state.team_passwords,
            "captain_logs": st.session_state.captain_logs,
            
            # Past Champions
            "past_champions": st.session_state.past_champions,
            "champion_history": st.session_state.champion_history,
            
            # Fixed Results data
            "fixed_results": st.session_state.fixed_results,
            "captain_fixed_matches": st.session_state.captain_fixed_matches,
            "admin_approved_results": st.session_state.admin_approved_results
        }
        with open(DB_FILE, "w") as f: 
            json.dump(data, f)
        return True
    except Exception as e:
        st.error(f"Failed to save data: {e}")
        return False

# --- NEW FEATURE: DATA MANAGEMENT FUNCTIONS ---

def download_backup():
    """Create a downloadable backup of all data"""
    data = {
        "teams": st.session_state.teams,
        "format": st.session_state.format,
        "current_round": st.session_state.current_round,
        "fixtures": st.session_state.fixtures,
        "results": st.session_state.results,
        "match_meta": st.session_state.match_meta,
        "started": st.session_state.started,
        "groups": st.session_state.groups,
        "champion": st.session_state.champion,
        "active_teams": st.session_state.active_teams,
        "team_badges": st.session_state.team_badges,
        "news": st.session_state.news,
        "legacy_stats": st.session_state.legacy_stats,
        "team_history": st.session_state.team_history,
        "eliminated_teams": st.session_state.eliminated_teams,
        "round_number": st.session_state.round_number,
        "survival_history": st.session_state.survival_history,
        "battle_phase": st.session_state.battle_phase,
        "bye_team": st.session_state.bye_team,
        "cumulative_stats": st.session_state.cumulative_stats,
        "cumulative_player_stats": st.session_state.cumulative_player_stats,
        "sudden_death_round": st.session_state.sudden_death_round,
        "phase1_match_count": st.session_state.phase1_match_count,
        "world_cup_stage": st.session_state.world_cup_stage,
        "knockout_bracket": st.session_state.knockout_bracket,
        "knockout_round": st.session_state.knockout_round,
        "knockout_winners": st.session_state.knockout_winners,
        "match_history": st.session_state.match_history,
        "captain_pins": st.session_state.captain_pins,
        "pending_reports": st.session_state.pending_reports,
        "tournament_code": st.session_state.tournament_code,
        "user_mode": st.session_state.user_mode,
        "logged_in_captain": st.session_state.logged_in_captain,
        "captain_pin_verified": st.session_state.captain_pin_verified,
        "team_passwords": st.session_state.team_passwords,
        "captain_logs": st.session_state.captain_logs,
        "past_champions": st.session_state.past_champions,
        "champion_history": st.session_state.champion_history,
        "fixed_results": st.session_state.fixed_results,
        "captain_fixed_matches": st.session_state.captain_fixed_matches,
        "admin_approved_results": st.session_state.admin_approved_results
    }
    
    # Convert to JSON string
    json_str = json.dumps(data, indent=2)
    
    # Create download link
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="dls_ultra_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json" class="stButton">📥 DOWNLOAD BACKUP</a>'
    return href

def restore_backup(uploaded_file):
    """Restore data from uploaded backup file"""
    try:
        # Read uploaded file
        data = json.load(uploaded_file)
        
        # Validate basic structure
        required_keys = ['teams', 'format', 'current_round', 'fixtures']
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Invalid backup file: missing {key}")
        
        # Clear current session state
        st.session_state.clear()
        
        # Load all data from backup
        for key, value in data.items():
            st.session_state[key] = value
        
        # Save to disk
        save_data_internal()
        
        return True, "Backup restored successfully!"
    except Exception as e:
        return False, f"Error restoring backup: {str(e)}"

def factory_reset():
    """Complete reset of all tournament data"""
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Re-initialize defaults
    init_defaults()
    
    # Delete database file if exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    return True

def delete_team(team_name):
    """Delete a team and all associated data"""
    if team_name in st.session_state.teams:
        # Remove from teams list
        st.session_state.teams.remove(team_name)
        
        # Remove from active teams if present
        if team_name in st.session_state.active_teams:
            st.session_state.active_teams.remove(team_name)
        
        # Remove from groups
        for group_name, teams in st.session_state.groups.items():
            if team_name in teams:
                st.session_state.groups[group_name].remove(team_name)
        
        # Remove associated data
        for key in ['team_badges', 'captain_pins', 'team_passwords', 'cumulative_stats', 'captain_fixed_matches']:
            if team_name in st.session_state.get(key, {}):
                del st.session_state[key][team_name]
        
        # Remove player stats for this team
        player_ids_to_remove = []
        for player_id in st.session_state.cumulative_player_stats:
            if f"|{team_name}" in player_id:
                player_ids_to_remove.append(player_id)
        
        for player_id in player_ids_to_remove:
            del st.session_state.cumulative_player_stats[player_id]
        
        # Remove from eliminated teams
        st.session_state.eliminated_teams = [e for e in st.session_state.eliminated_teams if e['team'] != team_name]
        
        # Regenerate fixtures without this team
        regenerate_fixtures()
        
        # Add to news
        st.session_state.news.insert(0, f"🗑️ Team '{team_name}' deleted")
        
        return True
    return False

def regenerate_fixtures():
    """Regenerate fixtures after team deletion"""
    if not st.session_state.started or not st.session_state.active_teams:
        return
    
    if "Survival" in st.session_state.format:
        # For Battle Royale, regenerate based on current phase
        current_phase = st.session_state.battle_phase
        fixtures = generate_fixtures_for_phase(st.session_state.active_teams, current_phase)
        st.session_state.fixtures = fixtures
    elif "League" in st.session_state.format:
        # Regenerate league fixtures
        matches = list(itertools.permutations(st.session_state.active_teams, 2))
        random.shuffle(matches)
        st.session_state.fixtures = matches
    elif "World Cup" in st.session_state.format and st.session_state.world_cup_stage == "Group Stage":
        # Reassign groups and regenerate fixtures
        shuffled = st.session_state.active_teams.copy()
        random.shuffle(shuffled)
        
        # Redistribute teams into groups
        groups = {}
        group_names = "ABCDEFGHIJKLMNOP"
        group_size = 4
        
        for i, team in enumerate(shuffled):
            group_idx = i // group_size
            if group_idx >= len(group_names):
                group_idx = len(group_names) - 1
            group_name = group_names[group_idx]
            
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(team)
        
        st.session_state.groups = groups
        
        # Generate new fixtures
        matches = []
        for g, teams in groups.items():
            matches.extend(list(itertools.combinations(teams, 2)))
        
        st.session_state.fixtures = matches
    elif "Knockout" in st.session_state.format:
        # Regenerate knockout bracket
        shuffled = st.session_state.active_teams.copy()
        random.shuffle(shuffled)
        
        # Ensure even number of teams
        if len(shuffled) % 2 != 0:
            shuffled.append("BYE")
        
        matches = []
        for i in range(0, len(shuffled), 2):
            if i + 1 < len(shuffled) and shuffled[i] != "BYE" and shuffled[i+1] != "BYE":
                matches.append((shuffled[i], shuffled[i + 1]))
        
        st.session_state.fixtures = matches

# --- CAPTAIN'S PORTAL FUNCTIONS ---

def generate_pin():
    """Generate a random 4-digit PIN"""
    return str(random.randint(1000, 9999))

def generate_team_password():
    """Generate a random password for team registration"""
    adjectives = ["Swift", "Brave", "Royal", "Golden", "Mighty", "Fierce", "Noble", "Valiant"]
    nouns = ["Lions", "Eagles", "Wolves", "Dragons", "Sharks", "Titans", "Gladiators", "Warriors"]
    return f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(10, 99)}"

def hash_password(password):
    """Simple hash for password storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_team_name(team_name):
    """Validate team name to prevent problematic characters"""
    if not team_name:
        return False, "Team name cannot be empty"
    
    # Check for forbidden characters
    forbidden_chars = ['_', 'v', '|', '/', '\\', '"', "'"]
    for char in forbidden_chars:
        if char in team_name:
            return False, f"Team name cannot contain '{char}' character"
    
    # Check length
    if len(team_name) > 50:
        return False, "Team name too long (max 50 characters)"
    
    return True, ""

def add_team_with_captain(team_name):
    """Add a team with captain credentials"""
    # Validate team name
    is_valid, error_msg = validate_team_name(team_name)
    if not is_valid:
        return error_msg, None, None
    
    if team_name and team_name not in st.session_state.teams:
        # Add team
        st.session_state.teams.append(team_name)
        st.session_state.team_badges[team_name] = random.choice(BADGE_POOL)
        
        # Generate PIN and password
        pin = generate_pin()
        password = generate_team_password()
        
        st.session_state.captain_pins[team_name] = pin
        st.session_state.team_passwords[team_name] = hash_password(password)
        
        # Initialize fixed matches tracking
        st.session_state.captain_fixed_matches[team_name] = []
        
        # Add to active teams if tournament started
        if st.session_state.started:
            st.session_state.active_teams.append(team_name)
            
            # Initialize stats
            if team_name not in st.session_state.cumulative_stats:
                st.session_state.cumulative_stats[team_name] = {
                    'P': 0, 'W': 0, 'D': 0, 'L': 0, 
                    'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0
                }
            
            # Add fixtures for the new team
            add_fixtures_for_new_team(team_name)
            
            st.toast(f"🧢 {team_name} joins the tournament!")
        
        # Log the registration
        log_captain_action(f"Team '{team_name}' registered", team_name)
        
        # Show credentials to user
        credentials_msg = f"""
        **Team Registered Successfully!**
        
        **Team:** {team_name}
        **Captain PIN:** `{pin}`
        **Team Password:** `{password}`
        
        ⚠️ **SAVE THESE CREDENTIALS NOW!**
        - You'll need the PIN to log in as captain
        - Share the password with your team members
        """
        
        return credentials_msg, pin, password
    return None, None, None

def add_fixtures_for_new_team(team_name):
    """Add fixtures for a newly added team"""
    if not st.session_state.started:
        return
    
    # Get all existing teams except the new one
    other_teams = [t for t in st.session_state.active_teams if t != team_name]
    
    # Add fixtures based on tournament format
    if "League" in st.session_state.format:
        # Add home and away matches against all other teams
        for opponent in other_teams:
            st.session_state.fixtures.append((team_name, opponent))
            st.session_state.fixtures.append((opponent, team_name))
    
    elif "World Cup" in st.session_state.format and st.session_state.world_cup_stage == "Group Stage":
        # Find a group to add the team to
        added = False
        for group_name, teams in st.session_state.groups.items():
            if len(teams) < 4:  # Add to group with space
                st.session_state.groups[group_name].append(team_name)
                # Add group matches
                for opponent in teams:
                    st.session_state.fixtures.append((team_name, opponent))
                    st.session_state.fixtures.append((opponent, team_name))
                added = True
                break
        
        if not added:
            # Create new group
            new_group = chr(65 + len(st.session_state.groups))  # A, B, C, etc.
            st.session_state.groups[new_group] = [team_name]
    
    elif "Knockout" in st.session_state.format:
        # Add to next available spot
        st.session_state.fixtures.append((team_name, "BYE" if len(st.session_state.active_teams) % 2 != 0 else other_teams[-1]))
    
    elif "Survival" in st.session_state.format:
        # Survival mode - add to next round's fixtures
        if st.session_state.fixtures:
            # Add the team to some existing fixtures
            for i in range(min(2, len(other_teams))):  # Give them 2 matches
                opponent = other_teams[i % len(other_teams)]
                st.session_state.fixtures.append((team_name, opponent))

def log_captain_action(action, team=None):
    """Log captain actions for audit trail"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        'timestamp': timestamp,
        'action': action,
        'team': team or st.session_state.logged_in_captain,
        'user_mode': st.session_state.user_mode
    }
    st.session_state.captain_logs.append(log_entry)
    
    # Keep only last 100 logs
    if len(st.session_state.captain_logs) > 100:
        st.session_state.captain_logs = st.session_state.captain_logs[-100:]

def submit_match_report(match_id, home_team, away_team, home_score, away_score, 
                        home_scorers="", away_scorers="", home_assists="", 
                        away_assists="", home_reds="", away_reds="", 
                        home_pens=0, away_pens=0, submitted_by=""):
    """Submit a match report for approval"""
    report = {
        'report_id': f"{match_id}_{datetime.now().timestamp()}",
        'match_id': match_id,
        'home_team': home_team,
        'away_team': away_team,
        'home_score': home_score,
        'away_score': away_score,
        'home_scorers': home_scorers,
        'away_scorers': away_scorers,
        'home_assists': home_assists,
        'away_assists': away_assists,
        'home_reds': home_reds,
        'away_reds': away_reds,
        'home_pens': home_pens,
        'away_pens': away_pens,
        'submitted_by': submitted_by,
        'submitted_at': datetime.now().isoformat(),
        'status': 'pending'
    }
    
    # Check if there's already a pending report for this match
    existing = [r for r in st.session_state.pending_reports if r['match_id'] == match_id]
    if existing:
        # Replace existing pending report
        st.session_state.pending_reports = [r for r in st.session_state.pending_reports if r['match_id'] != match_id]
    
    st.session_state.pending_reports.append(report)
    
    # Log the submission
    log_captain_action(f"Submitted match report: {home_team} {home_score}-{away_score} {away_team}", submitted_by)
    
    return report

def update_pending_report(report_id, home_score, away_score, home_scorers="", away_scorers="", 
                         home_assists="", away_assists="", home_reds="", away_reds="", 
                         home_pens=0, away_pens=0):
    """Update a pending report before approval (admin only)"""
    for report in st.session_state.pending_reports:
        if report['report_id'] == report_id:
            report['home_score'] = home_score
            report['away_score'] = away_score
            report['home_scorers'] = home_scorers
            report['away_scorers'] = away_scorers
            report['home_assists'] = home_assists
            report['away_assists'] = away_assists
            report['home_reds'] = home_reds
            report['away_reds'] = away_reds
            report['home_pens'] = home_pens
            report['away_pens'] = away_pens
            
            # Update fixed result if exists
            match_id = report['match_id']
            if match_id in st.session_state.fixed_results:
                st.session_state.fixed_results[match_id].update({
                    'home_score': home_score,
                    'away_score': away_score,
                    'home_scorers': home_scorers,
                    'away_scorers': away_scorers,
                    'home_assists': home_assists,
                    'away_assists': away_assists,
                    'home_reds': home_reds,
                    'away_reds': away_reds,
                    'home_pens': home_pens,
                    'away_pens': away_pens
                })
            
            log_captain_action(f"Updated pending report: {report['home_team']} {home_score}-{away_score} {report['away_team']}")
            return True
    
    return False

def approve_match_report(report_id):
    """Approve a pending match report"""
    report = next((r for r in st.session_state.pending_reports if r['report_id'] == report_id), None)
    if not report:
        return False
    
    # Apply the match result
    mid = report['match_id']
    h, a = report['home_team'], report['away_team']
    s1, s2 = report['home_score'], report['away_score']
    p1, p2 = report['home_pens'], report['away_pens']
    
    # Mark as approved by admin
    st.session_state.admin_approved_results[mid] = True
    
    # Update match result
    update_match_result_safely(mid, h, a, s1, s2, p1, p2, 
                              report['home_scorers'], report['away_scorers'],
                              report['home_assists'], report['away_assists'],
                              report['home_reds'], report['away_reds'])
    
    # Remove from pending reports
    st.session_state.pending_reports = [r for r in st.session_state.pending_reports if r['report_id'] != report_id]
    
    # Remove from fixed results if exists
    if mid in st.session_state.fixed_results:
        del st.session_state.fixed_results[mid]
    
    # Add to news
    st.session_state.news.insert(0, f"✅ {h} {s1}-{s2} {a} (Report approved)")
    
    # Log the approval
    log_captain_action(f"Approved match report: {h} {s1}-{s2} {a}")
    
    return True

def reject_match_report(report_id):
    """Reject a pending match report"""
    report = next((r for r in st.session_state.pending_reports if r['report_id'] == report_id), None)
    if not report:
        return False
    
    # Remove from pending reports
    st.session_state.pending_reports = [r for r in st.session_state.pending_reports if r['report_id'] != report_id]
    
    # Remove from fixed results if exists
    if report['match_id'] in st.session_state.fixed_results:
        del st.session_state.fixed_results[report['match_id']]
    
    # Log the rejection
    log_captain_action(f"Rejected match report: {report['home_team']} {report['home_score']}-{report['away_score']} {report['away_team']}")
    
    return True

def reset_match_result(match_id):
    """Reset a match result (admin only)"""
    if match_id in st.session_state.results:
        try:
            # Get match details
            if "_" in match_id:
                base = match_id.split('_')[0]
            else:
                base = match_id
            
            if "v" not in base:
                return False
            
            h, a = base.split('v')
        except Exception:
            return False
        
        # Remove from results
        del st.session_state.results[match_id]
        
        # Remove from match meta
        if match_id in st.session_state.match_meta:
            del st.session_state.match_meta[match_id]
        
        # Remove from match history
        if match_id in st.session_state.match_history:
            del st.session_state.match_history[match_id]
        
        # Remove from fixed results
        if match_id in st.session_state.fixed_results:
            del st.session_state.fixed_results[match_id]
        
        # Remove from admin approved results
        if match_id in st.session_state.admin_approved_results:
            del st.session_state.admin_approved_results[match_id]
        
        # Remove from captain fixed matches
        for team in st.session_state.captain_fixed_matches:
            if match_id in st.session_state.captain_fixed_matches[team]:
                st.session_state.captain_fixed_matches[team].remove(match_id)
        
        # Add to news
        st.session_state.news.insert(0, f"🔄 Match reset: {h} vs {a}")
        
        # Log the reset
        log_captain_action(f"Reset match: {h} vs {a}")
        
        return True
    return False

# --- NEW: FIXED RESULTS SYSTEM ---

def captain_can_fix_match(match_id, captain_team):
    """Check if a captain can fix a match result"""
    try:
        if "_" not in match_id or "v" not in match_id:
            return False
        
        base = match_id.split('_')[0]
        if 'v' not in base:
            return False
        
        h, a = base.split('v')
        
        # Captain can only fix matches involving their team
        return captain_team in [h, a]
    except Exception:
        return False

def fix_match_result_by_captain(match_id, home_team, away_team, home_score, away_score,
                               home_scorers="", away_scorers="", home_assists="", 
                               away_assists="", home_reds="", away_reds="", 
                               home_pens=0, away_pens=0, fixed_by=""):
    """Captain fixes a match result - creates a pending report"""
    
    # Create a fixed result record
    fixed_result = {
        'match_id': match_id,
        'home_team': home_team,
        'away_team': away_team,
        'home_score': home_score,
        'away_score': away_score,
        'home_scorers': home_scorers,
        'away_scorers': away_scorers,
        'home_assists': home_assists,
        'away_assists': away_assists,
        'home_reds': home_reds,
        'away_reds': away_reds,
        'home_pens': home_pens,
        'away_pens': away_pens,
        'fixed_by': fixed_by,
        'fixed_at': datetime.now().isoformat(),
        'status': 'pending'
    }
    
    # Store fixed result
    st.session_state.fixed_results[match_id] = fixed_result
    
    # Track which matches this captain has fixed
    if fixed_by not in st.session_state.captain_fixed_matches:
        st.session_state.captain_fixed_matches[fixed_by] = []
    
    if match_id not in st.session_state.captain_fixed_matches[fixed_by]:
        st.session_state.captain_fixed_matches[fixed_by].append(match_id)
    
    # Create a pending report for admin approval
    report = submit_match_report(match_id, home_team, away_team, home_score, away_score,
                                home_scorers, away_scorers, home_assists, away_assists,
                                home_reds, away_reds, home_pens, away_pens, fixed_by)
    
    # Log the action
    log_captain_action(f"Fixed match result: {home_team} {home_score}-{away_score} {away_team} (Pending approval)", fixed_by)
    
    return fixed_result, report

def get_match_result_status(match_id):
    """Get the status of a match result"""
    if match_id in st.session_state.admin_approved_results:
        return "approved"
    elif match_id in st.session_state.fixed_results:
        return "pending"
    elif match_id in st.session_state.results:
        return "completed"
    else:
        return "not_played"

# --- NEW: ADMIN CAPTAIN CONTROLS ---

def view_all_captain_pins():
    """Display all captain PINs for admin"""
    if not st.session_state.teams:
        return "No teams registered yet."
    
    pins_data = []
    for team in st.session_state.teams:
        pin = st.session_state.captain_pins.get(team, "Not set")
        pins_data.append({
            "Team": team,
            "Captain PIN": pin,
            "Status": "Active" if team in st.session_state.active_teams else "Inactive"
        })
    
    return pd.DataFrame(pins_data)

def reset_captain_pin(team_name):
    """Reset a captain's PIN"""
    if team_name in st.session_state.captain_pins:
        new_pin = generate_pin()
        st.session_state.captain_pins[team_name] = new_pin
        
        # Log the action
        log_captain_action(f"Reset PIN for {team_name} to {new_pin}")
        
        return True, new_pin
    return False, None

def view_team_credentials(team_name):
    """Get team credentials including password"""
    if team_name in st.session_state.teams:
        pin = st.session_state.captain_pins.get(team_name, "Not set")
        # Note: Passwords are hashed, so we can't show the original
        return {
            "team": team_name,
            "pin": pin,
            "hashed_password": st.session_state.team_passwords.get(team_name, "Not set"),
            "badge": st.session_state.team_badges.get(team_name, "🛡️")
        }
    return None

def regenerate_all_pins():
    """Regenerate PINs for all teams"""
    for team in st.session_state.teams:
        st.session_state.captain_pins[team] = generate_pin()
    
    # Log the action
    log_captain_action("Regenerated all captain PINs")
    
    return True

# --- PAST CHAMPIONS FEATURE ---

def add_past_champion(champion_name, year=None, tournament_format=None):
    """Add a past champion to the hall of fame"""
    if not champion_name:
        return False
    
    # Use current year if not specified
    if not year:
        year = datetime.now().year
    
    # Use current format if not specified
    if not tournament_format:
        tournament_format = st.session_state.format
    
    champion_entry = {
        'champion': champion_name,
        'year': year,
        'format': tournament_format,
        'added_at': datetime.now().isoformat()
    }
    
    # Add to past champions list
    st.session_state.past_champions.append(champion_entry)
    
    # Also add to champion history by year
    st.session_state.champion_history[str(year)] = {
        'champion': champion_name,
        'format': tournament_format
    }
    
    # Sort past champions by year (newest first)
    st.session_state.past_champions.sort(key=lambda x: x['year'], reverse=True)
    
    # Log the action
    log_captain_action(f"Added past champion: {champion_name} ({year})")
    
    return True

def remove_past_champion(index):
    """Remove a past champion from the hall of fame"""
    if 0 <= index < len(st.session_state.past_champions):
        removed = st.session_state.past_champions.pop(index)
        
        # Also remove from champion history
        year_key = str(removed['year'])
        if year_key in st.session_state.champion_history:
            del st.session_state.champion_history[year_key]
        
        # Log the action
        log_captain_action(f"Removed past champion: {removed['champion']} ({removed['year']})")
        
        return True
    return False

# --- NEW: MANUAL PLAYER STATS MANAGEMENT ---

def add_player_stat(player_name, team_name, stat_type, count=1):
    """Manually add player stat"""
    player_name = player_name.strip().title()
    if not player_name:
        return False
    
    player_id = f"{player_name}|{team_name}"
    
    # Initialize if not exists
    if player_id not in st.session_state.cumulative_player_stats:
        st.session_state.cumulative_player_stats[player_id] = {
            'Name': player_name,
            'Team': team_name,
            'G': 0, 'A': 0, 'R': 0
        }
    
    # Add stat
    st.session_state.cumulative_player_stats[player_id][stat_type] += count
    
    # Remove player if all stats are zero
    player_stats = st.session_state.cumulative_player_stats[player_id]
    if player_stats['G'] == 0 and player_stats['A'] == 0 and player_stats['R'] == 0:
        del st.session_state.cumulative_player_stats[player_id]
    
    return True

def delete_player_stat(player_id):
    """Delete a player's stats entirely"""
    if player_id in st.session_state.cumulative_player_stats:
        del st.session_state.cumulative_player_stats[player_id]
        return True
    return False

def edit_player_stat(player_id, stat_type, new_value):
    """Edit a specific player stat"""
    if player_id in st.session_state.cumulative_player_stats:
        st.session_state.cumulative_player_stats[player_id][stat_type] = max(0, new_value)
        
        # Remove player if all stats are zero
        player_stats = st.session_state.cumulative_player_stats[player_id]
        if player_stats['G'] == 0 and player_stats['A'] == 0 and player_stats['R'] == 0:
            del st.session_state.cumulative_player_stats[player_id]
        
        return True
    return False

# --- DEBUGGING HELPER FUNCTIONS ---

def debug_captain_view(captain_team):
    """Debug function to show what matches are available for captain"""
    debug_info = {
        "captain_team": captain_team,
        "active_teams": st.session_state.active_teams,
        "fixtures_count": len(st.session_state.fixtures),
        "captain_fixtures": []
    }
    
    for i, fix in enumerate(st.session_state.fixtures):
        if len(fix) < 2:
            continue
        h, a = fix[0], fix[1]
        if captain_team in [h, a]:
            mid = f"{h}v{a}_{i}"
            debug_info["captain_fixtures"].append({
                "match_id": mid,
                "home": h,
                "away": a,
                "index": i,
                "in_active_teams": h in st.session_state.active_teams and a in st.session_state.active_teams
            })
    
    return debug_info

def find_matches_for_team(team_name):
    """Find all matches for a specific team"""
    matches = []
    for i, fix in enumerate(st.session_state.fixtures):
        if len(fix) < 2:
            continue
        h, a = fix[0], fix[1]
        if team_name in [h, a]:
            mid = f"{h}v{a}_{i}"
            matches.append({
                "index": i,
                "home": h,
                "away": a,
                "match_id": mid,
                "status": get_match_result_status(mid)
            })
    return matches

# --- 🧠 BATTLE ROYALE CORE LOGIC ---

def generate_balanced_fixtures_fixed(teams, matches_per_team):
    """Generate fixtures where EVERY team plays exactly N matches"""
    if len(teams) < 2: return []
    
    # Create a round-robin schedule
    def round_robin(teams_list):
        """Generate round-robin pairs"""
        if len(teams_list) % 2:
            teams_list.append(None)
        
        n = len(teams_list)
        fixtures = []
        
        for round_num in range(n - 1):
            round_fixtures = []
            for i in range(n // 2):
                if teams_list[i] is not None and teams_list[n - 1 - i] is not None:
                    round_fixtures.append((teams_list[i], teams_list[n - 1 - i]))
            
            teams_list.insert(1, teams_list.pop())
            fixtures.extend(round_fixtures)
        
        return fixtures
    
    all_possible = list(itertools.combinations(teams, 2))
    random.shuffle(all_possible)
    
    if matches_per_team <= len(teams) - 1:
        fixtures = []
        for _ in range(matches_per_team):
            round_fixtures = round_robin(teams.copy())
            round_fixtures = [f for f in round_fixtures if f[0] is not None and f[1] is not None]
            fixtures.extend(round_fixtures)
        
        total_matches_needed = (len(teams) * matches_per_team) // 2
        if len(fixtures) >= total_matches_needed:
            return fixtures[:total_matches_needed]
    
    team_match_counts = {team: 0 for team in teams}
    fixtures = []
    available_pairs = all_possible.copy()
    
    iterations = 0
    while available_pairs and min(team_match_counts.values()) < matches_per_team:
        iterations += 1
        if iterations > 2000: break # Safety break
        
        for pair in available_pairs[:]:
            t1, t2 = pair
            if team_match_counts[t1] < matches_per_team and team_match_counts[t2] < matches_per_team:
                fixtures.append(pair)
                team_match_counts[t1] += 1
                team_match_counts[t2] += 1
                available_pairs.remove(pair)
                break
        else:
            break
    
    # Fallback to random pairings if balanced generation failed
    if min(team_match_counts.values()) < matches_per_team:
        needy_teams = [t for t in teams if team_match_counts[t] < matches_per_team]
        
        for i in range(len(needy_teams)):
            for j in range(i + 1, len(needy_teams)):
                t1, t2 = needy_teams[i], needy_teams[j]
                # Allow duplicates if absolutely necessary to get games
                existing = False
                for fix in fixtures:
                    if (fix[0] == t1 and fix[1] == t2) or (fix[0] == t2 and fix[1] == t1):
                        existing = True
                        break
                
                if not existing or len(fixtures) < len(teams):
                    fixtures.append((t1, t2))
                    team_match_counts[t1] += 1
                    team_match_counts[t2] += 1
    
    return fixtures

def generate_fixtures_for_phase(teams, phase):
    """Generate fixtures based on current phase"""
    shuffled = teams.copy()
    random.shuffle(shuffled)
    
    if phase == "Phase 1: The Purge":
        matches_per_team = 2
        fixtures = generate_balanced_fixtures_fixed(shuffled, matches_per_team)
        if not fixtures: # Emergency fallback
             fixtures = list(itertools.combinations(shuffled[:4], 2)) 
        return fixtures
    
    elif phase == "Phase 2: The Squeeze":
        fixtures = []
        for i in range(len(shuffled)):
            for j in range(i+1, len(shuffled)):
                fixtures.append((shuffled[i], shuffled[j]))
                fixtures.append((shuffled[j], shuffled[i]))
        random.shuffle(fixtures)
        return fixtures
    
    elif phase == "Phase 3: The Standoff":
        standings = get_cumulative_standings()
        if len(standings) < 3: return []
        
        standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
        
        leader = standings[0]['Team']
        second = standings[1]['Team']
        third = standings[2]['Team']
        
        st.session_state.bye_team = leader
        st.session_state.news.insert(0, f"👑 {leader} gets automatic BYE to Grand Final!")
        
        return [(second, third), (third, second)]
    
    elif phase == "Phase 4: The Grand Final":
        return [(shuffled[0], shuffled[1])]
    
    return []

def get_cumulative_standings():
    """Get current cumulative standings for all active teams - FIXED VERSION"""
    standings = []
    
    # DIRECTLY use cumulative stats - this is the key fix
    for team in st.session_state.active_teams:
        if team in st.session_state.cumulative_stats:
            stats = st.session_state.cumulative_stats[team]
            standings.append({
                'Team': team,
                'P': stats.get('P', 0),
                'W': stats.get('W', 0),
                'D': stats.get('D', 0),
                'L': stats.get('L', 0),
                'GF': stats.get('GF', 0),
                'GA': stats.get('GA', 0),
                'GD': stats.get('GD', 0),
                'Pts': stats.get('Pts', 0)
            })
        else:
            # Initialize with zeros if no stats yet
            standings.append({
                'Team': team,
                'P': 0, 'W': 0, 'D': 0, 'L': 0,
                'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0
            })
    
    return standings

def process_player_string_update(raw_str, team, stat_type):
    """Helper function to update player stats from a string"""
    if not raw_str: return
    
    # First, split by commas
    raw_parts = raw_str.split(',')
    
    for raw_player in raw_parts:
        raw_player = raw_player.strip()
        if not raw_player: continue
        
        count = 1
        name = raw_player
        
        # Handle different formats
        # Format 1: "Player (2)" - parentheses
        m_br = re.search(r'^(.*?)\s*\((\d+)\)$', raw_player)
        if m_br:
            name = m_br.group(1).strip()
            count = int(m_br.group(2))
        # Format 2: "Player x2" - x notation
        m_x = re.search(r'^(.*?)\s*[xX](\d+)$', raw_player)
        if m_x:
            name = m_x.group(1).strip()
            count = int(m_x.group(2))
        
        # Clean up name
        name = name.strip().title()
        if not name: continue
        
        # Create unique player ID
        player_id = f"{name}|{team}"
        
        # Initialize if not exists
        if player_id not in st.session_state.cumulative_player_stats:
            st.session_state.cumulative_player_stats[player_id] = {
                'Name': name,
                'Team': team,
                'G': 0, 'A': 0, 'R': 0
            }
        
        # Add stats
        st.session_state.cumulative_player_stats[player_id][stat_type] += count

def handle_battle_royale_elimination():
    """Execute Battle Royale protocol - UPDATED VERSION"""
    # Removed global try block to stop swallowing RerunException
    standings = get_cumulative_standings()
    
    # Sort by Points → GD → GF
    standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
    
    remaining = len(standings)
    
    # DETERMINE CURRENT PHASE
    if remaining >= 5:
        phase = "Phase 1: The Purge"
        elim_count = 2
    elif remaining == 4:
        phase = "Phase 2: The Squeeze"
        elim_count = 1
    elif remaining == 3:
        phase = "Phase 3: The Standoff"
        elim_count = 0
    elif remaining == 2:
        phase = "Phase 4: The Grand Final"
        elim_count = 0
    else:
        # Only 1 team left - CHAMPION!
        champion = standings[0]['Team']
        st.session_state.champion = champion
        st.session_state.news.insert(0, f"🏆 {champion} is the BATTLE ROYALE CHAMPION!")
        st.session_state.battle_phase = "CHAMPION CROWNED"
        
        # Add to past champions
        add_past_champion(champion, datetime.now().year, "Survival Mode (Battle Royale)")
        
        save_data_internal()
        safe_rerun()
        return
    
    # Update phase if changed
    if phase != st.session_state.battle_phase:
        st.session_state.battle_phase = phase
        st.session_state.news.insert(0, f"🔁 PHASE CHANGE: {phase}")
    
    # Handle eliminations based on phase
    eliminated_this_round = []
    
    if phase == "Phase 1: The Purge":
        bottom_teams = standings[-2:]
        for team_data in bottom_teams:
            team = team_data['Team']
            if team in st.session_state.active_teams:
                st.session_state.active_teams.remove(team)
                eliminated_this_round.append(team)
                st.session_state.eliminated_teams.append({
                    'team': team,
                    'round': st.session_state.round_number,
                    'position': remaining - standings.index(team_data),
                    'phase': phase
                })
        
        if eliminated_this_round:
            st.session_state.news.insert(0, f"💀 PURGED: {', '.join(eliminated_this_round)} eliminated!")
    
    elif phase == "Phase 2: The Squeeze":
        bottom_team = standings[-1]['Team']
        if bottom_team in st.session_state.active_teams:
            st.session_state.active_teams.remove(bottom_team)
            eliminated_this_round.append(bottom_team)
            st.session_state.eliminated_teams.append({
                'team': bottom_team,
                'round': st.session_state.round_number,
                'position': 4,
                'phase': phase
            })
        
        if eliminated_this_round:
            st.session_state.news.insert(0, f"💀 SQUEEZED OUT: {bottom_team} eliminated!")
    
    elif phase == "Phase 3: The Standoff":
        if st.session_state.sudden_death_round >= 2:
            leader = standings[0]['Team']
            second = standings[1]['Team']
            third = standings[2]['Team']
            
            match1_id = f"{second}v{third}_0"
            match2_id = f"{third}v{second}_1"
            
            res1 = st.session_state.results.get(match1_id, [0, 0])
            res2 = st.session_state.results.get(match2_id, [0, 0])
            
            second_goals = res1[0] + res2[1]
            third_goals = res1[1] + res2[0]
            
            if second_goals > third_goals:
                loser = third
                winner = second
            elif third_goals > second_goals:
                loser = second
                winner = third
            else:
                if len(res1) > 2 and len(res2) > 2:
                    second_pens = res1[2] + res2[3]
                    third_pens = res1[3] + res2[2]
                    loser = third if second_pens > third_pens else second
                    winner = second if second_pens > third_pens else third
                else:
                    loser = third if standings[1]['Pts'] > standings[2]['Pts'] else second
            
            if loser in st.session_state.active_teams:
                st.session_state.active_teams.remove(loser)
                eliminated_this_round.append(loser)
                st.session_state.eliminated_teams.append({
                    'team': loser,
                    'round': st.session_state.round_number,
                    'position': 3,
                    'phase': phase,
                    'reason': 'Lost Sudden Death Semi-Final'
                })
                st.session_state.news.insert(0, f"💀 SUDDEN DEATH: {loser} eliminated! {winner} advances to Final!")
            
            st.session_state.sudden_death_round = 0
            st.session_state.bye_team = None
    
    # Generate next round fixtures
    next_fixtures = generate_fixtures_for_phase(st.session_state.active_teams, phase)
    st.session_state.fixtures = next_fixtures
    
    # Update round info
    st.session_state.round_number += 1
    
    if phase == "Phase 3: The Standoff" and not eliminated_this_round:
        st.session_state.sudden_death_round += 1
        if st.session_state.sudden_death_round == 1:
            st.session_state.current_round = f"SUDDEN DEATH • Leg 1 • {phase}"
        else:
            st.session_state.current_round = f"SUDDEN DEATH • Leg 2 • {phase}"
    else:
        st.session_state.current_round = f"Round {st.session_state.round_number} • {phase}"
    
    # Reset match data for next round (but keep admin approved results)
    st.session_state.results = {}
    st.session_state.match_meta = {}
    st.session_state.fixed_results = {}
    st.session_state.captain_fixed_matches = {team: [] for team in st.session_state.active_teams}
    
    # Log history
    st.session_state.survival_history.append({
        'round': st.session_state.round_number - 1,
        'phase': phase,
        'remaining': len(st.session_state.active_teams),
        'eliminated': eliminated_this_round
    })
    
    save_data_internal()
    safe_rerun()

# --- 🏆 TOURNAMENT FORMAT COMPLETION ---

def generate_knockout_bracket(teams, round_name="Round of 16"):
    """Generate knockout bracket for given teams"""
    shuffled = teams.copy()
    random.shuffle(shuffled)
    
    bracket = {}
    matches = []
    
    # Create matches for current round
    for i in range(0, len(shuffled), 2):
        if i + 1 < len(shuffled):
            match_id = f"{round_name}_match_{len(matches)}"
            bracket[match_id] = {
                'home': shuffled[i],
                'away': shuffled[i + 1],
                'round': round_name,
                'winner': None,
                'result': None
            }
            matches.append((shuffled[i], shuffled[i + 1]))
    
    return bracket, matches

def advance_world_cup_knockout():
    """Advance World Cup to knockout stage"""
    if st.session_state.world_cup_stage != "Group Stage":
        return
    
    # Calculate group winners and runners-up
    group_winners = []
    group_runners = []
    
    for group_name, teams in st.session_state.groups.items():
        group_standings = []
        
        for team in teams:
            # Calculate team stats from results
            stats = {'Team': team, 'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0}
            
            for mid, res in st.session_state.results.items():
                try:
                    if "_" in mid:
                        base = mid.split('_')[0]
                    else:
                        base = mid
                    
                    if "v" not in base:
                        continue
                    
                    h, a = base.split('v')
                except:
                    continue
                
                if h == team or a == team:
                    is_home = h == team
                    s_h, s_a = res[0], res[1]
                    
                    stats['P'] += 1
                    stats['GF'] += s_h if is_home else s_a
                    stats['GA'] += s_a if is_home else s_h
                    stats['GD'] += (s_h - s_a) if is_home else (s_a - s_h)
                    
                    if is_home:
                        if s_h > s_a:
                            stats['W'] += 1
                            stats['Pts'] += 3
                        elif s_a > s_h:
                            stats['L'] += 1
                        else:
                            stats['D'] += 1
                            stats['Pts'] += 1
                    else:
                        if s_a > s_h:
                            stats['W'] += 1
                            stats['Pts'] += 3
                        elif s_h > s_a:
                            stats['L'] += 1
                        else:
                            stats['D'] += 1
                            stats['Pts'] += 1
            
            group_standings.append(stats)
        
        # Sort group standings
        group_standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
        
        if len(group_standings) >= 2:
            group_winners.append(group_standings[0]['Team'])
            group_runners.append(group_standings[1]['Team'])
    
    # Create Round of 16 bracket (World Cup format)
    knockout_teams = group_winners + group_runners
    random.shuffle(knockout_teams)
    
    # Generate bracket
    bracket, matches = generate_knockout_bracket(knockout_teams, "Round of 16")
    
    st.session_state.knockout_bracket = bracket
    st.session_state.fixtures = matches
    st.session_state.world_cup_stage = "Round of 16"
    st.session_state.current_round = "Round of 16"
    st.session_state.news.insert(0, "🏆 World Cup advances to Knockout Stage!")
    
    save_data_internal()

def advance_knockout_tournament():
    """Advance any knockout tournament to next round"""
    # Check if all current matches have results
    current_matches_complete = True
    for i, match in enumerate(st.session_state.fixtures):
        if len(match) < 2:
            continue
        h, a = match[0], match[1]
        mid = f"{h}v{a}_{i}"
        if mid not in st.session_state.results:
            current_matches_complete = False
            break
    
    if not current_matches_complete:
        st.warning("Cannot advance: Some matches in current round don't have results!")
        return
    
    # Determine winners
    winners = []
    for i, match in enumerate(st.session_state.fixtures):
        if len(match) < 2:
            continue
        h, a = match[0], match[1]
        mid = f"{h}v{a}_{i}"
        res = st.session_state.results[mid]
        
        if len(res) >= 2:
            if res[0] > res[1]:
                winners.append(h)
            elif res[1] > res[0]:
                winners.append(a)
            else:
                # Draw - check for penalties
                if len(res) > 2:
                    if res[2] > res[3]:
                        winners.append(h)
                    else:
                        winners.append(a)
                else:
                    # No penalties recorded - random winner
                    winners.append(random.choice([h, a]))
    
    # Check if we have a champion
    if len(winners) == 1:
        champion = winners[0]
        st.session_state.champion = champion
        st.session_state.news.insert(0, f"🏆 {champion} is the CHAMPION!")
        st.session_state.current_round = "TOURNAMENT COMPLETE"
        
        # Add to past champions
        add_past_champion(champion, datetime.now().year, st.session_state.format)
        
        save_data_internal()
        safe_rerun()
        return
    
    # Determine next round name
    round_names = {
        8: "Quarter Finals",
        4: "Semi Finals",
        2: "Final"
    }
    
    next_round = round_names.get(len(winners), f"Round {st.session_state.knockout_round + 1}")
    
    # Generate next round fixtures
    shuffled = winners.copy()
    random.shuffle(shuffled)
    
    next_fixtures = []
    for i in range(0, len(shuffled), 2):
        if i + 1 < len(shuffled):
            next_fixtures.append((shuffled[i], shuffled[i + 1]))
    
    st.session_state.fixtures = next_fixtures
    st.session_state.knockout_round += 1
    st.session_state.current_round = next_round
    st.session_state.results = {}
    st.session_state.match_meta = {}
    st.session_state.fixed_results = {}
    st.session_state.captain_fixed_matches = {team: [] for team in winners}
    
    # For World Cup, update stage
    if "World Cup" in st.session_state.format:
        stage_map = {
            "Round of 16": "Quarter Finals",
            "Quarter Finals": "Semi Finals",
            "Semi Finals": "Final"
        }
        if st.session_state.world_cup_stage in stage_map:
            st.session_state.world_cup_stage = stage_map[st.session_state.world_cup_stage]
    
    st.session_state.news.insert(0, f"⚽ Advancing to {next_round}!")
    save_data_internal()
    safe_rerun()

def update_match_result_safely(mid, h, a, s1, s2, p1=0, p2=0, gs1="", gs2="", ha="", aa="", hr="", ar=""):
    """Safely update match result without duplicate points - FIXED VERSION"""
    # Check if this match was already processed
    was_processed = mid in st.session_state.match_history
    
    if was_processed:
        # Remove old stats before adding new ones
        old_res = st.session_state.match_history[mid]
        old_s1, old_s2 = old_res['score']
        old_p1, old_p2 = old_res.get('pens', (0, 0))
        
        # Store old player strings to remove them
        old_meta = st.session_state.match_meta.get(mid, {})
        old_gs1 = old_meta.get('h_s', '')
        old_gs2 = old_meta.get('a_s', '')
        old_ha = old_meta.get('h_a', '')
        old_aa = old_meta.get('a_a', '')
        old_hr = old_meta.get('h_r', '')
        old_ar = old_meta.get('a_r', '')
        
        # Remove old team stats
        if h in st.session_state.cumulative_stats:
            stats = st.session_state.cumulative_stats[h]
            stats['P'] -= 1
            stats['GF'] -= old_s1
            stats['GA'] -= old_s2
            stats['GD'] -= (old_s1 - old_s2)
            
            if old_s1 > old_s2:
                stats['W'] -= 1
                stats['Pts'] -= 3
            elif old_s2 > old_s1:
                stats['L'] -= 1
            else:
                stats['D'] -= 1
                stats['Pts'] -= 1
        
        if a in st.session_state.cumulative_stats:
            stats = st.session_state.cumulative_stats[a]
            stats['P'] -= 1
            stats['GF'] -= old_s2
            stats['GA'] -= old_s1
            stats['GD'] -= (old_s2 - old_s1)
            
            if old_s2 > old_s1:
                stats['W'] -= 1
                stats['Pts'] -= 3
            elif old_s1 > old_s2:
                stats['L'] -= 1
            else:
                stats['D'] -= 1
                stats['Pts'] -= 1
        
        # Remove old player stats
        def remove_player_stats(raw_str, team, stat_type):
            if not raw_str: return
            raw_parts = raw_str.split(',')
            for raw_player in raw_parts:
                raw_player = raw_player.strip()
                if not raw_player: continue
                
                count = 1
                name = raw_player
                
                m_br = re.search(r'^(.*?)\s*\((\d+)\)$', raw_player)
                if m_br:
                    name = m_br.group(1).strip()
                    count = int(m_br.group(2))
                m_x = re.search(r'^(.*?)\s*[xX](\d+)$', raw_player)
                if m_x:
                    name = m_x.group(1).strip()
                    count = int(m_x.group(2))
                
                name = name.strip().title()
                if not name: continue
                
                player_id = f"{name}|{team}"
                
                if player_id in st.session_state.cumulative_player_stats:
                    st.session_state.cumulative_player_stats[player_id][stat_type] -= count
                    # Remove player if all stats are zero or negative
                    player_stats = st.session_state.cumulative_player_stats[player_id]
                    if player_stats['G'] <= 0 and player_stats['A'] <= 0 and player_stats['R'] <= 0:
                        del st.session_state.cumulative_player_stats[player_id]
        
        remove_player_stats(old_gs1, h, 'G')
        remove_player_stats(old_gs2, a, 'G')
        remove_player_stats(old_ha, h, 'A')
        remove_player_stats(old_aa, a, 'A')
        remove_player_stats(old_hr, h, 'R')
        remove_player_stats(old_ar, a, 'R')
    
    # Initialize cumulative stats if not exists
    if h not in st.session_state.cumulative_stats:
        st.session_state.cumulative_stats[h] = {
            'P': 0, 'W': 0, 'D': 0, 'L': 0, 
            'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0
        }
    if a not in st.session_state.cumulative_stats:
        st.session_state.cumulative_stats[a] = {
            'P': 0, 'W': 0, 'D': 0, 'L': 0, 
            'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0
        }
    
    # Update cumulative team stats
    st.session_state.cumulative_stats[h]['P'] += 1
    st.session_state.cumulative_stats[a]['P'] += 1
    st.session_state.cumulative_stats[h]['GF'] += s1
    st.session_state.cumulative_stats[h]['GA'] += s2
    st.session_state.cumulative_stats[h]['GD'] += (s1 - s2)
    st.session_state.cumulative_stats[a]['GF'] += s2
    st.session_state.cumulative_stats[a]['GA'] += s1
    st.session_state.cumulative_stats[a]['GD'] += (s2 - s1)
    
    if s1 > s2:
        st.session_state.cumulative_stats[h]['W'] += 1
        st.session_state.cumulative_stats[h]['Pts'] += 3
        st.session_state.cumulative_stats[a]['L'] += 1
    elif s2 > s1:
        st.session_state.cumulative_stats[a]['W'] += 1
        st.session_state.cumulative_stats[a]['Pts'] += 3
        st.session_state.cumulative_stats[h]['L'] += 1
    else:
        st.session_state.cumulative_stats[h]['D'] += 1
        st.session_state.cumulative_stats[h]['Pts'] += 1
        st.session_state.cumulative_stats[a]['D'] += 1
        st.session_state.cumulative_stats[a]['Pts'] += 1
    
    # Store match history
    st.session_state.match_history[mid] = {
        'score': (s1, s2),
        'pens': (p1, p2),
        'timestamp': datetime.now().isoformat()
    }
    
    # Store result
    if p1 > 0 or p2 > 0:
        st.session_state.results[mid] = [s1, s2, p1, p2]
    else:
        st.session_state.results[mid] = [s1, s2]
    
    # Store match meta
    st.session_state.match_meta[mid] = {
        'h_s': gs1, 'a_s': gs2, 
        'h_a': ha, 'a_a': aa, 
        'h_r': hr, 'a_r': ar
    }
    
    # Add new player stats
    process_player_string_update(gs1, h, 'G')
    process_player_string_update(gs2, a, 'G')
    process_player_string_update(ha, h, 'A')
    process_player_string_update(aa, a, 'A')
    process_player_string_update(hr, h, 'R')
    process_player_string_update(ar, a, 'R')

def verify_data_consistency():
    """Check if cumulative stats match with recorded results"""
    mismatches = []
    recalculated_stats = {}
    
    # Initialize all active teams
    for team in st.session_state.active_teams:
        recalculated_stats[team] = {
            'P': 0, 'W': 0, 'D': 0, 'L': 0, 
            'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0
        }
    
    # Recalculate from all recorded results
    for mid, res in st.session_state.results.items():
        try:
            if "_" in mid:
                base = mid.split('_')[0]
            else:
                base = mid
            
            if "v" not in base:
                continue
            
            h, a = base.split('v')
        except:
            continue
        
        # Skip if teams are not active (shouldn't happen but just in case)
        if h not in recalculated_stats:
            recalculated_stats[h] = {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0}
        if a not in recalculated_stats:
            recalculated_stats[a] = {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0}
        
        s_h, s_a = res[0], res[1]
        
        # Update recalculated stats
        recalculated_stats[h]['P'] += 1
        recalculated_stats[a]['P'] += 1
        recalculated_stats[h]['GF'] += s_h
        recalculated_stats[h]['GA'] += s_a
        recalculated_stats[h]['GD'] += (s_h - s_a)
        recalculated_stats[a]['GF'] += s_a
        recalculated_stats[a]['GA'] += s_h
        recalculated_stats[a]['GD'] += (s_a - s_h)
        
        if s_h > s_a:
            recalculated_stats[h]['W'] += 1
            recalculated_stats[h]['Pts'] += 3
            recalculated_stats[a]['L'] += 1
        elif s_a > s_h:
            recalculated_stats[a]['W'] += 1
            recalculated_stats[a]['Pts'] += 3
            recalculated_stats[h]['L'] += 1
        else:
            recalculated_stats[h]['D'] += 1
            recalculated_stats[h]['Pts'] += 1
            recalculated_stats[a]['D'] += 1
            recalculated_stats[a]['Pts'] += 1
    
    # Compare with stored cumulative stats
    for team in st.session_state.active_teams:
        if team in st.session_state.cumulative_stats and team in recalculated_stats:
            stored = st.session_state.cumulative_stats[team]
            calculated = recalculated_stats[team]
            
            for key in ['P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']:
                stored_val = stored.get(key, 0)
                calculated_val = calculated.get(key, 0)
                if stored_val != calculated_val:
                    mismatches.append({
                        'team': team,
                        'key': key,
                        'stored': stored_val,
                        'calculated': calculated_val
                    })
    
    return mismatches, recalculated_stats

# Initialize session state
if 'data_loaded' not in st.session_state:
    load_data()
    st.session_state.data_loaded = True

# Initialize session-specific admin access
if 'admin_pin_verified' not in st.session_state:
    st.session_state.admin_pin_verified = False
if 'admin_unlock' not in st.session_state:
    st.session_state.admin_unlock = False

init_defaults()

# --- 🏆 HEADER ---
st.markdown('<div class="big-title">DLS ULTRA</div>', unsafe_allow_html=True)

# Special Battle Royale header
if "Survival" in st.session_state.format:
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0; padding: 15px; background: linear-gradient(90deg, #000 0%, #5B0E14 50%, #000 100%); border-radius: 10px; border: 1px solid #F1E194;">
        <h2 style="color: #F1E194; font-family: 'Teko'; margin: 0;">💀 BATTLE ROYALE PROTOCOL</h2>
        <p style="color: #F1E194; font-family: 'Rajdhani'; margin: 5px 0 0 0;">"Survive the Cut. Trust No One."</p>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.champion:
    st.markdown(f'<div style="text-align: center; color:#F1E194; font-size: 2rem; font-family: Teko, sans-serif;">👑 CHAMPION: {st.session_state.champion} 👑</div>', unsafe_allow_html=True)
else:
    subtitle = f"{st.session_state.current_round}"
    if "Survival" in st.session_state.format:
        phase_badge = ""
        if "Phase 1" in st.session_state.battle_phase:
            phase_badge = '<span class="phase-badge phase-1">THE PURGE (2 matches each)</span>'
        elif "Phase 2" in st.session_state.battle_phase:
            phase_badge = '<span class="phase-badge phase-2">THE SQUEEZE (2 matches each)</span>'
        elif "Phase 3" in st.session_state.battle_phase:
            phase_badge = '<span class="phase-badge phase-3">THE STANDOFF</span>'
        elif "Phase 4" in st.session_state.battle_phase:
            phase_badge = '<span class="phase-badge phase-4">GRAND FINAL</span>'
        
        subtitle = f"Round {st.session_state.round_number} • {st.session_state.battle_phase} {phase_badge}"
    
    st.markdown(f'<div style="text-align: center; color: #F1E194; font-family: Rajdhani, sans-serif; margin-bottom: 2rem;">{subtitle}</div>', unsafe_allow_html=True)

# --- 🔒 SIDEBAR - CAPTAIN'S PORTAL & DATA MANAGEMENT ---
with st.sidebar:
    # User Mode Selector
    st.markdown("### 👤 USER MODE")
    user_mode = st.radio("Select Mode", ["Admin", "Captain"], 
                        key="user_mode_selector",
                        index=0 if st.session_state.user_mode == "Admin" else 1)
    
    if user_mode != st.session_state.user_mode:
        st.session_state.user_mode = user_mode
        if user_mode == "Admin":
            st.session_state.logged_in_captain = None
            st.session_state.captain_pin_verified = False
        save_data_internal()
        safe_rerun()
    
    st.markdown("---")
    
    if st.session_state.user_mode == "Admin":
        # ADMIN MODE
        st.markdown("### 🔐 ADMIN ACCESS")
        
        # Session-specific PIN verification
        if not st.session_state.admin_pin_verified:
            pin = st.text_input("ENTER ADMIN PIN", type="password", key="pin_input")
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔓 ", key="pin_unlock_btn", use_container_width=True):
                    if pin == "0209":
                        st.session_state.admin_pin_verified = True
                        st.session_state.admin_unlock = True
                        st.success("Admin access granted!")
                        safe_rerun()
                    elif pin:
                        st.error("Incorrect PIN!")
            
            if not pin:
                st.info("Enter PIN for ADMIN access")
        else:
            # ADMIN ACCESS GRANTED - Show all admin controls
            st.success("✅ ADMIN ACCESS GRANTED")
            
            # Pending reports notification
            pending_count = len(st.session_state.pending_reports)
            if pending_count > 0:
                st.warning(f"🔔 {pending_count} pending report(s) awaiting approval!")
            
            # --- TEAM EDITOR SECTION ---
            st.markdown("### 🏆 TEAM EDITOR")
            
            # Add new team
            with st.expander("➕ ADD CLUB", expanded=False):
                new_team = st.text_input("Team Name", key="add_team_input")
                if st.button("➕ ADD TEAM", key="add_team_btn"):
                    if new_team and new_team not in st.session_state.teams:
                        credentials_msg, pin, password = add_team_with_captain(new_team)
                        if credentials_msg and pin:
                            save_data_internal()
                            with st.expander("✅ CREDENTIALS - SAVE THESE!", expanded=True):
                                st.markdown(credentials_msg)
                            st.success(f"Team '{new_team}' added!")
                            safe_rerun()
                        elif credentials_msg:
                            st.error(credentials_msg)
                    elif new_team in st.session_state.teams:
                        st.error("Team already exists!")
            
            # Delete team
            with st.expander("🗑️ DELETE CLUB", expanded=False):
                if st.session_state.teams:
                    team_to_delete = st.selectbox("Select team to delete", 
                                                 ["Select..."] + st.session_state.teams,
                                                 key="delete_team_select")
                    
                    if team_to_delete != "Select...":
                        if st.button("🗑️ DELETE TEAM", key="delete_team_btn", type="secondary"):
                            if delete_team(team_to_delete):
                                save_data_internal()
                                st.success(f"Team '{team_to_delete}' deleted!")
                                safe_rerun()
                else:
                    st.info("No teams to delete")
            
            # Reset tournament
            with st.expander("🔄 RESET TOURNAMENT", expanded=False):
                st.warning("This will reset all stats but keep teams")
                if st.button("🔄 RESET ALL STATS", key="reset_stats_btn", type="secondary"):
                    # Reset all stats but keep teams
                    st.session_state.results = {}
                    st.session_state.match_meta = {}
                    st.session_state.match_history = {}
                    st.session_state.cumulative_stats = {}
                    st.session_state.cumulative_player_stats = {}
                    st.session_state.news = []
                    st.session_state.eliminated_teams = []
                    st.session_state.survival_history = []
                    st.session_state.round_number = 1
                    st.session_state.battle_phase = "Phase 1: The Purge"
                    st.session_state.bye_team = None
                    st.session_state.sudden_death_round = 0
                    st.session_state.champion = None
                    st.session_state.fixed_results = {}
                    st.session_state.captain_fixed_matches = {team: [] for team in st.session_state.teams}
                    st.session_state.admin_approved_results = {}
                    
                    # Reinitialize stats for all teams
                    for team in st.session_state.teams:
                        st.session_state.cumulative_stats[team] = {
                            'P': 0, 'W': 0, 'D': 0, 'L': 0, 
                            'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0
                        }
                    
                    # Regenerate fixtures
                    if st.session_state.started:
                        if "Survival" in st.session_state.format:
                            matches = generate_fixtures_for_phase(st.session_state.teams, "Phase 1: The Purge")
                            st.session_state.fixtures = matches
                        elif "League" in st.session_state.format:
                            matches = list(itertools.permutations(st.session_state.teams, 2))
                            random.shuffle(matches)
                            st.session_state.fixtures = matches
                        elif "World Cup" in st.session_state.format:
                            st.session_state.world_cup_stage = "Group Stage"
                            # Regenerate groups and fixtures
                            shuffled = st.session_state.teams.copy()
                            random.shuffle(shuffled)
                            groups = {}
                            group_names = "ABCDEFGHIJKLMNOP"
                            group_size = 4
                            
                            for i in range(0, len(shuffled), group_size):
                                group_idx = i // group_size
                                if group_idx < len(group_names):
                                    groups[group_names[group_idx]] = shuffled[i:i+group_size]
                            
                            st.session_state.groups = groups
                            matches = []
                            for g, teams in groups.items():
                                matches.extend(list(itertools.combinations(teams, 2)))
                            st.session_state.fixtures = matches
                        elif "Knockout" in st.session_state.format:
                            shuffled = st.session_state.teams.copy()
                            random.shuffle(shuffled)
                            if len(shuffled) % 2 != 0:
                                shuffled.append("BYE")
                            matches = []
                            for i in range(0, len(shuffled), 2):
                                if i + 1 < len(shuffled) and shuffled[i] != "BYE" and shuffled[i+1] != "BYE":
                                    matches.append((shuffled[i], shuffled[i + 1]))
                            st.session_state.fixtures = matches
                            st.session_state.knockout_round = 1
                    
                    save_data_internal()
                    st.success("All stats reset!")
                    safe_rerun()
            
            st.markdown("---")
            
            # --- CAPTAIN CONTROLS SECTION ---
            st.markdown("### 🧢 CAPTAIN CONTROLS")
            
            # View all captain PINs
            with st.expander("🔑 VIEW ALL CAPTAIN PINS", expanded=False):
                if st.session_state.teams:
                    pins_df = view_all_captain_pins()
                    if isinstance(pins_df, pd.DataFrame):
                        st.dataframe(pins_df, hide_index=True, use_container_width=True)
                        
                        # Export PINs as CSV
                        csv = pins_df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href = f'<a href="data:file/csv;base64,{b64}" download="captain_pins.csv" class="stButton">📥 Download PINs as CSV</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    else:
                        st.info(pins_df)
                else:
                    st.info("No teams registered yet.")
            
            # Reset individual captain PIN
            with st.expander("🔄 RESET CAPTAIN PIN", expanded=False):
                if st.session_state.teams:
                    team_to_reset = st.selectbox("Select team", 
                                                ["Select..."] + st.session_state.teams,
                                                key="reset_pin_select")
                    
                    if team_to_reset != "Select...":
                        current_pin = st.session_state.captain_pins.get(team_to_reset, "Not set")
                        st.info(f"Current PIN for {team_to_reset}: `{current_pin}`")
                        
                        if st.button("🔄 GENERATE NEW PIN", key="reset_pin_btn"):
                            success, new_pin = reset_captain_pin(team_to_reset)
                            if success:
                                save_data_internal()
                                st.success(f"New PIN for {team_to_reset}: `{new_pin}`")
                                safe_rerun()
                else:
                    st.info("No teams to reset")
            
            # Regenerate all PINs
            with st.expander("🔄 REGENERATE ALL PINS", expanded=False):
                st.warning("This will reset ALL captain PINs!")
                st.info("All captains will need to use their new PINs to log in.")
                
                if st.button("🔄 REGENERATE ALL CAPTAIN PINS", key="regen_all_pins_btn", type="secondary"):
                    if regenerate_all_pins():
                        save_data_internal()
                        st.success("All captain PINs regenerated!")
                        safe_rerun()
            
            # View team credentials
            with st.expander("👁️ VIEW TEAM CREDENTIALS", expanded=False):
                if st.session_state.teams:
                    selected_team = st.selectbox("Select team to view", 
                                                ["Select..."] + st.session_state.teams,
                                                key="view_creds_select")
                    
                    if selected_team != "Select...":
                        creds = view_team_credentials(selected_team)
                        if creds:
                            st.markdown(f"""
                            <div class="credentials-box">
                                <h4>🔐 {creds['team']} Credentials</h4>
                                <p><strong>Team:</strong> {creds['team']}</p>
                                <p><strong>Badge:</strong> {creds['badge']}</p>
                                <p><strong>Captain PIN:</strong> <span class="pin-display">{creds['pin']}</span></p>
                                <p><strong>Password Hash:</strong> <code>{creds['hashed_password'][:20]}...</code></p>
                                <p><small><em>Note: Password is hashed for security</em></small></p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No teams to view")
            
            st.markdown("---")
            
            # --- MANUAL PLAYER STATS EDITOR ---
            st.markdown("### ⚽ PLAYER STATS EDITOR")
            
            with st.expander("📝 MANUAL STATS CONTROL", expanded=False):
                if st.session_state.teams:
                    st.markdown("#### Add Player Stat")
                    col1, col2 = st.columns(2)
                    with col1:
                        player_name_input = st.text_input("Player Name", key="manual_player_name")
                        team_select = st.selectbox("Team", st.session_state.teams, key="manual_team_select")
                    with col2:
                        stat_type = st.selectbox("Stat Type", ["G", "A", "R"], key="manual_stat_type")
                        stat_count = st.number_input("Count", min_value=1, max_value=10, value=1, key="manual_stat_count")
                    
                    if st.button("➕ ADD STAT", key="manual_add_stat_btn"):
                        if player_name_input:
                            if add_player_stat(player_name_input, team_select, stat_type, stat_count):
                                save_data_internal()
                                st.success(f"Added {stat_count} {stat_type} for {player_name_input}")
                                safe_rerun()
                        else:
                            st.error("Please enter a player name")
                    
                    st.markdown("#### Edit/Delete Player Stats")
                    if st.session_state.cumulative_player_stats:
                        # Create dataframe for editing
                        player_data = []
                        for player_id, stats in st.session_state.cumulative_player_stats.items():
                            player_data.append({
                                'ID': player_id,
                                'Name': stats['Name'],
                                'Team': stats['Team'],
                                'Goals': stats['G'],
                                'Assists': stats['A'],
                                'Reds': stats['R']
                            })
                        
                        df_players = pd.DataFrame(player_data)
                        st.dataframe(df_players[['Name', 'Team', 'Goals', 'Assists', 'Reds']], 
                                   hide_index=True, use_container_width=True)
                        
                        # Edit player
                        player_to_edit = st.selectbox("Select player to edit", 
                                                     ["Select..."] + [f"{p['Name']} ({p['Team']})" for p in player_data],
                                                     key="edit_player_select")
                        
                        if player_to_edit != "Select...":
                            selected_player = next(p for p in player_data if f"{p['Name']} ({p['Team']})" == player_to_edit)
                            player_id = selected_player['ID']
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                new_goals = st.number_input("Goals", min_value=0, value=selected_player['Goals'], key="edit_goals")
                            with col2:
                                new_assists = st.number_input("Assists", min_value=0, value=selected_player['Assists'], key="edit_assists")
                            with col3:
                                new_reds = st.number_input("Reds", min_value=0, value=selected_player['Reds'], key="edit_reds")
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("💾 UPDATE", key="update_player_btn"):
                                    edit_player_stat(player_id, 'G', new_goals)
                                    edit_player_stat(player_id, 'A', new_assists)
                                    edit_player_stat(player_id, 'R', new_reds)
                                    save_data_internal()
                                    st.success("Player stats updated!")
                                    safe_rerun()
                            
                            with col_btn2:
                                if st.button("🗑️ DELETE", key="delete_player_btn", type="secondary"):
                                    if delete_player_stat(player_id):
                                        save_data_internal()
                                        st.success("Player deleted!")
                                        safe_rerun()
                    else:
                        st.info("No player stats to edit")
                else:
                    st.info("No teams available")
            
            st.markdown("---")
            
            # --- PAST CHAMPIONS MANAGEMENT ---
            st.markdown("### 🏆 PAST CHAMPIONS")
            
            with st.expander("📜 VIEW PAST CHAMPIONS", expanded=False):
                if st.session_state.past_champions:
                    for idx, champ in enumerate(st.session_state.past_champions[:5]):  # Show last 5
                        st.markdown(f"""
                        <div class="champion-card">
                            <div class="champion-year">{champ['year']}</div>
                            <div class="champion-name">{champ['champion']}</div>
                            <div class="champion-format">{champ['format']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No past champions recorded yet.")
            
            with st.expander("➕ ADD PAST CHAMPION", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    champ_name = st.text_input("Champion Team Name", key="add_champion_name")
                with col2:
                    champ_year = st.number_input("Year", min_value=2000, max_value=2100, value=datetime.now().year, key="add_champion_year")
                
                champ_format = st.selectbox("Tournament Format", 
                                          ["Home & Away League", "World Cup", "Classic Knockout", "Survival Mode (Battle Royale)"],
                                          key="add_champion_format")
                
                if st.button("🏆 ADD CHAMPION", key="add_champion_btn"):
                    if champ_name:
                        if add_past_champion(champ_name, champ_year, champ_format):
                            save_data_internal()
                            st.success(f"Added {champ_name} as {champ_year} champion!")
                            safe_rerun()
                    else:
                        st.error("Please enter a champion team name")
            
            with st.expander("🗑️ MANAGE CHAMPIONS", expanded=False):
                if st.session_state.past_champions:
                    for idx, champ in enumerate(st.session_state.past_champions):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"**{champ['year']}:** {champ['champion']} ({champ['format']})")
                        with col2:
                            if st.button("❌", key=f"remove_champ_{idx}"):
                                if remove_past_champion(idx):
                                    save_data_internal()
                                    st.success("Champion removed!")
                                    safe_rerun()
                else:
                    st.info("No champions to manage")
            
            st.markdown("---")
            
            # --- DATA MANAGEMENT SECTION ---
            st.markdown("### 💾 DATA MANAGEMENT")
            
            # Download backup
            with st.expander("📥 DOWNLOAD BACKUP", expanded=False):
                st.markdown(download_backup(), unsafe_allow_html=True)
            
            # Restore backup
            with st.expander("📤 RESTORE BACKUP", expanded=False):
                uploaded_file = st.file_uploader("Choose backup file", type=['json'], key="backup_uploader")
                if uploaded_file is not None:
                    if st.button("🔄 RESTORE FROM BACKUP", key="restore_backup_btn", type="secondary"):
                        success, message = restore_backup(uploaded_file)
                        if success:
                            st.success(message)
                            safe_rerun()
                        else:
                            st.error(message)
            
            # Factory reset
            with st.expander("⚙️ FACTORY RESET", expanded=False):
                st.error("⚠️ **DANGER ZONE** ⚠️")
                st.warning("This will delete ALL data including teams!")
                confirm = st.text_input("Type 'DELETE ALL' to confirm", key="factory_reset_confirm")
                if st.button("💣 FACTORY RESET", key="factory_reset_btn", type="secondary"):
                    if confirm == "DELETE ALL":
                        if factory_reset():
                            st.success("All data reset!")
                            safe_rerun()
                    else:
                        st.error("Please type 'DELETE ALL' to confirm")
            
            st.markdown("---")
            
            # --- TOURNAMENT CONTROLS SECTION ---
            st.markdown("### ⚙️ TOURNAMENT CONTROLS")
            
            # Tournament format changer
            with st.expander("🔄 CHANGE TOURNAMENT FORMAT", expanded=False):
                if not st.session_state.started:
                    st.info("Tournament hasn't started yet")
                else:
                    st.warning("⚠️ Changing format mid-tournament may cause data issues!")
                    new_format = st.selectbox("Select new format", 
                                            ["Home & Away League", "World Cup (Groups + Knockout)", 
                                             "Classic Knockout", "Survival Mode (Battle Royale)"],
                                            key="change_format_select")
                    
                    if st.button("🔄 CHANGE FORMAT", key="change_format_btn", type="secondary"):
                        st.session_state.format = new_format
                        save_data_internal()
                        st.success(f"Tournament format changed to {new_format}")
                        safe_rerun()
            
            # Tournament progress controls
            if st.session_state.started and not st.session_state.champion:
                st.markdown("#### 🎯 ADVANCE TOURNAMENT")
                
                if "World Cup" in st.session_state.format:
                    if st.session_state.world_cup_stage == "Group Stage":
                        if st.button("🏆 ADVANCE TO KNOCKOUT STAGE", key="advance_world_cup_btn", use_container_width=True):
                            advance_world_cup_knockout()
                    else:
                        if st.button("⚽ ADVANCE TO NEXT ROUND", key="advance_knockout_btn", use_container_width=True):
                            advance_knockout_tournament()
                elif "Knockout" in st.session_state.format:
                    if st.button("⚽ ADVANCE TO NEXT ROUND", key="advance_classic_knockout_btn", use_container_width=True):
                        advance_knockout_tournament()
                elif "Survival" in st.session_state.format:
                    if st.button("⏩ EXECUTE ELIMINATION", key="execute_elim_btn", use_container_width=True): 
                        st.toast("Processing Elimination...", icon="💀")
                        handle_battle_royale_elimination()
                
                # Force declare champion
                if st.session_state.active_teams:
                    with st.expander("🏆 FORCE DECLARE CHAMPION", expanded=False):
                        st.error("⚠️ **DANGER ZONE** ⚠️")
                        st.warning("This will immediately end the tournament!")
                        force_champion = st.selectbox("Select champion", 
                                                    ["Select..."] + st.session_state.active_teams,
                                                    key="force_champion_select")
                        
                        if force_champion != "Select...":
                            if st.button("👑 FORCE DECLARE CHAMPION", key="force_champion_btn", type="secondary"):
                                st.session_state.champion = force_champion
                                add_past_champion(force_champion, datetime.now().year, st.session_state.format)
                                st.session_state.news.insert(0, f"🏆 {force_champion} declared champion by admin!")
                                save_data_internal()
                                st.success(f"{force_champion} declared champion!")
                                safe_rerun()
            
            # Debug tools (Admin only)
            st.markdown("### 🐛 DEBUG TOOLS")
            
            if st.button("🔄 Refresh View", key="refresh_view_btn", use_container_width=True):
                safe_rerun()
            
            if st.button("🔍 Check Data Consistency", key="check_consistency_btn", use_container_width=True):
                mismatches, recalculated = verify_data_consistency()
                if mismatches:
                    st.error(f"Found {len(mismatches)} mismatches!")
                    for m in mismatches[:3]:  # Show first 3
                        st.write(f"{m['team']}: {m['key']} - Stored: {m['stored']}, Calculated: {m['calculated']}")
                    
                    if st.button("🔄 Fix All Mismatches", key="fix_mismatches_btn"):
                        for team, stats in recalculated.items():
                            st.session_state.cumulative_stats[team] = stats
                        save_data_internal()
                        st.success("Fixed all mismatches!")
                        safe_rerun()
                else:
                    st.success("All data is consistent! ✅")
            
            if st.button("📊 Show System Info", key="show_system_info_btn", use_container_width=True):
                st.write("**System Status:**")
                st.write(f"- Teams: {len(st.session_state.teams)}")
                st.write(f"- Active Teams: {len(st.session_state.active_teams)}")
                st.write(f"- Pending Reports: {len(st.session_state.pending_reports)}")
                st.write(f"- Captain Logs: {len(st.session_state.captain_logs)}")
                st.write(f"- Past Champions: {len(st.session_state.past_champions)}")
                st.write(f"- Fixed Results (Pending): {len(st.session_state.fixed_results)}")
                st.write(f"- Approved Results: {len(st.session_state.admin_approved_results)}")
                st.write(f"- Player Stats: {len(st.session_state.cumulative_player_stats)}")
                
                with st.expander("View Captain Logs", expanded=False):
                    for log in st.session_state.captain_logs[-10:]:  # Last 10 logs
                        st.write(f"{log['timestamp']}: {log['action']}")
            
            # Match Debugger Tool
            with st.expander("🔍 MATCH DEBUGGER", expanded=False):
                if st.session_state.teams:
                    team_to_check = st.selectbox("Check matches for team:", 
                                                ["Select..."] + st.session_state.teams,
                                                key="debug_team_select")
                    
                    if team_to_check != "Select...":
                        matches = find_matches_for_team(team_to_check)
                        st.write(f"**Matches for {team_to_check}:**")
                        if matches:
                            for match in matches:
                                status = "✅ Approved" if match['status'] == 'approved' else \
                                        "⏳ Pending" if match['status'] == 'pending' else \
                                        "✅ Completed" if match['status'] == 'completed' else \
                                        "❌ Not played"
                                st.write(f"- {match['home']} vs {match['away']} ({status}) - ID: {match['match_id']}")
                        else:
                            st.write("No matches found")
                        
                        # Show all fixtures (increased from 20 to 50)
                        st.write(f"**All fixtures ({len(st.session_state.fixtures)}):**")
                        for i, fix in enumerate(st.session_state.fixtures[:50]):  # First 50
                            if len(fix) >= 2:
                                st.write(f"{i}: {fix[0]} vs {fix[1]}")
            
            if st.button("🔒 LOGOUT", key="logout_btn", use_container_width=True):
                st.session_state.admin_pin_verified = False
                st.session_state.admin_unlock = False
                st.session_state.logged_in_captain = None
                st.session_state.captain_pin_verified = False
                save_data_internal()
                safe_rerun()
    
    else:
        # CAPTAIN MODE
        st.markdown("### 🧢 CAPTAIN LOGIN")
        
        if not st.session_state.captain_pin_verified:
            # Team selection - only show teams that exist in the tournament
            available_teams = st.session_state.teams
            
            if available_teams:
                selected_team = st.selectbox("SELECT YOUR TEAM", ["Select..."] + available_teams, key="captain_team_select")
                
                if selected_team != "Select...":
                    # PIN input
                    pin_input = st.text_input("ENTER CAPTAIN PIN", type="password", key="captain_pin_input")
                    
                    if st.button("LOGIN AS CAPTAIN", key="captain_login_btn"):
                        if selected_team in st.session_state.captain_pins:
                            if pin_input == st.session_state.captain_pins[selected_team]:
                                st.session_state.logged_in_captain = selected_team
                                st.session_state.captain_pin_verified = True
                                log_captain_action("Logged in as captain", selected_team)
                                save_data_internal()
                                st.success(f"Welcome, Captain of {selected_team}!")
                                safe_rerun()
                            else:
                                st.error("Incorrect PIN!")
                        else:
                            st.error("PIN not found for this team!")
            else:
                st.info("No teams available yet. Please register a team first.")
        
        if st.session_state.captain_pin_verified and st.session_state.logged_in_captain:
            st.success(f"Logged in as: {st.session_state.logged_in_captain}")
            
            with st.expander("📋 YOUR CREDENTIALS", expanded=False):
                st.info(f"**Team:** {st.session_state.logged_in_captain}")
                st.markdown(f"""
                <div class="credentials-box">
                    <p><strong>Captain PIN:</strong> <span class="pin-display">{st.session_state.captain_pins[st.session_state.logged_in_captain]}</span></p>
                    <p><small>Keep this PIN safe! You'll need it to log in.</small></p>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("🚪 LOGOUT", key="captain_logout_btn", use_container_width=True):
                log_captain_action("Logged out", st.session_state.logged_in_captain)
                st.session_state.logged_in_captain = None
                st.session_state.captain_pin_verified = False
                st.session_state.user_mode = "Admin"  # Reset to Admin mode on logout
                save_data_internal()
                safe_rerun()

# --- 🎮 MAIN INTERFACE ---
if not st.session_state.started:
    # PRE-SEASON LOBBY
    st.markdown(f"<div class='glass-panel captain-portal' style='text-align:center'><h2>🧢 TOURNAMENT LOBBY</h2><p>Register your team before the season starts</p></div>", unsafe_allow_html=True)
    
    # Tournament Code Display
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"""
        <div class='glass-panel' style='text-align:center'>
            <h3>📋 TOURNAMENT INFO</h3>
            <p><strong>Tournament Code:</strong> <code>{st.session_state.tournament_code}</code></p>
            <p>Share this code with your friends to join!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Show Past Champions (Public View)
    if st.session_state.past_champions:
        st.markdown("### 🏆 PAST CHAMPIONS")
        cols = st.columns(min(4, len(st.session_state.past_champions)))
        for idx, champ in enumerate(st.session_state.past_champions[:4]):  # Show first 4
            with cols[idx % len(cols)]:
                st.markdown(f"""
                <div class="champion-card">
                    <div class="champion-year">{champ['year']}</div>
                    <div class="champion-name">{champ['champion']}</div>
                    <div class="champion-format">{champ['format']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Team Registration Section
    st.markdown("### 🏆 REGISTER YOUR TEAM")
    
    reg_col1, reg_col2 = st.columns(2)
    
    with reg_col1:
        st.markdown("""
        #### 📝 HOW TO JOIN:
        1. **Enter Tournament Code** below
        2. **Choose a Team Name** (unique)
        3. Click **"REGISTER TEAM"**
        4. **SAVE YOUR CREDENTIALS** when they appear!
        """)
    
    with reg_col2:
        # Tournament code verification
        entered_code = st.text_input("ENTER TOURNAMENT CODE", key="tournament_code_input")
        
        if entered_code == st.session_state.tournament_code or st.session_state.admin_unlock:
            # Team registration form
            new_team_name = st.text_input("TEAM NAME", key="new_team_name_input")
            
            if st.button("🚀 REGISTER TEAM", key="register_team_btn", use_container_width=True):
                if new_team_name and new_team_name not in st.session_state.teams:
                    # Add team with captain credentials
                    credentials_msg, pin, password = add_team_with_captain(new_team_name)
                    
                    if credentials_msg and pin:
                        save_data_internal()
                        
                        # Show credentials in an expander
                        with st.expander("✅ REGISTRATION SUCCESSFUL - SAVE THESE!", expanded=True):
                            st.markdown(credentials_msg)
                        
                        st.success(f"Team '{new_team_name}' registered!")
                        safe_rerun()
                    elif credentials_msg:
                        st.error(credentials_msg)
                elif new_team_name in st.session_state.teams:
                    st.error("Team name already taken!")
        elif entered_code and entered_code != st.session_state.tournament_code:
            st.error("Incorrect tournament code!")
    
    # Show registered teams
    if st.session_state.teams:
        st.markdown("### 📊 REGISTERED TEAMS")
        cols = st.columns(4)
        for i, t in enumerate(st.session_state.teams):
            b = st.session_state.team_badges.get(t, "🛡️")
            with cols[i % 4]:
                # For public view, show masked PINs
                pin = st.session_state.captain_pins.get(t, "N/A")
                masked_pin = pin[:2] + "••" if len(pin) > 2 else "••••"
                st.markdown(f"""
                <div class='glass-panel' style='text-align:center'>
                    <h1>{b}</h1>
                    <h3>{t}</h3>
                    <small>PIN: {masked_pin}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Admin-only section for starting tournament
    if st.session_state.admin_unlock:
        st.markdown("---")
        st.markdown("### ⚙️ ADMIN CONTROLS")
        
        fmt = st.radio("SELECT TOURNAMENT FORMAT", 
                      ["Home & Away League", "World Cup (Groups + Knockout)", 
                       "Classic Knockout", "Survival Mode (Battle Royale)"], 
                      horizontal=True, key="format_radio")
        
        if st.button("🚀 START SEASON", key="init_season_btn", use_container_width=True):
            if len(st.session_state.teams) < 2:
                st.error("Need at least 2 teams to start!")
            else:
                st.session_state.format = fmt
                st.session_state.active_teams = st.session_state.teams.copy()
                
                # Initialize fixed matches tracking for all teams
                st.session_state.captain_fixed_matches = {team: [] for team in st.session_state.teams}
                
                if "Survival" in fmt:
                    st.session_state.current_round = "Round 1"
                    st.session_state.eliminated_teams = []
                    st.session_state.round_number = 1
                    st.session_state.survival_history = []
                    st.session_state.battle_phase = "Phase 1: The Purge"
                    st.session_state.bye_team = None
                    st.session_state.cumulative_stats = {}
                    st.session_state.cumulative_player_stats = {}
                    st.session_state.sudden_death_round = 0
                    st.session_state.phase1_match_count = 2
                    st.session_state.fixed_results = {}
                    st.session_state.admin_approved_results = {}
                    
                    # Initialize cumulative stats for all teams
                    for team in st.session_state.teams:
                        st.session_state.cumulative_stats[team] = {
                            'P': 0, 'W': 0, 'D': 0, 'L': 0, 
                            'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0
                        }
                    
                    matches = generate_fixtures_for_phase(st.session_state.teams, "Phase 1: The Purge")
                    st.session_state.fixtures = matches
                    st.session_state.current_round = f"Round 1 • {st.session_state.battle_phase}"
                    
                    st.success(f"💀 BATTLE ROYALE INITIALIZED! 2 matches per team.")
                
                elif "League" in fmt: 
                    matches = list(itertools.permutations(st.session_state.teams, 2))
                    random.shuffle(matches)
                    st.session_state.fixtures = matches
                    st.session_state.current_round = "League Phase"
                    st.success("🏆 League initialized! Home & Away format.")
                
                elif "World Cup" in fmt:
                    shuffled = st.session_state.teams.copy()
                    random.shuffle(shuffled)
                    groups = {}
                    group_names = "ABCDEFGHIJKLMNOP"
                    
                    # Create groups of 4 (or as close as possible)
                    group_size = 4
                    num_groups = max(1, (len(shuffled) + group_size - 1) // group_size)
                    
                    for i in range(num_groups):
                        group_teams = shuffled[i*group_size:(i+1)*group_size]
                        groups[group_names[i]] = group_teams
                    
                    st.session_state.groups = groups
                    matches = []
                    
                    # Generate group stage matches
                    for g, teams in groups.items():
                        matches.extend(list(itertools.combinations(teams, 2)))
                    
                    st.session_state.fixtures = matches
                    st.session_state.world_cup_stage = "Group Stage"
                    st.session_state.current_round = "Group Stage"
                    st.success(f"🌍 World Cup initialized! {len(groups)} groups created.")
                
                elif "Knockout" in fmt:
                    shuffled = st.session_state.teams.copy()
                    random.shuffle(shuffled)
                    
                    # Ensure even number of teams
                    if len(shuffled) % 2 != 0:
                        shuffled.append("BYE")
                    
                    matches = []
                    for i in range(0, len(shuffled), 2):
                        if i + 1 < len(shuffled) and shuffled[i] != "BYE" and shuffled[i+1] != "BYE":
                            matches.append((shuffled[i], shuffled[i + 1]))
                    
                    st.session_state.fixtures = matches
                    st.session_state.knockout_round = 1
                    st.session_state.current_round = "Round 1"
                    st.success("🎯 Knockout tournament initialized! Single elimination.")
                
                st.session_state.started = True
                save_data_internal()
                st.balloons()
                safe_rerun()
    
    # If captain is logged in but season hasn't started
    if st.session_state.user_mode == "Captain" and st.session_state.captain_pin_verified:
        st.markdown("---")
        st.info("⏳ **The tournament hasn't started yet.** The admin will start the season when all teams are ready.")
        st.warning("📋 **As a captain, you cannot start the season.** Only admins can start tournaments.")

else:
    # SEASON IN PROGRESS
    
    # Battle News Section (for Survival mode)
    if "Survival" in st.session_state.format:
        st.markdown("### 📰 BATTLE NEWS")
        
        # Current status metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Teams Alive", len(st.session_state.active_teams))
        with col2:
            st.metric("Round", st.session_state.round_number)
        with col3:
            st.metric("Eliminated", len(st.session_state.eliminated_teams))
        with col4:
            st.metric("Phase", st.session_state.battle_phase.split(":")[0])
        
        # Survival progress bar
        total_teams = len(st.session_state.teams)
        remaining_teams = len(st.session_state.active_teams)
        if total_teams > 0:
            survival_percent = (remaining_teams / total_teams) * 100
            
            st.markdown(f"**SURVIVAL PROGRESS:** {remaining_teams}/{total_teams} teams remaining ({survival_percent:.1f}%)")
            progress_html = f"""
            <div class="progress-container">
                <div class="progress-bar" style="width: {survival_percent}%">
                    {remaining_teams}/{total_teams}
                </div>
            </div>
            """
            st.markdown(progress_html, unsafe_allow_html=True)
        
        # News feed
        if st.session_state.news:
            st.markdown("#### 📋 RECENT EVENTS")
            news_container = st.container()
            with news_container:
                for i, news_item in enumerate(st.session_state.news[:10]):  # Show last 10 news items
                    st.markdown(f"""
                    <div class="news-item">
                        {news_item}
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
    
    # Pending reports approval section (Admin only) - WITH EDIT CAPABILITY
    if st.session_state.admin_unlock and st.session_state.pending_reports:
        st.markdown("### ⏳ PENDING REPORTS")
        
        for report in st.session_state.pending_reports:
            with st.container():
                st.markdown(f"""
                <div class='glass-panel pending-report'>
                    <h4>📋 Match Report Pending Approval</h4>
                    <p><strong>{report['home_team']} {report['home_score']}-{report['away_score']} {report['away_team']}</strong></p>
                    <p><small>Submitted by: {report['submitted_by']} at {report['submitted_at'][:16].replace('T', ' ')}</small></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Toggle edit mode
                edit_key = f"edit_mode_{report['report_id']}"
                if edit_key not in st.session_state:
                    st.session_state[edit_key] = False
                
                col1, col2, col3, col4 = st.columns([2,1,1,1])
                
                with col1:
                    with st.expander("📊 View/Edit Details", expanded=st.session_state.get(edit_key, False)):
                        if not st.session_state.get(edit_key, False):
                            # View mode
                            st.write(f"**Home Scorers:** {report['home_scorers'] or 'None'}")
                            st.write(f"**Away Scorers:** {report['away_scorers'] or 'None'}")
                            st.write(f"**Home Assists:** {report['home_assists'] or 'None'}")
                            st.write(f"**Away Assists:** {report['away_assists'] or 'None'}")
                            if report['home_pens'] > 0 or report['away_pens'] > 0:
                                st.write(f"**Penalties:** {report['home_pens']}-{report['away_pens']}")
                            
                            if st.button("✏️ Edit Report", key=f"enable_edit_{report['report_id']}"):
                                st.session_state[edit_key] = True
                                safe_rerun()
                        else:
                            # Edit mode
                            st.markdown("<div class='edit-mode' style='padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
                            
                            ec1, ec2 = st.columns(2)
                            with ec1:
                                edit_h_score = st.number_input(f"{report['home_team']} Score", 0, 20, value=report['home_score'], key=f"edit_hs_{report['report_id']}")
                            with ec2:
                                edit_a_score = st.number_input(f"{report['away_team']} Score", 0, 20, value=report['away_score'], key=f"edit_as_{report['report_id']}")
                            
                            # Penalties
                            if edit_h_score == edit_a_score and "League" not in st.session_state.format:
                                st.caption("Penalties")
                                ecp1, ecp2 = st.columns(2)
                                with ecp1:
                                    edit_h_pens = st.number_input(f"{report['home_team']} Pens", 0, 20, value=report.get('home_pens', 0), key=f"edit_hp_{report['report_id']}")
                                with ecp2:
                                    edit_a_pens = st.number_input(f"{report['away_team']} Pens", 0, 20, value=report.get('away_pens', 0), key=f"edit_ap_{report['report_id']}")
                            else:
                                edit_h_pens = 0
                                edit_a_pens = 0
                            
                            # Player stats
                            st.caption("Player Statistics")
                            esc1, esc2 = st.columns(2)
                            with esc1:
                                edit_h_scorers = st.text_input("Home Scorers", value=report.get('home_scorers', ''), key=f"edit_hsc_{report['report_id']}")
                                edit_h_assists = st.text_input("Home Assists", value=report.get('home_assists', ''), key=f"edit_ha_{report['report_id']}")
                                edit_h_reds = st.text_input("Home Reds", value=report.get('home_reds', ''), key=f"edit_hr_{report['report_id']}")
                            with esc2:
                                edit_a_scorers = st.text_input("Away Scorers", value=report.get('away_scorers', ''), key=f"edit_asc_{report['report_id']}")
                                edit_a_assists = st.text_input("Away Assists", value=report.get('away_assists', ''), key=f"edit_aa_{report['report_id']}")
                                edit_a_reds = st.text_input("Away Reds", value=report.get('away_reds', ''), key=f"edit_ar_{report['report_id']}")
                            
                            ebtn_col1, ebtn_col2 = st.columns(2)
                            with ebtn_col1:
                                if st.button("💾 Save Changes", key=f"save_edit_{report['report_id']}"):
                                    update_pending_report(
                                        report['report_id'],
                                        edit_h_score, edit_a_score,
                                        edit_h_scorers, edit_a_scorers,
                                        edit_h_assists, edit_a_assists,
                                        edit_h_reds, edit_a_reds,
                                        edit_h_pens, edit_a_pens
                                    )
                                    save_data_internal()
                                    st.session_state[edit_key] = False
                                    st.success("Report updated!")
                                    safe_rerun()
                            
                            with ebtn_col2:
                                if st.button("❌ Cancel", key=f"cancel_edit_{report['report_id']}"):
                                    st.session_state[edit_key] = False
                                    safe_rerun()
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"✅ APPROVE", key=f"approve_{report['report_id']}"):
                        if approve_match_report(report['report_id']):
                            save_data_internal()
                            st.success("Report approved!")
                            safe_rerun()
                
                with col3:
                    if st.button(f"❌ REJECT", key=f"reject_{report['report_id']}"):
                        if reject_match_report(report['report_id']):
                            save_data_internal()
                            st.warning("Report rejected!")
                            safe_rerun()
                
                with col4:
                    # Reset match button
                    match_id = report['match_id']
                    if match_id in st.session_state.results:
                        if st.button(f"🔄 RESET", key=f"reset_pending_{report['report_id']}"):
                            if reset_match_result(match_id):
                                # Also remove the pending report
                                reject_match_report(report['report_id'])
                                save_data_internal()
                                st.info("Match reset!")
                                safe_rerun()
        
        st.markdown("---")
    
    # Determine tabs based on format and user mode
    if st.session_state.user_mode == "Captain" and st.session_state.captain_pin_verified:
        # Captain view - simplified interface
        captain_team = st.session_state.logged_in_captain
        
        # Check if captain's team exists in tournament
        if captain_team not in st.session_state.teams:
            st.error(f"⚠️ **Your team '{captain_team}' has been deleted!**")
            st.info("Please contact the tournament admin.")
            if st.button("🚪 LOGOUT", key="captain_deleted_logout"):
                st.session_state.logged_in_captain = None
                st.session_state.captain_pin_verified = False
                st.session_state.user_mode = "Admin"
                save_data_internal()
                safe_rerun()
        # Check if captain's team is still active
        elif captain_team not in st.session_state.active_teams and captain_team not in [e['team'] for e in st.session_state.eliminated_teams]:
            st.error(f"⚠️ **Your team '{captain_team}' is not in the tournament!**")
            st.info("Please contact the tournament admin if you believe this is an error.")
            if st.button("🚪 LOGOUT", key="captain_inactive_logout"):
                st.session_state.logged_in_captain = None
                st.session_state.captain_pin_verified = False
                st.session_state.user_mode = "Admin"
                save_data_internal()
                safe_rerun()
        else:
            st.markdown(f"<div class='glass-panel captain-portal'><h2>🧢 CAPTAIN'S PORTAL - {captain_team}</h2><p>Manage your team's matches and reports</p></div>", unsafe_allow_html=True)
            
            # Captain's matches - only show matches involving their team
            st.markdown("### ⚽ YOUR MATCHES")
            
            # Debug info
            debug_info = debug_captain_view(captain_team)
            
            # If no matches found, show diagnostic info
            if not debug_info['captain_fixtures']:
                st.warning("⚠️ No matches found for your team!")
                st.markdown("#### All Available Matches:")
                for i, fix in enumerate(st.session_state.fixtures[:10]):  # Show first 10
                    if len(fix) < 2:
                        continue
                    h, a = fix[0], fix[1]
                    st.write(f"Match {i}: {h} vs {a}")
                
                # Check if captain's team is in active teams
                if captain_team not in st.session_state.active_teams:
                    st.error(f"❌ {captain_team} is not in active teams list!")
                    st.write(f"Active teams: {', '.join(st.session_state.active_teams)}")
                    st.write(f"All teams: {', '.join(st.session_state.teams)}")
                
                # Manual match entry form
                with st.expander("🆘 MANUAL MATCH ENTRY (Debug)", expanded=False):
                    st.markdown("If your match isn't showing above, you can manually enter it here:")
                    
                    # Get all opponents
                    opponents = [t for t in st.session_state.active_teams if t != captain_team]
                    
                    if opponents:
                        opponent = st.selectbox("Select opponent", opponents, key="manual_opponent")
                        is_home = st.radio("Are you home or away?", ["Home", "Away"], horizontal=True, key="manual_home_away")
                        
                        if is_home == "Home":
                            home_team, away_team = captain_team, opponent
                        else:
                            home_team, away_team = opponent, captain_team
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            home_score = st.number_input("Your Score", 0, 20, key="manual_home_score")
                        with col2:
                            away_score = st.number_input("Opponent Score", 0, 20, key="manual_away_score")
                        
                        # Create a manual match ID
                        manual_match_id = f"{home_team}v{away_team}_manual_{int(datetime.now().timestamp())}"
                        
                        if st.button("📨 SUBMIT MANUAL MATCH REPORT", key="manual_submit"):
                            # Create and submit report
                            report = submit_match_report(manual_match_id, home_team, away_team, home_score, away_score, 
                                                        submitted_by=captain_team)
                            
                            save_data_internal()
                            st.success("✅ Manual match report submitted for admin approval!")
                            safe_rerun()
            
            # Display captain's matches
            for match_info in debug_info['captain_fixtures']:
                i = match_info['index']
                h = match_info['home']
                a = match_info['away']
                mid = match_info['match_id']
                result_status = get_match_result_status(mid)
                
                with st.container():
                    st.markdown(f"<div class='glass-panel'>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([4,2,4])
                    b1 = st.session_state.team_badges.get(h, ""); b2 = st.session_state.team_badges.get(a, "")
                    
                    # Match display
                    col1.markdown(f"<h3 style='text-align:right'>{h} {b1}</h3>", unsafe_allow_html=True)
                    col3.markdown(f"<h3 style='text-align:left'>{b2} {a}</h3>", unsafe_allow_html=True)
                    
                    if result_status == "approved" and mid in st.session_state.results:
                        res = st.session_state.results[mid]
                        score = f"{res[0]} - {res[1]}"
                        if len(res) > 2:
                            score += f"\n(P: {res[2]}-{res[3]})"
                        col2.markdown(f"<h1 style='text-align:center; color:#F1E194'>{score}</h1>", unsafe_allow_html=True)
                        col2.success("✅ Match completed & approved")
                    elif result_status == "pending":
                        # Show pending result
                        if mid in st.session_state.fixed_results:
                            fixed = st.session_state.fixed_results[mid]
                            score = f"{fixed['home_score']} - {fixed['away_score']}"
                            col2.markdown(f"<h1 style='text-align:center; color:#FF9800'>{score}</h1>", unsafe_allow_html=True)
                            col2.warning("⏳ Pending approval")
                        else:
                            col2.markdown(f"<h1 style='text-align:center; color:#FF9800'>VS</h1>", unsafe_allow_html=True)
                            col2.info("⚠️ Result pending")
                    else:
                        col2.markdown(f"<h1 style='text-align:center; color:#946c1e'>VS</h1>", unsafe_allow_html=True)
                        
                        # Captain fixing form - only if captain's team is involved
                        expander_title = f"📝 FIX MATCH RESULT"
                        with st.expander(expander_title, expanded=True):
                            st.info("You can fix the result for this match. It will be sent for admin approval.")
                            
                            # Determine if captain's team is home or away
                            is_home = h == captain_team
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                if is_home:
                                    s1 = st.number_input(f"{h} Score", 0, 20, key=f"cap_s1_{mid}")
                                    s2 = st.number_input(f"{a} Score", 0, 20, key=f"cap_s2_{mid}")
                                else:
                                    s2 = st.number_input(f"{h} Score", 0, 20, key=f"cap_s2_{mid}")
                                    s1 = st.number_input(f"{a} Score", 0, 20, key=f"cap_s1_{mid}")
                            
                            # Penalties for knockout/draws
                            p1, p2 = 0, 0
                            show_pens = (s1 == s2 and "League" not in st.session_state.format)
                            
                            if show_pens:
                                st.caption("Penalties (if tied)")
                                pcol1, pcol2 = st.columns(2)
                                with pcol1:
                                    if is_home:
                                        p1 = st.number_input(f"{h} Pens", 0, 20, key=f"cap_p1_{mid}")
                                    else:
                                        p2 = st.number_input(f"{h} Pens", 0, 20, key=f"cap_p2_{mid}")
                                with pcol2:
                                    if is_home:
                                        p2 = st.number_input(f"{a} Pens", 0, 20, key=f"cap_p2_{mid}")
                                    else:
                                        p1 = st.number_input(f"{a} Pens", 0, 20, key=f"cap_p1_{mid}")
                            
                            # Player stats
                            st.caption("Player Statistics")
                            scol1, scol2 = st.columns(2)
                            
                            with scol1:
                                if is_home:
                                    gs = st.text_input("Your Scorers", key=f"cap_gs_{mid}", placeholder="Messi (2), Ronaldo, ...")
                                    ha = st.text_input("Your Assists", key=f"cap_ha_{mid}")
                                    hr = st.text_input("Your Red Cards", key=f"cap_hr_{mid}")
                                else:
                                    gs = st.text_input("Opponent Scorers", key=f"cap_gs_{mid}")
                                    ha = st.text_input("Opponent Assists", key=f"cap_ha_{mid}")
                                    hr = st.text_input("Opponent Red Cards", key=f"cap_hr_{mid}")
                            
                            with scol2:
                                if is_home:
                                    gs_opp = st.text_input("Opponent Scorers", key=f"cap_gs_opp_{mid}")
                                    ha_opp = st.text_input("Opponent Assists", key=f"cap_ha_opp_{mid}")
                                    hr_opp = st.text_input("Opponent Red Cards", key=f"cap_hr_opp_{mid}")
                                else:
                                    gs_opp = st.text_input("Your Scorers", key=f"cap_gs_opp_{mid}", placeholder="Messi (2), Ronaldo, ...")
                                    ha_opp = st.text_input("Your Assists", key=f"cap_ha_opp_{mid}")
                                    hr_opp = st.text_input("Your Red Cards", key=f"cap_hr_opp_{mid}")
                            
                            if st.button("📨 SUBMIT FOR APPROVAL", key=f"cap_submit_{mid}", use_container_width=True):
                                # Prepare and submit fixed result
                                if is_home:
                                    fixed_result, report = fix_match_result_by_captain(mid, h, a, s1, s2, gs, gs_opp, ha, ha_opp, hr, hr_opp, p1, p2, captain_team)
                                else:
                                    fixed_result, report = fix_match_result_by_captain(mid, h, a, s2, s1, gs_opp, gs, ha_opp, ha, hr_opp, hr, p2, p1, captain_team)
                                
                                save_data_internal()
                                st.success("✅ Result fixed! Awaiting Admin approval.")
                                safe_rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Captain's team info
            st.markdown("### 📊 YOUR TEAM STATS")
            
            if captain_team in st.session_state.cumulative_stats:
                stats = st.session_state.cumulative_stats[captain_team]
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Matches", stats['P'])
                col2.metric("Points", stats['Pts'])
                col3.metric("Goal Diff", stats['GD'])
                # Calculate position
                standings = get_cumulative_standings()
                standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
                position = next((i+1 for i, s in enumerate(standings) if s['Team'] == captain_team), "—")
                col4.metric("Position", position)
            
            # Tournament info for captain
            st.markdown("### 🏆 TOURNAMENT INFO")
            st.info(f"**Format:** {st.session_state.format}")
            st.info(f"**Current Round:** {st.session_state.current_round}")
            
            if "Survival" in st.session_state.format:
                st.warning("💀 **Battle Royale Mode:** Points carry over between rounds!")
            
            # Show past champions to captain
            if st.session_state.past_champions:
                st.markdown("### 🏆 PAST CHAMPIONS")
                for champ in st.session_state.past_champions[:3]:  # Show last 3
                    st.markdown(f"**{champ['year']}:** {champ['champion']} ({champ['format']})")
    
    else:
        # Admin or public view - full interface
        
        # Show Past Champions (Public View)
        if st.session_state.past_champions:
            st.markdown("### 🏆 PAST CHAMPIONS")
            cols = st.columns(min(4, len(st.session_state.past_champions)))
            for idx, champ in enumerate(st.session_state.past_champions[:4]):  # Show first 4
                with cols[idx % len(cols)]:
                    st.markdown(f"""
                    <div class="champion-card">
                        <div class="champion-year">{champ['year']}</div>
                        <div class="champion-name">{champ['champion']}</div>
                        <div class="champion-format">{champ['format']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("---")
        
        # Determine tabs based on format
        if "World Cup" in st.session_state.format and st.session_state.world_cup_stage == "Group Stage":
            tab_names = ["🏆 GROUPS", "⚽ MATCH CENTER", "⭐ STATS", "📊 TOURNAMENT INFO", "🏅 HALL OF FAME"]
        elif "World Cup" in st.session_state.format:
            tab_names = ["📊 KNOCKOUT", "⚽ MATCH CENTER", "⭐ STATS", "📊 TOURNAMENT INFO", "🏅 HALL OF FAME"]
        elif "Knockout" in st.session_state.format:
            tab_names = ["📊 BRACKET", "⚽ MATCH CENTER", "⭐ STATS", "📊 TOURNAMENT INFO", "🏅 HALL OF FAME"]
        elif "Survival" in st.session_state.format:
            tab_names = ["📊 CUMULATIVE TABLE", "⚽ MATCH CENTER", "⭐ STATS", "💀 BATTLE INFO", "🏅 HALL OF FAME"]
        else:  # League
            tab_names = ["📊 LEAGUE TABLE", "⚽ MATCH CENTER", "⭐ STATS", "📊 TOURNAMENT INFO", "🏅 HALL OF FAME"]
        
        tabs = st.tabs(tab_names)

        # --- TAB 1: Tables/Brackets ---
        with tabs[0]:
            if "World Cup" in st.session_state.format and st.session_state.world_cup_stage == "Group Stage":
                # Show group tables
                st.markdown("### 🌍 GROUP STAGE STANDINGS")
                
                for group_name, teams in st.session_state.groups.items():
                    with st.expander(f"Group {group_name}", expanded=True):
                        # Calculate standings for this group
                        standings = []
                        
                        for team in teams:
                            stats = {'Team': team, 'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0}
                            
                            # Calculate stats from group matches
                            for mid, res in st.session_state.results.items():
                                try:
                                    if "_" in mid:
                                        base = mid.split('_')[0]
                                    else:
                                        base = mid
                                    
                                    if "v" not in base:
                                        continue
                                    
                                    h, a = base.split('v')
                                except:
                                    continue
                                
                                # Check if this match involves our team
                                if h == team or a == team:
                                    # Check if both teams are in the same group
                                    other_team = a if h == team else h
                                    if other_team in teams:
                                        is_home = h == team
                                        s_h, s_a = res[0], res[1]
                                        
                                        stats['P'] += 1
                                        stats['GF'] += s_h if is_home else s_a
                                        stats['GA'] += s_a if is_home else s_h
                                        stats['GD'] += (s_h - s_a) if is_home else (s_a - s_h)
                                        
                                        if is_home:
                                            if s_h > s_a:
                                                stats['W'] += 1
                                                stats['Pts'] += 3
                                            elif s_a > s_h:
                                                stats['L'] += 1
                                            else:
                                                stats['D'] += 1
                                                stats['Pts'] += 1
                                        else:
                                            if s_a > s_h:
                                                stats['W'] += 1
                                                stats['Pts'] += 3
                                            elif s_h > s_a:
                                                stats['L'] += 1
                                            else:
                                                stats['D'] += 1
                                                stats['Pts'] += 1
                            
                            standings.append(stats)
                        
                        # Sort standings
                        standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
                        
                        # Display table
                        rows = []
                        for idx, s in enumerate(standings):
                            badge = st.session_state.team_badges.get(s['Team'], "🛡️")
                            rows.append({
                                "#": idx + 1,
                                "Team": f"{badge} {s['Team']}",
                                "P": s['P'], "W": s['W'], "D": s['D'], "L": s['L'], 
                                "GF": s['GF'], "GA": s['GA'], "GD": s['GD'], 
                                "Pts": s['Pts']
                            })
                        
                        if rows:
                            df = pd.DataFrame(rows)
                            st.dataframe(df[['#', 'Team', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']], 
                                       hide_index=True, use_container_width=True,
                                       column_config={
                                           "#": st.column_config.NumberColumn(width="small"),
                                           "Pts": st.column_config.ProgressColumn("Pts", format="%d", min_value=0, max_value=max(6, df['Pts'].max()))
                                       })
            
            elif "World Cup" in st.session_state.format or "Knockout" in st.session_state.format:
                # Show knockout bracket
                st.markdown("### 🎯 KNOCKOUT BRACKET")
                
                if st.session_state.fixtures:
                    col1, col2 = st.columns(2)
                    
                    for i, match in enumerate(st.session_state.fixtures):
                        if len(match) < 2:
                            continue
                        
                        h, a = match[0], match[1]
                        mid = f"{h}v{a}_{i}"
                        result_status = get_match_result_status(mid)
                        
                        with col1 if i % 2 == 0 else col2:
                            match_html = f"""
                            <div class='bracket-match'>
                                <strong>{h}</strong> vs <strong>{a}</strong><br>
                            """
                            
                            if result_status == "approved" and mid in st.session_state.results:
                                res = st.session_state.results[mid]
                                match_html += f"<strong>{res[0]} - {res[1]}</strong>"
                                if len(res) > 2:
                                    match_html += f" (P: {res[2]}-{res[3]})"
                            elif result_status == "pending":
                                if mid in st.session_state.fixed_results:
                                    fixed = st.session_state.fixed_results[mid]
                                    match_html += f"<span style='color: #FF9800; font-weight: bold;'>{fixed['home_score']} - {fixed['away_score']} (Pending)</span>"
                                else:
                                    match_html += "<span style='color: #FF9800;'>Pending</span>"
                            else:
                                match_html += "Not played"
                            
                            match_html += "</div>"
                            st.markdown(match_html, unsafe_allow_html=True)
                    
                    # Show tournament progress
                    if st.session_state.champion:
                        st.success(f"🏆 **CHAMPION: {st.session_state.champion}**")
                    else:
                        round_names = {
                            8: "Quarter Finals",
                            4: "Semi Finals",
                            2: "Final"
                        }
                        current_round = round_names.get(len(st.session_state.fixtures), f"Round {st.session_state.knockout_round}")
                        st.info(f"**Current Stage:** {current_round}")
                        
                        # Show remaining teams
                        remaining_teams = set()
                        for match in st.session_state.fixtures:
                            if len(match) >= 2:
                                remaining_teams.add(match[0])
                                remaining_teams.add(match[1])
                        
                        if remaining_teams:
                            st.markdown(f"**Teams Remaining:** {', '.join(sorted(remaining_teams))}")
            
            elif "Survival" in st.session_state.format:
                # Battle Royale table
                def render_battle_royale_table():
                    standings = get_cumulative_standings()
                    
                    if not standings:
                        st.info("No teams remaining")
                        return
                    
                    standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
                    
                    rows = []
                    for idx, s in enumerate(standings):
                        team = s['Team']
                        badge = st.session_state.team_badges.get(team, "🛡️")
                        
                        row_class = ""
                        if st.session_state.battle_phase == "Phase 1: The Purge" and idx >= len(standings) - 2:
                            row_class = "drop-zone"
                        elif st.session_state.battle_phase == "Phase 2: The Squeeze" and idx == len(standings) - 1:
                            row_class = "drop-zone"
                        elif st.session_state.bye_team == team:
                            row_class = "bye-zone"
                        
                        rows.append({
                            "#": idx + 1,
                            "Club": f"{badge} {team}",
                            "P": s['P'], "W": s['W'], "D": s['D'], "L": s['L'], 
                            "GF": s['GF'], "GA": s['GA'], "GD": s['GD'], 
                            "Pts": s['Pts']
                        })
                    
                    if rows:
                        df = pd.DataFrame(rows)
                        
                        st.markdown(f"**Teams Alive:** {len(st.session_state.active_teams)} | **Current Phase:** {st.session_state.battle_phase}")
                        
                        if st.session_state.battle_phase == "Phase 1: The Purge":
                            st.warning(f"⚠️ **DROP ZONE:** Bottom 2 teams will be eliminated after this round! (2 matches each)")
                        elif st.session_state.battle_phase == "Phase 2: The Squeeze":
                            st.warning(f"⚠️ **DROP ZONE:** Bottom team will be eliminated after this round! (2 matches each)")
                        elif st.session_state.battle_phase == "Phase 3: The Standoff":
                            st.info(f"👑 **BYE:** {st.session_state.bye_team} gets automatic pass to Final!")
                            st.warning(f"⚔️ **SUDDEN DEATH:** 2nd vs 3rd playing elimination match!")
                        
                        st.dataframe(df[['#', 'Club', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']], 
                                   hide_index=True, use_container_width=True,
                                   column_config={
                                       "#": st.column_config.NumberColumn(width="small"),
                                       "Pts": st.column_config.ProgressColumn("Pts", format="%d", min_value=0, max_value=max(100, df['Pts'].max()))
                                   })
                        
                        # Show eliminated teams
                        if st.session_state.eliminated_teams:
                            with st.expander(f"☠️ Eliminated Teams ({len(st.session_state.eliminated_teams)})", expanded=False):
                                elim_data = []
                                for e in st.session_state.eliminated_teams:
                                    elim_data.append({
                                        "Team": e['team'],
                                        "Round": e['round'],
                                        "Phase": e['phase'],
                                        "Position": f"{e['position']}th"
                                    })
                                if elim_data:
                                    elim_df = pd.DataFrame(elim_data)
                                    st.dataframe(elim_df, hide_index=True, use_container_width=True)
                
                render_battle_royale_table()
            
            else:  # League format
                def render_league_table():
                    standings = get_cumulative_standings()
                    
                    if not standings:
                        st.info("No teams in league")
                        return
                    
                    standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
                    
                    rows = []
                    for idx, s in enumerate(standings):
                        team = s['Team']
                        badge = st.session_state.team_badges.get(team, "🛡️")
                        
                        rows.append({
                            "#": idx + 1,
                            "Club": f"{badge} {team}",
                            "P": s['P'], "W": s['W'], "D": s['D'], "L": s['L'], 
                            "GF": s['GF'], "GA": s['GA'], "GD": s['GD'], 
                            "Pts": s['Pts']
                        })
                    
                    if rows:
                        df = pd.DataFrame(rows)
                        st.dataframe(df[['#', 'Club', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']], 
                                   hide_index=True, use_container_width=True,
                                   column_config={
                                       "#": st.column_config.NumberColumn(width="small"),
                                       "Pts": st.column_config.ProgressColumn("Pts", format="%d", min_value=0, max_value=max(100, df['Pts'].max()))
                                   })
                
                render_league_table()

        # --- TAB 2: Match Center ---
        with tabs[1]:
            # Team filter - only show for admin or public view
            filter_options = ["All"] + st.session_state.active_teams
            if st.session_state.user_mode == "Captain" and st.session_state.captain_pin_verified:
                # Captains automatically filter to their own team
                filter_team = st.session_state.logged_in_captain
                st.info(f"📋 Showing matches for your team: **{filter_team}**")
            else:
                filter_team = st.selectbox("FILTER TEAM", filter_options, key="team_filter")
            
            # Display matches
            for i, fix in enumerate(st.session_state.fixtures): 
                if len(fix) < 2: continue
                h, a = fix[0], fix[1]
                
                # Filter logic
                if filter_team != "All" and filter_team not in [h, a]: 
                    continue
                
                mid = f"{h}v{a}_{i}" 
                result_status = get_match_result_status(mid)
                
                is_sudden_death = (
                    st.session_state.battle_phase == "Phase 3: The Standoff" and 
                    st.session_state.sudden_death_round > 0
                )
                
                with st.container():
                    panel_class = "glass-panel"
                    if is_sudden_death:
                        panel_class += " sudden-death"
                    
                    st.markdown(f"<div class='{panel_class}'>", unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([4, 2, 4])
                    b1 = st.session_state.team_badges.get(h, ""); b2 = st.session_state.team_badges.get(a, "")
                    
                    # Match header
                    if is_sudden_death:
                        c1.markdown(f"<h3 style='text-align:right; color:#ff6b6b'>{h} {b1}</h3>", unsafe_allow_html=True)
                        c3.markdown(f"<h3 style='text-align:left; color:#ff6b6b'>{b2} {a}</h3>", unsafe_allow_html=True)
                        c2.markdown(f"<div style='text-align:center'><small>⚔️ SUDDEN DEATH • Leg {st.session_state.sudden_death_round}</small></div>", unsafe_allow_html=True)
                    else:
                        c1.markdown(f"<h3 style='text-align:right'>{h} {b1}</h3>", unsafe_allow_html=True)
                        c3.markdown(f"<h3 style='text-align:left'>{b2} {a}</h3>", unsafe_allow_html=True)
                    
                    # Score display based on status
                    if result_status == "approved" and mid in st.session_state.results:
                        res = st.session_state.results[mid]
                        sc = f"{res[0]} - {res[1]}"
                        if len(res) > 2: sc += f"\n(P: {res[2]}-{res[3]})"
                        score_color = "#ef4444" if is_sudden_death else "#F1E194"
                        c2.markdown(f"<h1 style='text-align:center; color:{score_color}'>{sc}</h1>", unsafe_allow_html=True)
                    elif result_status == "pending":
                        if mid in st.session_state.fixed_results:
                            fixed = st.session_state.fixed_results[mid]
                            sc = f"{fixed['home_score']} - {fixed['away_score']}"
                            c2.markdown(f"<h1 style='text-align:center; color:#FF9800'>{sc}</h1>", unsafe_allow_html=True)
                            c2.markdown("<div style='text-align:center; font-size: 0.8rem; color:#FF9800'>⏳ Pending Approval</div>", unsafe_allow_html=True)
                        else:
                            c2.markdown(f"<h1 style='text-align:center; color:#FF9800'>VS</h1>", unsafe_allow_html=True)
                            c2.markdown("<div style='text-align:center; font-size: 0.8rem; color:#FF9800'>Result Pending</div>", unsafe_allow_html=True)
                    else: 
                        if is_sudden_death:
                            c2.markdown(f"<h1 style='text-align:center; color:#ef4444'>⚔️ VS ⚔️</h1>", unsafe_allow_html=True)
                        else:
                            c2.markdown(f"<h1 style='text-align:center; color:#946c1e'>VS</h1>", unsafe_allow_html=True)
                    
                    # Admin controls for match reporting
                    if st.session_state.admin_unlock and not st.session_state.champion: 
                        expander_title = f"📝 ENTER/RESET RESULT"
                        with st.expander(expander_title, expanded=False):
                            if is_sudden_death:
                                st.warning("⚔️ **SUDDEN DEATH SEMI-FINAL:** Loser is ELIMINATED!")
                            
                            ac1, ac2 = st.columns(2)
                            
                            # Show current result if exists
                            current_home_score = 0
                            current_away_score = 0
                            current_home_pens = 0
                            current_away_pens = 0
                            current_meta = st.session_state.match_meta.get(mid, {})
                            
                            if result_status == "approved" and mid in st.session_state.results:
                                res = st.session_state.results[mid]
                                current_home_score = res[0]
                                current_away_score = res[1]
                                if len(res) > 2:
                                    current_home_pens = res[2]
                                    current_away_pens = res[3]
                            
                            s1 = ac1.number_input(f"{h}", 0, 20, value=current_home_score, key=f"s1_{mid}") 
                            s2 = ac2.number_input(f"{a}", 0, 20, value=current_away_score, key=f"s2_{mid}") 
                            p1, p2 = 0, 0
                            
                            # Show penalties for knockout matches or draws in non-league
                            show_pens = (s1 == s2 and "League" not in st.session_state.format) or is_sudden_death
                            
                            if show_pens:
                                st.caption("Penalties (if tied)")
                                p1 = ac1.number_input(f"P {h}", 0, 20, value=current_home_pens, key=f"p1_{mid}")
                                p2 = ac2.number_input(f"P {a}", 0, 20, value=current_away_pens, key=f"p2_{mid}")

                            sc1, sc2 = st.columns(2)
                            prev = current_meta
                            gs1_input = sc1.text_input("Scorers (Home)", value=prev.get('h_s',''), key=f"g1_{mid}", placeholder="Messi (2), ...")
                            gs2_input = sc2.text_input("Scorers (Away)", value=prev.get('a_s',''), key=f"g2_{mid}")
                            ha = sc1.text_input("Assists (Home)", value=prev.get('h_a',''), key=f"ah_{mid}")
                            aa = sc2.text_input("Assists (Away)", value=prev.get('a_a',''), key=f"aa_{mid}")
                            hr = sc1.text_input("Red Cards (Home)", value=prev.get('h_r',''), key=f"rh_{mid}")
                            ar = sc2.text_input("Red Cards (Away)", value=prev.get('a_r',''), key=f"ra_{mid}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("✅ CONFIRM RESULT", key=f"b_{mid}", use_container_width=True):
                                    # Use the safe update function and mark as approved
                                    update_match_result_safely(mid, h, a, s1, s2, p1, p2, gs1_input, gs2_input, ha, aa, hr, ar)
                                    st.session_state.admin_approved_results[mid] = True
                                    
                                    # Remove from fixed results if exists
                                    if mid in st.session_state.fixed_results:
                                        del st.session_state.fixed_results[mid]
                                    
                                    # Remove from pending reports
                                    st.session_state.pending_reports = [r for r in st.session_state.pending_reports if r['match_id'] != mid]
                                    
                                    save_data_internal()
                                    st.success("✅ Match recorded! Table updated.")
                                    safe_rerun()
                            
                            with col2:
                                if result_status != "not_played" and st.button("🔄 RESET MATCH", key=f"reset_{mid}", use_container_width=True):
                                    if reset_match_result(mid):
                                        save_data_internal()
                                        st.warning("Match reset!")
                                        safe_rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)

        # --- TAB 3: Stats ---
        with tabs[2]:
            # Get cumulative player stats
            player_stats = st.session_state.cumulative_player_stats
            
            if player_stats:
                # Convert to list for display
                data = []
                for player_id, stats in player_stats.items():
                    if isinstance(stats, dict):
                        data.append({
                            "Player": stats.get('Name', 'Unknown'),
                            "Club": stats.get('Team', 'Unknown'),
                            "Goals": stats.get('G', 0),
                            "Assists": stats.get('A', 0),
                            "Reds": stats.get('R', 0)
                        })
                
                if data:
                    df = pd.DataFrame(data)
                    
                    # Show Golden Boot and Playmaker leaders
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if not df.empty:
                            top_scorer = df.sort_values(by='Goals', ascending=False).iloc[0]
                            st.markdown(f"<div class='glass-panel' style='text-align:center'><h3>👑 GOLDEN BOOT</h3><h2 class='golden-boot'>{top_scorer['Player']} ({top_scorer['Club']}) - {top_scorer['Goals']} goals</h2></div>", unsafe_allow_html=True)
                    
                    with col2:
                        if not df.empty:
                            top_assister = df.sort_values(by='Assists', ascending=False).iloc[0]
                            st.markdown(f"<div class='glass-panel' style='text-align:center'><h3>🎯 TOP PLAYMAKER</h3><h2 style='color:#F1E194; font-weight:bold; font-size:1.5rem;'>{top_assister['Player']} ({top_assister['Club']}) - {top_assister['Assists']} assists</h2></div>", unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns(3)
                    
                    def show_stat(col, title, key, icon):
                        col.markdown(f"#### {icon} {title}")
                        if not df.empty:
                            top = df.sort_values(by=key, ascending=False).head(10).reset_index(drop=True)
                            top.index += 1
                            col.dataframe(top[['Player', 'Club', key]], use_container_width=True)
                    
                    show_stat(c1, "Goals", "Goals", "⚽")
                    show_stat(c2, "Assists", "Assists", "👟")
                    show_stat(c3, "Red Cards", "Reds", "🟥")
                    
                    # Show total stats
                    with st.expander("📊 TOTAL TOURNAMENT STATS", expanded=False):
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Total Players", len(df))
                        col2.metric("Total Goals", int(df['Goals'].sum()))
                        col3.metric("Total Assists", int(df['Assists'].sum()))
                        col4.metric("Total Red Cards", int(df['Reds'].sum()))
                else:
                    st.info("No player stats recorded yet. Report matches to see stats!")
            else:
                st.info("No player stats recorded yet. Report matches to see stats!")

        # --- TAB 4: Tournament Info ---
        with tabs[3]:
            if "Survival" in st.session_state.format:
                st.markdown("### 💀 BATTLE ROYALE PROTOCOL")
                
                # Protocol Rules
                with st.expander("📜 THE CORE RULES", expanded=True):
                    st.markdown("""
                    **1. The "Cumulative" Table**
                    - Points carry over FOREVER
                    - Player stats (goals, assists, reds) also carry over FOREVER
                    - Win 3-0 in Round 1 → carry 3 points and +3 GD into Round 2
                    - Strategy: Hoard points to stay safe from the "Drop Zone"
                    
                    **2. Matchmaking: Pure RNG**
                    - No fixed bracket
                    - After every round, all surviving teams are thrown into a hat and shuffled
                    - You could play the strongest team twice in a row, or dodge them until the end
                    - It is pure luck
                    """)
                
                with st.expander("🩸 THE ELIMINATION PHASES", expanded=False):
                    st.markdown("""
                    **Phase 1: The Purge (5+ Teams Alive)**
                    - Bottom 2 teams eliminated EVERY ROUND
                    - **2 matches per team each round**
                    - Example: 8 teams → Round 1 → 7th & 8th deleted
                    
                    **Phase 2: The Squeeze (4 Teams Alive)**
                    - Bottom 1 team eliminated per round
                    - 2 matches per team (home & away)
                    - You just have to be better than one other person
                    
                    **Phase 3: The Standoff (3 Teams Alive)**
                    - **1st Place**: Gets a BYE (Automatic pass to Grand Final)
                    - **2nd vs 3rd**: Play "Sudden Death" Semi-Final (2 legs)
                    - Loser eliminated, Winner advances to Final
                    
                    **Phase 4: The Grand Final (2 Teams Alive)**
                    - Final two survivors play one last match
                    - Highest points total at the end wins the crown
                    """)
                
                with st.expander("📊 TIE-BREAKERS (How to stay alive)", expanded=False):
                    st.markdown("""
                    If teams are level on points near the Drop Zone:
                    1. **Points** (Highest wins)
                    2. **Goal Difference** (Better GD wins)
                    3. **Goals For** (Most goals scored wins)
                    4. **Head-to-Head** (If applicable)
                    """)
                
                # Current Status
                st.markdown("### 🎯 CURRENT STATUS")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Teams Alive", len(st.session_state.active_teams))
                with col2:
                    st.metric("Round", st.session_state.round_number)
                with col3:
                    st.metric("Eliminated", len(st.session_state.eliminated_teams))
                with col4:
                    st.metric("Phase", st.session_state.battle_phase.split(":")[0])
            
            else:
                # Tournament info for all formats
                st.markdown("### 🏆 TOURNAMENT INFORMATION")
                
                if "World Cup" in st.session_state.format:
                    st.markdown("#### 🌍 WORLD CUP FORMAT")
                    if st.session_state.world_cup_stage == "Group Stage":
                        st.info("**Current Stage:** Group Stage")
                        st.markdown("""
                        **Format:**
                        1. **Group Stage**: Teams play round-robin within their groups
                        2. **Top 2 from each group** advance to knockout stage
                        3. **Knockout Stage**: Single elimination (Round of 16 → Quarter Finals → Semi Finals → Final)
                        
                        **Group Stage Rules:**
                        - 3 points for a win
                        - 1 point for a draw
                        - 0 points for a loss
                        - Tie-breakers: Goal Difference → Goals For → Head-to-Head
                        """)
                        
                        # Show group info
                        st.markdown("#### 📊 GROUPS")
                        for group_name, teams in st.session_state.groups.items():
                            st.markdown(f"**Group {group_name}:** {', '.join(teams)}")
                    
                    else:
                        st.info(f"**Current Stage:** {st.session_state.world_cup_stage}")
                        st.markdown("**Knockout Stage Rules:**")
                        st.markdown("""
                        - **Single elimination**
                        - **90 minutes**: If draw, go to extra time
                        - **Penalties**: If still draw after extra time
                        - **No away goals rule**
                        - **Random draw** for each round
                        """)
                        
                        if st.session_state.champion:
                            st.success(f"🏆 **WORLD CUP CHAMPION:** {st.session_state.champion}")
                
                elif "Knockout" in st.session_state.format:
                    st.markdown("#### 🎯 CLASSIC KNOCKOUT TOURNAMENT")
                    st.info(f"**Current Round:** {st.session_state.current_round}")
                    st.markdown("""
                    **Format:**
                    - **Single elimination** tournament
                    - **Direct knockout** from Round 1
                    - **Draws**: Go directly to penalties (no extra time)
                    - **Random draw** for each round
                    - **All matches** must have a winner
                    """)
                    
                    if st.session_state.champion:
                        st.success(f"🏆 **CHAMPION:** {st.session_state.champion}")
                    else:
                        # Show remaining teams count
                        remaining_teams = set()
                        for match in st.session_state.fixtures:
                            if len(match) >= 2:
                                remaining_teams.add(match[0])
                                remaining_teams.add(match[1])
                        
                        st.metric("Teams Remaining", len(remaining_teams))
                
                else:  # League format
                    st.markdown("#### 🏆 HOME & AWAY LEAGUE")
                    st.markdown("""
                    **Format:**
                    - **Double round-robin** (home and away)
                    - **3 points** for a win
                    - **1 point** for a draw
                    - **0 points** for a loss
                    - **Tie-breakers**: Goal Difference → Goals For → Head-to-Head
                    - **Season length**: (Teams × 2) - 2 matches per team
                    """)
                    
                    if st.session_state.champion:
                        st.success(f"🏆 **LEAGUE CHAMPION:** {st.session_state.champion}")
                    else:
                        # Calculate matches played
                        total_matches = len(st.session_state.fixtures)
                        played_matches = len(st.session_state.results)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Matches", total_matches)
                        with col2:
                            st.metric("Matches Played", played_matches)
                        with col3:
                            if total_matches > 0:
                                progress = int((played_matches / total_matches) * 100)
                                st.metric("Completion", f"{progress}%")
                
                # General tournament info for all formats
                st.markdown("---")
                st.markdown("#### 📋 TOURNAMENT DETAILS")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Teams", len(st.session_state.teams))
                    st.metric("Active Teams", len(st.session_state.active_teams))
                with col2:
                    st.metric("Tournament Format", st.session_state.format)
                    if st.session_state.champion:
                        st.metric("Status", "COMPLETED")
                    else:
                        st.metric("Status", "IN PROGRESS")
        
        # --- TAB 5: Hall of Fame ---
        with tabs[4]:
            st.markdown("### 🏅 HALL OF FAME")
            
            if st.session_state.past_champions:
                # Show all past champions
                st.markdown("#### 🏆 PAST CHAMPIONS")
                
                # Group by year
                champions_by_year = {}
                for champ in st.session_state.past_champions:
                    year = champ['year']
                    if year not in champions_by_year:
                        champions_by_year[year] = []
                    champions_by_year[year].append(champ)
                
                # Sort years descending
                sorted_years = sorted(champions_by_year.keys(), reverse=True)
                
                for year in sorted_years:
                    with st.expander(f"🎯 {year} SEASON", expanded=year == sorted_years[0]):
                        year_champs = champions_by_year[year]
                        cols = st.columns(min(3, len(year_champs)))
                        
                        for idx, champ in enumerate(year_champs):
                            with cols[idx % len(cols)]:
                                st.markdown(f"""
                                <div class="champion-card">
                                    <div class="champion-name">{champ['champion']}</div>
                                    <div class="champion-format">{champ['format']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                
                # Stats
                st.markdown("#### 📊 CHAMPIONSHIP STATS")
                
                # Calculate most successful teams
                champion_counts = {}
                for champ in st.session_state.past_champions:
                    team = champ['champion']
                    champion_counts[team] = champion_counts.get(team, 0) + 1
                
                if champion_counts:
                    # Most championships
                    most_champs = max(champion_counts.items(), key=lambda x: x[1])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Championships", len(st.session_state.past_champions))
                    with col2:
                        st.metric("Unique Champions", len(champion_counts))
                    with col3:
                        st.metric("Most Championships", f"{most_champs[0]} ({most_champs[1]})")
                    
                    # Show champion leaderboard
                    st.markdown("#### 👑 CHAMPION LEADERBOARD")
                    leaderboard = sorted(champion_counts.items(), key=lambda x: x[1], reverse=True)
                    leaderboard_data = []
                    for idx, (team, count) in enumerate(leaderboard[:10]):  # Top 10
                        leaderboard_data.append({
                            "Rank": idx + 1,
                            "Team": team,
                            "Championships": count,
                            "Last Win": next((c['year'] for c in st.session_state.past_champions if c['champion'] == team), "N/A")
                        })
                    
                    if leaderboard_data:
                        df_leaderboard = pd.DataFrame(leaderboard_data)
                        st.dataframe(df_leaderboard, hide_index=True, use_container_width=True)
            else:
                st.info("No past champions recorded yet. Complete tournaments to build the Hall of Fame!")
                
                # Show current champion if exists
                if st.session_state.champion:
                    st.markdown("#### 🏆 CURRENT CHAMPION")
                    st.markdown(f"""
                    <div class="champion-card">
                        <div class="champion-name">{st.session_state.champion}</div>
                        <div class="champion-format">{st.session_state.format}</div>
                        <div class="champion-year">Current Season</div>
                    </div>
                    """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""<div class="footer">OFFICIAL DLS TOURNAMENT ENGINE • CAPTAIN'S PORTAL EDITION <br> WRITTEN AND DESIGNED BY <span class="designer-name">OLUWATIMILEYIN IGBINLOLA</span></div>""", unsafe_allow_html=True)
