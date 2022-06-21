from core.picked_team import PickedTeam


def to_picked_team(json: dict) -> PickedTeam:
    return PickedTeam(
        name=json["picked_team"]["name"],
        score=json["picked_team"]["score"],
        picked_players=json["picked_team"]["picked_players"],
    )
