import sys
from typing import Optional


class Credentials:
    def __init__(self, username: Optional[str], password: Optional[str]):
        self.username = username if username is not None else sys.exit("Missing username")
        self.password = password if password is not None else sys.exit("Missing password")
