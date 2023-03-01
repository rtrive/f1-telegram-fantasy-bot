from datetime import datetime
from typing import List

from core.race import Race, RaceStatus


# TODO: Refactor using match case (it looks like ufmt doesn't work with that)
def to_race_status(race_state: str) -> RaceStatus:
    if race_state == "1":
        return RaceStatus.COMPLETED
    elif race_state == "0":
        return RaceStatus.SCHEDULED
    else:
        return RaceStatus.UNKNOWN


def to_race(game_period: dict) -> Race:
    return Race(
        race_id=game_period["RaceId"],
        name=game_period["MeetingLocation"],
        starts_at=datetime.strptime(
            game_period["SessionStartDate"], "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        status=to_race_status(game_period["MatchStatus"]),
    )


def to_races(
    json: dict,
) -> List[Race]:

    races = json["Data"]["Value"]
    response = []
    for race in races:
        if race["SessionType"] == "Race":
            response.append(race)
    return response
