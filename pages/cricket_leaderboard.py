
import streamlit as st
import pandas as pd
from database.cricket_stats import CricketStatsDB, PlayerStats
import json

def load_cricket_leaderboard():
    st.set_page_config(page_title="Cricket Match Leaderboard", layout="wide")
    
    # Initialize cricket stats database
    if 'cricket_db' not in st.session_state:
        st.session_state.cricket_db = CricketStatsDB(st.session_state.db)

    st.title("🏏 Cricket Match Leaderboard")
    
    # Tab-based navigation
    tab1, tab2, tab3 = st.tabs(["Leaderboard", "Add Player", "Update Stats"])
    
    with tab1:
        show_leaderboard()
        
    with tab2:
        add_new_player()
        
    with tab3:
        update_player_stats()

def show_leaderboard():
    players = st.session_state.cricket_db.get_all_players()
    if not players:
        st.info("No players in the database. Add some players to get started!")
        return
        
    df = pd.DataFrame([vars(p) for p in players])
    
    # Batting leaderboard
    st.subheader("🏏 Batting Leaderboard")
    batting_stats = df[['name', 'team', 'runs', 'strike_rate']]
    st.dataframe(batting_stats.sort_values('runs', ascending=False),
                use_container_width=True)
    
    # Bowling leaderboard
    st.subheader("🎯 Bowling Leaderboard")
    bowling_stats = df[['name', 'team', 'wickets', 'economy']]
    st.dataframe(bowling_stats.sort_values('wickets', ascending=False),
                use_container_width=True)

def add_new_player():
    st.subheader("Add New Player")
    with st.form("add_player"):
        name = st.text_input("Player Name")
        team = st.text_input("Team")
        player_id = st.number_input("Player ID", min_value=1, step=1)
        matches = st.number_input("Matches", min_value=0, step=1)
        runs = st.number_input("Runs", min_value=0, step=1)
        wickets = st.number_input("Wickets", min_value=0, step=1)
        strike_rate = st.number_input("Strike Rate", min_value=0.0, step=0.1)
        economy = st.number_input("Economy Rate", min_value=0.0, step=0.1)
        
        if st.form_submit_button("Add Player"):
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
            st.success(f"Added player {name} to the database!")

def update_player_stats():
    st.subheader("Update Player Stats")
    players = st.session_state.cricket_db.get_all_players()
    if not players:
        st.info("No players in the database!")
        return
        
    player_names = {p.player_id: p.name for p in players}
    selected_id = st.selectbox("Select Player", 
                             options=list(player_names.keys()),
                             format_func=lambda x: player_names[x])
    
    with st.form("update_stats"):
        runs = st.number_input("Additional Runs", min_value=0, step=1)
        wickets = st.number_input("Additional Wickets", min_value=0, step=1)
        
        if st.form_submit_button("Update Stats"):
            st.session_state.cricket_db.update_player_stats(
                selected_id, runs, wickets)
            st.success(f"Updated stats for {player_names[selected_id]}!")

if __name__ == "__main__":
    load_cricket_leaderboard()
