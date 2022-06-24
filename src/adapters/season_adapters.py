from datetime import datetime
from typing import List

from core.race import Race, RaceStatus


def to_race_status(race_state: str) -> RaceStatus:
    if race_state == "results":
        return RaceStatus.COMPLETED
    elif race_state == "default":
        return RaceStatus.SCHEDULED
    else:
        return RaceStatus.UNKNOWN


def to_race(game_period: dict) -> Race:
    return Race(
        race_id=game_period["id"],
        name=game_period["short_name"],
        starts_at=datetime.strptime(game_period["starts_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        status=to_race_status(game_period["state"]),
    )


def to_races(
    json: dict,
) -> List[Race]:
    return [
        to_race(race)
        for race in json["partner_game"]["current_partner_season"]["game_periods"]
    ]
