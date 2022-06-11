from typing import List

from core.leaderboard_entrants import LeaderboardEntrant


class LeagueStanding:
    def __init__(self, entrants: List[LeaderboardEntrant]):
        self.entrants = entrants
