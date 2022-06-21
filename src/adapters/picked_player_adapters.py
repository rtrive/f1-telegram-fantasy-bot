from typing import List
from core.picked_player import PickedPlayer

import prettytable as pt


def to_picked_players(json: dict) -> List[PickedPlayer]:
    return [
        to_picked_player(picked_player)
        for picked_player in json["picked_team"]["picked_players"]
    ]


def to_picked_player(json: dict) -> PickedPlayer:
    return PickedPlayer(
        player_id=json["player_id"],
        team_name=json["team_name"],
        team_abbreviation=json["team_abbreviation"],
        position=json["position"],
        score=json["score"],
    )


def picker_players_to_pretty_table(
    picker_players: List[PickedPlayer],
) -> pt.PrettyTable:
    table = pt.PrettyTable(["Player ID", "Type", "Team", "Score"])
    for e in picker_players:
        table.add_row([e.player_id, e.position, e.team_abbreviation, e.score])
    return table
