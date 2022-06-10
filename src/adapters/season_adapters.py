from datetime import datetime
from typing import List

from src.core.race import Race


def to_race(game_period: dict) -> Race:
    return Race(
        race_id=game_period["id"],
        name=game_period["name"],
        starts_at=datetime.strptime(game_period["starts_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
    )


def to_races(
    json: dict,
) -> List[Race]:
    return [
        to_race(race)
        for race in json["partner_game"]["current_partner_season"]["game_periods"]
    ]
