from core.user import User


class LeaderboardEntrant:
    def __init__(self, user: User, score: str, team_name: str):
        self.user = user
        self.score = score
        self.team_name = team_name
