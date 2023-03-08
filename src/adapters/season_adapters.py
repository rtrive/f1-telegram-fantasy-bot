from datetime import datetime
from typing import List

from core.race import Race, RaceStatus


# TODO: Refactor using match case (it looks like ufmt doesn't work with that)
def to_race_status(race_state: str) -> RaceStatus:
    if race_state == "4":
        return RaceStatus.COMPLETED
    elif race_state == "0":
        return RaceStatus.SCHEDULED
    else:
        return RaceStatus.UNKNOWN


def to_race(game_period: dict) -> Race:
    return Race(
        race_id=game_period["MeetingNumber"],  # To be checked with second race
        name=game_period["MeetingName"],
        starts_at=datetime.strptime(
            game_period["SessionStartDateISO8601"], "%Y-%m-%dT%H:%M:%S%z"
        ).replace(
            tzinfo=None
        ),  # Check if timezone will be a problem
        status=to_race_status(game_period["MatchStatus"]),
    )


def to_races(
    json: dict,
) -> List[Race]:
    races = json["Data"]["Value"]
    response = []
    for race in races:
        if race["SessionType"] == "Race":
            response.append(to_race(race))
    return response
