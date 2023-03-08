import datetime
from logging import Logger
from typing import List, Union

from adapters.leaderboard_adapters import to_league_standings
from adapters.picked_player_adapters import to_picked_players
from adapters.season_adapters import to_races
from core.error import Error
from core.league_standing import LeagueStanding
from core.picked_player import PickedPlayer
from core.race import Race, RaceStatus
from http_client import HTTPClient, HTTPMethod


class F1FantasyService:
    def __init__(
        self, http_client: HTTPClient, logger: Logger, cookies: str, league_id: str
    ):
        self.http_client = http_client
        self.logger = logger
        self.cookies = cookies
        self.league_id = league_id

    """Get the races for the season."""

    def get_season_races(self) -> Union[Error, List[Race]]:
        self.logger.debug("Getting all season")
        return self.http_client.make_request(
            method=HTTPMethod.GET,
            path="/feeds/schedule/raceday_en.json",
            headers={"Cookie": self.cookies},
            decoder=to_races,
        )

    """Get the last completed race"""

    def get_last_completed_race(
        self, season: int, now: datetime.datetime
    ) -> Union[Error, Race]:
        races = self.get_season_races(season=season)
        if not isinstance(races, Error):
            last_race = list(
                filter(
                    lambda race: race.start_timestamp < now
                    and race.status is RaceStatus.COMPLETED,
                    races,
                )
            )
            if last_race:
                return last_race.pop()
            else:
                return Error("There are no completed races")
        return races

    """Get the league standing"""

    def get_league_standing(self) -> Union[Error, LeagueStanding]:
        self.logger.debug("Get league standing")
        return self.http_client.make_request(
            method=HTTPMethod.GET,
            path=f"/services/user/leaderboard/{self.league_id}/pvtleagueuserrankget/1/2102210/0/1/1/10/",
            headers={"Cookie": self.cookies},
            decoder=to_league_standings,
        )

    """Get the last race standing"""

    def get_last_race_standing(self, race_id: int) -> Union[Error, LeagueStanding]:
        self.logger.debug("Getting last race standing")
        return self.http_client.make_request(
            method=HTTPMethod.GET,
            path=f"/f1/2022/leaderboards/leagues?v=1&game_period_id={race_id}&league_id={self.league_id}",  # noqa: E501
            headers={"Cookie": self.cookies},
            decoder=to_league_standings,
        )

    """Get the last race standing "of a single team"""

    def get_last_race_team_standing(
        self, race_id: int, user_id: str, f1_drivers: dict
    ) -> Union[Error, List[PickedPlayer]]:
        self.logger.debug("Getting last race team standing")
        return self.http_client.make_request(
            method=HTTPMethod.GET,
            path=f"/services/user/opponentteam/opponentgamedayplayerteamget/{race_id}/{user_id}/1/1/1",  # noqa: E501 TO BE CHECKED AFTER SECOND RACE
            headers={"Cookie": self.cookies},
            decoder=to_picked_players(f1_drivers),
        )
