from typing import Optional


class Credentials:
    def __init__(self, username: Optional[str], password: Optional[str]):
        self.username = username
        self.password = password
