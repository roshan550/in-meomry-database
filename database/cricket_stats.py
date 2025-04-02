
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

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
    rank: int = 0
    avatar: str = "default.png"
    last_updated: str = datetime.now().isoformat()

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class CricketStatsDB:
    def __init__(self, db):
        self.db = db
        
    def add_player(self, player: PlayerStats):
        try:
            # Validate player ID is an integer
            player.player_id = int(player.player_id)
            # Serialize player data to JSON string
            player_data = json.dumps(player.to_dict())
            key = f"player:{player.player_id}"
            
            # Use WAL to log the operation
            self.db.wal.log_operation("insert", key, player_data)
            self.db.insert(key, player_data)
            
            # Also log team mapping
            team_key = f"team:{player.team}:{player.player_id}"
            self.db.wal.log_operation("insert", team_key, str(player.player_id))
            self.db.insert(team_key, str(player.player_id))
            
        except ValueError as e:
            raise ValueError(f"Invalid player data: {str(e)}")
        except Exception as e:
            raise Exception(f"Error adding player: {str(e)}")
        
    def get_player(self, player_id: int) -> Optional[PlayerStats]:
        data = self.db.search(f"player:{player_id}")
        if data:
            try:
                player_dict = json.loads(data)
                return PlayerStats.from_dict(player_dict)
            except:
                return None
        return None
        
    def update_player_stats(self, player_id: int, runs: int = 0, wickets: int = 0):
        player = self.get_player(player_id)
        if player:
            player.runs += runs
            player.wickets += wickets
            player.matches += 1 if runs > 0 or wickets > 0 else 0
            player.last_updated = datetime.now().isoformat()
            self.add_player(player)
            return True
        return False
            
    def get_all_players(self) -> List[PlayerStats]:
        all_data = self.db.get_all_data()
        players = []
        for key, value in all_data:
            if isinstance(key, str) and key.startswith("player:"):
                try:
                    player_dict = json.loads(value)
                    players.append(PlayerStats.from_dict(player_dict))
                except:
                    continue
        # Sort by runs, ensure runs is treated as integer
        try:
            players.sort(key=lambda x: int(x.runs) if isinstance(x.runs, (int, str)) else 0, reverse=True)
        except Exception as e:
            print(f"Error sorting players: {str(e)}")
        return players
