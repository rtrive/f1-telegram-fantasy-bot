from core.user import User


def to_user(leaderboard_entrant: dict) -> User:
    return User(
<<<<<<< HEAD
        user_id=leaderboard_entrant["guid"],
=======
        user_id=leaderboard_entrant["teamId"],
>>>>>>> 49ae8c7 (Users (#46))
        username=leaderboard_entrant["userName"],
    )
