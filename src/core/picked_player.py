class PickedPlayer:
    def __init__(
        self,
        player_id: int,
        player_name: str,
        team_name: str,
        team_abbreviation: str,
        position: str,
        position_abbreviation: str,
        score: int,
    ):
        self.player_id = player_id
        self.player_name = player_name
        self.team_name = team_name
        self.team_abbreviation = team_abbreviation
        self.score = score
