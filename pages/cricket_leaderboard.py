
import streamlit as st
import pandas as pd
from database.cricket_stats import CricketStatsDB, PlayerStats

def load_cricket_leaderboard():
    st.title("🏏 Cricket Match Leaderboard")
    st.markdown("""
    <style>
    .stDataFrame {
        padding: 1rem;
        border-radius: 10px;
    }
    .stApp {
        background-color: transparent !important;
    }
    div[data-testid="stToolbar"] {
        display: none;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize cricket stats database
    if 'cricket_db' not in st.session_state:
        st.session_state.cricket_db = CricketStatsDB(st.session_state.db)

    tab1, tab2, tab3 = st.tabs(["📊 Leaderboard", "➕ Add Player", "🔄 Update Stats"])

    with tab1:
        show_leaderboard()

    with tab2:
        add_new_player()
        
    with tab3:
        update_player_stats()

def show_leaderboard():
    players = st.session_state.cricket_db.get_all_players()
    if not players:
        st.info("🏃 No players in the database. Add some players to get started!")
        return

    # Batting leaderboard
    st.subheader("🏏 Batting Leaderboard")
    batting_cols = ['Rank', 'Name', 'Team', 'Matches', 'Runs', 'Strike Rate']
    batting_data = []
    for idx, p in enumerate(sorted(players, key=lambda x: int(x.runs), reverse=True), 1):
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

def update_player_stats():
    st.subheader("Update Player Statistics")
    
    # Get all players for selection
    players = st.session_state.cricket_db.get_all_players()
    if not players:
        st.info("No players available to update. Please add players first.")
        return
        
    player_names = {f"{p.name} (ID: {p.player_id})": p.player_id for p in players}
    
    with st.form("update_stats", clear_on_submit=True):
        # Player selection
        selected_player = st.selectbox(
            "Select Player",
            options=list(player_names.keys()),
            key="update_player_select"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            additional_runs = st.number_input("Additional Runs", min_value=0, step=1)
            additional_matches = st.number_input("Additional Matches", min_value=0, step=1)
        with col2:
            additional_wickets = st.number_input("Additional Wickets", min_value=0, step=1)
            
        submitted = st.form_submit_button("Update Stats", use_container_width=True)
        
        if submitted and selected_player:
            try:
                player_id = player_names[selected_player]
                player = st.session_state.cricket_db.get_player(player_id)
                if player:
                    # Update player stats
                    player.runs += additional_runs
                    player.wickets += additional_wickets
                    player.matches += additional_matches
                    if additional_matches > 0:
                        # Update strike rate and economy if matches were played
                        player.strike_rate = (player.runs / player.matches) if player.matches > 0 else 0
                        player.economy = (player.wickets / player.matches) if player.matches > 0 else 0
                    
                    # Save updated player
                    st.session_state.cricket_db.add_player(player)
                    st.success(f"✅ Updated stats for {player.name}!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error updating player stats: {str(e)}")

def add_new_player():
    st.subheader("Add New Player")
    with st.form("add_player", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Player Name", key="name")
            player_id = st.number_input("Player ID", min_value=1, step=1)
            matches = st.number_input("Matches", min_value=0, step=1)
            balls_played = st.number_input("Balls Played", min_value=0, step=1)
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
                    balls_played=balls_played,
                    strike_rate=(runs * 100.0 / balls_played) if balls_played > 0 else 0.0,
                    economy=economy
                )
                st.session_state.cricket_db.add_player(player)
                st.success(f"✅ Added {name} to the database!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error adding player: {str(e)}")

if __name__ == "__main__":
    load_cricket_leaderboard()
