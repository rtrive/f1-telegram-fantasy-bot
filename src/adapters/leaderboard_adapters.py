from typing import List

from src.core.leaderboard_entrants import LeaderboardEntrant
from src.core.league_standing import LeagueStanding
from src.adapters.user_adapters import to_user


def to_leaderboard_entrant(leaderboard_entrant: dict) -> LeaderboardEntrant:
    return LeaderboardEntrant(
        user=to_user(leaderboard_entrant),
        score=leaderboard_entrant["score"],
        team_name=leaderboard_entrant["team_name"],
    )


def to_leaderboard_entrants(
        leaderboard_entrants: List[dict],
) -> List[LeaderboardEntrant]:
    entrants = []
    for e in leaderboard_entrants:
        entrants.append(to_leaderboard_entrant(e))
    return entrants


def to_league_standings(json: dict) -> LeagueStanding:
    return LeagueStanding(
        entrants=to_leaderboard_entrants(
            json["leaderboard"]["leaderboard_entrants"]
        )
    )
