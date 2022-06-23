from core.picked_player import PickedPlayer


class PickedTeam:
    def __init__(self, name: str, score: int, picked_players: PickedPlayer):
        self.name = name
        self.score = score
        self.picked_players = picked_players
