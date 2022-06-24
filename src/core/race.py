import datetime
from enum import Enum


class RaceStatus(Enum):
    UNKNOWN = "UNKNOWN"
    COMPLETED = "COMPLETED"
    ONGOING = "ONGOING"
    SCHEDULED = "SCHEDULED"


class Race:
    def __init__(
        self, race_id: int, name: str, starts_at: datetime.datetime, status: RaceStatus
    ):
        self.id = race_id
        self.name = name
        self.start_timestamp = starts_at
        self.status = status
