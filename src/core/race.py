import datetime


class Race:
    def __init__(self, race_id: int, name: str, starts_at: datetime.datetime):
        self.id = race_id
        self.name = name
        self.start_timestamp = starts_at
