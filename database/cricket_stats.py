
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PlayerStats:
    player_id: int
    name: str
    team: str
    matches: int
    runs: int
    wickets: int
    strike_rate: float
    economy: float
    avatar: str = "default.png"
    last_updated: str = datetime.now().isoformat()

class CricketStatsDB:
    def __init__(self, db):
        self.db = db  # InMemoryDB instance
        
    def add_player(self, player: PlayerStats):
        # Store player data with player_id as key
        self.db.insert(f"player:{player.player_id}", player.__dict__)
        # Index by team for team-wise queries
        self.db.insert(f"team:{player.team}:{player.player_id}", player.player_id)
        
    def get_player(self, player_id: int) -> Optional[PlayerStats]:
        data = self.db.search(f"player:{player_id}")
        return PlayerStats(**data) if data else None
        
    def update_player_stats(self, player_id: int, runs: int = 0, wickets: int = 0):
        player_data = self.db.search(f"player:{player_id}")
        if player_data:
            player = PlayerStats(**player_data)
            player.runs += runs
            player.wickets += wickets
            player.last_updated = datetime.now().isoformat()
            self.db.insert(f"player:{player_id}", player.__dict__)
            
    def get_all_players(self) -> List[PlayerStats]:
        all_data = self.db.get_all_data()
        players = []
        for key, value in all_data:
            if key.startswith("player:"):
                players.append(PlayerStats(**value))
        return sorted(players, key=lambda x: x.runs, reverse=True)
