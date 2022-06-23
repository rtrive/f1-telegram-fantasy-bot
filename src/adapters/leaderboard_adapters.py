from typing import List

import prettytable as pt
from adapters.user_adapters import to_user

from core.leaderboard_entrants import LeaderboardEntrant
from core.league_standing import LeagueStanding
from telegram import InlineKeyboardButton


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
        entrants=to_leaderboard_entrants(json["leaderboard"]["leaderboard_entrants"])
    )


def league_standing_to_pretty_table(standing: LeagueStanding) -> pt.PrettyTable:
    table = pt.PrettyTable(["Username", "Points"])
    for e in standing.entrants:
        table.add_row([e.user.username, e.score])
    return table


def entrant_to_pretty_input(standing: LeagueStanding) -> List[InlineKeyboardButton]:
    keyboard = []
    tmp = []
    for i in range(len(standing.entrants)):
        if i % 3 == 0:
            keyboard.append(tmp)
            tmp = []
        tmp.append(
            InlineKeyboardButton(
                standing.entrants[i].user.username,
                callback_data=standing.entrants[i].user.global_id,
            )
        )
    keyboard.append(tmp)
    return keyboard
