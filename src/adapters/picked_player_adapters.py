from typing import List

import prettytable as pt
from core.picked_player import PickedPlayer
from core.race import Race


def to_picked_players(players: dict):
    def from_json_to_picked_players(json: dict) -> List[PickedPlayer]:
        return [
            to_picked_player(picked_player, players)
            for picked_player in json["picked_team"]["picked_players"]
        ]

    return from_json_to_picked_players


def to_picked_player(json: dict, players: dict) -> PickedPlayer:
    return PickedPlayer(
        player_id=json["player_id"],
        player_name=players[json["player_id"]],
        team_name=json["team_name"],
        team_abbreviation=json["team_abbreviation"],
        position=json["position"],
        position_abbreviation=json["position_abbreviation"],
        score=json["score"],
    )


def picked_players_to_pretty_table(
    picked_players: List[PickedPlayer], last_race: Race
) -> pt.PrettyTable:
    table = pt.PrettyTable()
    table.title = last_race.name
    table.field_names = ["Name", "Team", "Score"]
    for e in picked_players:
        table.add_row(
            [
                f"{e.player_name}({e.position_abbreviation})",
                e.team_abbreviation,
                e.score,
            ]
        )
    return table
