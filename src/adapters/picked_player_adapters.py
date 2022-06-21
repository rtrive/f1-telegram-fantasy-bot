from typing import List

import prettytable as pt
import requests  # type: ignore
from core.picked_player import PickedPlayer

f1_all_players = {}


def player_id_to_name() -> dict:
    global f1_all_players
    if not f1_all_players:
        f1_players_req = requests.get(
            url="https://fantasy-api.formula1.com/f1/2022/players"
        )
        f1_players = (f1_players_req.json())["players"]
        f1_all_players = {}
        for f1_player in f1_players:
            f1_all_players[f1_player["id"]] = f1_player["last_name"]
        return f1_all_players
    return f1_all_players


def to_picked_players(json: dict) -> List[PickedPlayer]:
    return [
        to_picked_player(picked_player)
        for picked_player in json["picked_team"]["picked_players"]
    ]


def to_picked_player(json: dict) -> PickedPlayer:
    players = player_id_to_name()
    return PickedPlayer(
        player_id=json["player_id"],
        player_name=players[json["player_id"]],
        team_name=json["team_name"],
        team_abbreviation=json["team_abbreviation"],
        position=json["position"],
        position_abbreviation=json["position_abbreviation"],
        score=json["score"],
    )


def picker_players_to_pretty_table(
    picker_players: List[PickedPlayer],
) -> pt.PrettyTable:
    table = pt.PrettyTable(["Name", "Team", "Score"])
    for e in picker_players:
        table.add_row(
            [
                f"{e.player_name}({e.position_abbreviation})",
                e.team_abbreviation,
                e.score,
            ]
        )
    return table
