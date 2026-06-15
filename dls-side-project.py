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

# Optional: plotly for charts
try:
    import plotly.express as px
    plotly_available = True
except ImportError:
    plotly_available = False
    st.warning("Plotly not installed. Charts will be disabled. Run `pip install plotly` to enable.")

# --- CONFIGURATION ---
st.set_page_config(page_title="DLS Ultra Admin", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

# --- COMPATIBILITY SHIM ---
def safe_rerun():
    if hasattr(st, 'rerun'):
        st.rerun()
    elif hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    else:
        st.warning("⚠️ Auto-reload not supported. Please manually refresh your browser.")

# --- NEW CSS: DARK MODERN THEME with ELECTRIC CYAN ---
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    /* Background */
    .stApp {
        background: #0a0a0a;
        background-image: radial-gradient(circle at 25% 0%, #1a2a3a 0%, #0a0a0a 80%);
        color: #e2e8f0;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #f1f5f9 !important;
    }

    /* Main title */
    .big-title {
        font-size: 4rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #3b82f6 0%, #00e5ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    /* Glass cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        border-radius: 1rem;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    .glass-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6, #00e5ff);
        border: none;
        color: white;
        font-weight: 600;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        transition: transform 0.1s ease, box-shadow 0.2s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
        color: white;
    }
    .stButton > button:active {
        transform: translateY(1px);
    }

    /* Danger button override */
    div[data-testid="column"] .stButton > button:has(> :contains("DELETE")) {
        background: linear-gradient(90deg, #dc2626, #ef4444);
    }

    /* Inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 0.5rem !important;
        color: #f1f5f9 !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59,130,246,0.3);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
        border-bottom: 1px solid #334155;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0.5rem 0.5rem 0 0;
        padding: 0.5rem 1rem;
        font-weight: 500;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #3b82f6, #00e5ff);
        color: white;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(4px);
        border-radius: 0.75rem;
        padding: 0.5rem;
        border: 1px solid #334155;
    }
    div[data-testid="stMetricValue"] {
        color: #3b82f6 !important;
        font-weight: 700;
    }

    /* Progress bars */
    .progress-container {
        background: #1e293b;
        border-radius: 1rem;
        overflow: hidden;
    }
    .progress-bar {
        background: linear-gradient(90deg, #3b82f6, #00e5ff);
        height: 0.5rem;
        border-radius: 1rem;
    }

    /* Match cards */
    .match-card {
        background: rgba(30, 41, 59, 0.7);
        border-left: 4px solid #3b82f6;
        border-radius: 0.75rem;
        padding: 1rem;
        margin: 0.75rem 0;
    }
    .match-status {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-approved { color: #10b981; }
    .status-pending { color: #f59e0b; }
    .status-notplayed { color: #64748b; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.9);
        backdrop-filter: blur(16px);
        border-right: 1px solid #334155;
    }

    /* Badges */
    .team-badge {
        font-size: 2rem;
        line-height: 1;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        border-top: 1px solid #334155;
        font-size: 0.8rem;
        color: #64748b;
    }
    .designer-name {
        color: #3b82f6;
        font-weight: 600;
    }

    /* Info boxes */
    .info-box {
        background: rgba(59,130,246,0.1);
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- 💾 DATABASE & INITIALIZATION (unchanged logic, just keep everything) ---
DB_FILE = "dls_ultra_db.json"
BADGE_POOL = ["🦁", "🦅", "🐺", "🐉", "🦈", "🐍", "🐻", "🐝", "🦂", "🕷️", "⚓", "⚔️", "🛡️", "👑", "⚡", "🔥", "🌪️", "🌊", "🏰", "🚀", "💀", "👹", "👽", "🤖", "👻", "🎃", "💎", "🎯", "🎲", "🎱"]
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
        'captain_pins': {},
        'pending_reports': [],
        'tournament_code': DEFAULT_TOURNAMENT_CODE,
        'user_mode': 'Admin',
        'logged_in_captain': None,
        'captain_pin_verified': False,
        'team_passwords': {},
        'captain_logs': [],
        'past_champions': [],
        'champion_history': {},
        'fixed_results': {},
        'captain_fixed_matches': {},
        'admin_approved_results': {}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                for key in ['teams', 'format', 'current_round', 'fixtures', 'results', 
                          'match_meta', 'started', 'groups', 'champion', 'active_teams',
                          'team_badges', 'news', 'legacy_stats', 
                          'team_history', 'eliminated_teams', 'round_number', 
                          'survival_history', 'battle_phase', 'bye_team', 
                          'cumulative_stats', 'cumulative_player_stats', 
                          'sudden_death_round', 'phase1_match_count',
                          'world_cup_stage', 'knockout_bracket', 'knockout_round',
                          'knockout_winners', 'match_history', 'captain_pins', 'pending_reports',
                          'tournament_code', 'user_mode', 'logged_in_captain', 'captain_pin_verified',
                          'team_passwords', 'captain_logs', 'past_champions', 'champion_history',
                          'fixed_results', 'captain_fixed_matches', 'admin_approved_results']:
                    if key in data:
                        if key == 'fixtures':
                            st.session_state[key] = [tuple(f) for f in data[key]] if isinstance(data[key], list) else []
                        else:
                            st.session_state[key] = data[key]
                # Initialize badges, pins, etc. for any missing teams
                for t in st.session_state.teams:
                    if t not in st.session_state.team_badges:
                        st.session_state.team_badges[t] = random.choice(BADGE_POOL)
                    if t not in st.session_state.captain_pins:
                        st.session_state.captain_pins[t] = generate_pin()
                    if t not in st.session_state.captain_fixed_matches:
                        st.session_state.captain_fixed_matches[t] = []
        except Exception as e:
            st.error(f"Error loading data: {e}")
            init_defaults()
    else:
        init_defaults()

def save_data_internal():
    try:
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
        with open(DB_FILE, "w") as f:
            json.dump(data, f)
        return True
    except Exception as e:
        st.error(f"Failed to save data: {e}")
        return False

# --- Helper functions (all existing logic preserved, only adding new ones) ---
def generate_pin():
    return str(random.randint(1000, 9999))

def generate_team_password():
    adjectives = ["Swift", "Brave", "Royal", "Golden", "Mighty", "Fierce", "Noble", "Valiant"]
    nouns = ["Lions", "Eagles", "Wolves", "Dragons", "Sharks", "Titans", "Gladiators", "Warriors"]
    return f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(10, 99)}"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_team_name(team_name):
    if not team_name: return False, "Team name cannot be empty"
    forbidden_chars = ['_', 'v', '|', '/', '\\', '"', "'"]
    for char in forbidden_chars:
        if char in team_name:
            return False, f"Team name cannot contain '{char}' character"
    if len(team_name) > 50:
        return False, "Team name too long (max 50 characters)"
    return True, ""

def log_captain_action(action, team=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {'timestamp': timestamp, 'action': action, 'team': team or st.session_state.logged_in_captain, 'user_mode': st.session_state.user_mode}
    st.session_state.captain_logs.append(log_entry)
    if len(st.session_state.captain_logs) > 100:
        st.session_state.captain_logs = st.session_state.captain_logs[-100:]

def process_player_string_update(raw_str, team, stat_type):
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
        if player_id not in st.session_state.cumulative_player_stats:
            st.session_state.cumulative_player_stats[player_id] = {'Name': name, 'Team': team, 'G': 0, 'A': 0, 'R': 0}
        st.session_state.cumulative_player_stats[player_id][stat_type] += count

def update_match_result_safely(mid, h, a, s1, s2, p1=0, p2=0, gs1="", gs2="", ha="", aa="", hr="", ar=""):
    was_processed = mid in st.session_state.match_history
    if was_processed:
        old_res = st.session_state.match_history[mid]
        old_s1, old_s2 = old_res['score']
        old_p1, old_p2 = old_res.get('pens', (0,0))
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
            stats['P'] -= 1; stats['GF'] -= old_s1; stats['GA'] -= old_s2; stats['GD'] -= (old_s1 - old_s2)
            if old_s1 > old_s2: stats['W'] -= 1; stats['Pts'] -= 3
            elif old_s2 > old_s1: stats['L'] -= 1
            else: stats['D'] -= 1; stats['Pts'] -= 1
        if a in st.session_state.cumulative_stats:
            stats = st.session_state.cumulative_stats[a]
            stats['P'] -= 1; stats['GF'] -= old_s2; stats['GA'] -= old_s1; stats['GD'] -= (old_s2 - old_s1)
            if old_s2 > old_s1: stats['W'] -= 1; stats['Pts'] -= 3
            elif old_s1 > old_s2: stats['L'] -= 1
            else: stats['D'] -= 1; stats['Pts'] -= 1
        # Remove old player stats
        def remove_player_stats(raw_str, team, stat_type):
            if not raw_str: return
            parts = raw_str.split(',')
            for rp in parts:
                rp = rp.strip()
                if not rp: continue
                cnt = 1
                nm = rp
                m_br = re.search(r'^(.*?)\s*\((\d+)\)$', rp)
                if m_br: nm = m_br.group(1).strip(); cnt = int(m_br.group(2))
                m_x = re.search(r'^(.*?)\s*[xX](\d+)$', rp)
                if m_x: nm = m_x.group(1).strip(); cnt = int(m_x.group(2))
                nm = nm.strip().title()
                if not nm: continue
                pid = f"{nm}|{team}"
                if pid in st.session_state.cumulative_player_stats:
                    st.session_state.cumulative_player_stats[pid][stat_type] -= cnt
                    if st.session_state.cumulative_player_stats[pid]['G'] <= 0 and st.session_state.cumulative_player_stats[pid]['A'] <= 0 and st.session_state.cumulative_player_stats[pid]['R'] <= 0:
                        del st.session_state.cumulative_player_stats[pid]
        remove_player_stats(old_gs1, h, 'G')
        remove_player_stats(old_gs2, a, 'G')
        remove_player_stats(old_ha, h, 'A')
        remove_player_stats(old_aa, a, 'A')
        remove_player_stats(old_hr, h, 'R')
        remove_player_stats(old_ar, a, 'R')
    # Initialize stats if missing
    for team in [h,a]:
        if team not in st.session_state.cumulative_stats:
            st.session_state.cumulative_stats[team] = {'P':0,'W':0,'D':0,'L':0,'GF':0,'GA':0,'GD':0,'Pts':0}
    # Add new stats
    st.session_state.cumulative_stats[h]['P'] += 1
    st.session_state.cumulative_stats[a]['P'] += 1
    st.session_state.cumulative_stats[h]['GF'] += s1
    st.session_state.cumulative_stats[h]['GA'] += s2
    st.session_state.cumulative_stats[h]['GD'] += (s1 - s2)
    st.session_state.cumulative_stats[a]['GF'] += s2
    st.session_state.cumulative_stats[a]['GA'] += s1
    st.session_state.cumulative_stats[a]['GD'] += (s2 - s1)
    if s1 > s2:
        st.session_state.cumulative_stats[h]['W'] += 1; st.session_state.cumulative_stats[h]['Pts'] += 3
        st.session_state.cumulative_stats[a]['L'] += 1
    elif s2 > s1:
        st.session_state.cumulative_stats[a]['W'] += 1; st.session_state.cumulative_stats[a]['Pts'] += 3
        st.session_state.cumulative_stats[h]['L'] += 1
    else:
        st.session_state.cumulative_stats[h]['D'] += 1; st.session_state.cumulative_stats[h]['Pts'] += 1
        st.session_state.cumulative_stats[a]['D'] += 1; st.session_state.cumulative_stats[a]['Pts'] += 1
    st.session_state.match_history[mid] = {'score': (s1,s2), 'pens': (p1,p2), 'timestamp': datetime.now().isoformat()}
    if p1>0 or p2>0:
        st.session_state.results[mid] = [s1,s2,p1,p2]
    else:
        st.session_state.results[mid] = [s1,s2]
    st.session_state.match_meta[mid] = {'h_s':gs1,'a_s':gs2,'h_a':ha,'a_a':aa,'h_r':hr,'a_r':ar}
    process_player_string_update(gs1, h, 'G')
    process_player_string_update(gs2, a, 'G')
    process_player_string_update(ha, h, 'A')
    process_player_string_update(aa, a, 'A')
    process_player_string_update(hr, h, 'R')
    process_player_string_update(ar, a, 'R')

def get_cumulative_standings():
    standings = []
    for team in st.session_state.active_teams:
        if team in st.session_state.cumulative_stats:
            stats = st.session_state.cumulative_stats[team]
            standings.append({'Team':team,'P':stats.get('P',0),'W':stats.get('W',0),'D':stats.get('D',0),'L':stats.get('L',0),'GF':stats.get('GF',0),'GA':stats.get('GA',0),'GD':stats.get('GD',0),'Pts':stats.get('Pts',0)})
        else:
            standings.append({'Team':team,'P':0,'W':0,'D':0,'L':0,'GF':0,'GA':0,'GD':0,'Pts':0})
    return standings

def generate_balanced_fixtures_fixed(teams, matches_per_team):
    if len(teams) < 2: return []
    def round_robin(teams_list):
        if len(teams_list) % 2:
            teams_list.append(None)
        n = len(teams_list)
        fixtures = []
        for round_num in range(n-1):
            for i in range(n//2):
                if teams_list[i] is not None and teams_list[n-1-i] is not None:
                    fixtures.append((teams_list[i], teams_list[n-1-i]))
            teams_list.insert(1, teams_list.pop())
        return fixtures
    all_possible = list(itertools.combinations(teams,2))
    random.shuffle(all_possible)
    if matches_per_team <= len(teams)-1:
        fixtures = []
        for _ in range(matches_per_team):
            round_fixtures = round_robin(teams.copy())
            round_fixtures = [f for f in round_fixtures if f[0] is not None and f[1] is not None]
            fixtures.extend(round_fixtures)
        total_needed = (len(teams)*matches_per_team)//2
        if len(fixtures) >= total_needed:
            return fixtures[:total_needed]
    team_match_counts = {team:0 for team in teams}
    fixtures = []
    available_pairs = all_possible.copy()
    iterations = 0
    while available_pairs and min(team_match_counts.values()) < matches_per_team:
        iterations += 1
        if iterations > 2000: break
        for pair in available_pairs[:]:
            t1,t2 = pair
            if team_match_counts[t1] < matches_per_team and team_match_counts[t2] < matches_per_team:
                fixtures.append(pair)
                team_match_counts[t1] += 1
                team_match_counts[t2] += 1
                available_pairs.remove(pair)
                break
        else: break
    if min(team_match_counts.values()) < matches_per_team:
        needy = [t for t in teams if team_match_counts[t] < matches_per_team]
        for i in range(len(needy)):
            for j in range(i+1, len(needy)):
                t1,t2 = needy[i], needy[j]
                if not any((f[0]==t1 and f[1]==t2) or (f[0]==t2 and f[1]==t1) for f in fixtures) or len(fixtures) < len(teams):
                    fixtures.append((t1,t2))
                    team_match_counts[t1] += 1
                    team_match_counts[t2] += 1
    return fixtures

def generate_fixtures_for_phase(teams, phase):
    shuffled = teams.copy()
    random.shuffle(shuffled)
    if phase == "Phase 1: The Purge":
        return generate_balanced_fixtures_fixed(shuffled, 2)
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
        return [(second,third), (third,second)]
    elif phase == "Phase 4: The Grand Final":
        return [(shuffled[0], shuffled[1])]
    return []

def handle_battle_royale_elimination():
    standings = get_cumulative_standings()
    standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
    remaining = len(standings)
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
        champion = standings[0]['Team']
        st.session_state.champion = champion
        st.session_state.news.insert(0, f"🏆 {champion} is the BATTLE ROYALE CHAMPION!")
        st.session_state.battle_phase = "CHAMPION CROWNED"
        add_past_champion(champion, datetime.now().year, "Survival Mode (Battle Royale)")
        save_data_internal()
        safe_rerun()
        return
    if phase != st.session_state.battle_phase:
        st.session_state.battle_phase = phase
        st.session_state.news.insert(0, f"🔁 PHASE CHANGE: {phase}")
    eliminated_this_round = []
    if phase == "Phase 1: The Purge":
        bottom = standings[-2:]
        for team_data in bottom:
            team = team_data['Team']
            if team in st.session_state.active_teams:
                st.session_state.active_teams.remove(team)
                eliminated_this_round.append(team)
                st.session_state.eliminated_teams.append({'team':team,'round':st.session_state.round_number,'position':remaining-standings.index(team_data),'phase':phase})
        if eliminated_this_round:
            st.session_state.news.insert(0, f"💀 PURGED: {', '.join(eliminated_this_round)} eliminated!")
    elif phase == "Phase 2: The Squeeze":
        bottom_team = standings[-1]['Team']
        if bottom_team in st.session_state.active_teams:
            st.session_state.active_teams.remove(bottom_team)
            eliminated_this_round.append(bottom_team)
            st.session_state.eliminated_teams.append({'team':bottom_team,'round':st.session_state.round_number,'position':4,'phase':phase})
        if eliminated_this_round:
            st.session_state.news.insert(0, f"💀 SQUEEZED OUT: {bottom_team} eliminated!")
    elif phase == "Phase 3: The Standoff":
        if st.session_state.sudden_death_round >= 2:
            leader = standings[0]['Team']
            second = standings[1]['Team']
            third = standings[2]['Team']
            match1_id = f"{second}v{third}_0"
            match2_id = f"{third}v{second}_1"
            res1 = st.session_state.results.get(match1_id, [0,0])
            res2 = st.session_state.results.get(match2_id, [0,0])
            second_goals = res1[0] + res2[1]
            third_goals = res1[1] + res2[0]
            if second_goals > third_goals:
                loser = third
                winner = second
            elif third_goals > second_goals:
                loser = second
                winner = third
            else:
                if len(res1)>2 and len(res2)>2:
                    second_pens = res1[2] + res2[3]
                    third_pens = res1[3] + res2[2]
                    loser = third if second_pens > third_pens else second
                    winner = second if second_pens > third_pens else third
                else:
                    loser = third if standings[1]['Pts'] > standings[2]['Pts'] else second
            if loser in st.session_state.active_teams:
                st.session_state.active_teams.remove(loser)
                eliminated_this_round.append(loser)
                st.session_state.eliminated_teams.append({'team':loser,'round':st.session_state.round_number,'position':3,'phase':phase,'reason':'Lost Sudden Death Semi-Final'})
                st.session_state.news.insert(0, f"💀 SUDDEN DEATH: {loser} eliminated! {winner} advances to Final!")
            st.session_state.sudden_death_round = 0
            st.session_state.bye_team = None
    next_fixtures = generate_fixtures_for_phase(st.session_state.active_teams, phase)
    st.session_state.fixtures = next_fixtures
    st.session_state.round_number += 1
    if phase == "Phase 3: The Standoff" and not eliminated_this_round:
        st.session_state.sudden_death_round += 1
        if st.session_state.sudden_death_round == 1:
            st.session_state.current_round = f"SUDDEN DEATH • Leg 1 • {phase}"
        else:
            st.session_state.current_round = f"SUDDEN DEATH • Leg 2 • {phase}"
    else:
        st.session_state.current_round = f"Round {st.session_state.round_number} • {phase}"
    st.session_state.results = {}
    st.session_state.match_meta = {}
    st.session_state.fixed_results = {}
    st.session_state.captain_fixed_matches = {team: [] for team in st.session_state.active_teams}
    st.session_state.survival_history.append({'round':st.session_state.round_number-1,'phase':phase,'remaining':len(st.session_state.active_teams),'eliminated':eliminated_this_round})
    save_data_internal()
    safe_rerun()

def advance_knockout_tournament():
    current_matches_complete = True
    for i, match in enumerate(st.session_state.fixtures):
        if len(match) < 2: continue
        h,a = match[0], match[1]
        mid = f"{h}v{a}_{i}"
        if mid not in st.session_state.results:
            current_matches_complete = False
            break
    if not current_matches_complete:
        st.warning("Cannot advance: Some matches in current round don't have results!")
        return
    winners = []
    for i, match in enumerate(st.session_state.fixtures):
        if len(match) < 2: continue
        h,a = match[0], match[1]
        mid = f"{h}v{a}_{i}"
        res = st.session_state.results[mid]
        if len(res) >= 2:
            if res[0] > res[1]: winners.append(h)
            elif res[1] > res[0]: winners.append(a)
            else:
                if len(res) > 2:
                    if res[2] > res[3]: winners.append(h)
                    else: winners.append(a)
                else:
                    winners.append(random.choice([h,a]))
    if len(winners) == 1:
        champion = winners[0]
        st.session_state.champion = champion
        st.session_state.news.insert(0, f"🏆 {champion} is the CHAMPION!")
        st.session_state.current_round = "TOURNAMENT COMPLETE"
        add_past_champion(champion, datetime.now().year, st.session_state.format)
        save_data_internal()
        safe_rerun()
        return
    round_names = {8:"Quarter Finals",4:"Semi Finals",2:"Final"}
    next_round = round_names.get(len(winners), f"Round {st.session_state.knockout_round+1}")
    shuffled = winners.copy()
    random.shuffle(shuffled)
    next_fixtures = []
    for i in range(0, len(shuffled), 2):
        if i+1 < len(shuffled):
            next_fixtures.append((shuffled[i], shuffled[i+1]))
    st.session_state.fixtures = next_fixtures
    st.session_state.knockout_round += 1
    st.session_state.current_round = next_round
    st.session_state.results = {}
    st.session_state.match_meta = {}
    st.session_state.fixed_results = {}
    st.session_state.captain_fixed_matches = {team: [] for team in winners}
    if "World Cup" in st.session_state.format:
        stage_map = {"Round of 16":"Quarter Finals","Quarter Finals":"Semi Finals","Semi Finals":"Final"}
        if st.session_state.world_cup_stage in stage_map:
            st.session_state.world_cup_stage = stage_map[st.session_state.world_cup_stage]
    st.session_state.news.insert(0, f"⚽ Advancing to {next_round}!")
    save_data_internal()
    safe_rerun()

def advance_world_cup_knockout():
    if st.session_state.world_cup_stage != "Group Stage":
        return
    group_winners = []
    group_runners = []
    for group_name, teams in st.session_state.groups.items():
        group_standings = []
        for team in teams:
            stats = {'Team':team,'P':0,'W':0,'D':0,'L':0,'GF':0,'GA':0,'GD':0,'Pts':0}
            for mid, res in st.session_state.results.items():
                try:
                    if "_" in mid: base = mid.split('_')[0]
                    else: base = mid
                    if "v" not in base: continue
                    h,a = base.split('v')
                except: continue
                if h == team or a == team:
                    is_home = h==team
                    s_h,s_a = res[0],res[1]
                    stats['P']+=1
                    stats['GF']+= s_h if is_home else s_a
                    stats['GA']+= s_a if is_home else s_h
                    stats['GD']+= (s_h - s_a) if is_home else (s_a - s_h)
                    if is_home:
                        if s_h > s_a: stats['W']+=1; stats['Pts']+=3
                        elif s_a > s_h: stats['L']+=1
                        else: stats['D']+=1; stats['Pts']+=1
                    else:
                        if s_a > s_h: stats['W']+=1; stats['Pts']+=3
                        elif s_h > s_a: stats['L']+=1
                        else: stats['D']+=1; stats['Pts']+=1
            group_standings.append(stats)
        group_standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
        if len(group_standings) >= 2:
            group_winners.append(group_standings[0]['Team'])
            group_runners.append(group_standings[1]['Team'])
    knockout_teams = group_winners + group_runners
    random.shuffle(knockout_teams)
    def generate_knockout_bracket(teams, round_name):
        shuffled = teams.copy()
        random.shuffle(shuffled)
        bracket = {}
        matches = []
        for i in range(0, len(shuffled), 2):
            if i+1 < len(shuffled):
                match_id = f"{round_name}_match_{len(matches)}"
                bracket[match_id] = {'home':shuffled[i], 'away':shuffled[i+1], 'round':round_name, 'winner':None, 'result':None}
                matches.append((shuffled[i], shuffled[i+1]))
        return bracket, matches
    bracket, matches = generate_knockout_bracket(knockout_teams, "Round of 16")
    st.session_state.knockout_bracket = bracket
    st.session_state.fixtures = matches
    st.session_state.world_cup_stage = "Round of 16"
    st.session_state.current_round = "Round of 16"
    st.session_state.news.insert(0, "🏆 World Cup advances to Knockout Stage!")
    save_data_internal()

def add_team_with_captain(team_name):
    is_valid, error_msg = validate_team_name(team_name)
    if not is_valid:
        return error_msg, None, None
    if team_name and team_name not in st.session_state.teams:
        st.session_state.teams.append(team_name)
        st.session_state.team_badges[team_name] = random.choice(BADGE_POOL)
        pin = generate_pin()
        password = generate_team_password()
        st.session_state.captain_pins[team_name] = pin
        st.session_state.team_passwords[team_name] = hash_password(password)
        st.session_state.captain_fixed_matches[team_name] = []
        if st.session_state.started:
            st.session_state.active_teams.append(team_name)
            if team_name not in st.session_state.cumulative_stats:
                st.session_state.cumulative_stats[team_name] = {'P':0,'W':0,'D':0,'L':0,'GF':0,'GA':0,'GD':0,'Pts':0}
            # add fixtures for new team (simplified: just append random matches)
            other_teams = [t for t in st.session_state.active_teams if t != team_name]
            for opp in other_teams[:2]:  # just add a couple of fixtures to keep simple
                st.session_state.fixtures.append((team_name, opp))
        log_captain_action(f"Team '{team_name}' registered", team_name)
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

def submit_match_report(match_id, home_team, away_team, home_score, away_score, 
                        home_scorers="", away_scorers="", home_assists="", 
                        away_assists="", home_reds="", away_reds="", 
                        home_pens=0, away_pens=0, submitted_by="", comment=""):
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
        'status': 'pending',
        'comment': comment
    }
    existing = [r for r in st.session_state.pending_reports if r['match_id'] == match_id]
    if existing:
        st.session_state.pending_reports = [r for r in st.session_state.pending_reports if r['match_id'] != match_id]
    st.session_state.pending_reports.append(report)
    log_captain_action(f"Submitted match report: {home_team} {home_score}-{away_score} {away_team}", submitted_by)
    return report

def fix_match_result_by_captain(match_id, home_team, away_team, home_score, away_score,
                               home_scorers="", away_scorers="", home_assists="", 
                               away_assists="", home_reds="", away_reds="", 
                               home_pens=0, away_pens=0, fixed_by="", comment=""):
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
        'status': 'pending',
        'comment': comment
    }
    st.session_state.fixed_results[match_id] = fixed_result
    if fixed_by not in st.session_state.captain_fixed_matches:
        st.session_state.captain_fixed_matches[fixed_by] = []
    if match_id not in st.session_state.captain_fixed_matches[fixed_by]:
        st.session_state.captain_fixed_matches[fixed_by].append(match_id)
    report = submit_match_report(match_id, home_team, away_team, home_score, away_score,
                                home_scorers, away_scorers, home_assists, away_assists,
                                home_reds, away_reds, home_pens, away_pens, fixed_by, comment)
    log_captain_action(f"Fixed match result: {home_team} {home_score}-{away_score} {away_team} (Pending approval)", fixed_by)
    return fixed_result, report

def approve_match_report(report_id):
    report = next((r for r in st.session_state.pending_reports if r['report_id'] == report_id), None)
    if not report: return False
    mid = report['match_id']
    h,a = report['home_team'], report['away_team']
    s1,s2 = report['home_score'], report['away_score']
    p1,p2 = report['home_pens'], report['away_pens']
    st.session_state.admin_approved_results[mid] = True
    update_match_result_safely(mid, h, a, s1, s2, p1, p2,
                              report['home_scorers'], report['away_scorers'],
                              report['home_assists'], report['away_assists'],
                              report['home_reds'], report['away_reds'])
    st.session_state.pending_reports = [r for r in st.session_state.pending_reports if r['report_id'] != report_id]
    if mid in st.session_state.fixed_results:
        del st.session_state.fixed_results[mid]
    st.session_state.news.insert(0, f"✅ {h} {s1}-{s2} {a} (Report approved)")
    log_captain_action(f"Approved match report: {h} {s1}-{s2} {a}")
    return True

def reject_match_report(report_id):
    report = next((r for r in st.session_state.pending_reports if r['report_id'] == report_id), None)
    if not report: return False
    st.session_state.pending_reports = [r for r in st.session_state.pending_reports if r['report_id'] != report_id]
    if report['match_id'] in st.session_state.fixed_results:
        del st.session_state.fixed_results[report['match_id']]
    log_captain_action(f"Rejected match report: {report['home_team']} {report['home_score']}-{report['away_score']} {report['away_team']}")
    return True

def reset_match_result(match_id):
    if match_id in st.session_state.results:
        try:
            if "_" in match_id: base = match_id.split('_')[0]
            else: base = match_id
            if "v" not in base: return False
            h,a = base.split('v')
        except: return False
        del st.session_state.results[match_id]
        if match_id in st.session_state.match_meta: del st.session_state.match_meta[match_id]
        if match_id in st.session_state.match_history: del st.session_state.match_history[match_id]
        if match_id in st.session_state.fixed_results: del st.session_state.fixed_results[match_id]
        if match_id in st.session_state.admin_approved_results: del st.session_state.admin_approved_results[match_id]
        for team in st.session_state.captain_fixed_matches:
            if match_id in st.session_state.captain_fixed_matches[team]:
                st.session_state.captain_fixed_matches[team].remove(match_id)
        st.session_state.news.insert(0, f"🔄 Match reset: {h} vs {a}")
        log_captain_action(f"Reset match: {h} vs {a}")
        return True
    return False

def add_past_champion(champion_name, year=None, tournament_format=None):
    if not champion_name: return False
    if not year: year = datetime.now().year
    if not tournament_format: tournament_format = st.session_state.format
    champion_entry = {'champion':champion_name,'year':year,'format':tournament_format,'added_at':datetime.now().isoformat()}
    st.session_state.past_champions.append(champion_entry)
    st.session_state.champion_history[str(year)] = {'champion':champion_name,'format':tournament_format}
    st.session_state.past_champions.sort(key=lambda x: x['year'], reverse=True)
    log_captain_action(f"Added past champion: {champion_name} ({year})")
    return True

def remove_past_champion(index):
    if 0 <= index < len(st.session_state.past_champions):
        removed = st.session_state.past_champions.pop(index)
        year_key = str(removed['year'])
        if year_key in st.session_state.champion_history:
            del st.session_state.champion_history[year_key]
        log_captain_action(f"Removed past champion: {removed['champion']} ({removed['year']})")
        return True
    return False

def delete_team(team_name):
    if team_name in st.session_state.teams:
        st.session_state.teams.remove(team_name)
        if team_name in st.session_state.active_teams:
            st.session_state.active_teams.remove(team_name)
        for group in st.session_state.groups:
            if team_name in st.session_state.groups[group]:
                st.session_state.groups[group].remove(team_name)
        for key in ['team_badges','captain_pins','team_passwords','cumulative_stats','captain_fixed_matches']:
            if team_name in st.session_state.get(key, {}):
                del st.session_state[key][team_name]
        to_remove = []
        for pid in st.session_state.cumulative_player_stats:
            if f"|{team_name}" in pid:
                to_remove.append(pid)
        for pid in to_remove:
            del st.session_state.cumulative_player_stats[pid]
        st.session_state.eliminated_teams = [e for e in st.session_state.eliminated_teams if e['team'] != team_name]
        # regenerate fixtures? we'll just call a function to rebuild
        if st.session_state.started:
            # simple: clear and regenerate based on format
            if "League" in st.session_state.format:
                matches = list(itertools.permutations(st.session_state.active_teams, 2))
                random.shuffle(matches)
                st.session_state.fixtures = matches
            elif "World Cup" in st.session_state.format:
                # redo groups
                shuffled = st.session_state.active_teams.copy()
                random.shuffle(shuffled)
                groups = {}
                group_names = "ABCDEFGHIJKLMNOP"
                group_size = 4
                for i, team in enumerate(shuffled):
                    group_idx = i//group_size
                    if group_idx >= len(group_names): group_idx = len(group_names)-1
                    gname = group_names[group_idx]
                    groups.setdefault(gname, []).append(team)
                st.session_state.groups = groups
                matches = []
                for g, teams in groups.items():
                    matches.extend(list(itertools.combinations(teams,2)))
                st.session_state.fixtures = matches
            elif "Knockout" in st.session_state.format:
                shuffled = st.session_state.active_teams.copy()
                random.shuffle(shuffled)
                if len(shuffled)%2 != 0: shuffled.append("BYE")
                matches = []
                for i in range(0, len(shuffled), 2):
                    if i+1<len(shuffled) and shuffled[i]!="BYE" and shuffled[i+1]!="BYE":
                        matches.append((shuffled[i], shuffled[i+1]))
                st.session_state.fixtures = matches
            elif "Survival" in st.session_state.format:
                matches = generate_fixtures_for_phase(st.session_state.active_teams, st.session_state.battle_phase)
                st.session_state.fixtures = matches
        st.session_state.news.insert(0, f"🗑️ Team '{team_name}' deleted")
        save_data_internal()
        return True
    return False

def regenerate_fixtures():
    if not st.session_state.started or not st.session_state.active_teams: return
    if "Survival" in st.session_state.format:
        fixtures = generate_fixtures_for_phase(st.session_state.active_teams, st.session_state.battle_phase)
        st.session_state.fixtures = fixtures
    elif "League" in st.session_state.format:
        matches = list(itertools.permutations(st.session_state.active_teams, 2))
        random.shuffle(matches)
        st.session_state.fixtures = matches
    elif "World Cup" in st.session_state.format and st.session_state.world_cup_stage == "Group Stage":
        shuffled = st.session_state.active_teams.copy()
        random.shuffle(shuffled)
        groups = {}
        group_names = "ABCDEFGHIJKLMNOP"
        group_size = 4
        for i, team in enumerate(shuffled):
            group_idx = i//group_size
            if group_idx >= len(group_names): group_idx = len(group_names)-1
            gname = group_names[group_idx]
            groups.setdefault(gname, []).append(team)
        st.session_state.groups = groups
        matches = []
        for g, teams in groups.items():
            matches.extend(list(itertools.combinations(teams,2)))
        st.session_state.fixtures = matches
    elif "Knockout" in st.session_state.format:
        shuffled = st.session_state.active_teams.copy()
        random.shuffle(shuffled)
        if len(shuffled)%2 != 0: shuffled.append("BYE")
        matches = []
        for i in range(0, len(shuffled), 2):
            if i+1<len(shuffled) and shuffled[i]!="BYE" and shuffled[i+1]!="BYE":
                matches.append((shuffled[i], shuffled[i+1]))
        st.session_state.fixtures = matches

def download_backup():
    data = {k: st.session_state[k] for k in st.session_state.keys()}
    json_str = json.dumps(data, indent=2, default=str)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="dls_ultra_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json" class="stButton">📥 DOWNLOAD BACKUP</a>'
    return href

def restore_backup(uploaded_file):
    try:
        data = json.load(uploaded_file)
        required = ['teams','format','current_round','fixtures']
        for r in required:
            if r not in data: raise ValueError(f"Missing {r}")
        st.session_state.clear()
        for k,v in data.items():
            st.session_state[k] = v
        save_data_internal()
        return True, "Backup restored successfully!"
    except Exception as e:
        return False, f"Error restoring backup: {str(e)}"

def factory_reset():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_defaults()
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    return True

def get_match_result_status(match_id):
    if match_id in st.session_state.admin_approved_results: return "approved"
    elif match_id in st.session_state.fixed_results: return "pending"
    elif match_id in st.session_state.results: return "completed"
    else: return "not_played"

# --- NEW FEATURE: Helper functions ---
def find_matches_for_team(team_name):
    matches = []
    for i, fix in enumerate(st.session_state.fixtures):
        if len(fix) < 2: continue
        h,a = fix[0], fix[1]
        if team_name in [h,a]:
            mid = f"{h}v{a}_{i}"
            matches.append({"index":i,"home":h,"away":a,"match_id":mid,"status":get_match_result_status(mid)})
    return matches

def debug_captain_view(captain_team):
    debug_info = {"captain_team":captain_team,"active_teams":st.session_state.active_teams,"fixtures_count":len(st.session_state.fixtures),"captain_fixtures":[]}
    for i,fix in enumerate(st.session_state.fixtures):
        if len(fix) < 2: continue
        h,a = fix[0], fix[1]
        if captain_team in [h,a]:
            mid = f"{h}v{a}_{i}"
            debug_info["captain_fixtures"].append({"match_id":mid,"home":h,"away":a,"index":i,"in_active_teams": h in st.session_state.active_teams and a in st.session_state.active_teams})
    return debug_info

# --- NEW: Admin batch approve ---
def batch_approve_reports():
    for report in st.session_state.pending_reports:
        approve_match_report(report['report_id'])
    save_data_internal()

# --- NEW: Points progression chart ---
def get_points_progression(team):
    # Build progression from match history (sorted by timestamp)
    if not st.session_state.match_history:
        return []
    matches_for_team = []
    for mid, info in st.session_state.match_history.items():
        try:
            if "_" in mid: base = mid.split('_')[0]
            else: base = mid
            if "v" not in base: continue
            h,a = base.split('v')
            if team not in [h,a]: continue
            timestamp = info['timestamp']
            score = info['score']
            is_home = (team == h)
            s_team = score[0] if is_home else score[1]
            s_opp = score[1] if is_home else score[0]
            points = 3 if s_team > s_opp else (1 if s_team == s_opp else 0)
            matches_for_team.append((timestamp, points))
        except:
            continue
    matches_for_team.sort(key=lambda x: x[0])
    cumulative = []
    running = 0
    for _, pts in matches_for_team:
        running += pts
        cumulative.append(running)
    return cumulative

def show_team_charts():
    if not st.session_state.active_teams:
        st.info("No active teams.")
        return
    if not plotly_available:
        st.warning("Plotly not installed. Install with `pip install plotly` to see charts.")
        return
    team_choice = st.selectbox("Select team", st.session_state.active_teams)
    progression = get_points_progression(team_choice)
    if progression:
        fig = px.line(x=list(range(1,len(progression)+1)), y=progression, title=f"{team_choice} - Points Progression", labels={'x':'Matches Played','y':'Cumulative Points'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No match history for this team yet.")

# --- NEW: Advanced player rankings ---
def advanced_player_rankings():
    if not st.session_state.cumulative_player_stats:
        st.info("No player stats recorded.")
        return
    data = []
    for pid, stats in st.session_state.cumulative_player_stats.items():
        g = stats.get('G',0)
        a = stats.get('A',0)
        gp = stats.get('GP',0)  # not stored per player, but we can compute from team matches? skip for now.
        mvp = (g * 1.5) + a
        data.append({
            "Player": stats['Name'],
            "Team": stats['Team'],
            "Goals": g,
            "Assists": a,
            "MVP Index": round(mvp, 1)
        })
    df = pd.DataFrame(data)
    if not df.empty:
        st.subheader("⚡ MVP Index (Goals × 1.5 + Assists)")
        top_mvp = df.sort_values("MVP Index", ascending=False).head(10)
        st.dataframe(top_mvp, hide_index=True, use_container_width=True)
        st.subheader("⚽ Goals per Game")
        # approximate: if we had GP we'd compute; we can skip or compute from team matches played
        st.info("Goals per Game requires matches played per player – will be added in future.")
    else:
        st.info("No data.")

# --- NEW: Match Schedule Calendar ---
def match_schedule_calendar():
    if not st.session_state.fixtures:
        st.info("No fixtures.")
        return
    schedule_data = []
    for idx, fix in enumerate(st.session_state.fixtures):
        if len(fix) < 2: continue
        h,a = fix[0], fix[1]
        mid = f"{h}v{a}_{idx}"
        status = get_match_result_status(mid)
        schedule_data.append({
            "Home": h,
            "Away": a,
            "Status": status.capitalize(),
            "Match ID": mid
        })
    df = pd.DataFrame(schedule_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    # filter by team
    all_teams = list(set([f[0] for f in st.session_state.fixtures if len(f)>=2] + [f[1] for f in st.session_state.fixtures if len(f)>=2]))
    filter_team = st.selectbox("Filter by team", ["All"] + all_teams)
    if filter_team != "All":
        df = df[(df['Home'] == filter_team) | (df['Away'] == filter_team)]
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- NEW: Admin quick actions ---
def admin_quick_actions():
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Batch Approve All Reports"):
            batch_approve_reports()
            st.success("All pending reports approved!")
            safe_rerun()
    with col2:
        if st.button("🔄 Regenerate Fixtures"):
            regenerate_fixtures()
            save_data_internal()
            st.success("Fixtures regenerated!")
            safe_rerun()
    st.markdown("#### Reset a specific match")
    if st.session_state.fixtures:
        match_options = []
        for i, fix in enumerate(st.session_state.fixtures):
            if len(fix) >= 2:
                mid = f"{fix[0]}v{fix[1]}_{i}"
                match_options.append(mid)
        selected_match = st.selectbox("Select match ID", match_options)
        if st.button("Reset Selected Match"):
            if reset_match_result(selected_match):
                save_data_internal()
                st.success("Match reset!")
                safe_rerun()
            else:
                st.error("Could not reset match.")
    else:
        st.info("No fixtures to reset.")

# Initialize session state
if 'data_loaded' not in st.session_state:
    load_data()
    st.session_state.data_loaded = True
if 'admin_pin_verified' not in st.session_state:
    st.session_state.admin_pin_verified = False
if 'admin_unlock' not in st.session_state:
    st.session_state.admin_unlock = False
init_defaults()

# --- HEADER ---
st.markdown('<div class="big-title">DLS ULTRA</div>', unsafe_allow_html=True)
if st.session_state.champion:
    st.markdown(f'<div style="text-align: center; color:#3b82f6; font-size: 1.8rem; font-weight: bold;">👑 CHAMPION: {st.session_state.champion} 👑</div>', unsafe_allow_html=True)
else:
    subtitle = f"{st.session_state.current_round}"
    if "Survival" in st.session_state.format:
        phase_badge = ""
        if "Phase 1" in st.session_state.battle_phase: phase_badge = "THE PURGE"
        elif "Phase 2" in st.session_state.battle_phase: phase_badge = "THE SQUEEZE"
        elif "Phase 3" in st.session_state.battle_phase: phase_badge = "THE STANDOFF"
        elif "Phase 4" in st.session_state.battle_phase: phase_badge = "GRAND FINAL"
        subtitle = f"Round {st.session_state.round_number} • {st.session_state.battle_phase} {phase_badge}"
    st.markdown(f'<div style="text-align: center; color: #94a3b8; margin-bottom: 1rem;">{subtitle}</div>', unsafe_allow_html=True)

# --- SIDEBAR (User Mode + controls) ---
with st.sidebar:
    st.markdown("### 👤 USER MODE")
    user_mode = st.radio("Select Mode", ["Admin", "Captain"], key="user_mode_selector", index=0 if st.session_state.user_mode == "Admin" else 1)
    if user_mode != st.session_state.user_mode:
        st.session_state.user_mode = user_mode
        if user_mode == "Admin":
            st.session_state.logged_in_captain = None
            st.session_state.captain_pin_verified = False
        save_data_internal()
        safe_rerun()
    st.markdown("---")
    
    if st.session_state.user_mode == "Admin":
        if not st.session_state.admin_pin_verified:
            pin = st.text_input("ENTER ADMIN PIN", type="password", key="pin_input")
            if st.button("🔓 Unlock", key="pin_unlock_btn"):
                if pin == "0209":
                    st.session_state.admin_pin_verified = True
                    st.session_state.admin_unlock = True
                    st.success("Admin access granted!")
                    safe_rerun()
                else:
                    st.error("Incorrect PIN!")
            st.info("Enter PIN for ADMIN access")
        else:
            st.success("✅ ADMIN ACCESS")
            pending_count = len(st.session_state.pending_reports)
            if pending_count:
                st.warning(f"🔔 {pending_count} pending report(s)")
            st.markdown("### 🏆 TEAM EDITOR")
            with st.expander("➕ ADD CLUB"):
                new_team = st.text_input("Team Name")
                if st.button("➕ ADD TEAM"):
                    if new_team and new_team not in st.session_state.teams:
                        msg, pin, pwd = add_team_with_captain(new_team)
                        if msg:
                            save_data_internal()
                            st.success(f"Team '{new_team}' added!")
                            with st.expander("✅ CREDENTIALS - SAVE THESE!", expanded=True):
                                st.markdown(msg)
                            safe_rerun()
                        else:
                            st.error("Invalid team name")
                    else:
                        st.error("Team exists or invalid")
            with st.expander("🗑️ DELETE CLUB"):
                if st.session_state.teams:
                    team_to_delete = st.selectbox("Select team", ["Select..."] + st.session_state.teams)
                    if team_to_delete != "Select..." and st.button("🗑️ DELETE"):
                        if delete_team(team_to_delete):
                            save_data_internal()
                            st.success(f"Deleted {team_to_delete}")
                            safe_rerun()
            with st.expander("🔄 RESET TOURNAMENT"):
                st.warning("Reset all stats but keep teams")
                if st.button("🔄 RESET ALL STATS"):
                    st.session_state.results = {}
                    st.session_state.match_meta = {}
                    st.session_state.match_history = {}
                    st.session_state.cumulative_stats = {t:{'P':0,'W':0,'D':0,'L':0,'GF':0,'GA':0,'GD':0,'Pts':0} for t in st.session_state.teams}
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
                    st.session_state.captain_fixed_matches = {t:[] for t in st.session_state.teams}
                    st.session_state.admin_approved_results = {}
                    if st.session_state.started:
                        # regenerate fixtures based on current format
                        if "Survival" in st.session_state.format:
                            st.session_state.fixtures = generate_fixtures_for_phase(st.session_state.teams, "Phase 1: The Purge")
                        elif "League" in st.session_state.format:
                            st.session_state.fixtures = list(itertools.permutations(st.session_state.teams,2))
                            random.shuffle(st.session_state.fixtures)
                        elif "World Cup" in st.session_state.format:
                            # rebuild groups
                            shuffled = st.session_state.teams.copy()
                            random.shuffle(shuffled)
                            groups = {}
                            group_names = "ABCDEFGHIJKLMNOP"
                            group_size = 4
                            for i,team in enumerate(shuffled):
                                group_idx = i//group_size
                                if group_idx >= len(group_names): group_idx = len(group_names)-1
                                gname = group_names[group_idx]
                                groups.setdefault(gname, []).append(team)
                            st.session_state.groups = groups
                            matches = []
                            for g,teams in groups.items():
                                matches.extend(list(itertools.combinations(teams,2)))
                            st.session_state.fixtures = matches
                        elif "Knockout" in st.session_state.format:
                            shuffled = st.session_state.teams.copy()
                            random.shuffle(shuffled)
                            if len(shuffled)%2 != 0: shuffled.append("BYE")
                            matches = []
                            for i in range(0,len(shuffled),2):
                                if i+1<len(shuffled) and shuffled[i]!="BYE" and shuffled[i+1]!="BYE":
                                    matches.append((shuffled[i], shuffled[i+1]))
                            st.session_state.fixtures = matches
                    save_data_internal()
                    st.success("All stats reset!")
                    safe_rerun()
            st.markdown("---")
            st.markdown("### 🧢 CAPTAIN CONTROLS")
            with st.expander("🔑 VIEW ALL CAPTAIN PINS"):
                if st.session_state.teams:
                    pins_df = pd.DataFrame([{"Team":t,"PIN":st.session_state.captain_pins.get(t,"")} for t in st.session_state.teams])
                    st.dataframe(pins_df, hide_index=True)
            with st.expander("🔄 RESET CAPTAIN PIN"):
                team_reset = st.selectbox("Select team", st.session_state.teams)
                if st.button("Generate New PIN"):
                    new_pin = generate_pin()
                    st.session_state.captain_pins[team_reset] = new_pin
                    save_data_internal()
                    st.success(f"New PIN for {team_reset}: `{new_pin}`")
            st.markdown("---")
            st.markdown("### ⚙️ TOURNAMENT CONTROLS")
            if st.session_state.started and not st.session_state.champion:
                if "World Cup" in st.session_state.format:
                    if st.session_state.world_cup_stage == "Group Stage":
                        if st.button("🏆 ADVANCE TO KNOCKOUT STAGE"):
                            advance_world_cup_knockout()
                    else:
                        if st.button("⚽ ADVANCE TO NEXT ROUND"):
                            advance_knockout_tournament()
                elif "Knockout" in st.session_state.format:
                    if st.button("⚽ ADVANCE TO NEXT ROUND"):
                        advance_knockout_tournament()
                elif "Survival" in st.session_state.format:
                    if st.button("⏩ EXECUTE ELIMINATION"):
                        handle_battle_royale_elimination()
            st.markdown("### 💾 DATA MANAGEMENT")
            st.markdown(download_backup(), unsafe_allow_html=True)
            uploaded = st.file_uploader("Restore backup", type=['json'])
            if uploaded and st.button("Restore"):
                ok, msg = restore_backup(uploaded)
                if ok: st.success(msg); safe_rerun()
                else: st.error(msg)
            with st.expander("⚙️ FACTORY RESET"):
                st.error("⚠️ DANGER ZONE")
                confirm = st.text_input("Type 'DELETE ALL' to confirm")
                if st.button("💣 FACTORY RESET"):
                    if confirm == "DELETE ALL":
                        factory_reset()
                        st.success("All data reset!")
                        safe_rerun()
            st.markdown("### 🐛 DEBUG")
            if st.button("Refresh View"):
                safe_rerun()
            if st.button("🔒 LOGOUT"):
                st.session_state.admin_pin_verified = False
                st.session_state.admin_unlock = False
                safe_rerun()
    else:  # Captain mode
        if not st.session_state.captain_pin_verified:
            available_teams = st.session_state.teams
            if available_teams:
                selected_team = st.selectbox("SELECT YOUR TEAM", ["Select..."] + available_teams)
                if selected_team != "Select...":
                    pin_input = st.text_input("ENTER CAPTAIN PIN", type="password")
                    if st.button("LOGIN"):
                        if selected_team in st.session_state.captain_pins and pin_input == st.session_state.captain_pins[selected_team]:
                            st.session_state.logged_in_captain = selected_team
                            st.session_state.captain_pin_verified = True
                            log_captain_action("Logged in as captain", selected_team)
                            save_data_internal()
                            st.success(f"Welcome, Captain of {selected_team}!")
                            safe_rerun()
                        else:
                            st.error("Incorrect PIN!")
            else:
                st.info("No teams registered yet.")
        else:
            st.success(f"Logged in as: {st.session_state.logged_in_captain}")
            if st.button("🚪 LOGOUT"):
                log_captain_action("Logged out", st.session_state.logged_in_captain)
                st.session_state.logged_in_captain = None
                st.session_state.captain_pin_verified = False
                st.session_state.user_mode = "Admin"
                save_data_internal()
                safe_rerun()

# --- MAIN INTERFACE (if tournament started) ---
if not st.session_state.started:
    # PRE-SEASON LOBBY
    st.markdown("<div class='glass-card' style='text-align:center'><h2>🧢 TOURNAMENT LOBBY</h2><p>Register your team before the season starts</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"""
        <div class='glass-card' style='text-align:center'>
            <h3>📋 TOURNAMENT INFO</h3>
            <p><strong>Tournament Code:</strong> <code>{st.session_state.tournament_code}</code></p>
            <p>Share this code with your friends to join!</p>
        </div>
        """, unsafe_allow_html=True)
    if st.session_state.past_champions:
        st.markdown("### 🏆 PAST CHAMPIONS")
        cols = st.columns(min(4, len(st.session_state.past_champions)))
        for idx, champ in enumerate(st.session_state.past_champions[:4]):
            with cols[idx % len(cols)]:
                st.markdown(f"""
                <div class="glass-card" style="text-align:center">
                    <div class="champion-year">{champ['year']}</div>
                    <div class="champion-name">{champ['champion']}</div>
                    <div class="champion-format">{champ['format']}</div>
                </div>
                """, unsafe_allow_html=True)
    st.markdown("### 🏆 REGISTER YOUR TEAM")
    reg_col1, reg_col2 = st.columns(2)
    with reg_col1:
        st.markdown("""
        #### 📝 HOW TO JOIN:
        1. Enter Tournament Code
        2. Choose Team Name
        3. Click REGISTER
        4. SAVE YOUR CREDENTIALS!
        """)
    with reg_col2:
        entered_code = st.text_input("ENTER TOURNAMENT CODE", key="tournament_code_input")
        if entered_code == st.session_state.tournament_code or st.session_state.admin_unlock:
            new_team_name = st.text_input("TEAM NAME")
            if st.button("🚀 REGISTER TEAM"):
                if new_team_name and new_team_name not in st.session_state.teams:
                    msg, pin, pwd = add_team_with_captain(new_team_name)
                    if msg and pin:
                        save_data_internal()
                        with st.expander("✅ REGISTRATION SUCCESSFUL - SAVE THESE!", expanded=True):
                            st.markdown(msg)
                        st.success(f"Team '{new_team_name}' registered!")
                        safe_rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Team name taken or invalid")
        elif entered_code:
            st.error("Incorrect tournament code!")
    if st.session_state.teams:
        st.markdown("### 📊 REGISTERED TEAMS")
        cols = st.columns(4)
        for i, t in enumerate(st.session_state.teams):
            b = st.session_state.team_badges.get(t, "🛡️")
            with cols[i % 4]:
                pin = st.session_state.captain_pins.get(t, "N/A")
                masked = pin[:2] + "••" if len(pin) > 2 else "••••"
                st.markdown(f"""
                <div class='glass-card' style='text-align:center'>
                    <div class="team-badge">{b}</div>
                    <h4>{t}</h4>
                    <small>PIN: {masked}</small>
                </div>
                """, unsafe_allow_html=True)
    if st.session_state.admin_unlock:
        st.markdown("---")
        st.markdown("### ⚙️ ADMIN CONTROLS")
        fmt = st.radio("SELECT TOURNAMENT FORMAT", ["Home & Away League", "World Cup (Groups + Knockout)", "Classic Knockout", "Survival Mode (Battle Royale)"], horizontal=True)
        if st.button("🚀 START SEASON"):
            if len(st.session_state.teams) < 2:
                st.error("Need at least 2 teams")
            else:
                st.session_state.format = fmt
                st.session_state.active_teams = st.session_state.teams.copy()
                st.session_state.captain_fixed_matches = {t:[] for t in st.session_state.teams}
                if "Survival" in fmt:
                    st.session_state.current_round = "Round 1"
                    st.session_state.eliminated_teams = []
                    st.session_state.round_number = 1
                    st.session_state.survival_history = []
                    st.session_state.battle_phase = "Phase 1: The Purge"
                    st.session_state.bye_team = None
                    st.session_state.cumulative_stats = {t:{'P':0,'W':0,'D':0,'L':0,'GF':0,'GA':0,'GD':0,'Pts':0} for t in st.session_state.teams}
                    st.session_state.cumulative_player_stats = {}
                    st.session_state.sudden_death_round = 0
                    st.session_state.fixtures = generate_fixtures_for_phase(st.session_state.teams, "Phase 1: The Purge")
                    st.session_state.current_round = f"Round 1 • {st.session_state.battle_phase}"
                elif "League" in fmt:
                    matches = list(itertools.permutations(st.session_state.teams,2))
                    random.shuffle(matches)
                    st.session_state.fixtures = matches
                    st.session_state.current_round = "League Phase"
                elif "World Cup" in fmt:
                    shuffled = st.session_state.teams.copy()
                    random.shuffle(shuffled)
                    groups = {}
                    group_names = "ABCDEFGHIJKLMNOP"
                    group_size = 4
                    for i,team in enumerate(shuffled):
                        group_idx = i//group_size
                        if group_idx >= len(group_names): group_idx = len(group_names)-1
                        gname = group_names[group_idx]
                        groups.setdefault(gname, []).append(team)
                    st.session_state.groups = groups
                    matches = []
                    for g,teams in groups.items():
                        matches.extend(list(itertools.combinations(teams,2)))
                    st.session_state.fixtures = matches
                    st.session_state.world_cup_stage = "Group Stage"
                    st.session_state.current_round = "Group Stage"
                elif "Knockout" in fmt:
                    shuffled = st.session_state.teams.copy()
                    random.shuffle(shuffled)
                    if len(shuffled)%2 != 0: shuffled.append("BYE")
                    matches = []
                    for i in range(0,len(shuffled),2):
                        if i+1<len(shuffled) and shuffled[i]!="BYE" and shuffled[i+1]!="BYE":
                            matches.append((shuffled[i], shuffled[i+1]))
                    st.session_state.fixtures = matches
                    st.session_state.knockout_round = 1
                    st.session_state.current_round = "Round 1"
                st.session_state.started = True
                save_data_internal()
                st.balloons()
                safe_rerun()
else:
    # Season in progress
    # Live Activity Feed (NEW)
    with st.expander("📢 LIVE ACTIVITY FEED", expanded=False):
        if st.button("🔄 Refresh Feed"):
            safe_rerun()
        for news_item in st.session_state.news[:15]:
            st.markdown(f"<div class='info-box'>{news_item}</div>", unsafe_allow_html=True)
    # Determine tabs
    if "World Cup" in st.session_state.format and st.session_state.world_cup_stage == "Group Stage":
        tab_names = ["🏆 GROUPS", "⚽ MATCH CENTER", "⭐ STATS", "📊 TOURNAMENT INFO", "🏅 HALL OF FAME", "📈 CHARTS", "📅 SCHEDULE", "⚡ QUICK ACTIONS"]
    elif "World Cup" in st.session_state.format:
        tab_names = ["📊 KNOCKOUT", "⚽ MATCH CENTER", "⭐ STATS", "📊 TOURNAMENT INFO", "🏅 HALL OF FAME", "📈 CHARTS", "📅 SCHEDULE", "⚡ QUICK ACTIONS"]
    elif "Knockout" in st.session_state.format:
        tab_names = ["📊 BRACKET", "⚽ MATCH CENTER", "⭐ STATS", "📊 TOURNAMENT INFO", "🏅 HALL OF FAME", "📈 CHARTS", "📅 SCHEDULE", "⚡ QUICK ACTIONS"]
    elif "Survival" in st.session_state.format:
        tab_names = ["📊 CUMULATIVE TABLE", "⚽ MATCH CENTER", "⭐ STATS", "💀 BATTLE INFO", "🏅 HALL OF FAME", "📈 CHARTS", "📅 SCHEDULE", "⚡ QUICK ACTIONS"]
    else:
        tab_names = ["📊 LEAGUE TABLE", "⚽ MATCH CENTER", "⭐ STATS", "📊 TOURNAMENT INFO", "🏅 HALL OF FAME", "📈 CHARTS", "📅 SCHEDULE", "⚡ QUICK ACTIONS"]
    tabs = st.tabs(tab_names)
    
    # TAB 0: Tables/Brackets (same as before but simplified)
    with tabs[0]:
        if "World Cup" in st.session_state.format and st.session_state.world_cup_stage == "Group Stage":
            for group_name, teams in st.session_state.groups.items():
                with st.expander(f"Group {group_name}", expanded=True):
                    standings = []
                    for team in teams:
                        stats = {'Team':team,'P':0,'W':0,'D':0,'L':0,'GF':0,'GA':0,'GD':0,'Pts':0}
                        for mid, res in st.session_state.results.items():
                            try:
                                if "_" in mid: base = mid.split('_')[0]
                                else: base = mid
                                if "v" not in base: continue
                                h,a = base.split('v')
                            except: continue
                            if h==team or a==team:
                                other = a if h==team else h
                                if other not in teams: continue
                                is_home = h==team
                                s_h,s_a = res[0],res[1]
                                stats['P']+=1
                                stats['GF']+= s_h if is_home else s_a
                                stats['GA']+= s_a if is_home else s_h
                                stats['GD']+= (s_h - s_a) if is_home else (s_a - s_h)
                                if is_home:
                                    if s_h > s_a: stats['W']+=1; stats['Pts']+=3
                                    elif s_a > s_h: stats['L']+=1
                                    else: stats['D']+=1; stats['Pts']+=1
                                else:
                                    if s_a > s_h: stats['W']+=1; stats['Pts']+=3
                                    elif s_h > s_a: stats['L']+=1
                                    else: stats['D']+=1; stats['Pts']+=1
                        standings.append(stats)
                    standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
                    df = pd.DataFrame(standings)
                    df['Badge'] = df['Team'].apply(lambda t: st.session_state.team_badges.get(t, "🛡️"))
                    st.dataframe(df[['Badge','Team','P','W','D','L','GF','GA','GD','Pts']], hide_index=True)
        elif "Knockout" in st.session_state.format or "World Cup" in st.session_state.format:
            st.markdown("### KNOCKOUT BRACKET")
            for i, match in enumerate(st.session_state.fixtures):
                if len(match) < 2: continue
                h,a = match[0],match[1]
                mid = f"{h}v{a}_{i}"
                status = get_match_result_status(mid)
                score_str = "Not played"
                if status == "approved" and mid in st.session_state.results:
                    res = st.session_state.results[mid]
                    score_str = f"{res[0]} - {res[1]}"
                    if len(res)>2: score_str += f" (P: {res[2]}-{res[3]})"
                elif status == "pending":
                    score_str = "Pending"
                st.markdown(f"<div class='match-card'><b>{h}</b> vs <b>{a}</b> – {score_str}</div>", unsafe_allow_html=True)
        elif "Survival" in st.session_state.format:
            standings = get_cumulative_standings()
            standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
            df = pd.DataFrame(standings)
            df['Badge'] = df['Team'].apply(lambda t: st.session_state.team_badges.get(t,"🛡️"))
            st.dataframe(df[['Badge','Team','P','W','D','L','GF','GA','GD','Pts']], hide_index=True)
            if st.session_state.eliminated_teams:
                with st.expander("Eliminated Teams"):
                    elim_df = pd.DataFrame(st.session_state.eliminated_teams)
                    st.dataframe(elim_df[['team','round','phase','position']], hide_index=True)
        else:  # League
            standings = get_cumulative_standings()
            standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
            df = pd.DataFrame(standings)
            df['Badge'] = df['Team'].apply(lambda t: st.session_state.team_badges.get(t,"🛡️"))
            st.dataframe(df[['Badge','Team','P','W','D','L','GF','GA','GD','Pts']], hide_index=True)
    
    # TAB 1: MATCH CENTER (with captain fixing and admin approval)
    with tabs[1]:
        if st.session_state.user_mode == "Captain" and st.session_state.captain_pin_verified:
            captain_team = st.session_state.logged_in_captain
            st.markdown(f"### ⚽ Your Matches – {captain_team}")
            if captain_team not in st.session_state.teams:
                st.error("Your team has been deleted.")
            elif captain_team not in st.session_state.active_teams and captain_team not in [e['team'] for e in st.session_state.eliminated_teams]:
                st.error("Your team is no longer in the tournament.")
            else:
                matches = find_matches_for_team(captain_team)
                if not matches:
                    st.info("No matches found. Try refreshing.")
                    if st.button("Refresh matches"):
                        safe_rerun()
                for m in matches:
                    status = m['status']
                    with st.container():
                        st.markdown(f"<div class='match-card'>", unsafe_allow_html=True)
                        col1, col2, col3 = st.columns([3,1,3])
                        col1.markdown(f"<h4>{m['home']}</h4>", unsafe_allow_html=True)
                        col3.markdown(f"<h4>{m['away']}</h4>", unsafe_allow_html=True)
                        if status == "approved":
                            col2.markdown("✅ Completed")
                        elif status == "pending":
                            col2.markdown("⏳ Pending approval")
                        else:
                            col2.markdown("⚔️ Not played")
                            with st.expander("📝 Fix Result", expanded=False):
                                is_home = (captain_team == m['home'])
                                s1 = st.number_input(f"{m['home']} Score", 0,20, key=f"cap_s1_{m['match_id']}")
                                s2 = st.number_input(f"{m['away']} Score", 0,20, key=f"cap_s2_{m['match_id']}")
                                p1=p2=0
                                if s1==s2 and "League" not in st.session_state.format:
                                    p1 = st.number_input(f"{m['home']} Pens",0,20, key=f"cap_p1_{m['match_id']}")
                                    p2 = st.number_input(f"{m['away']} Pens",0,20, key=f"cap_p2_{m['match_id']}")
                                gs1 = st.text_input(f"{m['home']} Scorers", placeholder="Messi (2), ...", key=f"cap_gs1_{m['match_id']}")
                                gs2 = st.text_input(f"{m['away']} Scorers", key=f"cap_gs2_{m['match_id']}")
                                ha = st.text_input(f"{m['home']} Assists", key=f"cap_ha_{m['match_id']}")
                                aa = st.text_input(f"{m['away']} Assists", key=f"cap_aa_{m['match_id']}")
                                hr = st.text_input(f"{m['home']} Reds", key=f"cap_hr_{m['match_id']}")
                                ar = st.text_input(f"{m['away']} Reds", key=f"cap_ar_{m['match_id']}")
                                comment = st.text_area("Comment (optional)", key=f"cap_comm_{m['match_id']}")
                                if st.button("Submit Report", key=f"cap_submit_{m['match_id']}"):
                                    if is_home:
                                        fix_match_result_by_captain(m['match_id'], m['home'], m['away'], s1, s2, gs1, gs2, ha, aa, hr, ar, p1, p2, captain_team, comment)
                                    else:
                                        fix_match_result_by_captain(m['match_id'], m['home'], m['away'], s2, s1, gs2, gs1, aa, ha, ar, hr, p2, p1, captain_team, comment)
                                    save_data_internal()
                                    st.success("Result submitted for approval!")
                                    safe_rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Admin / public match center: show all matches with admin result entry
            filter_team = st.selectbox("Filter team", ["All"] + st.session_state.active_teams)
            for i, fix in enumerate(st.session_state.fixtures):
                if len(fix) < 2: continue
                h,a = fix[0], fix[1]
                if filter_team != "All" and filter_team not in [h,a]: continue
                mid = f"{h}v{a}_{i}"
                status = get_match_result_status(mid)
                with st.container():
                    st.markdown(f"<div class='match-card'>", unsafe_allow_html=True)
                    c1,c2,c3 = st.columns([3,1,3])
                    c1.markdown(f"<h4>{h}</h4>", unsafe_allow_html=True)
                    c3.markdown(f"<h4>{a}</h4>", unsafe_allow_html=True)
                    if status == "approved":
                        res = st.session_state.results[mid]
                        score = f"{res[0]} - {res[1]}"
                        if len(res)>2: score += f" (P: {res[2]}-{res[3]})"
                        c2.markdown(f"<h3>{score}</h3>", unsafe_allow_html=True)
                    elif status == "pending":
                        fixed = st.session_state.fixed_results.get(mid, {})
                        score = f"{fixed.get('home_score',0)} - {fixed.get('away_score',0)}"
                        c2.markdown(f"<h3 style='color:#f59e0b'>{score} (Pending)</h3>", unsafe_allow_html=True)
                    else:
                        c2.markdown("<h3 style='color:#64748b'>VS</h3>", unsafe_allow_html=True)
                    if st.session_state.admin_unlock:
                        with st.expander("Enter/Reset Result"):
                            s1 = st.number_input(f"{h}",0,20, key=f"s1_{mid}", value=0)
                            s2 = st.number_input(f"{a}",0,20, key=f"s2_{mid}", value=0)
                            p1=p2=0
                            if s1==s2 and "League" not in st.session_state.format:
                                p1 = st.number_input(f"{h} Pens",0,20, key=f"p1_{mid}")
                                p2 = st.number_input(f"{a} Pens",0,20, key=f"p2_{mid}")
                            gs1 = st.text_input(f"{h} Scorers", key=f"gs1_{mid}")
                            gs2 = st.text_input(f"{a} Scorers", key=f"gs2_{mid}")
                            ha = st.text_input(f"{h} Assists", key=f"ha_{mid}")
                            aa = st.text_input(f"{a} Assists", key=f"aa_{mid}")
                            hr = st.text_input(f"{h} Reds", key=f"hr_{mid}")
                            ar = st.text_input(f"{a} Reds", key=f"ar_{mid}")
                            if st.button("Confirm Result", key=f"confirm_{mid}"):
                                update_match_result_safely(mid, h, a, s1, s2, p1, p2, gs1, gs2, ha, aa, hr, ar)
                                st.session_state.admin_approved_results[mid] = True
                                if mid in st.session_state.fixed_results: del st.session_state.fixed_results[mid]
                                st.session_state.pending_reports = [r for r in st.session_state.pending_reports if r['match_id'] != mid]
                                save_data_internal()
                                st.success("Result recorded!")
                                safe_rerun()
                            if status != "not_played" and st.button("Reset Match", key=f"reset_{mid}"):
                                if reset_match_result(mid):
                                    save_data_internal()
                                    st.warning("Match reset!")
                                    safe_rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
    
    # TAB 2: STATS (enhanced with advanced player rankings)
    with tabs[2]:
        st.subheader("⚽ Player Stats")
        if st.session_state.cumulative_player_stats:
            data = []
            for pid, stats in st.session_state.cumulative_player_stats.items():
                g = stats.get('G',0)
                a = stats.get('A',0)
                mvp = g*1.5 + a
                data.append({"Player":stats['Name'],"Team":stats['Team'],"Goals":g,"Assists":a,"MVP Index":round(mvp,1)})
            df = pd.DataFrame(data)
            if not df.empty:
                st.dataframe(df.sort_values("Goals", ascending=False), hide_index=True, use_container_width=True)
                st.subheader("Top Scorers")
                st.dataframe(df.nlargest(10, "Goals")[['Player','Team','Goals']], hide_index=True)
                st.subheader("MVP Index (Goals×1.5 + Assists)")
                st.dataframe(df.nlargest(10, "MVP Index")[['Player','Team','MVP Index']], hide_index=True)
            else:
                st.info("No player stats recorded.")
        else:
            st.info("No player stats yet.")
    
    # TAB 3: Tournament Info (as before)
    with tabs[3]:
        if "Survival" in st.session_state.format:
            st.markdown("### 💀 BATTLE ROYALE PROTOCOL")
            st.markdown("""
            - Points carry over forever.
            - After each round, survivors are shuffled.
            - Elimination phases: Phase 1 (5+ teams) bottom 2 eliminated; Phase 2 (4 teams) bottom 1; Phase 3 (3 teams) 2nd vs 3rd sudden death; Phase 4 final.
            """)
        else:
            st.markdown("### Tournament Info")
            st.write(f"**Format:** {st.session_state.format}")
            st.write(f"**Teams:** {len(st.session_state.teams)}")
            st.write(f"**Active:** {len(st.session_state.active_teams)}")
            if st.session_state.champion:
                st.success(f"**Champion:** {st.session_state.champion}")
    
    # TAB 4: Hall of Fame
    with tabs[4]:
        st.markdown("### 🏆 HALL OF FAME")
        if st.session_state.past_champions:
            for champ in st.session_state.past_champions:
                st.markdown(f"<div class='glass-card'>{champ['year']} – {champ['champion']} ({champ['format']})</div>", unsafe_allow_html=True)
        else:
            st.info("No past champions yet.")
    
    # TAB 5: CHARTS (NEW)
    with tabs[5]:
        if plotly_available:
            show_team_charts()
        else:
            st.warning("Install plotly to see charts: `pip install plotly`")
    
    # TAB 6: SCHEDULE (NEW)
    with tabs[6]:
        match_schedule_calendar()
    
    # TAB 7: QUICK ACTIONS (NEW, admin only)
    with tabs[7]:
        if st.session_state.admin_unlock:
            admin_quick_actions()
        else:
            st.info("Quick actions are available to admin only.")

# --- FOOTER ---
st.markdown("""<div class="footer">DLS ULTRA • CAPTAIN'S PORTAL • DESIGNED BY OLUWATIMILEYIN IGBINLOLA</div>""", unsafe_allow_html=True)
