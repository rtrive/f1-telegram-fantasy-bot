class PickedPlayer:
    def __init__(
        self,
        player_id: int,
        team_name: str,
        team_abbreviation: str,
        position: str,
        score: int,
    ):
        self.player_id = player_id
        self.team_name = team_name
        self.team_abbreviation = team_abbreviation
        self.position = position
        self.score = score
