from src.core.user import User


def to_user(leaderboard_entrant: dict) -> User:
    return User(
        user_id=leaderboard_entrant["user_id"],
        global_id=leaderboard_entrant["user_global_id"],
        external_id=leaderboard_entrant["user_external_id"],
        username=leaderboard_entrant["username"],
    )
