from core.user import User


def to_user(leaderboard_entrant: dict) -> User:
    return User(
        user_id=leaderboard_entrant["teamId"],
        username=leaderboard_entrant["userName"],
    )
