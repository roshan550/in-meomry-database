
import streamlit as st
import pandas as pd
from database.cricket_stats import CricketStatsDB, PlayerStats

def show_cricket_page():
    st.title("🏏 Cricket Match Leaderboard")
    st.markdown("""
    <style>
    .stDataFrame {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize cricket stats database
    if 'cricket_db' not in st.session_state:
        st.session_state.cricket_db = CricketStatsDB(st.session_state.db)

    tab1, tab2 = st.tabs(["📊 Leaderboard", "➕ Add Player"])

    with tab1:
        show_leaderboard()

    with tab2:
        add_new_player()

def show_leaderboard():
    players = st.session_state.cricket_db.get_all_players()
    if not players:
        st.info("🏃 No players in the database. Add some players to get started!")
        return

    # Batting leaderboard
    st.subheader("🏏 Batting Leaderboard")
    batting_cols = ['Rank', 'Name', 'Team', 'Matches', 'Runs', 'Strike Rate']
    batting_data = []
    for idx, p in enumerate(sorted(players, key=lambda x: x.runs, reverse=True), 1):
        batting_data.append([
            idx, p.name, p.team, p.matches, p.runs, f"{p.strike_rate:.2f}"
        ])
    batting_df = pd.DataFrame(batting_data, columns=batting_cols)
    st.dataframe(batting_df, use_container_width=True, hide_index=True)

    # Bowling leaderboard
    st.subheader("🎯 Bowling Leaderboard")
    bowling_cols = ['Rank', 'Name', 'Team', 'Matches', 'Wickets', 'Economy']
    bowling_data = []
    for idx, p in enumerate(sorted(players, key=lambda x: x.wickets, reverse=True), 1):
        bowling_data.append([
            idx, p.name, p.team, p.matches, p.wickets, f"{p.economy:.2f}"
        ])
    bowling_df = pd.DataFrame(bowling_data, columns=bowling_cols)
    st.dataframe(bowling_df, use_container_width=True, hide_index=True)

def add_new_player():
    st.subheader("Add New Player")
    with st.form("add_player", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Player Name", key="name")
            player_id = st.number_input("Player ID", min_value=1, step=1)
            matches = st.number_input("Matches", min_value=0, step=1)
            strike_rate = st.number_input("Strike Rate", min_value=0.0, step=0.1)
        with col2:
            team = st.text_input("Team", key="team")
            runs = st.number_input("Runs", min_value=0, step=1)
            wickets = st.number_input("Wickets", min_value=0, step=1)
            economy = st.number_input("Economy Rate", min_value=0.0, step=0.1)
        
        submitted = st.form_submit_button("Add Player", use_container_width=True)
        if submitted and name and team:
            try:
                player = PlayerStats(
                    player_id=player_id,
                    name=name,
                    team=team,
                    matches=matches,
                    runs=runs,
                    wickets=wickets,
                    strike_rate=strike_rate,
                    economy=economy
                )
                st.session_state.cricket_db.add_player(player)
                st.success(f"✅ Added {name} to the database!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error adding player: {str(e)}")

if __name__ == "__main__":
    show_cricket_page()
